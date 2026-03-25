from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date
from pathlib import Path
from typing import Optional

THIS_DIR = Path(__file__).resolve().parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))

from tts import TtsConfig, synthesize_mp3  # noqa: E402


def _read_text(path: Optional[str]) -> str:
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def _slug(s: str) -> str:
    s2 = re.sub(r"[^a-zA-Z0-9]+", "-", s.strip()).strip("-").lower()
    return s2 or "podcast"


def main(argv: Optional[list[str]] = None) -> int:
    ap = argparse.ArgumentParser(description="Generate a podcast mp3 from a provided script.")
    ap.add_argument("--script-file", default=None, help="Path to script text (or omit to read from stdin)")
    ap.add_argument("--title", default="weekly-parasha")
    ap.add_argument("--out-dir", default=None, help="Output directory (default: <vault>/Podcast or ./out)")
    ap.add_argument("--vault", default=os.getenv("OBSIDIAN_VAULT", "/data/.openclaw/obsidian-vault"))
    ap.add_argument("--language", default="en-US")
    ap.add_argument("--voice", default="en-US-Journey-F")
    ap.add_argument("--speaking-rate", type=float, default=1.0)
    args = ap.parse_args(argv)

    script = _read_text(args.script_file).strip()
    if not script:
        raise SystemExit("Empty script input")

    out_dir = Path(args.out_dir) if args.out_dir else (Path(args.vault) / "Podcast")
    out_name = f"{date.today().isoformat()}-{_slug(args.title)}.mp3"
    out_path = out_dir / out_name

    cfg = TtsConfig(language_code=args.language, voice_name=args.voice, speaking_rate=args.speaking_rate)
    synthesize_mp3(text=script, out_path=out_path, cfg=cfg)

    print({"written": str(out_path), "bytes": out_path.stat().st_size})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

