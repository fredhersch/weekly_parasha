from __future__ import annotations

import argparse
import os
import sys
from dataclasses import asdict
from datetime import date, datetime
from pathlib import Path
from typing import Optional

# Repo skill layout: weekly-parasha-generate/{src,prompts}/
ROOT = Path(__file__).resolve().parent.parent
THIS_DIR = Path(__file__).resolve().parent
for p in (THIS_DIR, ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from claude import ClaudeConfig, complete  # noqa: E402
from parsha import ParshaInfo, resolve_parsha  # noqa: E402
from prompts.agent_prompts import (  # noqa: E402
    system_commentary,
    system_daily,
    system_dvar,
    system_research,
    system_script,
)
from render import NoteParts, render_markdown  # noqa: E402
from research import Source, collect_sources  # noqa: E402

SOURCES_SUFFIX = """
When "Context sources" are provided and non-empty, cite them in the body as [1], [2], etc. and end your response with:

### Sources
1. Title — URL
2. Title — URL

Do not invent URLs. If no context sources are listed, omit the ### Sources section entirely.
"""


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def _sources_block(sources: list[Source]) -> str:
    if not sources:
        return "(none)"
    lines = []
    for i, src in enumerate(sources, start=1):
        lines.append(f"{i}. {src.title} — {src.url}\n   Excerpt: {src.excerpt}")
    return "\n".join(lines)


def _context_prefix(*, parsha: ParshaInfo, theme: str, sources: list[Source]) -> str:
    return f"""Current parsha (English): {parsha.english}
Current parsha (Hebrew): {parsha.hebrew}
Calendar date for this run: {parsha.on_date.isoformat()}
Theme focus: {theme}

Context sources (for citation when relevant):
{_sources_block(sources)}
"""


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate weekly parasha study note for Obsidian.")
    ap.add_argument("--theme", default="general themes")
    ap.add_argument("--date", dest="on_date", default=None, help="YYYY-MM-DD (defaults to today)")
    ap.add_argument("--parsha", default=None, help="Override English parsha name (skips hdate map for label only)")
    ap.add_argument("--vault", default=os.getenv("OBSIDIAN_VAULT", "/data/.openclaw/obsidian-vault"))
    ap.add_argument("--folder", default=os.getenv("OBSIDIAN_FOLDER", "Torah Study"))
    ap.add_argument("--force", action="store_true")
    ap.add_argument(
        "--model",
        default=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
    )
    args = ap.parse_args(argv)

    on_date = _parse_date(args.on_date) if args.on_date else date.today()
    parsha_info = resolve_parsha(on_date=on_date)
    if args.parsha:
        parsha_info = ParshaInfo(
            english=args.parsha.strip(),
            hebrew=parsha_info.hebrew,
            on_date=on_date,
        )

    sources = collect_sources(parsha_info)
    ctx = _context_prefix(parsha=parsha_info, theme=args.theme, sources=sources)

    cfg = ClaudeConfig(model=args.model, max_tokens=4096, temperature=0.6)

    # Mirrors workflows/parasha_workflow.py user prompts; system = agents/*.py instructions.
    research_prompt = (
        "Research this week's Torah portion. The current parasha is given above. "
        "Draw on your knowledge of the text, Rashi, Ramban, and key themes."
    )
    if args.theme and args.theme != "general themes":
        research_prompt += f" Focus especially on the theme of: {args.theme}"

    research = complete(
        system=system_research() + SOURCES_SUFFIX,
        user=f"{ctx}\n\n{research_prompt}",
        config=cfg,
    )

    commentary = complete(
        system=system_commentary() + SOURCES_SUFFIX,
        user=f"{ctx}\n\nBased on this research, generate deep insights:\n\n{research}",
        config=cfg,
    )

    script = complete(
        system=system_script() + SOURCES_SUFFIX,
        user=f"{ctx}\n\nCreate a podcast script from this commentary:\n\n{commentary}",
        config=cfg,
    )

    dailies = complete(
        system=system_daily() + SOURCES_SUFFIX,
        user=(
            f"{ctx}\n\nBased on this research and commentary, create 6 daily parasha reflections "
            f"(Sunday through Erev Shabbat):\n\n{script}"
        ),
        config=cfg,
    )

    dvar_torah = complete(
        system=system_dvar() + SOURCES_SUFFIX,
        user=(
            f"{ctx}\n\nBased on this research and commentary, write a Dvar Torah for the Shabbat table:\n\n{script}"
        ),
        config=cfg,
    )

    note = render_markdown(
        NoteParts(
            date=on_date,
            parsha=parsha_info.english,
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
    out_path = out_dir / f"{on_date.isoformat()} - Parashat {parsha_info.english}.md"

    if out_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing note: {out_path} (use --force)")

    out_path.write_text(note, encoding="utf-8")

    print(
        {
            "written": str(out_path),
            "parsha": parsha_info.english,
            "hebrew": parsha_info.hebrew,
            "date": on_date.isoformat(),
            "theme": args.theme,
            "sources": [asdict(s) for s in sources],
        }
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
