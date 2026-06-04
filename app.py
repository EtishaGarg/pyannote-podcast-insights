from __future__ import annotations

import json
from pathlib import Path

import streamlit as st

from src.config import (
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    OPENAI_MODEL,
)
from src.pipeline import process_audio
from src.storage.files import create_job, write_bytes


st.set_page_config(page_title="Podcast Insights", layout="wide")


def _format_ts(seconds: float) -> str:
    minutes = int(seconds // 60)
    remaining_seconds = int(seconds % 60)
    return f"{minutes:02d}:{remaining_seconds:02d}"


st.title("Podcast Insights")
st.caption("Upload a short podcast clip to generate transcript, speaker stats, and content insights.")

with st.sidebar:
    st.subheader("Run Mode")
    st.write(f"`OPENAI_MODEL={OPENAI_MODEL}`")
    st.warning(
        "Real diarization and transcription are enabled. Expect model download "
        "latency on the first run."
    )

uploaded_file = st.file_uploader("Upload an mp3 or wav file", type=sorted(ALLOWED_EXTENSIONS))

if uploaded_file is not None:
    uploaded_bytes = uploaded_file.getvalue()
    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")
    if extension not in ALLOWED_EXTENSIONS:
        st.error("Unsupported file format.")
        st.stop()

    file_size_mb = len(uploaded_bytes) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        st.error(f"File exceeds {MAX_FILE_SIZE_MB} MB.")
        st.stop()

    st.audio(uploaded_bytes)

    if st.button("Process podcast", type="primary"):
        job_id, upload_dir, job_dir = create_job(uploaded_file.name)
        input_path = write_bytes(upload_dir, uploaded_file.name, uploaded_bytes)

        with st.status("Running pipeline", expanded=True) as status:
            try:
                st.write("Saving upload")
                st.write("Standardizing audio")
                st.write("Running diarization")
                st.write("Running transcription")
                st.write("Generating insights")
                results = process_audio(job_dir, input_path)
                status.update(label="Pipeline complete", state="complete")
            except Exception as exc:
                status.update(label="Pipeline failed", state="error")
                st.error(str(exc))
                st.stop()

        st.success(f"Finished job `{job_id}`")

        transcript_col, stats_col = st.columns([2, 1])
        with transcript_col:
            st.subheader("Transcript")
            for segment in results["transcript"]:
                st.markdown(
                    f"**{segment['speaker']}** `[{_format_ts(segment['start'])} - {_format_ts(segment['end'])}]`  \n"
                    f"{segment['text']}"
                )

        with stats_col:
            st.subheader("Speaker Stats")
            for speaker in results["speakers"]:
                st.metric(speaker["speaker_id"], f"{speaker['talk_time_sec']} sec")
                st.caption(
                    f"Turns: {speaker['turn_count']} · Longest monologue: {speaker['longest_monologue_sec']} sec"
                )

        st.subheader("Insights")
        if results.get("insights_error"):
            st.error(f"OpenAI insights failed: {results['insights_error']}")
        else:
            st.write(results["insights"]["summary"])
            st.write("**Topics**")
            st.write(", ".join(results["insights"]["topics"]))
            st.write(f"**Host guess:** {results['insights']['host_guess']}")
            st.caption(results["insights"]["host_guess_reason"])

            if results["insights"]["youtube_title_suggestions"]:
                st.write("**YouTube title suggestions**")
                for title in results["insights"]["youtube_title_suggestions"]:
                    st.markdown(f"- {title}")

            if results["insights"]["youtube_description"]:
                st.write("**YouTube description**")
                st.write(results["insights"]["youtube_description"])

            if results["insights"]["timestamps"]:
                st.write("**Timestamps**")
                for chapter in results["insights"]["timestamps"]:
                    st.markdown(
                        f"`[{_format_ts(chapter['start'])} - {_format_ts(chapter['end'])}]` "
                        f"**{chapter['title']}** — {chapter['reason']}"
                    )

        st.subheader("Shorts")
        if results["shorts"]:
            for clip in results["shorts"]:
                st.markdown(
                    f"**{clip['title']}** `[{_format_ts(clip['start'])} - {_format_ts(clip['end'])}]` — {clip['reason']}"
                )
        elif not results.get("insights_error"):
            st.write("No short clip suggestions returned.")

        st.download_button(
            "Download results JSON",
            data=json.dumps(results, indent=2),
            file_name=f"{job_id}_results.json",
            mime="application/json",
        )
else:
    st.write("Upload a file to start.")
