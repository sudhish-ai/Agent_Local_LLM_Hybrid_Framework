# SPDX-FileCopyrightText: 2026 Sudhish Singh
# SPDX-License-Identifier: MIT
# Owner: Sudhish Singh

from __future__ import annotations

from collections import defaultdict


class MetricsRegistry:
    """ALHF in-memory metrics registry."""

    def __init__(self) -> None:
        self._counters: dict[str, int] = defaultdict(int)

    def increment(
        self,
        metric_name: str,
        value: int = 1,
    ) -> None:
        self._counters[metric_name] += value

    def get(
        self,
        metric_name: str,
    ) -> int:
        return self._counters.get(
            metric_name,
            0,
        )

    def snapshot(self) -> dict[str, int]:
        return dict(
            self._counters,
        )
