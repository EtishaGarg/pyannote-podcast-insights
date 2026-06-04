from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
UPLOADS_DIR = STORAGE_DIR / "uploads"
JOBS_DIR = STORAGE_DIR / "jobs"

ALLOWED_EXTENSIONS = {"mp3", "wav"}
MAX_FILE_SIZE_MB = 100

HUGGINGFACE_TOKEN = os.getenv("HUGGINGFACE_TOKEN", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")
PYANNOTE_PIPELINE = os.getenv(
    "PYANNOTE_PIPELINE", "pyannote/speaker-diarization-community-1"
)
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
WHISPER_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
WHISPER_LANGUAGE = os.getenv("WHISPER_LANGUAGE", "").strip() or None
