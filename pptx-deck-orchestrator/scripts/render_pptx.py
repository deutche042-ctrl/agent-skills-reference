#!/usr/bin/env python3
"""Render a PPTX to PDF, per-slide PNGs, a montage, and a JSON report."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
from typing import Any

try:
    from PIL import Image, ImageDraw
except ImportError as exc:  # pragma: no cover - exercised only in dependency-missing environments.
    raise SystemExit("Pillow is required: install the 'Pillow' Python package.") from exc


class RenderError(RuntimeError):
    """Raised when a render dependency or conversion step fails."""


MAC_SOFFICE = Path("/Applications/LibreOffice.app/Contents/MacOS/soffice")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def artifact_record(
    path: Path,
    *,
    page: int | None = None,
    dimensions: dict[str, int] | None = None,
) -> dict[str, Any]:
    record: dict[str, Any] = {
        "path": str(path.resolve()),
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if page is not None:
        record["page"] = page
    if dimensions is not None:
        record["dimensions"] = dimensions
    return record


def find_executable(name: str, explicit: str | Path | None = None) -> Path:
    if explicit is not None:
        candidate = Path(explicit).expanduser().resolve()
        if candidate.is_file() and os.access(candidate, os.X_OK):
            return candidate
        raise RenderError(f"Explicit {name} executable is missing or not executable: {candidate}")

    discovered = shutil.which(name)
    if discovered:
        return Path(discovered).resolve()
    if name == "soffice" and MAC_SOFFICE.is_file() and os.access(MAC_SOFFICE, os.X_OK):
        return MAC_SOFFICE
    raise RenderError(
        f"Cannot find {name}. Install LibreOffice for soffice and Poppler for pdftoppm, "
        f"or pass --{name} /absolute/path/to/executable."
    )


def _run(command: list[str], *, timeout: int) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(
            command,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired as exc:
        raise RenderError(f"Command timed out after {timeout}s: {' '.join(command)}") from exc
    except OSError as exc:
        raise RenderError(f"Cannot run command {' '.join(command)}: {exc}") from exc
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "no diagnostic output").strip()
        raise RenderError(f"Command failed ({result.returncode}): {' '.join(command)}\n{detail}")
    return result


def prepare_output_dir(pptx: Path, requested: str | Path | None = None) -> Path:
    if requested is not None:
        output = Path(requested).expanduser().resolve()
        if output.exists() and not output.is_dir():
            raise RenderError(f"Output path exists and is not a directory: {output}")
        if output.exists() and any(output.iterdir()):
            raise RenderError(f"Output directory must be empty: {output}")
        output.mkdir(parents=True, exist_ok=True)
        return output

    base = pptx.with_name(f"{pptx.stem}-rendered")
    candidate = base
    suffix = 2
    while candidate.exists():
        candidate = base.with_name(f"{base.name}-{suffix}")
        suffix += 1
    candidate.mkdir(parents=True)
    return candidate


def _convert_to_pdf(pptx: Path, output_dir: Path, soffice: Path, timeout: int) -> Path:
    with tempfile.TemporaryDirectory(prefix="pptx-max-render-") as temp_dir:
        temp = Path(temp_dir)
        profile = temp / "lo-profile"
        profile.mkdir()
        _run(
            [
                str(soffice),
                f"-env:UserInstallation={profile.as_uri()}",
                "--headless",
                "--convert-to",
                "pdf",
                "--outdir",
                str(temp),
                str(pptx),
            ],
            timeout=timeout,
        )
        candidates = sorted(temp.glob("*.pdf"))
        if not candidates:
            raise RenderError("LibreOffice reported success but produced no PDF.")
        destination = output_dir / f"{pptx.stem}.pdf"
        shutil.copy2(candidates[0], destination)
    return destination


def _page_number(path: Path) -> int:
    match = re.search(r"-(\d+)\.png$", path.name)
    return int(match.group(1)) if match else 0


def _render_pages(pdf: Path, output_dir: Path, pdftoppm: Path, dpi: int, timeout: int) -> list[Path]:
    slides_dir = output_dir / "slides"
    slides_dir.mkdir()
    prefix = slides_dir / "slide"
    _run([str(pdftoppm), "-png", "-r", str(dpi), str(pdf), str(prefix)], timeout=timeout)
    raw = sorted(slides_dir.glob("slide-*.png"), key=_page_number)
    if not raw:
        raise RenderError("pdftoppm produced no slide images.")
    rendered: list[Path] = []
    for index, source in enumerate(raw, start=1):
        destination = slides_dir / f"slide-{index:03d}.png"
        if source != destination:
            source.rename(destination)
        rendered.append(destination)
    return rendered


def build_montage(
    images: list[Path],
    output: Path,
    *,
    columns: int = 4,
    thumb_width: int = 480,
    gutter: int = 24,
    label_height: int = 30,
) -> Path:
    if not images:
        raise RenderError("Cannot build a montage without slide images.")
    if columns < 1 or thumb_width < 80:
        raise RenderError("Montage columns must be >= 1 and thumbnail width must be >= 80.")

    thumbs: list[Image.Image] = []
    try:
        for path in images:
            with Image.open(path) as source:
                image = source.convert("RGB")
                target_height = max(1, round(image.height * thumb_width / image.width))
                thumbs.append(image.resize((thumb_width, target_height), Image.Resampling.LANCZOS))

        cell_height = max(image.height for image in thumbs)
        rows = math.ceil(len(thumbs) / columns)
        canvas_width = columns * thumb_width + (columns + 1) * gutter
        canvas_height = rows * (cell_height + label_height) + (rows + 1) * gutter
        canvas = Image.new("RGB", (canvas_width, canvas_height), (232, 234, 238))
        draw = ImageDraw.Draw(canvas)

        for index, image in enumerate(thumbs, start=1):
            row = (index - 1) // columns
            column = (index - 1) % columns
            x = gutter + column * (thumb_width + gutter)
            y = gutter + row * (cell_height + label_height + gutter)
            y_image = y + (cell_height - image.height) // 2
            canvas.paste(image, (x, y_image))
            draw.text((x, y + cell_height + 6), f"Slide {index}", fill=(28, 32, 38))

        output.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(output, format="PNG", optimize=True)
    finally:
        for image in thumbs:
            image.close()
    return output


def render_pptx(
    pptx: str | Path,
    *,
    output_dir: str | Path | None = None,
    soffice: str | Path | None = None,
    pdftoppm: str | Path | None = None,
    dpi: int = 120,
    columns: int = 4,
    thumb_width: int = 480,
    timeout: int = 180,
    font_inventory: str | Path | None = None,
) -> dict[str, Any]:
    source = Path(pptx).expanduser().resolve()
    if not source.is_file():
        raise RenderError(f"PPTX file not found: {source}")
    if source.suffix.lower() != ".pptx":
        raise RenderError(f"Expected a .pptx file: {source}")
    if not 36 <= dpi <= 600:
        raise RenderError("DPI must be between 36 and 600.")

    soffice_path = find_executable("soffice", soffice)
    pdftoppm_path = find_executable("pdftoppm", pdftoppm)
    output = prepare_output_dir(source, output_dir)
    pdf = _convert_to_pdf(source, output, soffice_path, timeout)
    pages = _render_pages(pdf, output, pdftoppm_path, dpi, timeout)
    montage = build_montage(pages, output / "montage.png", columns=columns, thumb_width=thumb_width)

    dimensions: list[dict[str, int]] = []
    for page in pages:
        with Image.open(page) as image:
            dimensions.append({"width": image.width, "height": image.height})
    slide_artifacts = [
        artifact_record(page, page=index, dimensions=dimensions[index - 1])
        for index, page in enumerate(pages, start=1)
    ]
    report: dict[str, Any] = {
        "version": "2.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_pptx": str(source),
        "source_sha256": sha256_file(source),
        "output_dir": str(output),
        "tools": {"soffice": str(soffice_path), "pdftoppm": str(pdftoppm_path), "pillow": Image.__version__},
        "dpi": dpi,
        "slide_count": len(pages),
        "pdf": str(pdf),
        "slides": [str(path) for path in pages],
        "slide_dimensions": dimensions,
        "montage": str(montage),
        "artifacts": {
            "pdf": artifact_record(pdf),
            "slides": slide_artifacts,
            "montage": artifact_record(montage),
        },
    }
    if font_inventory is not None:
        inventory_path = Path(font_inventory).expanduser().resolve()
        if not inventory_path.is_file():
            raise RenderError(f"Font inventory not found: {inventory_path}")
        report["font_inventory"] = artifact_record(inventory_path)
    report_path = output / "render-report.json"
    report["report"] = str(report_path)
    report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Render PPTX to PDF, slide PNGs, and a montage.")
    parser.add_argument("pptx", type=Path, help="PPTX to render")
    parser.add_argument("--output-dir", type=Path, help="New or empty output directory")
    parser.add_argument("--soffice", type=Path, help="Explicit soffice executable")
    parser.add_argument("--pdftoppm", type=Path, help="Explicit pdftoppm executable")
    parser.add_argument("--dpi", type=int, default=120, help="PNG render DPI, 36-600")
    parser.add_argument("--columns", type=int, default=4, help="Montage columns")
    parser.add_argument("--thumb-width", type=int, default=480, help="Montage thumbnail width")
    parser.add_argument("--timeout", type=int, default=180, help="Per-command timeout in seconds")
    parser.add_argument("--font-inventory", type=Path, help="V2.3 font-inventory.json to bind into the render report")
    parser.add_argument("--json", action="store_true", help="Emit JSON report to stdout")
    args = parser.parse_args(argv)

    try:
        report = render_pptx(
            args.pptx,
            output_dir=args.output_dir,
            soffice=args.soffice,
            pdftoppm=args.pdftoppm,
            dpi=args.dpi,
            columns=args.columns,
            thumb_width=args.thumb_width,
            timeout=args.timeout,
            font_inventory=args.font_inventory,
        )
    except RenderError as exc:
        if args.json:
            print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2))
        else:
            print(f"Render failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Rendered {report['slide_count']} slides")
        print(f"Montage: {report['montage']}")
        print(f"Report: {report['report']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
