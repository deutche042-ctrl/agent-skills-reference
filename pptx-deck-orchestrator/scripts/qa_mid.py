#!/usr/bin/env python3
"""Risk-sampled, cache-aware PPTX QA for the V2.3.2 Mid profile."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any, Iterable

from inventory_fonts import build_inventory
from qa_lite import EXIT_CODES, _find_cached_render, _next_render_dir, _write_json
from render_pptx import RenderError, render_pptx, sha256_file
from validate_delivery import validate_delivery
from validate_pptx import validate_pptx


MAX_REVIEW_PAGES = 6
PRIORITY_CODES = {
    "AUTOFIT_GROWTH_REVIEW",
    "BODY_FONT_TOO_SMALL",
    "CHART_SOURCE_MISSING",
    "FOOTER_TEXT_OVERFLOW",
    "OUT_OF_BOUNDS_REVIEW",
    "SHAPE_TO_FIT_BODY_TEXT",
    "TABLE_FOOTER_REVIEW",
    "TEXT_FRAME_NEAR_CAPACITY",
}


def _pick_even(values: Iterable[int], limit: int) -> list[int]:
    ordered = sorted(set(values))
    if limit <= 0 or not ordered:
        return []
    if len(ordered) <= limit:
        return ordered
    if limit == 1:
        return [ordered[len(ordered) // 2]]
    indexes = {round(index * (len(ordered) - 1) / (limit - 1)) for index in range(limit)}
    return [ordered[index] for index in sorted(indexes)]


def _build_review_scope(static: dict[str, Any]) -> list[dict[str, Any]]:
    summary = static.get("summary", {})
    slide_count = int(summary.get("slide_count", 0) or 0)
    if slide_count < 1:
        return []
    reasons: dict[int, set[str]] = {}

    def add(page: int, reason: str) -> None:
        if 1 <= page <= slide_count and len(reasons) < MAX_REVIEW_PAGES:
            reasons.setdefault(page, set()).add(reason)
        elif page in reasons:
            reasons[page].add(reason)

    add(1, "opening")
    add(slide_count, "closing")

    for page in _pick_even(summary.get("chart_pages", []), 3):
        add(page, "chart")

    issue_pages: dict[int, dict[str, Any]] = {}
    for issue in static.get("issues", []):
        page = issue.get("slide")
        if issue.get("severity") != "review_required" or not isinstance(page, int):
            continue
        entry = issue_pages.setdefault(page, {"score": 0, "codes": set()})
        code = str(issue.get("code", "review"))
        entry["score"] += 3 if code in PRIORITY_CODES else 1
        entry["codes"].add(code)
    ranked = sorted(issue_pages.items(), key=lambda item: (-item[1]["score"], item[0]))
    for page, entry in ranked:
        if page not in reasons and len(reasons) >= MAX_REVIEW_PAGES:
            break
        codes = ",".join(sorted(entry["codes"])[:3])
        add(page, f"static-risk:{codes}")

    coverage_target = min(4, slide_count, MAX_REVIEW_PAGES)
    for page in _pick_even(range(1, slide_count + 1), coverage_target):
        if len(reasons) >= MAX_REVIEW_PAGES:
            break
        add(page, "coverage-sample")

    return [
        {"page": page, "reasons": sorted(page_reasons)}
        for page, page_reasons in sorted(reasons.items())
    ]


def _parse_reviewed_pages(value: str, scope_pages: set[int]) -> set[int]:
    normalized = value.strip().lower()
    if not normalized:
        return set()
    if normalized == "scope":
        return set(scope_pages)
    pages: set[int] = set()
    for part in value.split(","):
        part = part.strip()
        if not part:
            continue
        pages.add(int(part))
    return pages


def _font_check(static: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    inventory_path = run_dir / "font-inventory.json"
    inventory: dict[str, Any] | None = None
    cache_reused = False
    if inventory_path.is_file():
        try:
            loaded = json.loads(inventory_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict) and isinstance(loaded.get("fonts"), list):
                inventory = loaded
                cache_reused = True
        except (OSError, json.JSONDecodeError):
            inventory = None
    if inventory is None:
        try:
            inventory = build_inventory()
            _write_json(inventory_path, inventory)
        except (OSError, RuntimeError, ValueError) as exc:
            return {
                "status": "unavailable",
                "message": str(exc),
                "cache_reused": False,
                "inventory": None,
                "used": static.get("summary", {}).get("fonts", []),
                "missing": [],
            }

    used = [font for font in static.get("summary", {}).get("fonts", []) if not font.startswith("+")]
    if static.get("summary", {}).get("has_embedded_fonts"):
        missing: list[str] = []
        status = "pass"
    else:
        installed = {font.casefold() for font in inventory.get("fonts", []) if isinstance(font, str)}
        missing = [font for font in used if font.casefold() not in installed]
        status = "review_required" if missing else "pass"
    return {
        "status": status,
        "cache_reused": cache_reused,
        "inventory": str(inventory_path),
        "used": used,
        "missing": missing,
    }


def run_mid_qa(
    pptx: Path,
    work_dir: Path,
    *,
    expected_aspect_ratio: str | None,
    visual_status: str,
    visual_note: str,
    reviewed_pages_raw: str,
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
    run_dir = work_dir.expanduser().resolve() / source_hash[:12]
    run_dir.mkdir(parents=True, exist_ok=True)

    static_started = perf_counter()
    static = validate_pptx(source, expected_aspect_ratio=expected_aspect_ratio)
    static_seconds = perf_counter() - static_started
    _write_json(run_dir / "static-validation.json", static)
    summary = static["summary"]

    scope = _build_review_scope(static)
    scope_path = run_dir / "review-scope.json"
    _write_json(scope_path, {"version": "2.3.2-mid", "max_pages": MAX_REVIEW_PAGES, "pages": scope})
    scope_pages = {item["page"] for item in scope}
    try:
        reviewed_pages = _parse_reviewed_pages(reviewed_pages_raw, scope_pages)
    except ValueError as exc:
        raise ValueError("--reviewed-pages must be 'scope' or a comma-separated page list") from exc

    font_started = perf_counter()
    font_check = _font_check(static, run_dir) if not summary.get("tool_failures") else {"status": "skipped"}
    font_seconds = perf_counter() - font_started
    delivery_check = validate_delivery(user_visible_files, expected_pptx=source)

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

    review_complete = reviewed_pages == scope_pages and bool(scope_pages)
    if summary.get("tool_failures") or render_error:
        status = "TOOL_FAILURE"
    elif summary.get("blocking"):
        status = "BLOCKED"
    elif not delivery_check["allowed"]:
        status = "BLOCKED"
    elif visual_status == "blocked":
        status = "BLOCKED"
    elif visual_status == "pass" and review_complete and delivery_check["allowed"] and render_report is not None:
        status = "PASS"
    else:
        status = "REVIEW_REQUIRED"

    result: dict[str, Any] = {
        "version": "2.3.2-mid",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "profile": "mid",
        "status": status,
        "exit_code": EXIT_CODES[status],
        "deliverable_allowed": status == "PASS",
        "next_action": {
            "PASS": "deliver",
            "REVIEW_REQUIRED": "inspect_montage_and_review_scope_then_confirm",
            "BLOCKED": "repair_then_rerun",
            "TOOL_FAILURE": "fix_tooling_then_rerun",
        }[status],
        "pptx": str(source),
        "pptx_sha256": source_hash,
        "slide_count": summary.get("slide_count", 0),
        "expected_aspect_ratio": expected_aspect_ratio,
        "static_summary": summary,
        "font_check": font_check,
        "visual_status": visual_status,
        "visual_note": visual_note,
        "delivery_check": delivery_check,
        "review_scope": scope,
        "review_scope_file": str(scope_path),
        "reviewed_pages": sorted(reviewed_pages),
        "review_complete": review_complete,
        "montage": render_report.get("montage") if isinstance(render_report, dict) else None,
        "render_dir": str(render_dir) if render_dir else None,
        "render_cache_reused": render_cache_reused,
        "render_error": render_error,
        "timing_seconds": {
            "static": round(static_seconds, 3),
            "font_inventory": round(font_seconds, 3),
            "render": round(render_seconds, 3),
            "total": round(perf_counter() - started, 3),
        },
        "qa_report": str(run_dir / "qa-report-mid.json"),
    }
    _write_json(run_dir / "qa-report-mid.json", result)
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run the risk-sampled PPTX Mid V2.3.2 QA gate.")
    parser.add_argument("pptx", type=Path)
    parser.add_argument("--work-dir", type=Path, required=True)
    parser.add_argument("--expected-aspect-ratio")
    parser.add_argument("--visual-status", choices=("pending", "pass", "blocked"), default="pending")
    parser.add_argument("--visual-note", default="")
    parser.add_argument("--reviewed-pages", default="")
    parser.add_argument(
        "--user-visible-file",
        action="append",
        type=Path,
        default=[],
        help="Optional planned outgoing file; repeat as needed. Non-PPTX extras are suppressed.",
    )
    parser.add_argument("--dpi", type=int, default=84)
    parser.add_argument("--columns", type=int, default=4)
    parser.add_argument("--thumb-width", type=int, default=360)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    try:
        result = run_mid_qa(
            args.pptx,
            args.work_dir,
            expected_aspect_ratio=args.expected_aspect_ratio,
            visual_status=args.visual_status,
            visual_note=args.visual_note,
            reviewed_pages_raw=args.reviewed_pages,
            user_visible_files=args.user_visible_file,
            dpi=args.dpi,
            columns=args.columns,
            thumb_width=args.thumb_width,
            timeout=args.timeout,
        )
    except (OSError, ValueError) as exc:
        print(f"Mid QA failed: {exc}", file=sys.stderr)
        return EXIT_CODES["TOOL_FAILURE"]
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"QA status: {result['status']}")
        print(f"Deliverable allowed: {str(result['deliverable_allowed']).lower()}")
        if result.get("montage"):
            print(f"Montage: {result['montage']}")
        print("Review pages: " + ", ".join(str(item["page"]) for item in result["review_scope"]))
        print(f"Render cache reused: {str(result['render_cache_reused']).lower()}")
        print(f"Delivery allowlist: {result['delivery_check']['status']}")
        print(f"Report: {result['qa_report']}")
    return result["exit_code"]


if __name__ == "__main__":
    sys.exit(main())
