"""Utilities for building and validating FFmpeg command invocations."""

from __future__ import annotations

import os
import shlex
import shutil
from typing import Iterable, List, Sequence


def _bundled_ffmpeg_path() -> str:
    base_dir = os.path.dirname(os.path.dirname(__file__))
    return os.path.join(base_dir, "bin", "ffmpeg", "ffmpeg")


def resolve_ffmpeg_binary() -> str:
    """Return the FFmpeg binary path honoring UA_FFMPEG_BIN and bundled builds."""
    env_path = os.environ.get("UA_FFMPEG_BIN")
    if env_path:
        return env_path

    bundled = _bundled_ffmpeg_path()
    if os.path.exists(bundled) and os.access(bundled, os.X_OK):
        return bundled

    discovered = shutil.which("ffmpeg")
    if discovered:
        return discovered

    # Fall back to the name so the caller gets a sensible error from the shell.
    return "ffmpeg"


FFMPEG_BINARY = resolve_ffmpeg_binary()


def sanitize_stream_label(label: str) -> str:
    """Ensure stream labels such as 0:v:0 remain ASCII-only."""
    sanitized = label.replace("✌", ":v:").replace("\u270C", ":v:")
    return sanitized


def _sanitize_arg(value: str) -> str:
    return sanitize_stream_label(value)


def ensure_map_targets(args: Sequence[str]) -> List[str]:
    """Guarantee every -map flag has a following target.

    If the target is missing or empty, default to the primary video stream.
    """

    sanitized: List[str] = list(args)
    idx = 0
    while idx < len(sanitized):
        if sanitized[idx] == "-map":
            if idx + 1 >= len(sanitized) or not sanitized[idx + 1].strip():
                sanitized.insert(idx + 1, "0:v:0")
            else:
                sanitized[idx + 1] = sanitize_stream_label(sanitized[idx + 1])
            idx += 1
        idx += 1
    return sanitized


def sanitize_command_args(args: Iterable[str]) -> List[str]:
    """Apply ASCII sanitisation and validate mapping arguments."""

    sanitized = [_sanitize_arg(str(arg)) for arg in args]
    return ensure_map_targets(sanitized)


def prepare_ffmpeg_command(command: Sequence[str] | Iterable[str]) -> List[str]:
    """Normalise a raw FFmpeg command list.

    The first argument is replaced with the resolved binary path, the command
    is sanitised, and mapping flags are validated.
    """

    cmd_list = [str(arg) for arg in command]
    if not cmd_list:
        raise ValueError("FFmpeg command cannot be empty")

    cmd_list[0] = FFMPEG_BINARY
    return sanitize_command_args(cmd_list)


def prepare_ffmpeg_object(command_obj) -> List[str]:
    """Normalise a command produced by ffmpeg-python."""

    cmd_list = list(command_obj.compile())
    return prepare_ffmpeg_command(cmd_list)


def format_command_for_logging(args: Sequence[str]) -> str:
    """Return a shell-escaped string representation suitable for logs."""

    return " ".join(shlex.quote(str(arg)) for arg in args)


def preview_stderr(stderr: bytes | str, limit: int = 40) -> str:
    """Return the first ``limit`` lines of FFmpeg stderr for debugging."""

    if isinstance(stderr, bytes):
        stderr_text = stderr.decode("utf-8", errors="replace")
    else:
        stderr_text = stderr

    lines = stderr_text.splitlines()
    if not lines:
        return ""
    preview = lines[: max(0, limit)]
    return "\n".join(preview)
