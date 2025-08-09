import streamlit as st
import requests

st.set_page_config(page_title="DIALOG", layout="wide")
API_URL = "https://pinal-api-dev.onrender.com/transcribe-with-diarization"


def format_time(sec):
    m = int(sec // 60)
    s = int(sec % 60)
    return f"{m}:{s:02d}"


# Session storage for files + transcripts
if "files" not in st.session_state:
    st.session_state.files = {}
if "active_file" not in st.session_state:
    st.session_state.active_file = None

# Upload
uploaded_file = st.file_uploader(" ", type=["mp3", "wav", "m4a"])
if uploaded_file and st.button("🚀 Transcribe"):
    with st.spinner("Transcribing file..."):
        files = {"file": (uploaded_file.name, uploaded_file, uploaded_file.type)}
        response = requests.post(API_URL, files=files)
    if response.status_code == 200:
        st.session_state.files[uploaded_file.name] = {
            "segments": response.json(),
            "type": uploaded_file.type
        }
        st.session_state.active_file = uploaded_file.name
    else:
        st.error(f"API error: {response.text}")

col1, col2 = st.columns([1, 3])

# File list
with col1:
    st.header("🗂 Files")
    for fname in st.session_state.files:
        if st.button(fname):
            st.session_state.active_file = fname

# File Transcript
with col2:
    if st.session_state.active_file:
        data = st.session_state.files[st.session_state.active_file]
        st.header(f"🎙 {st.session_state.active_file}")
        for seg in data["segments"]:
            if seg["text"].strip():
                st.markdown(f"**{seg['speaker']}** ({format_time(seg['start'])} → {format_time(seg['end'])})")
                st.write(seg["text"])
                st.divider()
    else:
        st.info("Upload a file to start.")
