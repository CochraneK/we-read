#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Runtime entrypoint for the public Pages report.

The WeRead monthly `/readdata/detail` payload stores day-level reading seconds in
`readTimes`. Older docs/fixtures may expose `dailyReadTimes` on annual payloads,
so this adapter supports both and injects the normalized daily series into the
Pages builder without duplicating the full renderer.
"""
from __future__ import annotations

import build_pages_report as report


_legacy_daily_read_times = report.daily_read_times


def daily_read_times(readdata: dict) -> dict[str, int]:
    result: dict[str, int] = {}
    for period in (readdata.get("monthly") or {}).values():
        for raw_day, raw_seconds in ((period or {}).get("readTimes") or {}).items():
            parsed = report.parse_timestamp(raw_day)
            if not parsed:
                continue
            try:
                seconds = max(0, int(raw_seconds or 0))
            except (TypeError, ValueError):
                continue
            key = parsed.strftime("%Y-%m-%d")
            result[key] = max(result.get(key, 0), seconds)

    if result:
        return dict(sorted(result.items()))
    return _legacy_daily_read_times(readdata)


def main() -> None:
    report.daily_read_times = daily_read_times
    report.main()


if __name__ == "__main__":
    main()
