from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


def resolve_ffmpeg() -> tuple[str, dict[str, str]]:
    candidates = [
        "/opt/homebrew/opt/ffmpeg@7/bin/ffmpeg",
        "/usr/local/opt/ffmpeg@7/bin/ffmpeg",
        shutil.which("ffmpeg"),
    ]

    ffmpeg_path = next(
        (candidate for candidate in candidates if candidate and Path(candidate).exists()),
        None,
    )
    if ffmpeg_path is None:
        raise RuntimeError("ffmpeg is not installed.")

    env = os.environ.copy()
    if "ffmpeg@7" in ffmpeg_path:
        lib_dir = str(Path(ffmpeg_path).resolve().parents[1] / "lib")
        existing = env.get("DYLD_FALLBACK_LIBRARY_PATH", "")
        env["DYLD_FALLBACK_LIBRARY_PATH"] = (
            f"{lib_dir}:{existing}" if existing else lib_dir
        )

    return ffmpeg_path, env


def standardize_audio(input_path: Path, output_path: Path) -> Path:
    try:
        ffmpeg_path, env = resolve_ffmpeg()
    except RuntimeError:
        shutil.copy2(input_path, output_path)
        return output_path

    command = [
        ffmpeg_path,
        "-y",
        "-i",
        str(input_path),
        "-ar",
        "16000",
        "-ac",
        "1",
        str(output_path),
    ]
    subprocess.run(command, check=True, capture_output=True, env=env)
    return output_path
