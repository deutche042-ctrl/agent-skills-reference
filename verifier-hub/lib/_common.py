"""Shared output protocol + helpers for the verifier CLI.

Every ``cmd_*`` function in lib/<family>.py SHOULD return a plain dict and
let the dispatcher in bin/verifier wrap it via ``ok()`` / ``err()`` and
``emit()`` it.  Functions MAY raise ``VerifierError`` to bubble a
recoverable error up; anything else propagates as an unhandled exception.

Output schema (one JSON object on stdout, no extra text):

    {"ok": true,  "tool": "<family>.<sub>", "result": {...}, "evidence": {...}}
    {"ok": false, "tool": "<family>.<sub>", "error": {"code": "...", "msg": "..."}}

``evidence`` is intentionally separate from ``result``: ``result`` is the
machine-readable answer; ``evidence`` is the human-quotable string the
judge can paste into ``questionnaire.md`` rationale.
"""
from __future__ import annotations

import json
import mimetypes
import os
import sys
from typing import Any


# ---------------------------------------------------------------------------
# Error codes — kept as a flat enum so SKILL.md / agent prompts can list them.
# ---------------------------------------------------------------------------

class ErrCode:
    FILE_NOT_FOUND = "FILE_NOT_FOUND"
    NOT_A_FILE = "NOT_A_FILE"
    BAD_EXT = "BAD_EXT"
    PARSE_ERROR = "PARSE_ERROR"
    LOCATOR_INVALID = "LOCATOR_INVALID"
    NOT_FOUND = "NOT_FOUND"
    DEP_MISSING = "DEP_MISSING"
    BAD_ARGS = "BAD_ARGS"
    INTERNAL = "INTERNAL"


class VerifierError(Exception):
    """Recoverable, JSON-serializable error from a verifier subcommand."""
    def __init__(self, code: str, msg: str) -> None:
        super().__init__(msg)
        self.code = code
        self.msg = msg


# ---------------------------------------------------------------------------
# Output wrappers
# ---------------------------------------------------------------------------

def ok(tool: str, result: Any, evidence: Any | None = None) -> dict:
    out: dict = {"ok": True, "tool": tool, "result": result}
    if evidence is not None:
        out["evidence"] = evidence
    return out


def err(tool: str, code: str, msg: str) -> dict:
    return {"ok": False, "tool": tool, "error": {"code": code, "msg": msg}}


def emit(payload: dict) -> int:
    """Write a single-line JSON to stdout; return shell exit code."""
    print(json.dumps(payload, ensure_ascii=False))
    return 0 if payload.get("ok") else 1


# ---------------------------------------------------------------------------
# Path / file helpers
# ---------------------------------------------------------------------------

def resolve_path(p: str) -> str:
    """Expand ``~`` and resolve to absolute path, but do NOT require existence."""
    return os.path.abspath(os.path.expanduser(p))


def require_file(path: str, expected_exts: tuple[str, ...] | None = None) -> str:
    """Validate that ``path`` is an existing file and (optionally) has an allowed extension.

    Raises VerifierError on any failure.  Returns the absolute path.
    """
    abs_path = resolve_path(path)
    if not os.path.exists(abs_path):
        raise VerifierError(ErrCode.FILE_NOT_FOUND, f"file does not exist: {abs_path}")
    if not os.path.isfile(abs_path):
        raise VerifierError(ErrCode.NOT_A_FILE, f"not a regular file: {abs_path}")
    if expected_exts:
        ext = os.path.splitext(abs_path)[1].lower()
        if ext not in expected_exts:
            raise VerifierError(
                ErrCode.BAD_EXT,
                f"unsupported extension {ext!r} for {abs_path}; expected one of {list(expected_exts)}",
            )
    return abs_path


def detect_kind(path: str) -> str:
    """Cheap file-kind detector based on extension + mimetype.

    Returns one of: ``xlsx``, ``docx``, ``pdf``, ``pptx``, ``text``, ``image``,
    ``binary``, ``unknown``.  Used by ``file_io.artifact_list``.
    """
    ext = os.path.splitext(path)[1].lower()
    if ext in (".xlsx", ".xlsm"):
        return "xlsx"
    if ext in (".docx", ".docm"):
        return "docx"
    if ext == ".pdf":
        return "pdf"
    if ext in (".pptx", ".pptm"):
        return "pptx"
    if ext in (".md", ".txt", ".csv", ".html", ".htm", ".json", ".yaml", ".yml", ".log"):
        return "text"
    if ext in (".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"):
        return "image"
    mime, _ = mimetypes.guess_type(path)
    if mime and mime.startswith("text/"):
        return "text"
    if mime and mime.startswith("image/"):
        return "image"
    if mime is None:
        return "unknown"
    return "binary"


