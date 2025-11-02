# Project Structure Steering Document

## Repository Layout

```
SD-Model-Manager/
├── .kiro/                          # Kiro spec-driven development
│   ├── steering/                   # Project steering documents
│   │   ├── product.md             # Product vision and features
│   │   ├── tech.md                # Technology stack and patterns
│   │   └── structure.md           # This file
│   └── specs/                     # Feature specifications
│       └── [feature-name]/        # Per-feature spec directory
│           ├── requirements.md    # Detailed requirements
│           ├── design.md          # Technical design
│           └── tasks.md           # Implementation tasks
├── src/sd_model_manager/          # Main package
│   ├── __init__.py
│   ├── __main__.py                # CLI entry point
│   ├── config.py                  # Application configuration
│   ├── download/                  # Download functionality (Phase 2)
│   │   ├── __init__.py
│   │   ├── civitai_client.py     # Civitai API client
│   │   ├── download_service.py    # Download orchestration
│   │   └── models.py              # Download data models
│   ├── registry/                  # Model registry (Phase 3)
│   │   ├── __init__.py
│   │   ├── scanners.py           # Filesystem scanners
│   │   ├── repositories.py        # Model data access
│   │   └── models.py              # Registry data models
│   ├── ui/                        # Web interface
│   │   ├── __init__.py
│   │   ├── api/                   # FastAPI backend
│   │   │   ├── __init__.py
│   │   │   ├── main.py           # FastAPI app factory
│   │   │   ├── download.py       # Download endpoints
│   │   │   └── models.py         # Model registry endpoints
│   │   └── frontend/             # React SPA
│   │       ├── src/
│   │       │   ├── App.tsx       # Root component
│   │       │   ├── main.tsx      # React entry point
│   │       │   ├── pages/        # Page components
│   │       │   │   ├── DownloadPage.tsx
│   │       │   │   └── ModelsPage.tsx
│   │       │   ├── components/   # Reusable components
│   │       │   │   ├── DownloadForm.tsx
│   │       │   │   ├── DownloadProgress.tsx
│   │       │   │   └── ModelCard.tsx
│   │       │   └── hooks/        # React hooks
│   │       │       ├── useDownload.ts
│   │       │       └── useModels.ts
│   │       ├── package.json
│   │       ├── tsconfig.json
│   │       └── vite.config.ts
│   └── lib/                       # Shared utilities
│       ├── __init__.py
│       ├── errors.py              # Exception hierarchy
│       └── logging_config.py      # Logging setup
├── tests/                         # Test suite
│   └── sd_model_manager/
│       ├── download/              # Download tests
│       │   ├── test_civitai_client.py
│       │   └── test_download_service.py
│       ├── registry/              # Registry tests (Phase 3)
│       └── ui/                    # UI tests
├── docs/                          # Documentation
│   ├── FRONTEND_SETUP.md         # Frontend setup guide
│   ├── LOGGING_STRATEGY.md       # Logging patterns
│   ├── TESTING_GUIDE.md          # Testing guidelines
│   └── PHASE2_COMMIT_READY.md    # Phase 2 summary
├── logs/                          # Application logs (auto-created)
│   └── app.log
├── models/                        # Default model storage (auto-created)
├── CLAUDE.md                      # Claude Code project context
├── pyproject.toml                # Python package configuration
├── uv.lock                        # Locked dependencies
└── README.md                      # Project documentation
```

## Module Responsibilities

### `download/` - Download Management
**Purpose**: Download models from Civitai with progress tracking

**Files**:
- `civitai_client.py`: API client for Civitai (metadata, download URLs)
- `download_service.py`: File download with progress tracking
- `models.py`: Pydantic models (DownloadRequest, DownloadProgress)

**Key Patterns**:
- Async/await for non-blocking downloads
- WebSocket for real-time progress updates
- Retry logic with exponential backoff
- HTTP redirect following (`follow_redirects=True`)

### `registry/` - Model Registry
**Purpose**: Scan and manage local model files

**Files** (Phase 3):
- `scanners.py`: Filesystem scanning (LoRA, Checkpoint, VAE, Embedding)
- `repositories.py`: Model data access and storage
- `models.py`: Pydantic models (ModelMetadata, ScanResult)

**Key Patterns**:
- Incremental scanning (detect changes only)
- Metadata extraction from `.civitai.info` files
- Model type detection via file patterns
- Caching for performance

### `ui/api/` - Backend API
**Purpose**: REST and WebSocket endpoints

