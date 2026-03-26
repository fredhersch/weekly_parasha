from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import hdate

from parsha_map import PARSHA_MAP


@dataclass(frozen=True)
class ParshaInfo:
    """Current parsha for a civil date (hdate), with English name from PARSHA_MAP."""

    english: str
    hebrew: str
    on_date: date


def resolve_parsha(*, on_date: date) -> ParshaInfo:
    h = hdate.HDateInfo(on_date)
    hebrew = str(h.parasha).strip()
    english = PARSHA_MAP.get(hebrew, hebrew)
    return ParshaInfo(english=english, hebrew=hebrew, on_date=on_date)
