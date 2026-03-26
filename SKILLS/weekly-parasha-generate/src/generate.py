from __future__ import annotations

import argparse
import os
import sys
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
from git_second_brain import push_note, resolve_git_root  # noqa: E402
from render import NoteParts, render_markdown  # noqa: E402

# Default Obsidian vault on the VPS (override with OBSIDIAN_VAULT / OBSIDIAN_FOLDER).
DEFAULT_OBSIDIAN_VAULT = "/data/.openclaw/obsidian-vault"
DEFAULT_OBSIDIAN_FOLDER = "Torah Study"


def _parse_date(s: str) -> date:
    return datetime.strptime(s, "%Y-%m-%d").date()


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate weekly parasha study note for Obsidian.")
    ap.add_argument("--theme", default="general themes")
    ap.add_argument("--date", dest="on_date", default=None, help="YYYY-MM-DD (defaults to today)")
    ap.add_argument("--parsha", default=None, help="Override English parsha name (skips hdate map for label only)")
    ap.add_argument(
        "--vault",
        default=os.getenv("OBSIDIAN_VAULT", DEFAULT_OBSIDIAN_VAULT),
        help=f"Obsidian vault root (default: {DEFAULT_OBSIDIAN_VAULT})",
    )
    ap.add_argument(
        "--folder",
        default=os.getenv("OBSIDIAN_FOLDER", DEFAULT_OBSIDIAN_FOLDER),
        help=f"Subfolder under vault (default: {DEFAULT_OBSIDIAN_FOLDER!r})",
    )
    ap.add_argument("--force", action="store_true")
    ap.add_argument(
        "--model",
        default=os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6"),
    )
    ap.add_argument(
        "--no-git-push",
        action="store_true",
        help="Do not commit/push the new note to the second-brain git repo after writing.",
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

    cfg = ClaudeConfig(model=args.model, max_tokens=4096, temperature=0.6)

    # User messages mirror workflows/parasha_workflow.py. System = agents/*.py only.
    # Parsha is stated on the research step only (replaces get_parsha_info).
    research_prompt = (
        f"Research this week's Torah portion. The parasha is Parashat {parsha_info.english} "
        f"(Hebrew: {parsha_info.hebrew}). "
        "Draw on your knowledge of the text, Rashi, Ramban, and key themes."
    )
    if args.theme and args.theme != "general themes":
        research_prompt += f" Focus especially on the theme of: {args.theme}"

    research = complete(
        system=system_research(),
        user=research_prompt,
        config=cfg,
    )

    commentary = complete(
        system=system_commentary(),
        user=f"Based on this research, generate deep insights:\n\n{research}",
        config=cfg,
    )

    script = complete(
        system=system_script(),
        user=f"Create a podcast script from this commentary:\n\n{commentary}",
        config=cfg,
    )

    dailies = complete(
        system=system_daily(),
        user=(
            "Based on this research and commentary, create 6 daily parasha reflections "
            f"(Sunday through Erev Shabbat):\n\n{script}"
        ),
        config=cfg,
    )

    dvar_torah = complete(
        system=system_dvar(),
        user=(
            "Based on this research and commentary, write a Dvar Torah for the Shabbat table:\n\n"
            f"{script}"
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

    vault_root = Path(args.vault).expanduser().resolve()
    out_dir = vault_root / args.folder
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{on_date.isoformat()} - Parashat {parsha_info.english}.md"

    if out_path.exists() and not args.force:
        raise SystemExit(f"Refusing to overwrite existing note: {out_path} (use --force)")

    out_path.write_text(note, encoding="utf-8")

    summary: dict = {
        "written": str(out_path.resolve()),
        "vault": str(vault_root),
        "folder": args.folder,
        "parsha": parsha_info.english,
        "hebrew": parsha_info.hebrew,
        "date": on_date.isoformat(),
        "theme": args.theme,
    }

    git_push_enabled = os.getenv("SECOND_BRAIN_GIT_PUSH", "1").strip().lower() not in (
        "0",
        "false",
        "no",
        "off",
    )
    if not args.no_git_push and git_push_enabled:
        git_root = resolve_git_root(vault_root=vault_root)
        commit_msg = (
            f"Torah study: Parashat {parsha_info.english} ({on_date.isoformat()})"
        )
        git_result = push_note(
            git_root=git_root,
            file_path=out_path.resolve(),
            commit_message=commit_msg,
        )
        summary["git_push"] = git_result
        if not git_result.get("ok") and not git_result.get("skipped"):
            print(summary)
            raise SystemExit(
                f"Git push failed at step {git_result.get('step')!r}: "
                f"{git_result.get('stderr') or git_result.get('stdout') or git_result}"
            )

    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
