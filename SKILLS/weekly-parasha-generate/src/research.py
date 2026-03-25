from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

import requests

from parsha import ParshaInfo


@dataclass(frozen=True)
class Source:
    id: str
    title: str
    url: str
    excerpt: str
    retrieved_at: str


def _now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _safe_get_text(url: str, *, timeout: int = 30) -> str:
    resp = requests.get(
        url,
        timeout=timeout,
        headers={
            "User-Agent": "weekly-parasha-skill/1.0 (https://github.com/fredhersch/weekly_parasha)"
        },
    )
    resp.raise_for_status()
    return resp.text


def _wikipedia_title_candidates(parsha: str) -> list[str]:
    # Common patterns on Wikipedia:
    # - "Tzav" (may not exist)
    # - "Tzav (parsha)"
    # - "Tzav (Torah portion)" (less common)
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


def collect_sources(info: ParshaInfo) -> list[Source]:
    sources: list[Source] = []

    # Hebcal leyning summary is reliable and structured.
    summary = (info.hebcal_item.get("summary") or "").strip()
    if summary:
        sources.append(
            Source(
                id="hebcal_leyning",
                title=f"Hebcal leyning: {info.parsha}",
                url=info.hebcal_url,
                excerpt=f"{info.parsha}: {summary}",
                retrieved_at=_now_iso(),
            )
        )

    wiki = _wikipedia_summary(info.parsha)
    if wiki:
        sources.append(wiki)

    # Always include a canonical landing page, even if we don't fetch it.
    # This keeps citations stable for readers.
    sefaria_url = f"https://www.sefaria.org/topics/parashat-{info.parsha.lower()}"
    sources.append(
        Source(
            id="sefaria_topic",
            title=f"Sefaria topic: Parashat {info.parsha}",
            url=sefaria_url,
            excerpt="Topic page for the weekly parasha (background and links).",
            retrieved_at=_now_iso(),
        )
    )

    return sources

