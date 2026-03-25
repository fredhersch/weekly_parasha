from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Allow running as a plain script: `python SKILLS/weekly-parasha-generate/src/generate.py`
THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from claude import ClaudeConfig, complete  # noqa: E402
from parsha import hebcal_weekly_parsha  # noqa: E402
from render import NoteParts, render_markdown  # noqa: E402
from research import collect_sources, Source  # noqa: E402


SYSTEM_BASE = """You are a learned Torah teacher and writer.
Write in warm, accessible English for a broad audience.
When you cite sources, use numbered citations like [1], [2] and then include a final section:

### Sources
1. Title — URL
2. Title — URL

Do not invent URLs. Only cite from the provided sources list."""


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _sources_block(sources: list[Source]) -> str:
    lines = []
    for i, src in enumerate(sources, start=1):
        lines.append(f"{i}. {src.title} — {src.url}\n   Excerpt: {src.excerpt}")
    return "\n".join(lines)


def _mk_prompt(*, parsha: str, theme: str, sources: list[Source], task: str) -> str:
    return f"""Parsha: {parsha}
Theme focus: {theme}

Sources (use these for citations):
{_sources_block(sources)}

Task:
{task}
"""


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate weekly parasha study note for Obsidian.")
    ap.add_argument("--theme", default="general themes")
    ap.add_argument("--date", dest="on_date", default=None, help="YYYY-MM-DD (defaults to today)")
    ap.add_argument("--parsha", default=None, help="Override parsha name (otherwise computed)")
    ap.add_argument("--vault", default=os.getenv("OBSIDIAN_VAULT", "/data/.openclaw/obsidian-vault"))
    ap.add_argument("--folder", default=os.getenv("OBSIDIAN_FOLDER", "Torah Study"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--model", default=os.getenv("CLAUDE_MODEL", "claude-3-7-sonnet-latest"))
    args = ap.parse_args(argv)

    on_date = _parse_date(args.on_date) if args.on_date else date.today()
    info = hebcal_weekly_parsha(on_date=on_date, diaspora=True)
    parsha = args.parsha.strip() if args.parsha else info.parsha

    sources = collect_sources(info)

    cfg = ClaudeConfig(model=args.model, max_tokens=3200, temperature=0.6)

    research = complete(
        system=SYSTEM_BASE,
        user=_mk_prompt(
            parsha=parsha,
            theme=args.theme,
            sources=sources,
            task="Write a structured research summary: key themes, key moments in the narrative, and 2-3 classical commentary angles (Rashi/Ramban style). Keep it concise but substantial.",
        ),
        config=cfg,
    )

    commentary = complete(
        system=SYSTEM_BASE,
        user=_mk_prompt(
            parsha=parsha,
            theme=args.theme,
            sources=sources,
            task=f"Based on this research, write 3–4 original insights (2–3 paragraphs each), connecting the parsha to modern life.\n\nResearch:\n{research}",
        ),
        config=cfg,
    )

    script = complete(
        system=SYSTEM_BASE,
        user=_mk_prompt(
            parsha=parsha,
            theme=args.theme,
            sources=sources,
            task=f"Turn the commentary into a 6–8 minute podcast script (750–1250 words). Include stage directions like [PAUSE], [EMPHASIS], [MUSIC CUE]. Structure: Hook → Parsha intro → Deep dive → Life application → Close.\n\nCommentary:\n{commentary}",
        ),
        config=cfg,
    )

    dailies = complete(
        system=SYSTEM_BASE,
        user=_mk_prompt(
            parsha=parsha,
            theme=args.theme,
            sources=sources,
            task=f"Create 6 daily reflections, each 150–200 words, that build toward Shabbat.\nUse exactly these headers:\n**Day 1 — Sunday**\n**Day 2 — Monday**\n**Day 3 — Tuesday**\n**Day 4 — Wednesday**\n**Day 5 — Thursday**\n**Day 6 — Erev Shabbat**\nDays 1–5 end with a single question. Day 6 ends with a Shabbat blessing.\n\nResearch:\n{research}\n\nCommentary:\n{commentary}",
        ),
        config=cfg,
    )

    dvar_torah = complete(
        system=SYSTEM_BASE,
        user=_mk_prompt(
            parsha=parsha,
            theme=args.theme,
            sources=sources,
            task=f"Write a Dvar Torah of 300–350 words.\nStart with: **Dvar Torah — Parashat {parsha}**\nNo bullet points.\nInclude one classical source and one modern voice, and end with Shabbat Shalom.\n\nResearch:\n{research}\n\nCommentary:\n{commentary}",
        ),
        config=cfg,
    )

    note = render_markdown(
        NoteParts(
            date=on_date,
            parsha=parsha,
            theme=args.theme,
            research=research,
            commentary=commentary,
            script=script,
            dailies=dailies,
            dvar_torah=dvar_torah,
        )
    )

    out_dir = Path(args.vault) / args.folder
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{on_date.isoformat()} - Parashat {parsha}.md"

    if out_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing note: {out_path} (use --force)")

    out_path.write_text(note, encoding="utf-8")

    # Print a small JSON-ish summary for automation/logging (stdout).
    print(
        {
            "written": str(out_path),
            "parsha": parsha,
            "date": on_date.isoformat(),
            "theme": args.theme,
            "sources": [asdict(s) for s in sources],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

