---
name: weekly-parasha-generate
description: Generates a weekly Torah study note (research, commentary, podcast script, daily reflections, dvar torah) and writes a single Markdown file into an Obsidian vault. Use when preparing the weekly parasha study output for Obsidian.
---

# Weekly Parasha (Obsidian Note Generator)

## What this skill does

- Resolves the current parsha with `hdate` and `PARSHA_MAP` (same mapping as `app.py`)
- Uses the same **instruction prompts** as `agents/*.py` (via `prompts/agent_prompts.py`) as the **only** system instructions to the model (no extra context block on every step)
- States English + Hebrew parsha **only** in the research user message (same role as the old `get_parsha_info` tool)
- Uses Claude via the official Anthropic Python SDK (`anthropic`) to generate:
  - Research
  - Commentary
  - Podcast Script
  - Daily Reflections (6 days)
  - Dvar Torah
- Writes **one** Markdown file on disk under the Obsidian vault:
  - **Path:** `/data/.openclaw/obsidian-vault/Torah Study/` (defaults: vault `OBSIDIAN_VAULT=/data/.openclaw/obsidian-vault`, folder `OBSIDIAN_FOLDER=Torah Study`)
  - **Filename:** `YYYY-MM-DD - Parashat <EnglishParsha>.md`
  - **Note shape:** YAML frontmatter includes `title` (date + “Torah Study” + **parsha name**), plus `date`, `parsha`, `theme`, `generator`. The visible H1 matches that `title`. Then sections `## Research`, `## Commentary`, `## Podcast Script`, `## Daily Reflections`, `## Dvar Torah` (see `src/render.py`).
  - Paths are **expanded and resolved** (`~` → home, absolute path) before writing.
- After the file is written, **commits and pushes** the second-brain git repo by default (see below).

## Requirements

- Environment variable: `ANTHROPIC_API_KEY`
- Python 3.10+ recommended

## Install (VPS)

From the repo root:

```bash
python3 -m venv SKILLS/weekly-parasha-generate/.venv
SKILLS/weekly-parasha-generate/.venv/bin/pip install -r SKILLS/weekly-parasha-generate/requirements.txt
```

## Run

Default run (writes into `/data/.openclaw/obsidian-vault/Torah Study/`):

```bash
SKILLS/weekly-parasha-generate/.venv/bin/python SKILLS/weekly-parasha-generate/src/generate.py
```

With a theme:

```bash
SKILLS/weekly-parasha-generate/.venv/bin/python SKILLS/weekly-parasha-generate/src/generate.py --theme "faith and trust in God"
```

Override date or parsha:

```bash
SKILLS/weekly-parasha-generate/.venv/bin/python SKILLS/weekly-parasha-generate/src/generate.py --date 2026-03-28 --parsha "Tzav"
```

## Configuration

- `OBSIDIAN_VAULT` (default: `/data/.openclaw/obsidian-vault`)
- `OBSIDIAN_FOLDER` (default: `Torah Study`)
- `CLAUDE_MODEL` (default: `claude-sonnet-4-6`, matching `agents/*.py`)

### Second-brain git (commit + push)

By default, after saving the note the script runs `git add`, `git commit`, and `git push` in the **second-brain** repository root:

- **Git root:** `SECOND_BRAIN_GIT_ROOT` or `OBSIDIAN_GIT_ROOT` if set; otherwise the resolved `OBSIDIAN_VAULT` path (must contain a `.git` directory).
- **Disable:** `SECOND_BRAIN_GIT_PUSH=0` or pass `--no-git-push`.
- **Failure:** exits non-zero if `git commit` or `git push` fails (so automation can retry). If the path is not a git repo, push is skipped and reported in the printed summary under `git_push`.

## Output

- File: `YYYY-MM-DD - Parashat <Parsha>.md`
- Frontmatter `title` / H1: `YYYY-MM-DD — Torah Study — Parashat <Parsha>`
- Headings:
  - `## Research`
  - `## Commentary`
  - `## Podcast Script`
  - `## Daily Reflections`
  - `## Dvar Torah`

