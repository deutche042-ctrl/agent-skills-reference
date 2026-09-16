"""One-shot browser-use Python cell runner.

The parent FastAPI process starts this module in a fresh Python 3.10 process for
every request.  stdin and stdout form a private JSON protocol; user stdout and
stderr are captured so they cannot corrupt that protocol.
"""

from __future__ import annotations

import base64
import builtins
import contextlib
import io
import json
import mimetypes
import os
import re
import sys
import tempfile
import time
import traceback
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Dict, Iterable, List, Optional

try:
    from application.computer_use_compat import (
        install_contract_fixes,
        normalize_contract_error,
    )
except ModuleNotFoundError as exc:
    if exc.name != "application":
        raise
    # The Go service runs this file by absolute path, while the legacy FastAPI
    # endpoint runs it as ``python -m application.computer_use_cell``.
    from computer_use_compat import install_contract_fixes, normalize_contract_error


MAX_OUTPUT_BYTES = 1024 * 1024
MAX_DOM_BYTES = 2 * 1024 * 1024
MAX_IMAGE_COUNT = 16
MAX_IMAGE_BYTES = 32 * 1024 * 1024
MAX_ERROR_BYTES = 16 * 1024
_ERROR_CODE_RE = re.compile(r"^[A-Za-z0-9_.:-]+$")
_DOM_SCOPE_RE = re.compile(
    r"(?:^|\s)(?:scope=(d[1-9][0-9]*)(?:\s|$)|@(d[1-9][0-9]*):e[1-9][0-9]*)"
)


class _BoundedTextBuffer(io.TextIOBase):
    def __init__(
        self, limit: int, on_change: Optional[Callable[[], None]] = None
    ) -> None:
        self._limit = limit
        self._parts: List[str] = []
        self._kept_bytes = 0
        self._dropped_bytes = 0
        self._on_change = on_change

    def writable(self) -> bool:
        return True

    def write(self, value: str) -> int:
        text = str(value)
        encoded = text.encode("utf-8", errors="replace")
        remaining = max(0, self._limit - self._kept_bytes)
        kept = _prefix_by_utf8_bytes(text, remaining)
        if kept:
            self._parts.append(kept)
            self._kept_bytes += len(kept.encode("utf-8"))
        self._dropped_bytes += max(0, len(encoded) - len(kept.encode("utf-8")))
        if self._on_change is not None:
            self._on_change()
        return len(text)

    def value(self) -> str:
        value = "".join(self._parts)
        if self._dropped_bytes:
            value += f"\n[truncated kind=output omitted={self._dropped_bytes}]"
        return value

    def drain(self, *, final: bool = False) -> str:
        value = "".join(self._parts)
        self._parts.clear()
        if final and self._dropped_bytes:
            value += f"\n[truncated kind=output omitted={self._dropped_bytes}]"
        return value

    def set_on_change(self, callback: Optional[Callable[[], None]]) -> None:
        self._on_change = callback


def _prefix_by_utf8_bytes(value: str, limit: int) -> str:
    if limit <= 0:
        return ""
    encoded = value.encode("utf-8", errors="replace")
    if len(encoded) <= limit:
        return encoded.decode("utf-8")
    return encoded[:limit].decode("utf-8", errors="ignore")


def _extract_observations(payload: Any) -> Iterable[Dict[str, Any]]:
    if isinstance(payload, dict):
        observations = payload.get("observations")
        if isinstance(observations, list):
            for observation in observations:
                if isinstance(observation, dict):
                    yield observation
        data = payload.get("data")
        if isinstance(data, (dict, list)):
            yield from _extract_observations(data)
    elif isinstance(payload, list):
        for item in payload:
            if isinstance(item, (dict, list)):
                yield from _extract_observations(item)


def _append_output_event(
    events: List[Dict[str, Any]], output: _BoundedTextBuffer, *, final: bool = False
) -> None:
    text = output.drain(final=final)
    if text:
        events.append({"kind": "output", "text": text})


class _JSONResponseProxy:
    def __init__(self, response: Any, payload: Dict[str, Any]) -> None:
        self._response = response
        self._payload = payload

    def json(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        return self._payload

    def __getattr__(self, name: str) -> Any:
        return getattr(self._response, name)


def _is_browser_use_execute_request(args: Any, kwargs: Dict[str, Any]) -> bool:
    url = args[0] if args else kwargs.get("url")
    return str(url or "").rstrip("/").endswith("/v1/browser-use/execute")


def _patch_httpx_observation_capture(
    events: List[Dict[str, Any]],
    output: _BoundedTextBuffer,
    checkpoint: Optional[Callable[..., None]] = None,
):
    import httpx

    original_post = httpx.post

    def capturing_post(*args: Any, **kwargs: Any):
        _append_output_event(events, output)
        event_count = len(events)
        response = original_post(*args, **kwargs)
        try:
            payload = response.json()
            if not _is_browser_use_execute_request(args, kwargs) or not isinstance(
                payload, dict
            ):
                return response
            daemon_output = payload.get("output")
            if isinstance(daemon_output, list):
                for message in daemon_output:
                    output.write(str(message))
                    output.write("\n")
                _append_output_event(events, output)
            events.extend(
                {"kind": "observation", "observation": observation}
                for observation in _extract_observations(payload)
            )
            if isinstance(daemon_output, list):
                sdk_payload = dict(payload)
                sdk_payload["output"] = []
                response = _JSONResponseProxy(response, sdk_payload)
        except Exception:
            pass
        if checkpoint is not None and len(events) > event_count:
            checkpoint(force=True)
        return response

    httpx.post = capturing_post
    return httpx, original_post


@contextlib.contextmanager
def _browser_only_imports():
    original_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any):
        if name == "seed_computer_use" or name.startswith("seed_computer_use."):
            raise RuntimeError("computer-use plane is disabled in browser-only mode")
        return original_import(name, *args, **kwargs)

    builtins.__import__ = guarded_import
    try:
        yield
    finally:
        builtins.__import__ = original_import


