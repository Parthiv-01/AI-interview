from transformers import pipeline
import torch
import logging
from typing import Dict

class FallbackModels:
    def __init__(self):
        self._init_models()
        
    def _init_models(self):
        try:
            # Smaller model as fallback
            self.text_model = pipeline(
                "text-generation",
                model="distilgpt2",
                device=0 if torch.cuda.is_available() else -1
            )
            # Whisper for audio fallback
            import whisper
            self.audio_model = whisper.load_model("tiny")
        except Exception as e:
            logging.error(f"Failed to load fallback models: {e}")
            self.text_model = None
            self.audio_model = None
    
    def generate_question(self, context: str) -> str:
        if not self.text_model:
            return "Tell me about your experience with the technologies mentioned in your resume."
        
        prompt = f"Generate one technical interview question based on this resume context: {context[:1000]}"
        try:
            result = self.text_model(prompt, max_length=100, num_return_sequences=1)
            return result[0]['generated_text']
        except Exception as e:
            logging.error(f"Fallback question generation failed: {e}")
            return "Can you walk me through your most relevant project experience?"
    
    def evaluate_response(self, question: str, audio_path: str) -> Dict:
        if not self.audio_model:
            return {
                "score": 5.0,
                "feedback": "Evaluation service unavailable. Please try again later."
            }
        
        try:
            result = self.audio_model.transcribe(audio_path)
            transcript = result["text"]
            
            # Simple evaluation based on transcript length
            score = min(10, len(transcript.split()) / 10)
            
            return {
                "score": round(score, 1),
                "feedback": f"Transcript: {transcript[:200]}...",
                "full_transcript": transcript
            }
        except Exception as e:
            logging.error(f"Fallback evaluation failed: {e}")
            return {
                "score": 0.0,
                "feedback": "Could not evaluate response due to technical issues."
            }