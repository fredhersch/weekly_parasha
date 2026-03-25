from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import hdate

from parsha_map import PARSHA_MAP


@dataclass(frozen=True)
class ParshaInfo:
    """Current parsha for a civil date (hdate), with English name from PARSHA_MAP."""

    english: str
    hebrew: str
    on_date: date


def _next_shabbat(d: date) -> date:
    days_ahead = (5 - d.weekday()) % 7
    return d + timedelta(days=days_ahead)


def resolve_parsha(*, on_date: date) -> ParshaInfo:
    h = hdate.HDateInfo(on_date)
    hebrew = str(h.parasha).strip()
    english = PARSHA_MAP.get(hebrew, hebrew)
    return ParshaInfo(english=english, hebrew=hebrew, on_date=on_date)


def next_shabbat_for(on_date: date) -> date:
    return _next_shabbat(on_date)