def _error_code(
    exc: BaseException, browser_use_module: Optional[ModuleType] = None
) -> str:
    normalized = normalize_contract_error(exc, browser_use_module)
    if normalized is not None:
        return normalized[0]
    value = getattr(exc, "code", "")
    if value is not None:
        candidate = str(value).strip()
        if candidate and _ERROR_CODE_RE.fullmatch(candidate):
            return candidate
    if isinstance(exc, SyntaxError):
        return "PY_SYNTAX_ERROR"
    if isinstance(exc, RuntimeError) and "browser-only mode" in str(exc):
        return "CNGC_PLANE_DISABLED"
    name = type(exc).__name__.upper()
    return "PY_" + re.sub(r"[^A-Z0-9_]+", "_", name)


def _error_text(
    exc: BaseException, browser_use_module: Optional[ModuleType] = None
) -> str:
    line_number = getattr(exc, "lineno", None)
    if line_number is None:
        for frame in reversed(traceback.extract_tb(exc.__traceback__)):
            if frame.filename == "<computer_use_tool cell 1>":
                line_number = frame.lineno
                break
    location = f" line={line_number}" if line_number else ""
    normalized = normalize_contract_error(exc, browser_use_module)
    marker = f"[error code={_error_code(exc, browser_use_module)}{location}]"
    recovery = normalized[1].strip() if normalized is not None else ""
    reserved = len((marker + recovery).encode("utf-8")) + 2
    traceback_text = "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    ).strip()
    traceback_text = _prefix_by_utf8_bytes(
        traceback_text or type(exc).__name__, max(0, MAX_ERROR_BYTES - reserved)
    ).strip()
    parts = [marker, traceback_text]
    if recovery:
        parts.append(recovery)
    return "\n".join(parts)


def _observation_scope(observation: Dict[str, Any], text: str) -> str:
    scope = str(observation.get("scope") or "").strip()
    if scope.lower() not in {"", "unknown", "none", "null"}:
        return scope
    match = _DOM_SCOPE_RE.search(text)
    if match is None:
        return "unknown"
    return next((group for group in match.groups() if group), "unknown")