def file_size(path: str) -> int:
    try:
        return os.path.getsize(path)
    except OSError:
        return -1


# ---------------------------------------------------------------------------
# Lazy-import helper — used by lib/<family>.py whose dependency is heavy /
# may not always be installed (e.g. pdfplumber).
# ---------------------------------------------------------------------------

def lazy_import(module_name: str, hint: str | None = None) -> Any:
    """Import a module on demand; raise VerifierError(DEP_MISSING) if unavailable."""
    try:
        return __import__(module_name, fromlist=["*"])
    except ImportError as e:
        msg = f"required dependency missing: {module_name} ({e})"
        if hint:
            msg += f" — install hint: {hint}"
        raise VerifierError(ErrCode.DEP_MISSING, msg) from e


# ---------------------------------------------------------------------------
# Locator parsing — the same JSON-blob locator works across families:
#   xlsx: {"sheet": "P&L", "cell": "F12"}
#   docx: {"heading_regex": "区位优势", "min_chars": 80}
# Subcommands accept either ``--locator '<json>'`` or family-specific shorthand
# flags.  Helper kept thin to avoid a per-family JSON-blob bikeshed.
# ---------------------------------------------------------------------------

def parse_locator(raw: str | None) -> dict:
    """Parse a ``--locator`` JSON string; return ``{}`` on None.  Raises BAD_ARGS."""
    if raw is None or raw == "":
        return {}
    try:
        loc = json.loads(raw)
    except json.JSONDecodeError as e:
        raise VerifierError(ErrCode.LOCATOR_INVALID, f"--locator must be JSON: {e}") from e
    if not isinstance(loc, dict):
        raise VerifierError(ErrCode.LOCATOR_INVALID, "--locator JSON must be an object")
    return loc


# ---------------------------------------------------------------------------
# Numeric tolerance — shared between xlsx.assert_value, num.assert and rubric.numeric.
# ---------------------------------------------------------------------------

def in_tolerance(actual: Any, expected: float, tol_abs: float | None,
                 tol_rel: float | None) -> tuple[bool, str]:
    """Return (passed, explanation).  At least one of tol_abs/tol_rel must be given."""
    try:
        a = float(actual)
    except (TypeError, ValueError):
        return False, f"actual value {actual!r} is not numeric"
    e = float(expected)
    if tol_abs is None and tol_rel is None:
        # Default: exact equality
        return a == e, f"expected {e}, actual {a} (exact)"
    if tol_abs is not None and abs(a - e) <= tol_abs:
        return True, f"expected {e}, actual {a}, |Δ|={abs(a - e):.6g} ≤ tol_abs={tol_abs}"
    if tol_rel is not None and e != 0 and abs(a - e) / abs(e) <= tol_rel:
        return True, f"expected {e}, actual {a}, |Δ|/|exp|={abs(a - e) / abs(e):.6g} ≤ tol_rel={tol_rel}"
    parts = [f"expected {e}, actual {a}, |Δ|={abs(a - e):.6g}"]
    if tol_abs is not None:
        parts.append(f"tol_abs={tol_abs}")
    if tol_rel is not None:
        parts.append(f"tol_rel={tol_rel}")
    return False, "; ".join(parts)


# ---------------------------------------------------------------------------
# Evidence helper — keep produced evidence shapes consistent.
# ---------------------------------------------------------------------------

def evidence(file: str | None = None, locator: Any | None = None,
             quote: str | None = None, **extras: Any) -> dict:
    """Build a uniform evidence dict.  ``quote`` is a short human-readable string."""
    out: dict = {}
    if file:
        out["file"] = file
    if locator is not None:
        out["locator"] = locator
    if quote is not None:
        out["quote"] = quote
    for k, v in extras.items():
        out[k] = v
    return out
