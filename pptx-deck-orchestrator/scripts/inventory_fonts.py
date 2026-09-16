#!/usr/bin/env python3
"""Create the reproducible font inventory consumed by the V2.3 gate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any


def _load_manifest(path: Path) -> list[str]:
    payload: Any = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("fonts")
    if not isinstance(payload, list) or not all(isinstance(item, str) for item in payload):
        raise ValueError("font manifest must be an array or an object with a fonts array")
    return payload


def _fontconfig_fonts(executable: str) -> list[str]:
    result = subprocess.run(
        [executable, "--format", "%{family}\n", ":"],
        check=False,
        capture_output=True,
        text=True,
        timeout=60,
    )
    if result.returncode != 0:
        raise RuntimeError((result.stderr or result.stdout or "fc-list failed").strip())
    fonts: set[str] = set()
    for line in result.stdout.splitlines():
        for family in line.split(","):
            if family.strip():
                fonts.add(family.strip())
    return sorted(fonts, key=str.casefold)


def build_inventory(manifest: Path | None = None) -> dict[str, Any]:
    if manifest is not None:
        fonts = sorted(set(_load_manifest(manifest)), key=str.casefold)
        provider = {"type": "manifest", "path": str(manifest.resolve())}
    else:
        executable = shutil.which("fc-list")
        if not executable:
            raise RuntimeError("fc-list is unavailable; pass --manifest with a trusted font list")
        fonts = _fontconfig_fonts(executable)
        provider = {"type": "fontconfig", "executable": str(Path(executable).resolve())}
    return {
        "version": "2.3",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "provider": provider,
        "fonts": fonts,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Create a PPTX Max V2.3 font inventory.")
    parser.add_argument("--manifest", type=Path, help="Trusted JSON font list when Fontconfig is unavailable")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        inventory = build_inventory(args.manifest)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(inventory, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    except (OSError, ValueError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Font inventory failed: {exc}", file=sys.stderr)
        return 2
    print(args.output.resolve())
    return 0


if __name__ == "__main__":
    sys.exit(main())
