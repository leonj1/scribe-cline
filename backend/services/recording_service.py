import os
from typing import List
from repositories.mysql_repository import MySQLRecordingRepository
from llm.requestyai_provider import RequestYaiProvider
from models import Recording
from config import settings


class RecordingService:
    """Service for handling recording operations"""
    
    def __init__(self, recording_repository: MySQLRecordingRepository, llm_provider: RequestYaiProvider):
        self.recording_repository = recording_repository
        self.llm_provider = llm_provider
    
    def assemble_chunks(self, recording_id: str) -> str:
        """
        Assemble all audio chunks for a recording into a single file
        
        Args:
            recording_id: ID of the recording
            
        Returns:
            Path to the assembled audio file
        """
        chunks = self.recording_repository.get_chunks(recording_id)
        
        if not chunks:
            raise ValueError(f"No chunks found for recording {recording_id}")
        
        # Sort chunks by index
        chunks.sort(key=lambda x: x.chunk_index)
        
        # Create output file path
        output_filename = f"{recording_id}.wav"
        output_path = os.path.join(settings.AUDIO_STORAGE_PATH, output_filename)
        
        # Ensure storage directory exists
        os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
        
        # Concatenate all chunks into a single file
        with open(output_path, 'wb') as outfile:
            for chunk in chunks:
                if os.path.exists(chunk.audio_blob_path):
                    with open(chunk.audio_blob_path, 'rb') as infile:
                        outfile.write(infile.read())
        
        return output_path
    
    def transcribe_recording(self, audio_path: str) -> str:
        """
        Transcribe audio file using LLM provider
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            Transcribed text
        """
        return self.llm_provider.transcribe_audio(audio_path)
    
    def finish_recording(self, recording_id: str) -> Recording:
        """
        Finish a recording: assemble chunks, transcribe, and update database
        
        Args:
            recording_id: ID of the recording to finish
            
        Returns:
            Updated Recording object
        """
        # Assemble audio chunks
        audio_path = self.assemble_chunks(recording_id)
        
        # Transcribe audio
        transcription = self.transcribe_recording(audio_path)
        
        # Update recording in database
        recording = self.recording_repository.mark_ended(
            recording_id=recording_id,
            audio_file_path=audio_path,
            transcription=transcription
        )
        
        if not recording:
            raise ValueError(f"Recording {recording_id} not found")
        
        return recording