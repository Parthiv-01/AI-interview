import streamlit as st
from utils.pdf_extractor import PDFTextExtractor
from utils.audio_processor import AudioInterviewer
import librosa
import soundfile as sf
import io
import uuid
import os

# Initialize components
pdf_extractor = PDFTextExtractor()
interviewer = AudioInterviewer()

# Session state
def init_session():
    defaults = {
        "session_id": str(uuid.uuid4()),
        "resume_text": "",
        "questions": [],
        "responses": [],
        "current_q": 0,
        "audio_data": None,
        "sr": 16000
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

def upload_resume():
    st.header("📄 Upload Resume")
    pdf = st.file_uploader("Choose PDF file", type="pdf")
    
    if pdf and not st.session_state.resume_text:
        with st.spinner("Processing resume..."):
            try:
                st.session_state.resume_text = pdf_extractor.extract_text(pdf)
                st.success("Resume processed successfully!")
            except ValueError as e:
                st.error(str(e) + ". Please upload a text-based PDF.")
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")

def record_audio():
    st.header("🎤 Record Your Answer")
    audio_bytes = st.file_uploader("Or upload audio file", type=["wav", "mp3"])
    
    if audio_bytes:
        try:
            audio, sr = librosa.load(io.BytesIO(audio_bytes.read()), sr=16000)
            st.session_state.audio_data = audio
            st.session_state.sr = sr
            st.audio(audio_bytes, format="audio/wav")
            return True
        except Exception as e:
            st.error(f"Error loading audio: {str(e)}")
    return False

def conduct_interview():
    if not st.session_state.resume_text:
        return
    
    st.header("💬 Mock Interview")
    
    # Generate first question if needed
    if not st.session_state.questions:
        with st.spinner("Generating first question..."):
            question = interviewer.generate_question(st.session_state.resume_text)
            st.session_state.questions.append(question)
            st.rerun()
    
    # Show current question
    current_q = st.session_state.questions[st.session_state.current_q]
    st.subheader(f"Question {st.session_state.current_q + 1}")
    st.write(current_q)
    
    # Audio recording/upload
    has_audio = record_audio()
    
    if has_audio and st.button("Submit Answer"):
        with st.spinner("Evaluating your response..."):
            evaluation = interviewer.evaluate_response(
                current_q,
                st.session_state.audio_data,
                st.session_state.sr
            )
            
            st.session_state.responses.append({
                "question": current_q,
                "evaluation": evaluation
            })
            
            # Show feedback
            st.subheader("📝 Feedback")
            st.metric("Score", f"{evaluation['score']}/10")
            st.write(evaluation["feedback"])
            
            # Clear audio for next question
            st.session_state.audio_data = None
            
            # Move to next question or finish
            if st.session_state.current_q < 4:  # Max 5 questions
                st.session_state.current_q += 1
                with st.spinner("Generating next question..."):
                    new_question = interviewer.generate_question(st.session_state.resume_text)
                    st.session_state.questions.append(new_question)
                    st.rerun()
            else:
                st.success("🎉 Interview completed!")
                if st.button("Start New Interview"):
                    st.session_state.clear()
                    init_session()
                    st.rerun()

def main():
    st.set_page_config(page_title="AI Mock Interview", layout="wide")
    st.title("🎙️ AI-Powered Mock Interview")
    
    init_session()
    upload_resume()
    conduct_interview()

if __name__ == "__main__":
    main()