import streamlit as st
import requests

st.set_page_config(page_title="DIALOG", layout="wide")
API_URL = "https://pinal-api-dev.onrender.com/transcribe"


def format_time(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m}:{s:02d}"


def transcript_to_txt(segments):
    """Export transcript as plain text."""
    lines = []
    for seg in segments:
        if seg["text"].strip():
            lines.append(f"{seg['speaker']}: {seg['text']}")
    return "\n".join(lines)


def transcript_to_srt(segments):
    """Export transcript in .srt subtitle format."""
    def format_time_srt(seconds: float) -> str:
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = int(seconds % 60)
        ms = int((seconds % 1) * 1000)
        return f"{h:02}:{m:02}:{s:02},{ms:03}"

    srt_lines = []
    for i, seg in enumerate(segments, start=1):
        if not seg["text"].strip():
            continue
        start = format_time_srt(seg["start"])
        end = format_time_srt(seg["end"])
        srt_lines.append(f"{i}\n{start} --> {end}\n{seg['speaker']}: {seg['text']}\n")
    return "\n".join(srt_lines)


# Session storage
if "files" not in st.session_state:
    st.session_state.files = {}
if "active_file" not in st.session_state:
    st.session_state.active_file = None

# Sidebar for options
st.sidebar.header("⚙️ Settings")
mode = st.sidebar.radio(
    "Choose mode",
    ["Transcription (same language)", "Translation (English)"],
    index=0
)
mode_param = "transcription" if "Transcription" in mode else "translation"

# Upload + action
uploaded_file = st.file_uploader("Upload audio", type=["mp3", "wav", "m4a", "mp4"])
if uploaded_file and st.button("🚀 Process"):
    with st.spinner("Processing file..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(f"{API_URL}?mode={mode_param}", files=files)
    if response.status_code == 200:
        st.session_state.files[uploaded_file.name] = {
            "segments": response.json(),
            "type": uploaded_file.type,
            "mode": mode_param,
        }
        st.session_state.active_file = uploaded_file.name
    else:
        st.error(f"API error: {response.text}")

col1, col2 = st.columns([1, 3])

# File list
with col1:
    st.header("🗂 Files")
    for fname, fdata in st.session_state.files.items():
        label = fname
        if fdata.get("mode") == "translation":
            label += " 🌍"
        if st.button(label):
            st.session_state.active_file = fname

# Transcript view
with col2:
    if st.session_state.active_file:
        data = st.session_state.files[st.session_state.active_file]
        st.header(f"🎙 {st.session_state.active_file}")
        if data.get("mode") == "translation":
            st.caption("Translated to English")
        else:
            st.caption("Transcribed in original language")

        segments = data["segments"]

        # Download buttons
        txt_data = transcript_to_txt(segments)
        srt_data = transcript_to_srt(segments)

        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                "⬇️ Download TXT",
                txt_data,
                file_name=f"{st.session_state.active_file}.txt",
                mime="text/plain"
            )
        with col_dl2:
            st.download_button(
                "⬇️ Download SRT",
                srt_data,
                file_name=f"{st.session_state.active_file}.srt",
                mime="text/plain"
            )

        # Display transcript
        for seg in segments:
            if seg["text"].strip():
                st.markdown(f"**{seg['speaker']}** ({format_time(seg['start'])} → {format_time(seg['end'])})")
                st.write(seg["text"])
                st.divider()
    else:
        st.info("Upload a file to start.")
