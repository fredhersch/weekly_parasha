import os
from dataclasses import dataclass
from typing import Optional

from anthropic import Anthropic


@dataclass(frozen=True)
class ClaudeConfig:
    model: str
    max_tokens: int = 3000
    temperature: float = 0.6


def _default_model() -> str:
    return os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")


def complete(*, system: str, user: str, config: Optional[ClaudeConfig] = None) -> str:
    cfg = config or ClaudeConfig(model=_default_model())
    client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    msg = client.messages.create(
        model=cfg.model,
        max_tokens=cfg.max_tokens,
        temperature=cfg.temperature,
        system=system,
        messages=[{"role": "user", "content": user}],
    )

    # Anthropic SDK returns content blocks; we want the concatenated text.
    chunks: list[str] = []
    for block in msg.content:
        if getattr(block, "type", None) == "text":
            chunks.append(block.text)
    return "".join(chunks).strip()

