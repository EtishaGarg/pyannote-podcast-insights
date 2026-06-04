from __future__ import annotations
from pathlib import Path
from pyannote.audio import Pipeline
from src.config import HUGGINGFACE_TOKEN, PYANNOTE_PIPELINE


_PIPELINE = None


def _load_pipeline():
    global _PIPELINE

    if _PIPELINE is not None:
        return _PIPELINE

    _PIPELINE = Pipeline.from_pretrained(
        PYANNOTE_PIPELINE,
        token=HUGGINGFACE_TOKEN,
    )

    return _PIPELINE


def run_diarization(audio_path: Path) -> list[dict]:
    pipeline = _load_pipeline()
    output = pipeline(str(audio_path), num_speakers=2)
    diarization = getattr(output, "exclusive_speaker_diarization", None)

    return [
        {
            "start": round(turn.start, 3),
            "end": round(turn.end, 3),
            "speaker": speaker,
        }
        for turn, speaker in diarization
    ]
