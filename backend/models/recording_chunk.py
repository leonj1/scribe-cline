from sqlalchemy import Column, String, DateTime, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from database import Base


class RecordingChunk(Base):
    __tablename__ = "recording_chunks"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    recording_id = Column(String(36), ForeignKey("recordings.id"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    audio_blob_path = Column(String(512), nullable=False)
    duration_seconds = Column(Float, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    recording = relationship("Recording", back_populates="chunks")