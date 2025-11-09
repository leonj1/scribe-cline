import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from config import settings
from database import init_db
from routers import auth_router, recordings_router

# Create FastAPI app
app = FastAPI(
    title="Audio Transcription Service API",
    description="Healthcare audio transcription platform with Google OAuth and LLM integration",
    version="1.0.0"
)

# Add session middleware for OAuth
app.add_middleware(SessionMiddleware, secret_key=settings.JWT_SECRET)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(recordings_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    # Create audio storage directory
    os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
    
    # Initialize database tables
    init_db()
    print("Database initialized successfully")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Audio Transcription Service API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)