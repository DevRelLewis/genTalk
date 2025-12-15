import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import tempfile
import base64

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

LANGUAGES = {
    "English": "en",
    "Spanish": "es",
    "French": "fr",
    "German": "de",
    "Italian": "it",
    "Portuguese": "pt",
    "Dutch": "nl",
    "Russian": "ru",
    "Chinese": "zh",
    "Japanese": "ja",
    "Korean": "ko",
    "Nepali": "ne"
}

VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]

MAX_TRANSCRIPT_TURNS = 20

if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "selected_language" not in st.session_state:
    st.session_state.selected_language = "English"
if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = "alloy"
if "last_audio_id" not in st.session_state:
    st.session_state.last_audio_id = None
if "processing" not in st.session_state:
    st.session_state.processing = False
if "show_recorder" not in st.session_state:
    st.session_state.show_recorder = False

st.title("GetTalk - Live Speech-to-Speech")

col1, col2 = st.columns(2)
with col1:
    language = st.selectbox(
        "Language",
        options=list(LANGUAGES.keys()),
        index=list(LANGUAGES.keys()).index(st.session_state.selected_language)
    )
    st.session_state.selected_language = language

with col2:
    voice = st.selectbox(
        "AI Voice",
        options=VOICES,
        index=VOICES.index(st.session_state.selected_voice)
    )
    st.session_state.selected_voice = voice

st.markdown("---")

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    if st.button("🎤 Start Conversation", use_container_width=True, type="primary"):
        st.session_state.show_recorder = True
        st.rerun()

if st.session_state.show_recorder:
    st.markdown("**Record your message:**")
    audio_value = st.audio_input("Click to record")

    if st.button("Stop & Clear"):
        st.session_state.show_recorder = False
        st.session_state.last_audio_id = None
        st.rerun()

st.markdown("---")


def transcribe_audio(audio_bytes):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
        tmp_file.write(audio_bytes.getvalue())
        tmp_file_path = tmp_file.name

    try:
        with open(tmp_file_path, "rb") as audio_file:
            transcript = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language=LANGUAGES[st.session_state.selected_language]
            )
        return transcript.text
    finally:
        os.unlink(tmp_file_path)


def get_ai_response(user_message):
    language_name = st.session_state.selected_language

    response = client.chat.completions.create(
        model="gpt-4.5",
        messages=[
            {"role": "system", "content": f"You are a helpful assistant. Always respond in {language_name}."},
            {"role": "user", "content": user_message}
        ],
        max_tokens=150
    )
    return response.choices[0].message.content


def text_to_speech(text):
    response = client.audio.speech.create(
        model="tts-1",
        voice=st.session_state.selected_voice,
        input=text
    )
    return response.content


def add_to_transcript(speaker, message):
    st.session_state.transcript.append({"speaker": speaker, "message": message})
    if len(st.session_state.transcript) > MAX_TRANSCRIPT_TURNS:
        st.session_state.transcript = st.session_state.transcript[-MAX_TRANSCRIPT_TURNS:]


def process_input(user_text):
    if not user_text or not user_text.strip():
        return

    user_text = user_text.strip()
    add_to_transcript("user", user_text)

    try:
        ai_response = get_ai_response(user_text)
        add_to_transcript("ai", ai_response)

        audio_data = text_to_speech(ai_response)

        audio_base64 = base64.b64encode(audio_data).decode()
        audio_html = f'<audio autoplay controls><source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3"></audio>'
        st.markdown(audio_html, unsafe_allow_html=True)

        st.session_state.processing = False

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.session_state.processing = False


if st.session_state.show_recorder and 'audio_value' in locals() and audio_value is not None and not st.session_state.processing:
    audio_id = id(audio_value)

    if st.session_state.last_audio_id != audio_id:
        st.session_state.last_audio_id = audio_id
        st.session_state.processing = True

        with st.spinner("Transcribing..."):
            try:
                transcribed_text = transcribe_audio(audio_value)
                if transcribed_text:
                    st.info(f"You said: {transcribed_text}")
                    process_input(transcribed_text)
            except Exception as e:
                st.error(f"Transcription failed: {str(e)}")
                st.session_state.processing = False

st.markdown("### Transcript")

if st.session_state.transcript:
    for turn in st.session_state.transcript:
        if turn["speaker"] == "user":
            st.markdown(f"👤 **You:** {turn['message']}")
        else:
            st.markdown(f"🤖 **AI:** {turn['message']}")
else:
    st.info("No conversation yet. Click 'Start Conversation' to begin!")