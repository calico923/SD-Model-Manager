# Technical Steering Document

## Architecture Overview

**Monorepo Structure**: Backend and frontend in unified Python package
- Backend: FastAPI REST API + WebSocket server
- Frontend: React SPA served via Vite dev server
- Integration: Vite proxy for development, static serving for production

## Technology Stack

### Backend
- **Python**: 3.11+ (required)
- **FastAPI**: 0.100+ for REST API and WebSocket
- **Pydantic**: V2 for data validation and settings
- **httpx**: Async HTTP client with redirect support
- **SQLAlchemy**: (Future) For model registry database
- **pytest**: Testing framework with async support

### Frontend
- **React**: 18.2+ with TypeScript
- **TypeScript**: 5.0+ for type safety
- **Vite**: 4.4+ for build and dev server
- **Tailwind CSS**: 3.3+ for styling
- **React Router**: 6.15+ for client-side routing

### Development Tools
- **uv**: Python package manager and virtual environment
- **npm**: Frontend package management
- **pytest**: Backend testing
- **pytest-asyncio**: Async test support
- **pytest-cov**: Code coverage reporting

## Configuration

### Backend Configuration (`src/sd_model_manager/config.py`)
```python
host: str = "127.0.0.1"
port: int = 8188
model_dir: Path = "./models"
log_level: str = "INFO"
log_dir: Path = "./logs"
civitai_api_key: str = ""  # Optional
```

### Frontend Configuration (`vite.config.ts`)
```typescript
server: {
  port: 5173,
  proxy: {
    '/api': 'http://localhost:8188',
    '/ws': 'ws://localhost:8188'
  }
}
```

## Development Commands

### Backend Development
```bash
# Install dependencies
uv sync

# Run backend server (development)
python -m sd_model_manager

# Run backend server (production)
uvicorn sd_model_manager.ui.api.main:create_app --host 0.0.0.0 --port 8188

# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/sd_model_manager --cov-report=html
```

### Frontend Development
```bash
# Navigate to frontend directory
cd src/sd_model_manager/ui/frontend

# Install dependencies
npm install

# Run dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

### Full Stack Development
```bash
# Terminal 1: Backend
python -m sd_model_manager

# Terminal 2: Frontend
cd src/sd_model_manager/ui/frontend && npm run dev

# Access application at http://localhost:5173/
```

## API Design Patterns

### REST Endpoints
- `/api/download` - POST: Start model download
- `/api/models` - GET: List scanned models
- `/api/models/scan` - POST: Trigger filesystem scan
- `/api/models/{id}` - GET: Get model details

### WebSocket Endpoints
- `/ws/download/{task_id}` - Real-time download progress

### Response Format
```typescript
interface ApiResponse<T> {
  success: boolean
  data?: T
  error?: string
}
```

## Error Handling Strategy

### Backend
- Custom exception hierarchy (`lib/errors.py`)
- `DownloadError`, `NetworkError`, `ValidationError`
- Structured error responses with context
- Comprehensive logging (`lib/logging_config.py`)

### Frontend
- Centralized error handling in hooks
- User-friendly error messages
- Toast notifications for errors
- Retry logic for transient failures

## Testing Strategy

### Backend Testing
- **Unit Tests**: Individual functions and classes (pytest)
- **Integration Tests**: API endpoints and services
- **Mock External APIs**: httpx_mock for Civitai API
- **Coverage Target**: >80% for new code

### Frontend Testing
- (Future) React Testing Library for components
- (Future) Vitest for unit tests
- (Future) Playwright for E2E tests

## Security Considerations

### API Security
- CORS configuration for frontend
- Optional API key for Civitai
- Input validation via Pydantic
- Path traversal protection

### File System Security
- Sandboxed model directory
- File type validation
- Size limits on uploads/downloads
- No arbitrary file execution

## Performance Targets

### Backend
- API response: <200ms for metadata queries
- File scan: <5 seconds for 1000 models
- Download speed: Limited by network, not CPU
- WebSocket latency: <100ms for progress updates

### Frontend
- Initial load: <3s on 3G
- Time to interactive: <5s
- Bundle size: <500KB initial
- 60fps UI interactions

## Deployment

### Current (Development)
- Backend: Python process via `python -m sd_model_manager`
- Frontend: Vite dev server via `npm run dev`
- Proxy: Vite proxy for API/WebSocket routing

### Future (Production)
- Backend: uvicorn with multiple workers
- Frontend: Static files served by FastAPI
- Reverse proxy: nginx or Caddy
- Process manager: systemd or Docker