def _event_content(events: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    content: List[Dict[str, str]] = []
    dom_bytes = 0
    image_bytes = 0
    image_count = 0
    omitted_images = 0

    for event in events:
        if event.get("kind") == "output":
            text = str(event.get("text") or "").strip()
            if text:
                content.append({"type": "text", "text": "[output]\n" + text})
            continue
        observation = event.get("observation")
        if not isinstance(observation, dict):
            continue
        kind = str(observation.get("kind") or observation.get("type") or "unknown")
        scope = str(observation.get("scope") or "")
        tag = str(observation.get("tag") or "")
        if kind == "dom":
            text = str(observation.get("text") or "")
            scope = _observation_scope(observation, text)
            remaining = max(0, MAX_DOM_BYTES - dom_bytes)
            kept = _prefix_by_utf8_bytes(text, remaining)
            dom_bytes += len(kept.encode("utf-8"))
            descriptor = f"[obs type=dom scope={scope or 'unknown'}]"
            if kept:
                descriptor += "\n" + kept
            if kept != text:
                descriptor += (
                    "\n[truncated kind=dom omitted="
                    f"{len(text.encode('utf-8')) - len(kept.encode('utf-8'))}]"
                )
            content.append({"type": "text", "text": descriptor})
            continue

        if kind == "image":
            descriptor = f"[obs type=image scope={scope or 'unknown'}"
            if tag:
                descriptor += f" tag={tag}"
            descriptor += "]"
            content.append({"type": "text", "text": descriptor})
            raw_path = observation.get("path")
            if image_count >= MAX_IMAGE_COUNT or not isinstance(raw_path, str):
                omitted_images += 1
                continue
            try:
                path = Path(raw_path)
                data = path.read_bytes()
            except (OSError, ValueError):
                content.append({"type": "text", "text": "[image unavailable]"})
                continue
            if not data or image_bytes + len(data) > MAX_IMAGE_BYTES:
                omitted_images += 1
                continue
            mime_type = mimetypes.guess_type(path.name)[0]
            if mime_type not in {"image/png", "image/jpeg"}:
                mime_type = (
                    "image/png" if data.startswith(b"\x89PNG\r\n\x1a\n") else None
                )
            if mime_type not in {"image/png", "image/jpeg"}:
                content.append(
                    {"type": "text", "text": "[image skipped unsupported_mime]"}
                )
                continue
            content.append(
                {
                    "type": "image",
                    "mime_type": mime_type,
                    "data": base64.b64encode(data).decode("ascii"),
                }
            )
            image_count += 1
            image_bytes += len(data)

    if omitted_images:
        content.append(
            {"type": "text", "text": f"[truncated kind=image omitted={omitted_images}]"}
        )
    return content


def _observation_content(observations: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    return _event_content(
        [
            {"kind": "observation", "observation": observation}
            for observation in observations
        ]
    )


def _build_response(
    status: str,
    events: List[Dict[str, Any]],
    *,
    error: str = "",
    pending_output: str = "",
    merge_first_output: bool = True,
) -> Dict[str, Any]:
    response_events = list(events)
    if pending_output:
        response_events.append({"kind": "output", "text": pending_output})
    content: List[Dict[str, str]] = [
        {"type": "text", "text": f"[result status={status}]"}
    ]
    event_content = _event_content(response_events)
    has_observation = any(
        event.get("kind") == "observation" for event in response_events
    )
    if merge_first_output and not has_observation and event_content:
        content[0]["text"] += "\n" + event_content[0]["text"]
        content.extend(event_content[1:])
    else:
        content.extend(event_content)
    if error:
        if len(content) == 1:
            content[0]["text"] += "\n" + error
        else:
            content.append({"type": "text", "text": error})
    return {"status": status, "content": content}


def _write_response_file(path: str, response: Dict[str, Any]) -> None:
    parent = str(Path(path).resolve().parent)
    fd, temporary_path = tempfile.mkstemp(prefix="computer-use-response-", dir=parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(response, handle, ensure_ascii=False, separators=(",", ":"))
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, path)
    finally:
        try:
            os.unlink(temporary_path)
        except FileNotFoundError:
            pass


def execute(payload: Dict[str, Any]) -> Dict[str, Any]:
    code = payload["code"]
    group_id = payload.get("group_id")
    if group_id is not None:
        if not isinstance(group_id, str) or not group_id.strip():
            raise ValueError("invalid browser group id")
        os.environ["BROWSER_GROUP_ID"] = group_id
    endpoint = payload.get("endpoint")
    if endpoint is not None:
        if not isinstance(endpoint, str) or not endpoint.strip():
            raise ValueError("invalid browser use endpoint")
        os.environ["SEED_BROWSER_USE_ENDPOINT"] = endpoint
    events: List[Dict[str, Any]] = []
    output = _BoundedTextBuffer(MAX_OUTPUT_BYTES)
    status = "ok"
    error = ""
    httpx_module = None
    original_post = None
    browser_use_module: Optional[ModuleType] = None
    response_path = payload.get("response_path")
    last_checkpoint = 0.0

    def checkpoint(*, force: bool = False) -> None:
        nonlocal last_checkpoint
        if not isinstance(response_path, str) or not response_path:
            return
        now = time.monotonic()
        if not force and now - last_checkpoint < 0.1:
            return
        partial = _build_response(
            "running",
            events,
            pending_output=output.value(),
            merge_first_output=False,
        )
        try:
            _write_response_file(response_path, partial)
        except OSError:
            # A checkpoint must never change user-code semantics.  The final
            # response write remains authoritative and is allowed to fail.
            return
        last_checkpoint = now

    output.set_on_change(checkpoint)
    try:
        with (
            _browser_only_imports(),
            contextlib.redirect_stdout(output),
            contextlib.redirect_stderr(output),
        ):
            import seed_browser_use

            browser_use_module = seed_browser_use
            install_contract_fixes(seed_browser_use)

            httpx_module, original_post = _patch_httpx_observation_capture(
                events, output, checkpoint
            )
            compiled = compile(code, "<computer_use_tool cell 1>", "exec")
            namespace: Dict[str, Any] = {
                "__name__": "__main__",
                "__builtins__": builtins,
            }
            exec(compiled, namespace, namespace)
    except BaseException as exc:
        status = "error"
        error = _error_text(exc, browser_use_module)
    finally:
        if httpx_module is not None and original_post is not None:
            httpx_module.post = original_post
        _append_output_event(events, output, final=True)
    return _build_response(status, events, error=error)


def main() -> int:
    payload: Any = {}
    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict) or not isinstance(payload.get("code"), str):
            raise ValueError("invalid cell request")
        response = execute(payload)
    except BaseException as exc:
        response = {
            "status": "error",
            "content": [
                {
                    "type": "text",
                    "text": f"[result status=error]\n[error code=CELL_PROTOCOL_ERROR]\n{type(exc).__name__}",
                }
            ],
        }
    response_path = payload.get("response_path") if isinstance(payload, dict) else None
    if isinstance(response_path, str) and response_path:
        _write_response_file(response_path, response)
    else:
        json.dump(response, sys.__stdout__, ensure_ascii=False, separators=(",", ":"))
        sys.__stdout__.flush()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
