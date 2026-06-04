from __future__ import annotations
from pathlib import Path
from faster_whisper import WhisperModel
from src.config import (
    WHISPER_BEAM_SIZE,
    WHISPER_COMPUTE_TYPE,
    WHISPER_DEVICE,
    WHISPER_LANGUAGE,
    WHISPER_MODEL,
)

_MODEL = None


def _load_model():
    global _MODEL

    if _MODEL is not None:
        return _MODEL

    _MODEL = WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
    )

    return _MODEL


def run_transcription(audio_path: Path) -> list[dict]:
    model = _load_model()

    segments, _ = model.transcribe(
        str(audio_path),
        beam_size=WHISPER_BEAM_SIZE,
        language=WHISPER_LANGUAGE,
        vad_filter=True,
        word_timestamps=True,
    )

    return [
        {
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "text": segment.text.strip(),
            "words": [
                {
                    "start": round(word.start, 3) if word.start is not None else None,
                    "end": round(word.end, 3) if word.end is not None else None,
                    "word": word.word.strip(),
                }
                for word in (segment.words or [])
                if word.word and word.word.strip()
            ],
        }
        for segment in segments
        if segment.text and segment.text.strip()
    ]
