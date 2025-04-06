import transformers
import librosa
import numpy as np
from typing import Dict, List

class AudioInterviewer:
    def __init__(self):
        self.pipe = transformers.pipeline(
            model='fixie-ai/ultravox-v0_5-llama-3_2-1b',
            trust_remote_code=True
        )
    
    def generate_question(self, context: str, audio: np.ndarray = None, sr: int = 16000) -> str:
        """Generate interview question based on context or audio"""
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
        
        if audio is not None:
            output = self.pipe(
                {'audio': audio, 'turns': turns, 'sampling_rate': sr},
                max_new_tokens=50
            )
        else:
            output = self.pipe(
                {'turns': turns},
                max_new_tokens=50
            )
        
        return output[0]['generation']['content']

    def evaluate_response(self, question: str, audio: np.ndarray, sr: int = 16000) -> Dict:
        """Evaluate audio response to interview question"""
        turns = [
            {
                "role": "system",
                "content": "You are an interview evaluator. Provide constructive feedback on this answer."
            },
            {
                "role": "user",
                "content": f"Question: {question}\nPlease evaluate this response:"
            }
        ]
        
        output = self.pipe(
            {'audio': audio, 'turns': turns, 'sampling_rate': sr},
            max_new_tokens=100
        )
        
        feedback = output[0]['generation']['content']
        
        # Simple scoring based on response length (more sophisticated scoring could be added)
        score = min(10, len(feedback.split()) / 10)
        
        return {
            "score": round(score, 1),
            "feedback": feedback
        }