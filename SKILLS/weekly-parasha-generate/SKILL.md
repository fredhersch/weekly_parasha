---
name: weekly-parasha-generate
description: Generates a weekly Torah study note (research, commentary, podcast script, daily reflections, dvar torah) and writes a single Markdown file into an Obsidian vault. Use when preparing the weekly parasha study output for Obsidian.
---

# Weekly Parasha (Obsidian Note Generator)

## What this skill does

- Computes the upcoming Shabbat parsha using Hebcal
- Collects a small live research bundle (Hebcal + Wikipedia summary when available)
- Uses Claude via the official Anthropic Python SDK (`anthropic`) to generate:
  - Research
  - Commentary
  - Podcast Script
  - Daily Reflections (6 days)
  - Dvar Torah
- Writes **one** Markdown note into the Obsidian vault folder:
  - `/data/.openclaw/obsidian-vault/Torah Study/`

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
- `CLAUDE_MODEL` (default: `claude-3-7-sonnet-latest`)

## Output

- File: `YYYY-MM-DD - Parashat <Parsha>.md`
- Headings:
  - `## Research`
  - `## Commentary`
  - `## Podcast Script`
  - `## Daily Reflections`
  - `## Dvar Torah`

