from __future__ import annotations

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


def render_markdown(parts: NoteParts) -> str:
    # Title includes date + parsha for Obsidian (frontmatter `title` + visible H1).
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

    body = "\n\n".join(
        [
            f"# {title}",
            "## Research",
            parts.research.strip(),
            "## Commentary",
            parts.commentary.strip(),
            "## Podcast Script",
            parts.script.strip(),
            "## Daily Reflections",
            parts.dailies.strip(),
            "## Dvar Torah",
            parts.dvar_torah.strip(),
        ]
    ).strip()

    return f"{fm}\n\n{body}\n"

