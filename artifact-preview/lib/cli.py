"""argparse-based CLI for the artifact-preview skill.

Subcommands:
    render <file>      → render and emit JSON summary to stdout
    info <hash|dir>    → dump manifest as JSON
    list               → list cached previews under default root
    clean [<hash>]     → remove a cached preview (or --all)

The CLI is invoked by the model via the hub's ``bin/preview`` entry
point (which handles ``sys.path`` setup before importing this module).
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import logging
import shutil
import sys
from pathlib import Path
from typing import Any

from ._types import Manifest, RenderOptions
from .cache import default_output_root
from .dispatch import detect_kind, render
from .manifest import load_manifest


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="preview",
        description=(
            "Render workspace artifacts to text + screenshots that the model "
            "can consume via Read. Run `preview render <file>` to render; "
            "the JSON output points at the manifest, text dump, thumbnail, "
            "and collage(s)."
        ),
    )
    p.add_argument(
        "--log-level",
        default="WARNING",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("render", help="render an artifact to text + images")
    r.add_argument("path", help="file path inside the workspace")
    r.add_argument("--output-root", help="override .preview/ root (env: ARTIFACT_PREVIEW_HOME)")
    r.add_argument("--max-pages", type=int, default=12)
    r.add_argument("--page-range", help='1-indexed selector, e.g. "1-5,10"')
    r.add_argument("--no-collage", action="store_true")
    r.add_argument("--no-thumbnail", action="store_true")
    r.add_argument("--text-only", action="store_true",
                   help="skip image rendering; emit text + manifest only")
    r.add_argument("--force", action="store_true", help="ignore cache; re-render")
    r.add_argument("--jpeg-quality", type=int, default=85)
    r.add_argument("--out-max-dim", type=int, default=2048)

    i = sub.add_parser("info", help="dump the manifest for a previously rendered file")
    i.add_argument("target", help="cache hash, output dir, or original file path")
    i.add_argument("--output-root")

    sub.add_parser("list", help="list cached previews")

    c = sub.add_parser("clean", help="remove a cached preview")
    c.add_argument("hash", nargs="?", help="cache hash; omit with --all to clean everything")
    c.add_argument("--all", action="store_true")
    c.add_argument("--output-root")

    return p


def _resolve_target(target: str, root: Path) -> Path | None:
    """Map a CLI ``info`` target into an output dir."""
    cand = Path(target)
    if cand.is_dir() and (cand / "manifest.json").exists():
        return cand
    cand2 = root / target
    if cand2.is_dir() and (cand2 / "manifest.json").exists():
        return cand2
    if cand.is_file():
        from .cache import compute_source_hash

        h = compute_source_hash(cand)
        cand3 = root / h
        if (cand3 / "manifest.json").exists():
            return cand3
    return None


def _cmd_render(args: argparse.Namespace) -> int:
    opts = RenderOptions(
        max_pages=args.max_pages,
        collage=not args.no_collage,
        page_range=args.page_range,
        thumbnail=not args.no_thumbnail,
        text_only=args.text_only,
        force=args.force,
        jpeg_quality=args.jpeg_quality,
        out_max_dim=args.out_max_dim,
    )
    src = Path(args.path)
    if not src.exists():
        print(json.dumps({"ok": False, "error": f"file not found: {src}"}), file=sys.stderr)
        return 2
    kind = detect_kind(src)
    if kind == "unknown":
        print(json.dumps({
            "ok": False,
            "error": f"unsupported extension: {src.suffix}",
            "hint": "supported: pdf, pptx, docx, xlsx, html, png/jpg, txt/md, zip",
        }), file=sys.stderr)
        return 3

    manifest = render(src, args.output_root, opts)
    out = {
        "ok": True,
        "output_dir": manifest.output_dir,
        "manifest": str(Path(manifest.output_dir) / "manifest.json"),
        "kind": manifest.kind,
        "page_count": manifest.page_count,
        "rendered_page_count": manifest.rendered_page_count,
        "collage_count": manifest.collage_count,
        "extracted_text_chars": manifest.extracted_text_chars,
        "text": (
            str(Path(manifest.output_dir) / manifest.text_relpath)
            if manifest.text_relpath else None
        ),
        "thumbnail": (
            str(Path(manifest.output_dir) / manifest.thumbnail_relpath)
            if manifest.thumbnail_relpath else None
        ),
        "collages": [
            str(Path(manifest.output_dir) / c.relpath) for c in manifest.collages
        ],
        "pages": [
            str(Path(manifest.output_dir) / p.relpath) for p in manifest.pages
        ],
        "warnings": manifest.warnings,
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


def _cmd_info(args: argparse.Namespace) -> int:
    root = Path(args.output_root) if args.output_root else default_output_root()
    out_dir = _resolve_target(args.target, root)
    if out_dir is None:
        print(json.dumps({"ok": False, "error": f"no preview found for: {args.target}"}),
              file=sys.stderr)
        return 4
    m = load_manifest(out_dir)
    print(json.dumps(_manifest_payload(m), indent=2, ensure_ascii=False))
    return 0


def _manifest_payload(m: Manifest) -> dict[str, Any]:
    """Serialize Manifest dataclass for the ``info`` subcommand."""
    return {
        "schema_version": m.schema_version,
        "source_path": m.source_path,
        "source_filename": m.source_filename,
        "source_hash": m.source_hash,
        "source_size_bytes": m.source_size_bytes,
        "kind": m.kind,
        "rendered_at_utc": m.rendered_at_utc,
        "output_dir": m.output_dir,
        "page_count": m.page_count,
        "rendered_page_count": m.rendered_page_count,
        "collage_count": m.collage_count,
        "extracted_text_chars": m.extracted_text_chars,
        "text_relpath": m.text_relpath,
        "thumbnail_relpath": m.thumbnail_relpath,
        "pages": [dataclasses.asdict(p) for p in m.pages],
        "collages": [dataclasses.asdict(c) for c in m.collages],
        "warnings": list(m.warnings),
        "options": dict(m.options),
        "summary": dict(m.summary),
    }


def _cmd_list(_args: argparse.Namespace) -> int:
    root = default_output_root()
    if not root.exists():
        print(json.dumps({"ok": True, "root": str(root), "entries": []}, indent=2))
        return 0
    entries = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        mf = child / "manifest.json"
        if not mf.exists():
            continue
        try:
            m = load_manifest(child)
            entries.append({
                "hash": child.name,
                "source_filename": m.source_filename,
                "kind": m.kind,
                "rendered_at_utc": m.rendered_at_utc,
                "page_count": m.page_count,
                "collage_count": m.collage_count,
            })
        except Exception as exc:
            entries.append({"hash": child.name, "error": str(exc)})
    print(json.dumps({"ok": True, "root": str(root), "entries": entries},
                     indent=2, ensure_ascii=False))
    return 0


def _cmd_clean(args: argparse.Namespace) -> int:
    root = Path(args.output_root) if args.output_root else default_output_root()
    if args.all:
        if root.exists():
            shutil.rmtree(root)
        print(json.dumps({"ok": True, "removed": str(root)}))
        return 0
    if not args.hash:
        print(json.dumps({"ok": False, "error": "specify <hash> or --all"}),
              file=sys.stderr)
        return 5
    target = root / args.hash
    if not target.exists():
        print(json.dumps({"ok": False, "error": f"no such cache entry: {args.hash}"}),
              file=sys.stderr)
        return 6
    shutil.rmtree(target)
    print(json.dumps({"ok": True, "removed": str(target)}))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(levelname)s %(name)s: %(message)s",
    )
    if args.cmd == "render":
        return _cmd_render(args)
    if args.cmd == "info":
        return _cmd_info(args)
    if args.cmd == "list":
        return _cmd_list(args)
    if args.cmd == "clean":
        return _cmd_clean(args)
    parser.print_help()
    return 1
