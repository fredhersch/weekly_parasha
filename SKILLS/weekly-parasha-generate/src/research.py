from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from parsha import ParshaInfo, next_shabbat_for


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    excerpt: str
    retrieved_at: str


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _wikipedia_title_candidates(parsha: str) -> list[str]:
    p = parsha.strip()
    return [p, f"{p} (parsha)", f"{p} (Torah portion)"]


def _wikipedia_summary(parsha: str) -> Optional[Source]:
    for title in _wikipedia_title_candidates(parsha):
        api = f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}"
        try:
            data = requests.get(api, timeout=30).json()
            if data.get("type") == "https://mediawiki.org/wiki/HyperSwitch/errors/not_found":
                continue
            extract = (data.get("extract") or "").strip()
            page_url = ((data.get("content_urls") or {}).get("desktop") or {}).get("page") or ""
            if extract and page_url:
                return Source(
                    id="wikipedia",
                    title=f"Wikipedia: {title}",
                    url=page_url,
                    excerpt=extract[:800],
                    retrieved_at=_now_iso(),
                )
        except Exception:
            continue
    return None


def _hebcal_leyning(*, shabbat: date, diaspora: bool = True) -> Optional[Source]:
    url = "https://www.hebcal.com/leyning"
    params: dict = {"cfg": "json", "date": shabbat.isoformat()}
    if diaspora:
        params["i"] = "on"
    try:
        resp = requests.get(url, params=params, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        items = data.get("items") or []
        if not items:
            return None
        item = items[0]
        summary = (item.get("summary") or "").strip()
        name = item.get("name") or {}
        label = (name.get("en") or "").strip() or str(item.get("title") or "").strip()
        hebcal_url = (
            f"https://www.hebcal.com/leyning?cfg=json&date={shabbat.isoformat()}"
            + ("&i=on" if diaspora else "")
        )
        if summary:
            return Source(
                id="hebcal_leyning",
                title=f"Hebcal leyning: {label}",
                url=hebcal_url,
                excerpt=f"{label}: {summary}",
                retrieved_at=_now_iso(),
            )
    except Exception:
        return None
    return None


def collect_sources(info: ParshaInfo) -> list[Source]:
    """Live context for citations (no third-party Torah text APIs)."""
    sources: list[Source] = []

    shabbat = next_shabbat_for(info.on_date)
    hebcal = _hebcal_leyning(shabbat=shabbat, diaspora=True)
    if hebcal:
        sources.append(hebcal)

    wiki = _wikipedia_summary(info.english)
    if wiki:
        sources.append(wiki)

    return sources
