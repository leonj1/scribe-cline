import os
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
from starlette.requests import Request
from config import settings
from database import get_db
from repositories.mysql_repository import MySQLUserRepository, MySQLRecordingRepository
from services.auth_service import AuthService
from services.recording_service import RecordingService
from llm.requestyai_provider import RequestYaiProvider
from pydantic import BaseModel

router = APIRouter(prefix="/recordings", tags=["recordings"])


# Pydantic models for request/response
class RecordingResponse(BaseModel):
    id: str
    user_id: str
    status: str
    audio_file_path: str | None
    transcription_text: str | None
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Dependency to get current user from JWT token
async def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Extract and verify user from JWT token"""
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(' ')[1]
    
    user_repo = MySQLUserRepository(db)
    auth_service = AuthService(user_repo)
    
    user_id = auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    user = user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get("", response_model=List[RecordingResponse])
async def list_recordings(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all recordings for the current user"""
    recording_repo = MySQLRecordingRepository(db)
    recordings = recording_repo.list_recordings(current_user.id)
    
    return [
        RecordingResponse(
            id=r.id,
            user_id=r.user_id,
            status=r.status.value,
            audio_file_path=r.audio_file_path,
            transcription_text=r.transcription_text,
            created_at=r.created_at.isoformat(),
            updated_at=r.updated_at.isoformat()
        )
        for r in recordings
    ]


@router.post("", response_model=RecordingResponse)
async def create_recording(
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new recording session"""
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.create_recording(current_user.id)
    
    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat()
    )


@router.post("/{recording_id}/chunks")
async def upload_chunk(
    recording_id: str,
    chunk_index: int = Form(...),
    audio_chunk: UploadFile = File(...),
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload an audio chunk for a recording"""
    recording_repo = MySQLRecordingRepository(db)
    
    # Verify recording exists and belongs to user
    recording = recording_repo.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to upload to this recording"
        )
    
    # Create chunks directory
    chunks_dir = os.path.join(settings.AUDIO_STORAGE_PATH, "chunks", recording_id)
    os.makedirs(chunks_dir, exist_ok=True)
    
    # Save chunk file
    chunk_filename = f"chunk_{chunk_index}_{audio_chunk.filename}"
    chunk_path = os.path.join(chunks_dir, chunk_filename)
    
    with open(chunk_path, "wb") as f:
        content = await audio_chunk.read()
        f.write(content)
    
    # Add chunk to database
    chunk = recording_repo.add_chunk(recording_id, chunk_index, chunk_path)
    
    return {
        "message": "Chunk uploaded successfully",
        "chunk_id": chunk.id,
        "chunk_index": chunk.chunk_index
    }


@router.patch("/{recording_id}/pause")
async def pause_recording(
    recording_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a recording as paused"""
    recording_repo = MySQLRecordingRepository(db)
    
    # Verify recording exists and belongs to user
    recording = recording_repo.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recording"
        )
    
    recording = recording_repo.mark_paused(recording_id)
    
    return {
        "message": "Recording paused",
        "status": recording.status.value
    }


@router.post("/{recording_id}/finish")
async def finish_recording(
    recording_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Finish a recording, assemble chunks, and trigger transcription"""
    recording_repo = MySQLRecordingRepository(db)
    
    # Verify recording exists and belongs to user
    recording = recording_repo.get_recording(recording_id)
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to modify this recording"
        )
    
    # Assemble chunks and transcribe
    llm_provider = RequestYaiProvider()
    recording_service = RecordingService(recording_repo, llm_provider)
    
    try:
        recording = recording_service.finish_recording(recording_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to finish recording: {str(e)}"
        )
    
    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat()
    )


@router.get("/{recording_id}", response_model=RecordingResponse)
async def get_recording(
    recording_id: str,
    current_user = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific recording by ID"""
    recording_repo = MySQLRecordingRepository(db)
    recording = recording_repo.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recording not found"
        )
    
    if recording.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this recording"
        )
    
    return RecordingResponse(
        id=recording.id,
        user_id=recording.user_id,
        status=recording.status.value,
        audio_file_path=recording.audio_file_path,
        transcription_text=recording.transcription_text,
        created_at=recording.created_at.isoformat(),
        updated_at=recording.updated_at.isoformat()
    )