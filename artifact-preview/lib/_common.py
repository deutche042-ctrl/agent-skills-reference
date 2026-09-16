"""Shared error / dep-import / locator helpers for ``artifact-preview``.

Mirrors the protocol used by ``verifier-hub/lib/_common.py`` so the model
sees a consistent JSON shape:

    {"ok": true,  "tool": "render", "result": {...}}
    {"ok": false, "tool": "render", "error": {"code": "DEP_MISSING", "msg": "..."}}

When a third-party package is missing on the VM (``PyMuPDF``,
``python-pptx``, ``openpyxl``, ``Pillow``, ``playwright``) the CLI returns
``DEP_MISSING`` so the model can ``pip install`` and retry — the same
fallback verifier-hub uses.

System-level deps (``LibreOffice`` for PPTX, ``Chromium`` for HTML) are
*not* installable from the model side; for those, the renderer returns
an empty page list and a ``warnings`` entry so the rest of the manifest
(text + collages from other inputs) stays useful.
"""
from __future__ import annotations

import json
import sys
from typing import Any


# ── Error codes ────────────────────────────────────────────────────────


class ErrCode:
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    NOT_A_FILE = "NOT_A_FILE"
    BAD_EXT = "BAD_EXT"
    PARSE_ERROR = "PARSE_ERROR"
    DEP_MISSING = "DEP_MISSING"
    BAD_ARGS = "BAD_ARGS"
    INTERNAL = "INTERNAL"


class ArtifactPreviewError(Exception):
    """Recoverable, JSON-serializable error from a render subcommand."""

    def __init__(self, code: str, msg: str) -> None:
        super().__init__(msg)
        self.code = code
        self.msg = msg


# ── lazy_import (verifier-hub-compatible) ──────────────────────────────


def lazy_import(module_name: str, hint: str | None = None) -> Any:
    """Import ``module_name`` on demand; raise ``DEP_MISSING`` if absent.

    Identical contract to ``verifier-hub/lib/_common.py:lazy_import``: the
    error message includes a ``hint`` (typically ``pip install <pkg>``)
    so the model can self-heal.
    """
    try:
        return __import__(module_name, fromlist=["*"])
    except ImportError as exc:
        msg = f"required dependency missing: {module_name} ({exc})"
        if hint:
            msg += f" — install hint: {hint}"
        raise ArtifactPreviewError(ErrCode.DEP_MISSING, msg) from exc


# ── JSON output protocol ──────────────────────────────────────────────


def ok(tool: str, result: dict, **extra: Any) -> dict:
    payload = {"ok": True, "tool": tool, "result": result}
    payload.update(extra)
    return payload


def err(tool: str, code: str, msg: str, **extra: Any) -> dict:
    payload = {"ok": False, "tool": tool, "error": {"code": code, "msg": msg}}
    payload.update(extra)
    return payload


def emit(payload: dict) -> None:
    """Write ``payload`` as a single JSON line to stdout + flush."""
    sys.stdout.write(json.dumps(payload, ensure_ascii=False))
    sys.stdout.write("\n")
    sys.stdout.flush()
