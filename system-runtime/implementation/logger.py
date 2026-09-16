import logging
import os
import re
import sys

from application.trace_id_filter import get_agent_id, get_session_id, get_tool_use_id, get_trace_id


_LEVEL_CONFIG = {
    logging.DEBUG: ("DEBUG", "🔍"),
    logging.INFO: (" INFO", "ℹ️"),
    logging.WARNING: (" WARN", "⚠️"),
    logging.ERROR: ("ERROR", "❗"),
    logging.CRITICAL: ("ERROR", "❗"),
}
_EVENTS = {
    ("python_runtime", "reported"): ("python_runtime_reported", "python"),
    ("code_execution", "started"): ("code_execution_started", "jupyter"),
    ("code_execution", "succeeded"): ("code_execution_succeeded", "jupyter"),
    ("code_execution", "failed"): ("code_execution_failed", "jupyter"),
    ("code_execution", "timed_out"): ("code_execution_timed_out", "jupyter"),
}
_CONTROL_CHARS = re.compile(r"[\x00-\x1f\x7f]")


def _escape(value):
    value = str(value)
    return _CONTROL_CHARS.sub(lambda match: "\\x%02x" % ord(match.group(0)), value).replace("\\x0a", "\\n").replace("\\x0d", "\\r").replace("\\x09", "\\t")


class VMFormatter(logging.Formatter):
    def format(self, record):
        message = _escape(record.getMessage())
        level, icon = _LEVEL_CONFIG.get(record.levelno, (" INFO", "ℹ️"))
        operation = getattr(record, "vm_operation", "python_runtime")
        state = getattr(record, "vm_state", "reported")
        event, module = _EVENTS.get((operation, state), ("python_runtime_reported", "python"))
        method = getattr(record, "vm_method", record.filename)
        hierarchy = getattr(record, "vm_hierarchy", "--")
        lifecycle = getattr(record, "vm_lifecycle", "runtime")

        fields = []
        if lifecycle != "runtime":
            fields.append("lifecycle=%s" % _escape(lifecycle))
        session_id = get_session_id() or os.getenv("SESSION_ID", "")
        if session_id:
            fields.append("session_id=%s" % _escape(session_id))
        agent_id = get_agent_id() or os.getenv("AGENT_ID", "")
        if agent_id:
            fields.append("agent_id=%s" % _escape(agent_id))
        log_id = get_trace_id() or ""
        if log_id:
            fields.append("log_id=%s" % _escape(log_id))
        tool_use_id = get_tool_use_id() or ""
        if tool_use_id:
            fields.append("tool_use_id=%s" % _escape(tool_use_id))
        if record.exc_info:
            fields.append("error=%s" % _escape(self.formatException(record.exc_info)))

        timestamp = self.formatTime(record, "%Y-%m-%d %H:%M:%S")
        milliseconds = int(record.msecs)
        return "%s.%03d [VM] %s %s %s %s [python_server/%s][%s] %s | %s" % (
            timestamp,
            milliseconds,
            level,
            icon,
            hierarchy,
            event,
            module,
            method,
            message,
            " ".join(fields),
        )


class VMLoggerAdapter(logging.LoggerAdapter):
    def with_operation(self, operation, state="reported", hierarchy="--"):
        extra = dict(self.extra)
        extra.update(
            {
                "vm_operation": operation,
                "vm_state": state,
                "vm_hierarchy": hierarchy,
            }
        )
        return VMLoggerAdapter(self.logger, extra)

    def with_lifecycle(self, lifecycle):
        extra = dict(self.extra)
        extra["vm_lifecycle"] = lifecycle
        return VMLoggerAdapter(self.logger, extra)


def _build_logger():
    base = logging.getLogger("mcp_vm.python_server")
    base.setLevel(logging.INFO)
    base.propagate = False
    if not any(getattr(handler, "_mcp_vm_handler", False) for handler in base.handlers):
        handler = logging.StreamHandler(sys.stdout)
        handler._mcp_vm_handler = True
        handler.setFormatter(VMFormatter())
        base.addHandler(handler)
    return base


logger = _build_logger()


def with_operation(operation, state="reported", hierarchy="--"):
    return VMLoggerAdapter(
        logger,
        {
            "vm_operation": operation,
            "vm_state": state,
            "vm_hierarchy": hierarchy,
        },
    )


def set_log_level(level):
    if isinstance(level, str):
        normalized = level.upper()
        if normalized not in {"DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL"}:
            raise ValueError("Invalid logging level")
        level = logging.WARNING if normalized == "WARN" else getattr(logging, normalized)
    elif not isinstance(level, int):
        raise ValueError("Logging level must be a logging module level")

    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
    logger.info("logging level configured: %s", logging.getLevelName(level))
