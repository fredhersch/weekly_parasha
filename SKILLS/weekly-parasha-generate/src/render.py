from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class NoteParts:
    date: date
    parsha: str
    theme: str
    research: str
    commentary: str
    script: str
    dailies: str
    dvar_torah: str


def _yaml_escape(value: str) -> str:
    v = value.replace('"', '\\"')
    return f"\"{v}\""


# Strip leading line(s) the model may echo (duplicate ## Research / ## Commentary / etc.).
_LEADING_HEADING_ECHO = re.compile(
    r"^\s*(?:#{1,6}\s*)?"
    r"(?:Research|Commentary|Podcast(?:\s+Script)?|Daily\s+Reflections?|Dvar\s+Torah)"
    r"(?:\s*[:\-–—])?\s*\n+",
    re.IGNORECASE,
)


def _sanitize_section_body(body: str) -> str:
    t = body.strip()
    for _ in range(8):
        nxt = _LEADING_HEADING_ECHO.sub("", t, count=1)
        if nxt == t:
            break
        t = nxt.strip()
    return t.strip()


def render_markdown(parts: NoteParts) -> str:
    title = f"{parts.date.isoformat()} — Torah Study — Parashat {parts.parsha}"
    fm = "\n".join(
        [
            "---",
            f"title: {_yaml_escape(title)}",
            f"date: {parts.date.isoformat()}",
            f"parsha: {_yaml_escape(parts.parsha)}",
            f"theme: {_yaml_escape(parts.theme)}",
            "generator: weekly-parasha-generate",
            "---",
        ]
    )

    research = _sanitize_section_body(parts.research)
    commentary = _sanitize_section_body(parts.commentary)
    script = _sanitize_section_body(parts.script)
    dailies = _sanitize_section_body(parts.dailies)
    dvar_torah = _sanitize_section_body(parts.dvar_torah)

    body = "\n\n".join(
        [
            f"# {title}",
            "## Research",
            research,
            "## Commentary",
            commentary,
            "## Podcast Script",
            script,
            "## Daily Reflections",
            dailies,
            "## Dvar Torah",
            dvar_torah,
        ]
    ).strip()

    return f"{fm}\n\n{body}\n"
