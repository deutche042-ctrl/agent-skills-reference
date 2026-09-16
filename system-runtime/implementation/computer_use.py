"""Browser-only, one-shot Python cell endpoint for computer_use_tool."""

from __future__ import annotations

import asyncio
import base64
import binascii
import contextlib
import hashlib
import json
import os
import signal
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict

from application.logger import logger
from application.router import TimedRoute


MIN_TIMEOUT_MS = 1_000
MAX_TIMEOUT_MS = 900_000
MAX_CODE_BYTES = 256 * 1024
MAX_TITLE_CHARS = 80
MAX_CHILD_RESPONSE_BYTES = 48 * 1024 * 1024
MAX_DECODED_IMAGE_BYTES = 32 * 1024 * 1024
DEFAULT_PYTHON_BIN = "/usr/bin/python3.10"
DEFAULT_BROWSER_USE_ENDPOINT = "http://127.0.0.1:8091"
CELL_SAFETY_TIMEOUT_SECONDS = 15 * 60
_BACKGROUND_CELL_TASKS: set[asyncio.Task] = set()


class ComputerUseRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    plane: str
    timeout_ms: int = 120_000
    title: str = ""


router = APIRouter(prefix="/computer_use", route_class=TimedRoute)


def _validate_request(command: ComputerUseRequest) -> bytes:
    plane = command.plane.strip().lower()
    if plane in {"cu", "mixed"}:
        raise HTTPException(
            status_code=405,
            detail=f"computer_use_tool method not supported for plane {plane}",
        )
    if plane != "bu":
        raise HTTPException(
            status_code=400, detail="computer_use_tool plane must be bu"
        )
    if not command.code.strip():
        raise HTTPException(
            status_code=400, detail="computer_use_tool code must not be empty"
        )
    try:
        encoded_code = command.code.encode("utf-8")
    except UnicodeEncodeError as exc:
        raise HTTPException(
            status_code=400,
            detail="computer_use_tool code must be valid UTF-8",
        ) from exc
    if len(encoded_code) > MAX_CODE_BYTES:
        raise HTTPException(
            status_code=413, detail="computer_use_tool code exceeds 262144 bytes"
        )
    if len(command.title) > MAX_TITLE_CHARS:
        raise HTTPException(
            status_code=400, detail="computer_use_tool title exceeds 80 characters"
        )
    if not MIN_TIMEOUT_MS <= command.timeout_ms <= MAX_TIMEOUT_MS:
        raise HTTPException(
            status_code=400,
            detail="computer_use_tool timeout_ms must be between 1000 and 900000",
        )
    return encoded_code


def _effective_agent_id(request: Request) -> str:
    agent_id = (request.headers.get("x-agent-id") or "").strip()
    if agent_id:
        return agent_id
    session_id = (request.headers.get("x-session-id") or "").strip()
    if session_id:
        return session_id
    raise HTTPException(
        status_code=400,
        detail="computer_use_tool requires x-agent-id or x-session-id",
    )


def _error_response(code: str, detail: str) -> Dict[str, Any]:
    return {
        "status": "error",
        "content": [
            {
                "type": "text",
                "text": f"[result status=error]\n[error code={code}]\n{detail}",
            }
        ],
    }


def _safety_timeout_response() -> Dict[str, Any]:
    return {
        "status": "timeout",
        "content": [
            {
                "type": "text",
                "text": (
                    "[result status=timeout]\n"
                    "[error code=CELL_SAFETY_TIMEOUT]\n"
                    f"Execution reached the independent safety timeout of {CELL_SAFETY_TIMEOUT_SECONDS * 1000}ms. "
                    "GUI actions may already have run; observe before retrying."
                ),
            }
        ],
    }


