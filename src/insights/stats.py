from __future__ import annotations

from collections import defaultdict

from src.schemas import SpeakerStats, TranscriptSegment


def compute_speaker_stats(transcript: list[TranscriptSegment]) -> list[SpeakerStats]:
    stats: dict[str, dict[str, float | int]] = defaultdict(
        lambda: {"talk_time_sec": 0.0, "turn_count": 0, "longest_monologue_sec": 0.0}
    )

    for segment in transcript:
        duration = segment.end - segment.start
        speaker_stats = stats[segment.speaker]
        speaker_stats["talk_time_sec"] += duration
        speaker_stats["turn_count"] += 1
        speaker_stats["longest_monologue_sec"] = max(
            float(speaker_stats["longest_monologue_sec"]),
            duration,
        )

    return [
        SpeakerStats(
            speaker_id=speaker,
            label=speaker,
            talk_time_sec=round(float(values["talk_time_sec"]), 2),
            turn_count=int(values["turn_count"]),
            longest_monologue_sec=round(float(values["longest_monologue_sec"]), 2),
        )
        for speaker, values in sorted(stats.items())
    ]
