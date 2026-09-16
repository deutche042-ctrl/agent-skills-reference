"""Compatibility fixes for the pinned ``seed_browser_use`` public contract.

The runtime image owns the complete SDK.  This module only patches contract
regressions that can be repaired at the one-shot cell boundary without
replacing or hiding any of the SDK's public APIs.
"""

from __future__ import annotations

import difflib
import functools
import re
from types import ModuleType
from typing import Any, Optional, Tuple


_MISSING = object()
_UNKNOWN_API_RES = (
    re.compile(
        r"module ['\"]seed_browser_use['\"] has no attribute ['\"]([^'\"]+)['\"]"
    ),
    re.compile(
        r"unknown (?:bu )?api[^A-Za-z0-9_]+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE
    ),
)
_STALE_ERROR_FRAGMENTS = (
    "session stale",
    "session is stale",
    "stale session",
    "invalid session",
    "session not found",
    "no active session",
    "session closed",
    "session detached",
    "detached session",
    "target closed",
)


class BUContractError(RuntimeError):
    """Runtime error carrying a stable BU error code."""

    def __init__(self, code: str, detail: str) -> None:
        super().__init__(detail)
        self.code = code


def _wrap_javascript(expression: str) -> str:
    stripped = expression.lstrip()
    statement_prefixes = (
        "const ",
        "let ",
        "var ",
        "function ",
        "class ",
        "if ",
        "for ",
        "while ",
        "switch ",
        "try ",
    )
    has_top_level_return = re.match(r"^return(?:\s|;|\(|$)", stripped) is not None
    if has_top_level_return or any(
        stripped.startswith(prefix) for prefix in statement_prefixes
    ):
        return "(() => {\n" + expression + "\n})()"
    return expression


def _install_js(module: ModuleType) -> None:
    original = getattr(module, "js", None)
    if not callable(original):
        return

    @functools.wraps(original)
    def compatible_js(expression: str, *args: Any, **kwargs: Any) -> Any:
        return original(_wrap_javascript(expression), *args, **kwargs)

    module.js = compatible_js


def _install_type(module: ModuleType) -> None:
    original = getattr(module, "type", None)
    if not callable(original):
        return

    @functools.wraps(original)
    def compatible_type(
        ref: Any,
        text: Any = _MISSING,
        *,
        submit: Optional[bool] = None,
    ) -> Any:
        if text is _MISSING:
            print("BU type usage: bu.type(ref, text, *, submit=None)")
            return None
        return original(ref, text, submit=submit)

    module.type = compatible_type


def _install_navigate(module: ModuleType) -> None:
    original = getattr(module, "navigate", None)
    cdp = getattr(module, "cdp", None)
    if not callable(original) or not callable(cdp):
        return

    @functools.wraps(original)
    def compatible_navigate(destination: Any, *args: Any, **kwargs: Any) -> Any:
        action = str(destination).strip().lower()
        if action in {"back", "forward"}:
            try:
                history = cdp("Page.getNavigationHistory")
            except Exception:
                history = None
            if isinstance(history, dict):
                entries = history.get("entries")
                current_index = history.get("currentIndex")
                if isinstance(entries, list) and isinstance(current_index, int):
                    unavailable = (
                        current_index <= 0
                        if action == "back"
                        else current_index >= len(entries) - 1
                    )
                    if unavailable:
                        raise BUContractError(
                            "BU_NAV_WAIT_TIMEOUT",
                            f"Cannot navigate {action}: no matching history entry became available.",
                        )
        return original(destination, *args, **kwargs)

    module.navigate = compatible_navigate


def install_contract_fixes(module: ModuleType) -> None:
    """Install idempotent compatibility wrappers on the imported SDK module."""

    if getattr(module, "__mcp_vm_contract_fixes__", False):
        return
    _install_js(module)
    _install_type(module)
    _install_navigate(module)
    module.__mcp_vm_contract_fixes__ = True


def normalize_contract_error(
    exc: BaseException,
    module: Optional[ModuleType],
) -> Optional[Tuple[str, str]]:
    """Map cross-layer exceptions to stable, actionable BU contract errors."""

    message = str(exc).strip()
    unknown_match = next(
        (
            pattern.search(message)
            for pattern in _UNKNOWN_API_RES
            if pattern.search(message)
        ),
        None,
    )
    if unknown_match:
        name = unknown_match.group(1)
        candidates = []
        if module is not None:
            exported = getattr(module, "__all__", ())
            if isinstance(exported, (list, tuple)):
                candidates = [str(item) for item in exported]
        suggestions = difflib.get_close_matches(name, candidates, n=1, cutoff=0.55)
        suggestion = f" Did you mean '{suggestions[0]}'?" if suggestions else ""
        return "BU_UNKNOWN_API", f"Unknown BU API '{name}'.{suggestion}"

    lowered = message.lower()
    declared_code = str(getattr(exc, "code", "") or "").upper()
    if any(fragment in lowered for fragment in _STALE_ERROR_FRAGMENTS) or (
        declared_code == "BU_RUNTIME" and "session" in lowered
    ):
        return (
            "BU_SESSION_STALE",
            "The active browser session is stale. Call bu.resync(), then bu.snapshot() before retrying.",
        )
    return None


__all__ = ["BUContractError", "install_contract_fixes", "normalize_contract_error"]
