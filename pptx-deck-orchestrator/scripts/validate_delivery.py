#!/usr/bin/env python3
"""Normalize default delivery to one validated user-visible PPTX."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Iterable


def validate_delivery(
    user_visible_files: Iterable[str | Path],
    *,
    expected_pptx: str | Path | None = None,
    require_exists: bool = True,
) -> dict[str, Any]:
    files = [Path(item).expanduser() for item in user_visible_files]
    issues: list[dict[str, Any]] = []
    chosen: Path | None = None

    if expected_pptx is not None:
        chosen = Path(expected_pptx).expanduser().resolve()
    else:
        candidates = [path.resolve() for path in files if path.suffix.casefold() == ".pptx"]
        unique_candidates = list(dict.fromkeys(candidates))
        if len(unique_candidates) == 1:
            chosen = unique_candidates[0]
        else:
            issues.append({
                "code": "DELIVERY_PPTX_AMBIGUOUS",
                "message": "Delivery normalization needs one unambiguous PPTX candidate.",
                "pptx_candidates": [str(path) for path in unique_candidates],
            })

    if chosen is not None:
        if chosen.suffix.casefold() != ".pptx":
            issues.append({
                "code": "DELIVERY_FILE_NOT_PPTX",
                "message": "The validated delivery file must end in .pptx case-insensitively.",
                "path": str(chosen),
            })
        if require_exists and not chosen.is_file():
            issues.append({
                "code": "DELIVERY_PPTX_MISSING",
                "message": "The validated delivery PPTX does not exist.",
                "path": str(chosen),
            })

    allowed = not issues
    chosen_resolved = chosen.resolve() if chosen is not None else None
    suppressed = [
        str(path)
        for path in files
        if chosen_resolved is None or path.resolve() != chosen_resolved
    ]
    return {
        "version": "2.3.2",
        "status": "PASS" if allowed else "BLOCKED",
        "allowed": allowed,
        "input_user_visible_files": [str(path) for path in files],
        "user_visible_file_count": 1 if allowed else 0,
        "user_visible_files": [str(chosen)] if allowed and chosen is not None else [],
        "suppressed_user_visible_files": suppressed,
        "changed": allowed and ([path.resolve() for path in files] != [chosen_resolved]),
        "issues": issues,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Normalize default delivery to one validated .pptx file.")
    parser.add_argument("user_visible_files", nargs="*")
    parser.add_argument("--expected-pptx", type=Path)
    parser.add_argument("--no-require-exists", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_delivery(
        args.user_visible_files,
        expected_pptx=args.expected_pptx,
        require_exists=not args.no_require_exists,
    )
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"Delivery status: {result['status']}")
        print(f"Allowed: {str(result['allowed']).lower()}")
        for issue in result["issues"]:
            print(f"[{issue['code']}] {issue['message']}")
    return 0 if result["allowed"] else 3


if __name__ == "__main__":
    sys.exit(main())
