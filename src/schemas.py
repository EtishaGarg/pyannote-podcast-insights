from __future__ import annotations

from datetime import datetime, timezone
from typing import Literal

from pydantic import BaseModel, Field


class TranscriptSegment(BaseModel):
    start: float
    end: float
    speaker: str
    text: str


class SpeakerStats(BaseModel):
    speaker_id: str
    label: str
    talk_time_sec: float
    turn_count: int
    longest_monologue_sec: float


class ShortCandidate(BaseModel):
    title: str
    start: float
    end: float
    reason: str


class TimestampChapter(BaseModel):
    title: str
    start: float
    end: float
    reason: str


class Insights(BaseModel):
    summary: str
    topics: list[str]
    host_guess: str
    host_guess_reason: str
    timestamps: list[TimestampChapter]
    youtube_description: str
    youtube_title_suggestions: list[str]




class JobMeta(BaseModel):
    job_id: str
    filename: str
    status: Literal["uploaded", "processing", "completed", "failed"]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    error: str | None = None
