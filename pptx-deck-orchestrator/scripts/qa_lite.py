#!/usr/bin/env python3
"""Fast, cache-aware PPTX QA for PPTX Lite V2.3.2."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any

from render_pptx import RenderError, render_pptx, sha256_file
from validate_delivery import validate_delivery
from validate_pptx import validate_pptx


EXIT_CODES = {"PASS": 0, "REVIEW_REQUIRED": 2, "BLOCKED": 3, "TOOL_FAILURE": 4}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _inside(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _load_valid_render(render_dir: Path, source_hash: str, slide_count: int) -> dict[str, Any] | None:
    report_path = render_dir / "render-report.json"
    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(report, dict):
        return None
    if report.get("source_sha256") != source_hash or report.get("slide_count") != slide_count:
        return None
    artifacts = report.get("artifacts")
    montage_record = artifacts.get("montage") if isinstance(artifacts, dict) else None
    if not isinstance(montage_record, dict) or not isinstance(montage_record.get("path"), str):
        return None
    montage = Path(montage_record["path"]).expanduser().resolve()
    if not _inside(montage, render_dir) or not montage.is_file():
        return None
    if montage_record.get("sha256") != sha256_file(montage):
        return None
    slides = artifacts.get("slides") if isinstance(artifacts, dict) else None
    if not isinstance(slides, list) or len(slides) != slide_count:
        return None
    for page, record in enumerate(slides, start=1):
        if not isinstance(record, dict) or record.get("page") != page or not isinstance(record.get("path"), str):
            return None
        slide = Path(record["path"]).expanduser().resolve()
        if not _inside(slide, render_dir) or not slide.is_file():
            return None
    return report


def _find_cached_render(run_dir: Path, source_hash: str, slide_count: int) -> tuple[dict[str, Any] | None, Path | None]:
    for render_dir in sorted(run_dir.glob("rendered*")):
        if not render_dir.is_dir():
            continue
        report = _load_valid_render(render_dir, source_hash, slide_count)
        if report is not None:
            return report, render_dir
    return None, None


def _next_render_dir(run_dir: Path) -> Path:
    candidate = run_dir / "rendered"
    index = 2
    while candidate.exists():
        candidate = run_dir / f"rendered-{index}"
        index += 1
    return candidate


def run_lite_qa(
    pptx: Path,
    work_dir: Path,
    *,
    expected_aspect_ratio: str | None,
    visual_status: str,
    visual_note: str,
    user_visible_files: list[Path],
    dpi: int,
    columns: int,
    thumb_width: int,
    timeout: int,
) -> dict[str, Any]:
    started = perf_counter()
    source = pptx.expanduser().resolve()
    if not source.is_file() or source.suffix.lower() != ".pptx":
        raise ValueError(f"PPTX does not exist or has the wrong suffix: {source}")
    source_hash = sha256_file(source)
    root = work_dir.expanduser().resolve()
    run_dir = root / source_hash[:12]
    run_dir.mkdir(parents=True, exist_ok=True)

    static_started = perf_counter()
    static = validate_pptx(source, expected_aspect_ratio=expected_aspect_ratio)
    static_seconds = perf_counter() - static_started
    _write_json(run_dir / "static-validation.json", static)
    summary = static["summary"]
    delivery_check = validate_delivery(user_visible_files, expected_pptx=source)
    risk_pages = sorted({
        issue.get("slide")
        for issue in static.get("issues", [])
        if issue.get("severity") == "review_required" and isinstance(issue.get("slide"), int)
    })

    render_report: dict[str, Any] | None = None
    render_dir: Path | None = None
    render_seconds = 0.0
    render_cache_reused = False
    render_error: str | None = None
    if not summary.get("tool_failures") and not summary.get("blocking"):
        render_report, render_dir = _find_cached_render(run_dir, source_hash, summary["slide_count"])
        if render_report is not None:
            render_cache_reused = True
        else:
            render_dir = _next_render_dir(run_dir)
            render_started = perf_counter()
            try:
                render_report = render_pptx(
                    source,
                    output_dir=render_dir,
                    dpi=dpi,
                    columns=columns,
                    thumb_width=thumb_width,
                    timeout=timeout,
                )
            except (OSError, RenderError) as exc:
                render_error = str(exc)
            render_seconds = perf_counter() - render_started

    if summary.get("tool_failures") or render_error:
        status = "TOOL_FAILURE"
    elif summary.get("blocking"):
        status = "BLOCKED"
    elif not delivery_check["allowed"]:
        status = "BLOCKED"
    elif visual_status == "blocked":
        status = "BLOCKED"
    elif visual_status == "pass" and delivery_check["allowed"] and render_report is not None:
        status = "PASS"
    else:
        status = "REVIEW_REQUIRED"

    montage = render_report.get("montage") if isinstance(render_report, dict) else None
    result: dict[str, Any] = {
        "version": "2.3.2-lite",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": "lite",
        "status": status,
        "exit_code": EXIT_CODES[status],
        "deliverable_allowed": status == "PASS",
        "next_action": {
            "PASS": "deliver",
            "REVIEW_REQUIRED": "inspect_montage_then_rerun_with_visual_status_pass",
            "BLOCKED": "repair_then_rerun",
            "TOOL_FAILURE": "fix_tooling_then_rerun",
        }[status],
        "pptx": str(source),
        "pptx_sha256": source_hash,
        "slide_count": summary.get("slide_count", 0),
        "expected_aspect_ratio": expected_aspect_ratio,
        "static_summary": summary,
        "risk_pages": risk_pages,
        "visual_status": visual_status,
        "visual_note": visual_note,
        "delivery_check": delivery_check,
        "montage": montage,
        "render_dir": str(render_dir) if render_dir else None,
        "render_cache_reused": render_cache_reused,
        "render_error": render_error,
        "timing_seconds": {
            "static": round(static_seconds, 3),
            "render": round(render_seconds, 3),
            "total": round(perf_counter() - started, 3),
        },
        "qa_report": str(run_dir / "qa-report.json"),
    }
    _write_json(run_dir / "qa-report.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the fast PPTX Lite V2.3.2 QA gate.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--expected-aspect-ratio")
    parser.add_argument("--visual-status", choices=("pending", "pass", "blocked"), default="pending")
    parser.add_argument("--visual-note", default="")
    parser.add_argument(
        "--user-visible-file",
        action="append",
        type=Path,
        default=[],
        help="Optional planned outgoing file; repeat as needed. Non-PPTX extras are suppressed.",
    )
    parser.add_argument("--dpi", type=int, default=60)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=280)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_lite_qa(
            args.pptx,
            args.work_dir,
            expected_aspect_ratio=args.expected_aspect_ratio,
            visual_status=args.visual_status,
            visual_note=args.visual_note,
            user_visible_files=args.user_visible_file,
            dpi=args.dpi,
            columns=args.columns,
            thumb_width=args.thumb_width,
            timeout=args.timeout,
        )
    except (OSError, ValueError) as exc:
        print(f"Lite QA failed: {exc}", file=sys.stderr)
        return EXIT_CODES["TOOL_FAILURE"]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"QA status: {result['status']}")
        print(f"Deliverable allowed: {str(result['deliverable_allowed']).lower()}")
        if result.get("montage"):
            print(f"Montage: {result['montage']}")
        if result.get("risk_pages"):
            print("Risk pages: " + ", ".join(map(str, result["risk_pages"])))
        print(f"Render cache reused: {str(result['render_cache_reused']).lower()}")
        print(f"Delivery allowlist: {result['delivery_check']['status']}")
        print(f"Report: {result['qa_report']}")
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