def _validate_child_response(raw: bytes) -> Dict[str, Any]:
    if not raw or len(raw) > MAX_CHILD_RESPONSE_BYTES:
        raise ValueError("child response size is invalid")
    response = json.loads(raw)
    if not isinstance(response, dict):
        raise ValueError("child response is not an object")
    status = response.get("status")
    if status not in {"ok", "error"}:
        raise ValueError("child status is invalid")
    content = response.get("content")
    if not isinstance(content, list) or not content:
        raise ValueError("child content is empty")
    first = content[0]
    if not isinstance(first, dict) or first.get("type") != "text":
        raise ValueError("child first content is not text")
    first_line = str(first.get("text") or "").split("\n", 1)[0]
    if first_line != f"[result status={status}]":
        raise ValueError("child result status mismatch")

    decoded_image_bytes = 0
    for item in content:
        if not isinstance(item, dict):
            raise ValueError("child content item is invalid")
        item_type = item.get("type")
        if item_type == "text":
            if not isinstance(item.get("text"), str):
                raise ValueError("child text item is invalid")
            if "mime_type" in item or "data" in item:
                raise ValueError("child text item contains image fields")
            continue
        if item_type != "image":
            raise ValueError("child content type is invalid")
        if item.get("mime_type") not in {"image/png", "image/jpeg"}:
            raise ValueError("child image mime type is invalid")
        if "text" in item or not isinstance(item.get("data"), str):
            raise ValueError("child image item is invalid")
        try:
            decoded = base64.b64decode(item["data"], validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("child image base64 is invalid") from exc
        if not decoded:
            raise ValueError("child image is empty")
        decoded_image_bytes += len(decoded)
        if decoded_image_bytes > MAX_DECODED_IMAGE_BYTES:
            raise ValueError("child images exceed decoded byte limit")
    return response


async def _kill_process_group(process: asyncio.subprocess.Process) -> None:
    if process.returncode is not None:
        return
    try:
        os.killpg(process.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    await process.wait()


def _retain_background_cell(task: asyncio.Task) -> None:
    _BACKGROUND_CELL_TASKS.add(task)

    def consume_result(completed: asyncio.Task) -> None:
        _BACKGROUND_CELL_TASKS.discard(completed)
        with contextlib.suppress(asyncio.CancelledError, Exception):
            completed.result()

    task.add_done_callback(consume_result)


async def _run_cell(command: ComputerUseRequest, group_id: str) -> Dict[str, Any]:
    env = os.environ.copy()
    env.update(
        {
            "BROWSER_GROUP_ID": group_id,
            "SEED_BROWSER_USE_ENDPOINT": os.getenv(
                "SEED_BROWSER_USE_ENDPOINT", DEFAULT_BROWSER_USE_ENDPOINT
            ),
            "PYTHONUNBUFFERED": "1",
        }
    )
    python_bin = os.getenv("COMPUTER_USE_PYTHON_BIN", DEFAULT_PYTHON_BIN)
    working_dir = str(Path(__file__).resolve().parents[1])
    process = await asyncio.create_subprocess_exec(
        python_bin,
        "-m",
        "application.computer_use_cell",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.DEVNULL,
        cwd=working_dir,
        env=env,
        start_new_session=True,
    )
    request_bytes = json.dumps(
        {"code": command.code}, ensure_ascii=False, separators=(",", ":")
    ).encode("utf-8")
    communicate_task = asyncio.create_task(process.communicate(request_bytes))
    try:
        stdout, _ = await asyncio.wait_for(
            asyncio.shield(communicate_task), timeout=CELL_SAFETY_TIMEOUT_SECONDS
        )
    except asyncio.TimeoutError:
        await _kill_process_group(process)
        communicate_task.cancel()
        with contextlib.suppress(asyncio.CancelledError, Exception):
            await communicate_task
        return _safety_timeout_response()
    except asyncio.CancelledError:
        # Request cancellation only ends the caller's wait.  Keep draining the
        # child pipes so an already-started GUI cell can finish safely.
        _retain_background_cell(communicate_task)
        raise
    if process.returncode != 0:
        return _error_response(
            "CELL_RUNNER_EXIT", "The browser-use cell runner exited unexpectedly."
        )
    try:
        return _validate_child_response(stdout)
    except (UnicodeDecodeError, ValueError, json.JSONDecodeError):
        return _error_response(
            "CELL_RUNNER_PROTOCOL_ERROR",
            "The browser-use cell runner returned an invalid response.",
        )


@router.post("/execute")
async def execute_computer_use(command: ComputerUseRequest, request: Request):
    encoded_code = _validate_request(command)
    group_id = _effective_agent_id(request)
    code_bytes = len(encoded_code)
    code_hash = hashlib.sha256(encoded_code).hexdigest()
    logger.info(
        "computer use cell starting, plane=bu timeout_ms=%d code_bytes=%d code_sha256=%s",
        command.timeout_ms,
        code_bytes,
        code_hash,
    )
    try:
        response = await _run_cell(command, group_id)
    except OSError as exc:
        logger.error(
            "computer use cell spawn failed, error_type=%s code_bytes=%d code_sha256=%s",
            type(exc).__name__,
            code_bytes,
            code_hash,
        )
        raise HTTPException(
            status_code=500, detail="computer_use_tool runner unavailable"
        ) from exc

    text_count = sum(1 for item in response["content"] if item["type"] == "text")
    image_count = sum(1 for item in response["content"] if item["type"] == "image")
    logger.info(
        "computer use cell completed, status=%s timeout_ms=%d code_bytes=%d code_sha256=%s text_count=%d image_count=%d",
        response["status"],
        command.timeout_ms,
        code_bytes,
        code_hash,
        text_count,
        image_count,
    )
    return response


__all__ = ["router"]
