# 🩺 Audio Transcription Service

A healthcare-focused audio transcription platform with Google OAuth authentication, chunked audio recording, and AI-powered transcription using LLM providers.

## Features

- ✅ Google OAuth 2.0 Authentication
- ✅ Real-time audio recording with chunked uploads
- ✅ Pause/Resume recording functionality
- ✅ Automatic transcription via LLM provider (RequestYai)
- ✅ Three-pane dashboard interface
- ✅ Recording history management
- ✅ Repository pattern for database abstraction
- ✅ Docker containerization
- ✅ Railway deployment ready

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database operations
- **MySQL** - Primary database
- **Authlib** - Google OAuth integration
- **PyJWT** - JWT token management
- **Pydantic** - Data validation

### Frontend
- **React 18** - UI framework
- **Ant Design** - UI component library
- **Axios** - HTTP client
- **React Router** - Navigation

## Architecture

```
├── backend/               # FastAPI application
│   ├── models/           # Database models (User, Recording, RecordingChunk)
│   ├── repositories/     # Repository pattern implementations
│   ├── services/         # Business logic (Auth, Recording)
│   ├── routers/          # API endpoints (auth, recordings)
│   ├── llm/              # LLM provider abstraction
│   └── main.py           # Application entry point
├── frontend/             # React application
│   ├── src/
│   │   ├── pages/       # Landing, Dashboard, AuthCallback
│   │   ├── components/  # RecordingList, RecordingView, WaveformAnimation
│   │   └── context/     # AuthContext for state management
│   └── public/
└── docker-compose.yml    # Multi-container orchestration
```

## Local Development Setup

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Google Cloud Console account (for OAuth credentials)

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/scribe-cline.git
cd scribe-cline
```

### Step 2: Configure Google OAuth

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select existing
3. Enable Google+ API
4. Create OAuth 2.0 credentials:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/auth/google/callback`
5. Copy the Client ID and Client Secret

### Step 3: Environment Configuration

Create a `.env` file from the example:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-actual-client-secret
JWT_SECRET=generate-a-strong-random-string-here
LLM_API_KEY=your-requestyai-api-key-if-available
```

### Step 4: Start the Application

Using the Makefile:

```bash
make start
```

Or manually with Docker Compose:

```bash
docker compose up -d
```

This will start:
- MySQL on port 3306
- Backend API on port 8000
- Frontend on port 3000

### Step 5: Verify Services

Check that all containers are running:

```bash
docker compose ps
```

Test the backend:

```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

Test the frontend:

```bash
curl -I http://localhost:3000
# Expected: 200 OK
```

View API documentation:

```bash
open http://localhost:8000/docs
```

### Step 6: Access the Application

Open your browser and navigate to:

```
http://localhost:3000
```

Click "Login with Google" to authenticate.

## Stopping the Application

```bash
make stop
```

Or:

```bash
docker compose down
```

## Restarting the Application

```bash
make restart
```

## API Endpoints

### Authentication
- `GET /auth/google/login` - Initiate Google OAuth flow
- `GET /auth/google/callback` - OAuth callback handler
- `GET /auth/verify` - Verify JWT token

### Recordings
- `GET /recordings` - List user's recordings
- `POST /recordings` - Create new recording session
- `GET /recordings/{id}` - Get recording details
- `POST /recordings/{id}/chunks` - Upload audio chunk
- `PATCH /recordings/{id}/pause` - Pause recording
- `POST /recordings/{id}/finish` - Finish and transcribe recording

## Railway Deployment

### Prerequisites
- Railway account
- Railway CLI installed
- Railway token

### Deploy to Railway

1. **Set Railway Token**:
```bash
export RAILWAY_TOKEN=20727ba7-8cd3-4a1b-a566-c2014ce081da
```

2. **Initialize Railway Project**:
```bash
railway init
```

3. **Add MySQL Database**:
```bash
railway add --database mysql
```

4. **Set Environment Variables**:
```bash
railway variables set GOOGLE_CLIENT_ID=your-client-id
railway variables set GOOGLE_CLIENT_SECRET=your-secret
railway variables set JWT_SECRET=your-jwt-secret
railway variables set LLM_API_KEY=your-llm-key
```

5. **Deploy Backend**:
```bash
cd backend
railway up
```

6. **Deploy Frontend**:
```bash
cd ../frontend
railway up
```

7. **Update OAuth Redirect URI**:
After deployment, update your Google OAuth credentials with the Railway backend URL:
```
https://your-backend-url.railway.app/auth/google/callback
```

## Development

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm start
```

## Database Schema

### Users Table
- id (UUID)
- google_id (unique)
- email
- display_name
- avatar_url
- created_at, updated_at

### Recordings Table
- id (UUID)
- user_id (FK)
- status (active, paused, ended)
- audio_file_path
- transcription_text
- llm_provider
- created_at, updated_at

### Recording Chunks Table
- id (UUID)
- recording_id (FK)
- chunk_index
- audio_blob_path
- duration_seconds
- uploaded_at

## LLM Provider

The system uses an abstracted LLM provider interface. Currently configured with a mock RequestYai provider.

To integrate the real API:

1. Edit `backend/llm/requestyai_provider.py`
2. Replace the mock implementation with actual API calls
3. Add your API key to environment variables

## Security Considerations

- All API endpoints (except auth) require JWT authentication
- Audio files stored with unique recording IDs
- CORS configured for specific frontend origin
- Database passwords should be changed in production
- Use HTTPS in production environments

## Troubleshooting

### Port Already in Use
If ports 3000, 8000, or 3306 are already in use:
```bash
# Stop conflicting services or change ports in docker-compose.yml
```

### Database Connection Issues
```bash
# Check MySQL container logs
docker logs transcription-mysql

# Restart MySQL container
docker compose restart mysql
```

### OAuth Errors
- Ensure redirect URI matches exactly in Google Console
- Check that GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are correct
- Verify the callback URL is accessible

## License

MIT

## Contributing

Contributions welcome! Please open an issue or submit a pull request.

## Support

For issues and questions, please open a GitHub issue.