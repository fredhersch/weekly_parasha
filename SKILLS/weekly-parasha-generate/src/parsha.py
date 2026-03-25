from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Optional

import requests


@dataclass(frozen=True)
class ParshaInfo:
    parsha: str
    hebrew: Optional[str]
    shabbat_date: date
    hebcal_item: dict
    hebcal_url: str


def _parse_iso_date(d: str) -> date:
    return datetime.strptime(d, "%Y-%m-%d").date()


def _next_shabbat(d: date) -> date:
    # Python: Monday=0 ... Saturday=5, Sunday=6. Shabbat is Saturday.
    days_ahead = (5 - d.weekday()) % 7
    return d + timedelta(days=days_ahead)


def hebcal_weekly_parsha(*, on_date: date, diaspora: bool = True) -> ParshaInfo:
    shabbat = _next_shabbat(on_date)
    url = "https://www.hebcal.com/leyning"
    params = {"cfg": "json", "date": shabbat.isoformat()}
    if diaspora:
        params["i"] = "on"

    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    data = resp.json()

    items = data.get("items") or []
    if not items:
        raise RuntimeError(f"Hebcal returned no items for {shabbat.isoformat()}")

    item = items[0]
    name = item.get("name") or {}
    parsha = (name.get("en") or "").strip() or str(item.get("title") or "").strip()
    hebrew = (name.get("he") or "").strip() or None

    hebcal_url = (
        f"https://www.hebcal.com/leyning?cfg=json&date={shabbat.isoformat()}"
        + ("&i=on" if diaspora else "")
    )

    return ParshaInfo(
        parsha=parsha,
        hebrew=hebrew,
        shabbat_date=shabbat,
        hebcal_item=item,
        hebcal_url=hebcal_url,
    )

