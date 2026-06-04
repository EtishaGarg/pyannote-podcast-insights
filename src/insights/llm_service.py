from __future__ import annotations

import json

from src.config import OPENAI_API_KEY, OPENAI_MODEL
from src.schemas import Insights, ShortCandidate, TimestampChapter, TranscriptSegment


INSIGHTS_SCHEMA = {
    "name": "podcast_insights",
    "strict": True,
    "schema": {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "summary": {"type": "string"},
            "topics": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 6,
            },
            "host_guess": {"type": "string"},
            "host_guess_reason": {"type": "string"},
            "youtube_description": {"type": "string"},
            "youtube_title_suggestions": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 3,
                "maxItems": 5,
            },
            "timestamps": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["title", "start", "end", "reason"],
                },
                "minItems": 3,
                "maxItems": 8,
            },
            "shorts": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "title": {"type": "string"},
                        "start": {"type": "number"},
                        "end": {"type": "number"},
                        "reason": {"type": "string"},
                    },
                    "required": ["title", "start", "end", "reason"],
                },
                "minItems": 3,
                "maxItems": 5,
            },
        },
        "required": [
            "summary",
            "topics",
            "host_guess",
            "host_guess_reason",
            "youtube_description",
            "youtube_title_suggestions",
            "timestamps",
            "shorts",
        ],
    },
}


def _transcript_payload(transcript: list[TranscriptSegment]) -> list[dict]:
    return [
        {
            "start": round(segment.start, 3),
            "end": round(segment.end, 3),
            "speaker": segment.speaker,
            "text": segment.text,
        }
        for segment in transcript
    ]


def generate_insights(transcript: list[TranscriptSegment]) -> tuple[Insights, list[ShortCandidate]]:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY.")

    try:
        from openai import OpenAI
    except ImportError as exc:
        raise RuntimeError(
            "OpenAI SDK is not installed. Run `pip install -r requirements.txt`."
        ) from exc

    client = OpenAI(api_key=OPENAI_API_KEY)
    transcript_payload = _transcript_payload(transcript)

    response = client.responses.create(
        model=OPENAI_MODEL,
        input=[
            {
                "role": "system",
                "content": [
                    {
                        "type": "input_text",
                        "text": (
                            "Analyze the provided speaker-labeled podcast transcript. "
                            "Return only the structured JSON matching the requested schema. "
                            "Do not invent speakers or timestamps. Use timestamps from the transcript. "
                            "For timestamps, generate YouTube-style chapter markers. Prefer chapter starts at host questions. "
                            "Use the guessed host speaker to identify "
                            "question-led transitions when possible. Also generate a strong YouTube description and at least "
                            "three clickable but accurate title suggestions. Make sure the title suggestions include: "
                            "one SEO-safe title, one curiosity-driven title, and one technical or developer-focused title. "
                            "For shorts, identify 3 to 5 strong short-form clip candidates using exact transcript timestamps. "
                            "Prefer clips built around a strong hook, a host question followed by a clear answer, a surprising "
                            "insight, a memorable quote, or a concise technical point. Avoid clips that start or end mid-thought "
                            "when possible, and favor segments that can stand alone in short-form distribution."
                        ),
                    }
                ],
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "input_text",
                        "text": json.dumps(
                            {
                                "task": "Generate podcast insights and short clip candidates.",
                                "transcript": transcript_payload,
                            }
                        ),
                    }
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                **INSIGHTS_SCHEMA,
            }
        },
    )

    payload = json.loads(response.output_text)
    insights = Insights(
        summary=str(payload["summary"]),
        topics=[str(topic) for topic in payload["topics"]],
        host_guess=str(payload["host_guess"]),
        host_guess_reason=str(payload["host_guess_reason"]),
        youtube_description=str(payload["youtube_description"]),
        youtube_title_suggestions=[
            str(title) for title in payload["youtube_title_suggestions"]
        ],
        timestamps=[
            TimestampChapter(
                title=str(item["title"]),
                start=float(item["start"]),
                end=float(item["end"]),
                reason=str(item["reason"]),
            )
            for item in payload["timestamps"]
        ],
    )
    shorts = [
        ShortCandidate(
            title=str(item["title"]),
            start=float(item["start"]),
            end=float(item["end"]),
            reason=str(item["reason"]),
        )
        for item in payload["shorts"]
    ]
    return insights, shorts
