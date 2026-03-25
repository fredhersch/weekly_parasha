from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from google.cloud import texttospeech


@dataclass(frozen=True)
class TtsConfig:
    language_code: str = "en-US"
    voice_name: str = "en-US-Journey-F"
    speaking_rate: float = 1.0


def synthesize_mp3(*, text: str, out_path: Path, cfg: TtsConfig) -> None:
    client = texttospeech.TextToSpeechClient()

    synthesis_input = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(language_code=cfg.language_code, name=cfg.voice_name)
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3,
        speaking_rate=cfg.speaking_rate,
    )

    resp = client.synthesize_speech(input=synthesis_input, voice=voice, audio_config=audio_config)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(resp.audio_content)

