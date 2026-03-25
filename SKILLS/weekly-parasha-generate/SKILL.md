---
name: weekly-parasha-generate
description: Generates a weekly Torah study note (research, commentary, podcast script, daily reflections, dvar torah) and writes a single Markdown file into an Obsidian vault. Use when preparing the weekly parasha study output for Obsidian.
---

# Weekly Parasha (Obsidian Note Generator)

## What this skill does

- Resolves the current parsha with `hdate` and `PARSHA_MAP` (same mapping as `app.py`)
- Collects optional live context for citations (Hebcal leyning summary + Wikipedia when available)
- Uses the same **instruction prompts** as `agents/*.py` (via `prompts/agent_prompts.py`)
- Uses Claude via the official Anthropic Python SDK (`anthropic`) to generate:
  - Research
  - Commentary
  - Podcast Script
  - Daily Reflections (6 days)
  - Dvar Torah
- Writes **one** Markdown file to the **local filesystem** (Obsidian vault), same layout as before:
  - **Directory:** `{OBSIDIAN_VAULT}/{OBSIDIAN_FOLDER}/` (defaults: `/data/.openclaw/obsidian-vault/Torah Study/`)
  - **Filename:** `YYYY-MM-DD - Parashat <EnglishParsha>.md`
  - **Note shape:** YAML frontmatter (`date`, `parsha`, `theme`, `generator`) then `# Torah Study — Parashat …` and sections `## Research`, `## Commentary`, `## Podcast Script`, `## Daily Reflections`, `## Dvar Torah` (see `src/render.py`).
  - Paths are **expanded and resolved** (`~` → home, absolute path) before writing.

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

## Output

- File: `YYYY-MM-DD - Parashat <Parsha>.md`
- Headings:
  - `## Research`
  - `## Commentary`
  - `## Podcast Script`
  - `## Daily Reflections`
  - `## Dvar Torah`

