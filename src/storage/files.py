from __future__ import annotations

import json
import uuid
from pathlib import Path

from src.config import JOBS_DIR, UPLOADS_DIR
from src.schemas import JobMeta


def ensure_storage_dirs() -> None:
    UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    JOBS_DIR.mkdir(parents=True, exist_ok=True)


def create_job(filename: str) -> tuple[str, Path, Path]:
    ensure_storage_dirs()
    job_id = uuid.uuid4().hex[:12]
    upload_dir = UPLOADS_DIR / job_id
    job_dir = JOBS_DIR / job_id
    upload_dir.mkdir(parents=True, exist_ok=True)
    job_dir.mkdir(parents=True, exist_ok=True)
    meta = JobMeta(job_id=job_id, filename=filename, status="uploaded")
    write_json(job_dir / "meta.json", meta.model_dump(mode="json"))
    return job_id, upload_dir, job_dir


def write_bytes(upload_dir: Path, filename: str, data: bytes) -> Path:
    target_path = upload_dir / filename
    target_path.write_bytes(data)
    return target_path


def write_json(path: Path, payload: dict | list) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> dict | list:
    return json.loads(path.read_text(encoding="utf-8"))


def update_job_status(job_dir: Path, status: str, error: str | None = None) -> None:
    meta_path = job_dir / "meta.json"
    meta = read_json(meta_path)
    meta["status"] = status
    meta["error"] = error
    write_json(meta_path, meta)
