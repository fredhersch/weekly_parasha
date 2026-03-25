---
name: weekly-parasha-podcast
description: Generates a podcast MP3 from a provided script text (produced by the weekly parasha generator). Use when converting the generated script into audio.
---

# Weekly Parasha (Podcast Generator)

## What this skill does

- Accepts a script (from Skill 1) via `--script-file` or stdin
- Uses Google Cloud Text-to-Speech to generate a **single MP3**
- Saves locally (no upload in the first version)

## Requirements

- `GOOGLE_APPLICATION_CREDENTIALS` set to a Google service account JSON with Text-to-Speech access
- Optional: `OBSIDIAN_VAULT` (default: `/data/.openclaw/obsidian-vault`)

## Install (VPS)

From the repo root:

```bash
python3 -m venv SKILLS/weekly-parasha-podcast/.venv
SKILLS/weekly-parasha-podcast/.venv/bin/pip install -r SKILLS/weekly-parasha-podcast/requirements.txt
```

## Run

From a script file:

```bash
SKILLS/weekly-parasha-podcast/.venv/bin/python SKILLS/weekly-parasha-podcast/src/podcast.py --script-file /path/to/script.txt --title \"Parashat Tzav\"
```

From stdin:

```bash
cat /path/to/script.txt | SKILLS/weekly-parasha-podcast/.venv/bin/python SKILLS/weekly-parasha-podcast/src/podcast.py --title \"Parashat Tzav\"
```

## Output

By default, writes into:

- `/data/.openclaw/obsidian-vault/Podcast/YYYY-MM-DD-weekly-parasha.mp3`

Override output directory with `--out-dir`.

