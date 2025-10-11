"""Helpers for determining safe worker pool sizes."""

from __future__ import annotations

import os
from typing import Optional


def compute_worker_count(task_count: int, configured_limit: Optional[int] = None, cpu_count: Optional[int] = None) -> int:
    """Return a safe worker count for the given task volume.

    * ``task_count`` of zero or less returns ``0`` to indicate no work.
    * ``configured_limit`` of ``None`` or ``0`` defers to system CPU count.
    * The returned value is never greater than ``task_count`` and never less than
      ``1`` when tasks are pending.
    """

    if task_count <= 0:
        return 0

    if cpu_count is None:
        cpu_count = os.cpu_count() or 1

    limit = configured_limit if configured_limit not in (None, 0) else cpu_count

    if limit <= 0:
        limit = 1

    workers = min(task_count, limit)
    return max(1, workers)
