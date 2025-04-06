import transformers
import librosa
import numpy as np
from typing import Dict, List, Optional
import logging
from utils.fallback_models import FallbackModels
import os
import tempfile

class AudioInterviewer:
    def __init__(self):
        self.fallback = FallbackModels()
        self._init_primary_model()
    
    def _init_primary_model(self):
        try:
            self.pipe = transformers.pipeline(
                model='fixie-ai/ultravox-v0_5-llama-3_2-1b',
                trust_remote_code=True
            )
            self.model_available = True
        except Exception as e:
            logging.warning(f"Primary model unavailable, using fallback: {e}")
            self.model_available = False
    
    def generate_question(self, context: str) -> str:
        if not self.model_available:
            return self.fallback.generate_question(context)
        
        try:
            turns = [
                {
                    "role": "system",
                    "content": "You are a professional interviewer. Generate one technical question based on the context."
                },
                {
                    "role": "user",
                    "content": context[:2000]  # Limit context size
                }
            ]
            
            output = self.pipe(
                {'turns': turns},
                max_new_tokens=50
            )
            return output[0]['generation']['content']
        except Exception as e:
            logging.error(f"Question generation failed, using fallback: {e}")
            return self.fallback.generate_question(context)

    def evaluate_response(self, question: str, audio_bytes: bytes) -> Dict:
        # Save audio to temp file for processing
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            try:
                tmp.write(audio_bytes)
                tmp_path = tmp.name
                
                if not self.model_available:
                    return self.fallback.evaluate_response(question, tmp_path)
                
                try:
                    audio, sr = librosa.load(tmp_path, sr=16000)
                    
                    turns = [
                        {
                            "role": "system",
                            "content": "You are an interview evaluator. Provide constructive feedback."
                        },
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": f"Question: {question}"},
                                {"type": "audio", "audio": audio},
                                {"type": "text", "text": "Evaluate this response."}
                            ]
                        }
                    ]
                    
                    output = self.pipe(
                        {'audio': audio, 'turns': turns, 'sampling_rate': sr},
                        max_new_tokens=100
                    )
                    
                    feedback = output[0]['generation']['content']
                    score = min(10, len(feedback.split()) / 10)  # Simple scoring
                    
                    return {
                        "score": round(score, 1),
                        "feedback": feedback
                    }
                except Exception as e:
                    logging.error(f"Primary evaluation failed, using fallback: {e}")
                    return self.fallback.evaluate_response(question, tmp_path)
            finally:
                try:
                    os.unlink(tmp_path)
                except:
                    pass