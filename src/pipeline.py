from __future__ import annotations

from pathlib import Path

from src.alignment.merge import assign_speakers_to_transcript
from src.audio.preprocess import standardize_audio
from src.diarization.pyannote_service import run_diarization
from src.insights.llm_service import generate_insights
from src.insights.stats import compute_speaker_stats
from src.storage.files import update_job_status, write_json
from src.transcription.whisper_service import run_transcription


def process_audio(job_dir: Path, input_path: Path) -> dict:
    update_job_status(job_dir, "processing")

    try:
        normalized_path = input_path.parent / "normalized.wav"
        standardize_audio(input_path, normalized_path)

        diarization = run_diarization(normalized_path)
        transcription = run_transcription(normalized_path)
        transcript = assign_speakers_to_transcript(diarization, transcription)
        speakers = compute_speaker_stats(transcript)

        transcript_payload = [segment.model_dump() for segment in transcript]
        speakers_payload = [speaker.model_dump() for speaker in speakers]
        insights_error = None

        try:
            insights, shorts = generate_insights(transcript)
            insights_payload = insights.model_dump()
            shorts_payload = [clip.model_dump() for clip in shorts]
        except Exception as exc:
            insights_error = str(exc)
            insights_payload = {
                "summary": "",
                "topics": [],
                "host_guess": "",
                "host_guess_reason": "",
                "youtube_description": "",
                "youtube_title_suggestions": [],
                "timestamps": [],
            }
            shorts_payload = []

        write_json(job_dir / "diarization.json", {"segments": diarization})
        write_json(job_dir / "transcription.json", {"segments": transcription})
        write_json(job_dir / "transcript.json", {"segments": transcript_payload})
        write_json(job_dir / "speakers.json", {"speakers": speakers_payload})
        write_json(
            job_dir / "insights.json",
            {
                "insights": insights_payload,
                "error": insights_error,
            },
        )
        write_json(job_dir / "shorts.json", {"shorts": shorts_payload})
        update_job_status(job_dir, "completed")

        return {
            "diarization": diarization,
            "transcription": transcription,
            "transcript": transcript_payload,
            "speakers": speakers_payload,
            "insights": insights_payload,
            "insights_error": insights_error,
            "shorts": shorts_payload,
        }
    except Exception as exc:
        update_job_status(job_dir, "failed", error=str(exc))
        raise
