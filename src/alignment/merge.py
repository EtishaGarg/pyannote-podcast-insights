from __future__ import annotations
from src.schemas import TranscriptSegment

def assign_speakers_to_transcript(
    diarization_segments: list[dict],
    transcription_segments: list[dict],
    fill_nearest: bool = False,
) -> list[TranscriptSegment]:
    diarization_segments = sorted(diarization_segments, key=lambda x: x["start"])
    aligned_segments: list[TranscriptSegment] = []

    for seg in transcription_segments:
        seg_start = seg.get("start", 0.0)
        seg_end = seg.get("end", 0.0)
        speaker_overlap: dict[str, float] = {}

        for dia in diarization_segments:
            intersection = min(dia["end"], seg_end) - max(dia["start"], seg_start)
            if intersection <= 0:
                continue

            speaker = dia["speaker"]
            speaker_overlap[speaker] = speaker_overlap.get(speaker, 0.0) + intersection

        if speaker_overlap:
            speaker = max(speaker_overlap.items(), key=lambda x: x[1])[0]
        elif fill_nearest and diarization_segments:
            midpoint = (seg_start + seg_end) / 2
            nearest = min(
                diarization_segments,
                key=lambda x: abs(((x["start"] + x["end"]) / 2) - midpoint),
            )
            speaker = nearest["speaker"]
        else:
            speaker = "UNKNOWN"

        aligned_segments.append(
            TranscriptSegment(
                start=seg_start,
                end=seg_end,
                speaker=speaker,
                text=seg.get("text", "").strip(),
            )
        )

    return aligned_segments