**Files**:
- `main.py`: FastAPI app factory, CORS, logging setup
- `download.py`: `/api/download`, `/ws/download/{task_id}`
- `models.py`: `/api/models`, `/api/models/scan`, `/api/models/{id}`

**Key Patterns**:
- BackgroundTasks for async operations
- Pydantic request/response models
- Structured error responses
- WebSocket connection management

### `ui/frontend/` - React SPA
**Purpose**: User interface for download and viewing

**Structure**:
- `pages/`: Full-page components (DownloadPage, ModelsPage)
- `components/`: Reusable UI components
- `hooks/`: Custom React hooks for API integration

**Key Patterns**:
- Custom hooks for API calls (`useDownload`, `useModels`)
- WebSocket integration in hooks
- Loading/error states
- Responsive design with Tailwind CSS

### `lib/` - Shared Utilities
**Purpose**: Cross-cutting concerns

**Files**:
- `errors.py`: Exception hierarchy (DownloadError, NetworkError)
- `logging_config.py`: Rotating file handler, structured logging

**Key Patterns**:
- Single logging initialization with guard
- Structured exception context
- Configuration-driven logging

## File Naming Conventions

### Python Files
- **Services**: `*_service.py` (e.g., `download_service.py`)
- **API Clients**: `*_client.py` (e.g., `civitai_client.py`)
- **Data Models**: `models.py` (Pydantic models)
- **Utilities**: `*_config.py`, `*_utils.py`

### TypeScript Files
- **Pages**: `*Page.tsx` (e.g., `DownloadPage.tsx`)
- **Components**: `*.tsx` (e.g., `ModelCard.tsx`)
- **Hooks**: `use*.ts` (e.g., `useDownload.ts`)
- **Types**: `types.ts`, `*.types.ts`

### Test Files
- **Unit Tests**: `test_*.py` (e.g., `test_civitai_client.py`)
- **Integration Tests**: `test_integration_*.py`

## Import Patterns

### Backend
```python
# Absolute imports from package root
from sd_model_manager.download.civitai_client import CivitaiClient
from sd_model_manager.lib.errors import DownloadError
from sd_model_manager.config import get_config
```

### Frontend
```typescript
// Relative imports for project files
import { useDownload } from '../hooks/useDownload'
import { DownloadForm } from '../components/DownloadForm'

// Absolute imports for node_modules
import { useState, useEffect } from 'react'
```

## Configuration Files

### Backend Configuration
- `pyproject.toml`: Package metadata, dependencies, tool configs
- `uv.lock`: Locked dependency versions
- `src/sd_model_manager/config.py`: Application settings

### Frontend Configuration
- `package.json`: NPM scripts and dependencies
- `tsconfig.json`: TypeScript compiler options
- `vite.config.ts`: Build and dev server config
- `tailwind.config.js`: Tailwind CSS customization

## Git Workflow

### Branch Strategy
- `main`: Stable releases only
- `phase[N]/[feature-name]`: Feature development branches
  - `phase2/download-implementation` (completed)
  - `phase3/viewer-development` (current)

### Commit Patterns
- Descriptive prefixes: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`
- Reference phase numbers: `feat: Phase 2.15 - Fix logging initialization`

## Documentation Organization

### In-Code Documentation
- Docstrings: Google style for Python
- Type hints: Comprehensive for Python
- JSDoc: For complex TypeScript functions

### External Documentation
- `docs/`: Architecture and guides
- `.kiro/specs/`: Feature specifications
- `README.md`: Project overview and setup

## Testing Organization

### Test Structure
```
tests/
└── sd_model_manager/
    ├── download/
    │   ├── test_civitai_client.py      # Unit tests
    │   └── test_download_service.py     # Unit tests
    ├── registry/                        # Phase 3 tests
    └── ui/
        └── api/
            └── test_download_endpoints.py  # Integration tests
```

### Test Naming
- Test files: `test_*.py`
- Test classes: `Test*` (e.g., `TestCivitaiClient`)
- Test functions: `test_*` (e.g., `test_get_download_url`)

## Phase-Specific Patterns

### Phase 2 (Download) - Completed
- CLI → API → UI progression
- TDD with comprehensive test coverage
- Background task execution via FastAPI
- WebSocket for real-time updates

### Phase 3 (Viewer) - Current
- Filesystem scanning before API development
- Model registry pattern
- Grid view with lazy loading
- Search and filter capabilities
