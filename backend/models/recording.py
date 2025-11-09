from sqlalchemy import Column, String, DateTime, Enum, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum
from database import Base


class RecordingStatus(enum.Enum):
    active = "active"
    paused = "paused"
    ended = "ended"


class Recording(Base):
    __tablename__ = "recordings"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    status = Column(Enum(RecordingStatus), default=RecordingStatus.active, nullable=False)
    audio_file_path = Column(String(512), nullable=True)
    transcription_text = Column(Text, nullable=True)
    llm_provider = Column(String(50), default="requestyai", nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="recordings")
    chunks = relationship("RecordingChunk", back_populates="recording", cascade="all, delete-orphan")