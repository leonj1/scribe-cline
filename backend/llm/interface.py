from typing import Protocol


class LLMProvider(Protocol):
    """Interface for LLM transcription providers"""
    
    def transcribe_audio(self, audio_path: str) -> str:
        """
        Takes a path to an audio file and returns transcription text.
        
        Args:
            audio_path: Path to the audio file to transcribe
            
        Returns:
            Transcribed text as a string
        """
        ...