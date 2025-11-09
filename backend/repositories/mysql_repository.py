from typing import List, Optional
from sqlalchemy.orm import Session
from models import User, Recording, RecordingChunk
from models.recording import RecordingStatus
from datetime import datetime


class MySQLUserRepository:
    """MySQL implementation of UserRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, google_id: str, email: str, display_name: str, avatar_url: str) -> User:
        user = User(
            google_id=google_id,
            email=email,
            display_name=display_name,
            avatar_url=avatar_url
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()
    
    def get_user_by_google_id(self, google_id: str) -> Optional[User]:
        return self.db.query(User).filter(User.google_id == google_id).first()
    
    def update_user(self, user_id: str, **kwargs) -> Optional[User]:
        user = self.get_user_by_id(user_id)
        if user:
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            user.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(user)
        return user


class MySQLRecordingRepository:
    """MySQL implementation of RecordingRepository"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_recording(self, user_id: str) -> Recording:
        recording = Recording(user_id=user_id)
        self.db.add(recording)
        self.db.commit()
        self.db.refresh(recording)
        return recording
    
    def get_recording(self, recording_id: str) -> Optional[Recording]:
        return self.db.query(Recording).filter(Recording.id == recording_id).first()
    
    def list_recordings(self, user_id: str) -> List[Recording]:
        return self.db.query(Recording).filter(Recording.user_id == user_id).order_by(Recording.created_at.desc()).all()
    
    def add_chunk(self, recording_id: str, chunk_index: int, chunk_path: str, duration: Optional[float] = None) -> RecordingChunk:
        chunk = RecordingChunk(
            recording_id=recording_id,
            chunk_index=chunk_index,
            audio_blob_path=chunk_path,
            duration_seconds=duration
        )
        self.db.add(chunk)
        self.db.commit()
        self.db.refresh(chunk)
        return chunk
    
    def get_chunks(self, recording_id: str) -> List[RecordingChunk]:
        return self.db.query(RecordingChunk).filter(
            RecordingChunk.recording_id == recording_id
        ).order_by(RecordingChunk.chunk_index).all()
    
    def mark_paused(self, recording_id: str) -> Optional[Recording]:
        recording = self.get_recording(recording_id)
        if recording:
            recording.status = RecordingStatus.paused
            recording.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(recording)
        return recording
    
    def mark_ended(self, recording_id: str, audio_file_path: str, transcription: str) -> Optional[Recording]:
        recording = self.get_recording(recording_id)
        if recording:
            recording.status = RecordingStatus.ended
            recording.audio_file_path = audio_file_path
            recording.transcription_text = transcription
            recording.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(recording)
        return recording