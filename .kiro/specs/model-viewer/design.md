# Technical Design Document: Model Viewer

## Overview

### Purpose
The Model Viewer provides a web-based interface for Stable Diffusion artists to view, search, organize, and manage their local model collections. It scans the filesystem for model files, integrates Civitai metadata, displays preview images, and enables category-based organization (Active/Archive) to optimize ComfyUI startup performance.

### Goals
1. **Visual Catalog**: Grid-based display with preview images and metadata
2. **Efficient Discovery**: Fast search and filtering across large collections (1000+ models)
3. **Category Management**: Move models between Active/Archive to control ComfyUI loading
4. **Metadata Integration**: Parse and display Civitai metadata from `.civitai.info` files
5. **Performance**: Sub-5-second scanning for 1000 models, sub-1-second grid rendering
6. **Architectural Consistency**: Reuse Phase 2 patterns (Pydantic V2, FastAPI, async/await)

### Non-Goals
1. **Phase 1**: Model editing, metadata modification, or file deletion
2. **Phase 1**: Direct Civitai API integration (uses existing `.civitai.info` files only)
3. **Phase 1**: Database persistence (uses in-memory caching with future DB migration path)
4. **Phase 1**: Bulk file operations beyond move (e.g., rename, duplicate detection)
5. **Phase 1**: Advanced filtering (multiple tags, date ranges, size ranges)

---

## Architecture

### High-Level Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (React)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ ModelsPage   │  │ ModelCard    │  │ SearchBar    │      │
│  │              │  │ (Grid Item)  │  │ & Filters    │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                  │                  │               │
│         └──────────────────┴──────────────────┘               │
│                             │                                 │
└─────────────────────────────┼─────────────────────────────────┘
                              │ HTTP REST
┌─────────────────────────────┼─────────────────────────────────┐
│                             ▼                                 │
│                   ModelsAPI (FastAPI Router)                  │
│  ┌──────────────────────────────────────────────────────┐    │
│  │ GET /api/models        → List all models            │    │
│  │ POST /api/models/scan  → Trigger filesystem scan    │    │
│  │ GET /api/models/{id}   → Get model details          │    │
│  │ POST /api/models/{id}/move → Move file (category)   │    │
│  │ POST /api/models/bulk-move → Move multiple models   │    │
│  └──────────────┬───────────────────────────────────────┘    │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐    │
│  │         ModelRepository (Service Layer)              │    │
│  │  - In-memory cache (Dict[str, ModelInfo])            │    │
│  │  - Singleton pattern (like ProgressManager)          │    │
│  │  - Cache invalidation on scan/move                   │    │
│  └──────────────┬───────────────────────────────────────┘    │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐    │
│  │          ModelScanner (Business Logic)               │    │
│  │  - Async filesystem traversal (pathlib.Path.rglob)   │    │
│  │  - File type detection (path patterns)               │    │
│  │  - Civitai metadata parsing (JSON)                   │    │
│  │  - Preview image URL extraction                      │    │
│  └──────────────┬───────────────────────────────────────┘    │
│                 │                                             │
│  ┌──────────────▼───────────────────────────────────────┐    │
│  │          FileOperations (Utility Layer)              │    │
│  │  - Atomic file movement (shutil.move)                │    │
│  │  - Path validation (prevent traversal)               │    │
│  │  - Directory creation (preserve structure)           │    │
│  │  - Rollback on failure (exception handling)          │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
└───────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                   Shared Infrastructure                       │
│  ┌────────────┐  ┌────────────┐  ┌─────────────────────┐    │
│  │ Config     │  │ AppError   │  │ ProgressManager     │    │
│  │ (Pydantic  │  │ Hierarchy  │  │ (Future: scan       │    │
│  │ Settings)  │  │            │  │ progress tracking)  │    │
│  └────────────┘  └────────────┘  └─────────────────────┘    │
└───────────────────────────────────────────────────────────────┘
```

### Integration with Existing System

**Reused Components** (from Phase 2):
1. **Configuration**: `Config` class extends to include `model_scan_dir`, `active_dir`, `archive_dir`
2. **Error Handling**: `AppError` → `ModelError` → `ModelScanError`, `ModelMoveError`
3. **Logging**: Shared `logging_config.py` with structured logging
4. **FastAPI Application**: Factory pattern from `main.py`, router registration
5. **CORS Configuration**: Same development settings for React frontend

**New Components**:
1. **Registry Module**: `src/sd_model_manager/registry/` (scanners, repositories, models)
2. **Models API**: `src/sd_model_manager/ui/api/models.py` (APIRouter)
3. **Frontend Pages**: `src/sd_model_manager/ui/frontend/src/pages/ModelsPage.tsx`

---

## Technology Alignment

### Backend Stack (Existing Patterns)

| Technology | Version | Usage | Existing Pattern |
|------------|---------|-------|------------------|
| Python | 3.11+ | Async/await runtime | `download/civitai_client.py` |
| FastAPI | 0.100+ | REST API framework | `ui/api/main.py` factory |
| Pydantic | V2 | Data validation | `download/schemas.py` |
| pytest | Latest | Testing framework | `tests/` structure |
| httpx | Latest | Async HTTP (future) | `download/civitai_client.py` |

**Alignment Strategy**:
- Follow async/await patterns from `CivitaiClient`
- Use Pydantic V2 `BaseModel` with `model_config` and field validators
- Implement factory pattern for testability (like `create_app()`)
- Use `BackgroundTasks` for long-running scans (like download)

### Frontend Stack (Existing Patterns)

| Technology | Version | Usage | Existing Pattern |
|------------|---------|-------|------------------|
| React | 18.2+ | UI framework | `ui/frontend/src/` |
| TypeScript | 5.0+ | Type safety | `*.tsx` files |
| Vite | 4.4+ | Build tool | `vite.config.ts` |
| Tailwind CSS | Latest | Styling | Utility classes |

**Alignment Strategy**:
- Reuse React hooks patterns from Download page
- Follow TypeScript interface definitions
- Use same Tailwind configuration and design tokens
- Maintain consistent error handling patterns

---

## Key Design Decisions

### Decision 1: In-Memory Caching vs Database Persistence

**Context**: Need to store scan results for fast retrieval without rescanning on every request.

**Options Considered**:
1. **SQLite Database**: Persistent storage, complex queries, ACID guarantees
2. **In-Memory Dict**: Fast access, simple implementation, lost on restart
3. **Redis Cache**: Distributed, fast, requires additional infrastructure

**Decision**: **In-Memory Dict (Phase 1)** with **SQLite migration path (Future)**

**Rationale**:
- **Phase 1 Simplicity**: In-memory caching with singleton `ModelRepository` pattern (like `ProgressManager`)
- **Performance**: Dict lookup O(1) vs DB query overhead
- **Migration Path**: Pydantic models map directly to SQLAlchemy ORM for future DB persistence
- **Scan Frequency**: Manual scans via UI button, not automatic on every request
- **Acceptable Trade-off**: Scan on startup (first request) is acceptable for Phase 1

**Implementation**:
```python
# Phase 1: In-memory cache
class ModelRepository:
    _instance = None
    _models: Dict[str, ModelInfo] = {}

    @classmethod
    def get_instance(cls) -> "ModelRepository":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

# Future: SQLAlchemy migration
# class ModelRecord(Base):
#     __tablename__ = "models"
#     id = Column(String, primary_key=True)
#     ...
```

**Consequences**:
- ✅ Simple implementation, no DB dependencies
- ✅ Fast read performance (dict lookup)
- ✅ Easy testing (reset state between tests)
- ❌ Scan required on server restart
- ❌ No persistence across restarts
- 🔄 Future: Add SQLite with minimal Pydantic model changes

---

### Decision 2: Background Scanning vs Synchronous Scanning

**Context**: Scanning 1000 models takes 3-5 seconds (I/O bound), blocking API responses is bad UX.

**Options Considered**:
1. **Synchronous Scan**: Simple, blocks API response, timeout risk
2. **Background Task (FastAPI)**: Non-blocking, progress tracking, complexity
3. **Async Scan (no progress)**: Non-blocking, no progress updates

**Decision**: **Background Task with Progress Tracking** (Phase 1: Optional)

**Rationale**:
- **Phase 2 Pattern**: Download feature uses `BackgroundTasks` + `ProgressManager`
- **UX Requirement**: Requirement 7 specifies loading states and "Scanning..." message
- **Performance**: <5s scan time is acceptable for sync on first load
- **Trade-off**: Phase 1 uses sync scan, Phase 2 adds background + WebSocket

**Implementation Strategy**:

**Phase 1 (Minimal)**: Synchronous scan on first request
```python
@router.post("/scan", response_model=ScanResponse)
async def scan_models(config: Config = Depends(get_config)):
    scanner = ModelScanner(config)
    models = await scanner.scan()  # Async I/O, but blocks API response
    return ScanResponse(models=models, scanned_count=len(models))
```

**Phase 2 (Enhanced)**: Background task + progress tracking
```python
@router.post("/scan", response_model=ScanResponse)
async def scan_models(background_tasks: BackgroundTasks, config: Config = Depends(get_config)):
    task_id = str(uuid.uuid4())
    progress_manager.create_task(task_id, "Model Scan", 0)
    background_tasks.add_task(execute_scan, task_id, config)
    return ScanResponse(task_id=task_id, status="started")

# WebSocket endpoint for progress
@router.websocket("/ws/scan/{task_id}")
async def scan_progress_websocket(websocket: WebSocket, task_id: str):
    # Similar to download progress pattern
```

**Consequences**:
- ✅ Phase 1: Simple synchronous implementation
- ✅ Phase 2: Reuses proven download progress pattern
- ✅ Consistent UX across features
- 🔄 Migration path: Add `background_tasks` parameter later

---

### Decision 3: File Movement Strategy (Atomic vs Multi-Step)

**Context**: Moving models between Active/Archive requires safe file operations with rollback capability.

**Options Considered**:
1. **shutil.move (atomic)**: Single OS call, atomic on same filesystem
2. **Copy + Verify + Delete**: Multi-step, safer but slower
3. **Symlinks**: Fast, but ComfyUI may not follow symlinks

**Decision**: **shutil.move with Exception Handling and Validation**

**Rationale**:
- **Atomicity**: `shutil.move()` is atomic on same filesystem (models typically on same drive)
- **Performance**: Single OS operation, fast for large files
- **Rollback**: Exception handling prevents partial moves
- **Validation**: Pre-flight checks (destination exists, disk space, no path traversal)

**Implementation**:
```python
async def move_model_file(
    source_path: Path,
    dest_path: Path,
    validate: bool = True
) -> MoveResult:
    if validate:
        # Pre-flight checks
        if not source_path.exists():
            raise ModelMoveError("Source file not found", code="SOURCE_NOT_FOUND")
        if dest_path.exists():
            raise ModelMoveError("Destination already exists", code="FILE_EXISTS")
        if ".." in str(dest_path):
            raise ModelMoveError("Path traversal detected", code="INVALID_PATH")

    try:
        # Create destination directory (preserve structure)
        dest_path.parent.mkdir(parents=True, exist_ok=True)

        # Atomic move (same filesystem)
        shutil.move(str(source_path), str(dest_path))

        return MoveResult(
            success=True,
            old_path=str(source_path),
            new_path=str(dest_path)
        )
    except Exception as e:
        # Rollback not needed (atomic operation failed)
        raise ModelMoveError(f"Move failed: {str(e)}", code="MOVE_FAILED") from e
```

**Consequences**:
- ✅ Fast single-operation move
- ✅ Atomic on same filesystem
- ✅ Clear error handling with specific codes
- ❌ Requires same filesystem assumption
- 🔄 Future: Add cross-filesystem detection (copy+delete fallback)

---

## System Flows

### Flow 1: Initial Model Scan

```
User                Frontend              API                   Scanner            Repository
  │                    │                   │                      │                    │
  │ Load Models Page   │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │                    │ GET /api/models   │                      │                    │
  │                    ├──────────────────>│                      │                    │
  │                    │                   │ Check cache empty    │                    │
  │                    │                   ├─────────────────────────────────────────>│
  │                    │                   │                      │ Cache empty        │
  │                    │                   │<─────────────────────────────────────────┤
  │                    │                   │ Trigger auto-scan    │                    │
  │                    │                   ├─────────────────────>│                    │
  │                    │                   │                      │ Scan filesystem    │
  │                    │                   │                      │ (async rglob)      │
  │                    │                   │                      │ Parse .civitai.info│
  │                    │                   │                      │ Extract metadata   │
  │                    │                   │ Models list          │                    │
  │                    │                   │<─────────────────────┤                    │
  │                    │                   │ Store in cache       │                    │
  │                    │                   ├─────────────────────────────────────────>│
  │                    │ 200 OK (models[]) │                      │                    │
  │                    │<──────────────────┤                      │                    │
  │ Display grid view  │                   │                      │                    │
  │<───────────────────┤                   │                      │                    │
```

**Performance Targets**:
- Scan 1000 models: <5 seconds
- API response (cached): <200ms
- Grid render: <1 second

**Error Handling**:
- Filesystem access denied → `ModelScanError(code="ACCESS_DENIED")`
- Invalid `.civitai.info` JSON → Skip metadata, use filename
- No models found → Return empty array with warning log

---

### Flow 2: Search and Filter

```
User                Frontend              API                   Repository
  │                    │                   │                      │
  │ Type search query  │                   │                      │
  ├───────────────────>│                   │                      │
  │                    │ Filter locally    │                      │
  │                    │ (no API call)     │                      │
  │ Display filtered   │                   │                      │
  │<───────────────────┤                   │                      │
  │                    │                   │                      │
  │ Select type filter │                   │                      │
  ├───────────────────>│                   │                      │
  │                    │ Apply filter      │                      │
  │                    │ (client-side)     │                      │
  │ Display filtered   │                   │                      │
  │<───────────────────┤                   │                      │
```

**Design Decision**: **Client-Side Filtering**
- **Rationale**: <1000 models fit in browser memory (~10MB JSON)
- **Performance**: <100ms filter update (JS array operations)
- **Simplicity**: No backend pagination complexity
- **Future**: Add server-side filtering for >5000 models

---

### Flow 3: Move Model to Archive

```
User                Frontend              API                   FileOps            Repository
  │                    │                   │                      │                    │
  │ Click "Archive"    │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │                    │ Show confirmation │                      │                    │
  │                    │ dialog            │                      │                    │
  │ Confirm move       │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │                    │ POST /api/models/{id}/move               │                    │
  │                    │ {category: "archive"}                    │                    │
  │                    ├──────────────────>│                      │                    │
  │                    │                   │ Validate request     │                    │
  │                    │                   │ (path traversal)     │                    │
  │                    │                   │ Build dest path      │                    │
  │                    │                   │ Move file            │                    │
  │                    │                   ├─────────────────────>│                    │
  │                    │                   │                      │ shutil.move()      │
  │                    │                   │                      │ Create dirs        │
  │                    │                   │ Success              │                    │
  │                    │                   │<─────────────────────┤                    │
  │                    │                   │ Update cache         │                    │
  │                    │                   ├─────────────────────────────────────────>│
  │                    │ 200 OK (new_path) │                      │                    │
  │                    │<──────────────────┤                      │                    │
  │ Show notification  │                   │                      │                    │
  │ "Press 'r' in      │                   │                      │                    │
  │ ComfyUI to refresh"│                   │                      │                    │
  │<───────────────────┤                   │                      │                    │
```

**Error Scenarios**:
1. **File exists at destination** → 409 Conflict, show error dialog
2. **Source file missing** → 404 Not Found, refresh model list
3. **Permission denied** → 500 Internal Error, show retry button
4. **Disk space full** → 500 Internal Error with specific message

---

### Flow 4: Bulk Move Operation

```
User                Frontend              API                   FileOps            Repository
  │                    │                   │                      │                    │
  │ Select 3 models    │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │ Click "Move        │                   │                      │                    │
  │ Selected"          │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │                    │ Show confirmation │                      │                    │
  │                    │ "Move 3 models?"  │                      │                    │
  │ Confirm            │                   │                      │                    │
  ├───────────────────>│                   │                      │                    │
  │                    │ POST /api/models/bulk-move               │                    │
  │                    │ {ids: [...], category: "archive"}        │                    │
  │                    ├──────────────────>│                      │                    │
  │                    │                   │ For each model:      │                    │
  │                    │                   │   Validate           │                    │
  │                    │                   │   Move file          │                    │
  │                    │                   ├─────────────────────>│                    │
  │                    │                   │                      │ shutil.move()      │
  │                    │                   │<─────────────────────┤                    │
  │                    │                   │   Update cache       │                    │
  │                    │                   ├─────────────────────────────────────────>│
  │                    │                   │ (Continue on error)  │                    │
  │                    │ 200 OK            │                      │                    │
  │                    │ {moved: 2,        │                      │                    │
  │                    │  failed: 1,       │                      │                    │
  │                    │  details: [...]}  │                      │                    │
  │                    │<──────────────────┤                      │                    │
  │ Show summary       │                   │                      │                    │
  │ "2 moved, 1 failed"│                   │                      │                    │
  │<───────────────────┤                   │                      │                    │
```

**Design Decision**: **Continue on Failure**
- **Rationale**: Move remaining models even if one fails
- **UX**: Show detailed results with success/failure breakdown
- **Rollback**: No transaction rollback (each move is atomic)

---

## Components and Interfaces

### Backend Components

#### 1. ModelScanner (Business Logic)

**Location**: `src/sd_model_manager/registry/scanners.py`

**Responsibilities**:
- Scan filesystem for model files (async I/O)
- Parse `.civitai.info` metadata (JSON)
- Extract preview image URLs
- Determine model type from path patterns

**Interface**:
```python
class ModelScanner:
    """Scans filesystem for Stable Diffusion model files."""

    def __init__(self, config: Config):
        self.config = config
        self.base_path = Path(config.model_scan_dir)
        self.supported_extensions = {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}

    async def scan(self) -> list[ModelInfo]:
        """Scan model directory and return list of discovered models."""
        models = []
        async for file_path in self._scan_files():
            model_info = await self._process_file(file_path)
            models.append(model_info)
        return models

    async def _scan_files(self) -> AsyncIterator[Path]:
        """Async generator for filesystem traversal (single-pass)."""
        # Single traversal checking all extensions (performance optimization)
        # Avoids 5 separate rglob calls
        def scan_sync():
            for file_path in self.base_path.rglob("*"):
                # Case-insensitive extension check for cross-platform compatibility
                if file_path.is_file() and file_path.suffix.lower() in self.supported_extensions:
                    yield file_path

        # Run blocking I/O in thread pool
        loop = asyncio.get_event_loop()
        files = await loop.run_in_executor(None, list, scan_sync())
        for file_path in files:
            yield file_path

    async def _process_file(self, file_path: Path) -> ModelInfo:
        """Process single model file and extract metadata."""
        # Read .civitai.info if exists
        metadata = await self._read_civitai_metadata(file_path)

        # Determine model type from path
        model_type = self._detect_model_type(file_path)

        # Extract file metadata
        stats = file_path.stat()

        return ModelInfo(
            id=self._generate_id(file_path),
            filename=file_path.name,
            file_path=str(file_path),
            file_size=stats.st_size,
            model_type=model_type,
            created_at=datetime.fromtimestamp(stats.st_ctime),
            modified_at=datetime.fromtimestamp(stats.st_mtime),
            civitai_metadata=metadata,
            preview_url=metadata.preview_url if metadata else None,
            category=self._detect_category(file_path)
        )

    def _detect_model_type(self, file_path: Path) -> ModelType:
        """Detect model type based on directory path patterns (cross-platform)."""
        # Use Path.parts for Windows/Unix compatibility (no string matching)
        parts_lower = [part.lower() for part in file_path.parts]

        # Check for LoRA directories
        if any(part in {"lora", "loras"} for part in parts_lower):
            return ModelType.LORA
        # Check for Checkpoint directories
        elif any(part in {"checkpoints", "stable-diffusion"} for part in parts_lower):
            return ModelType.CHECKPOINT
        # Check for VAE directories
        elif "vae" in parts_lower:
            return ModelType.VAE
        # Check for Embeddings directories
        elif "embeddings" in parts_lower:
            return ModelType.EMBEDDING
        else:
            return ModelType.UNKNOWN

    def _detect_category(self, file_path: Path) -> Category:
        """Detect category (Active/Archive) from file path (cross-platform)."""
        # Use Path.is_relative_to() for config-based detection (Windows compatible)
        try:
            active_path = Path(self.config.active_dir).resolve()
            archive_path = Path(self.config.archive_dir).resolve()
            resolved_file = file_path.resolve()

            if resolved_file.is_relative_to(archive_path):
                return Category.ARCHIVE
            elif resolved_file.is_relative_to(active_path):
                return Category.ACTIVE
            else:
                return Category.ACTIVE  # Default
        except (ValueError, AttributeError):
            # Fallback if config paths not set or is_relative_to fails
            return Category.ACTIVE

    async def _read_civitai_metadata(self, file_path: Path) -> Optional[CivitaiMetadata]:
        """Read and parse .civitai.info file if exists."""
        info_file = file_path.with_suffix(file_path.suffix + ".civitai.info")
        if not info_file.exists():
            return None

        try:
            async with aiofiles.open(info_file, "r", encoding="utf-8") as f:
                content = await f.read()
                data = json.loads(content)
                return CivitaiMetadata.model_validate(data)
        except (json.JSONDecodeError, ValidationError) as e:
            logger.warning(f"Failed to parse {info_file}: {e}")
            return None

    def _generate_id(self, file_path: Path) -> str:
        """Generate stable ID for model (hash of relative path)."""
        relative_path = file_path.relative_to(self.base_path)
        return hashlib.sha256(str(relative_path).encode()).hexdigest()[:16]
```

**Testing Strategy**:
- Unit tests with temp directory and mock files
- Test .civitai.info parsing (valid, invalid, missing)
- Test model type detection (all path patterns)
- Test async file iteration performance

---

#### 2. ModelRepository (Service Layer)

**Location**: `src/sd_model_manager/registry/repositories.py`

**Responsibilities**:
- In-memory cache management (singleton pattern)
- CRUD operations on model collection
- Cache invalidation on scan/move operations

**Interface**:
```python
class ModelRepository:
    """Singleton repository for model data with in-memory caching."""

    _instance: Optional["ModelRepository"] = None
    _models: Dict[str, ModelInfo] = {}
    _last_scan: Optional[datetime] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    def get_instance(cls) -> "ModelRepository":
        """Get singleton instance."""
        return cls()

    def get_all(self) -> list[ModelInfo]:
        """Get all models from cache."""
        return list(self._models.values())

    def get_by_id(self, model_id: str) -> Optional[ModelInfo]:
        """Get model by ID."""
        return self._models.get(model_id)

    def update_cache(self, models: list[ModelInfo]) -> None:
        """Update cache with new scan results."""
        self._models = {model.id: model for model in models}
        self._last_scan = datetime.now()

    def update_model(self, model_id: str, updates: dict[str, Any]) -> None:
        """Update specific model fields (e.g., after file move)."""
        if model_id in self._models:
            model = self._models[model_id]
            updated_model = model.model_copy(update=updates)
            self._models[model_id] = updated_model

    def is_cache_empty(self) -> bool:
        """Check if cache needs initial scan."""
        return len(self._models) == 0

    def clear_cache(self) -> None:
        """Clear cache (for testing)."""
        self._models.clear()
        self._last_scan = None
```

**Pattern Alignment**:
- Singleton pattern (like `ProgressManager` in Phase 2)
- In-memory dict for fast lookups
- Future migration: Replace dict with SQLAlchemy session

---

#### 3. ModelsAPI (FastAPI Router)

**Location**: `src/sd_model_manager/ui/api/models.py`

**Responsibilities**:
- REST endpoint implementation
- Request validation (Pydantic)
- Response formatting (success/error)
- Integration with scanner and repository

**Interface**:
```python
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from ..lib.errors import AppError, ModelScanError, ModelMoveError

router = APIRouter(prefix="/api/models", tags=["models"])

def get_repository() -> ModelRepository:
    """Dependency injection for repository."""
    return ModelRepository.get_instance()

def get_scanner(config: Config = Depends(get_config)) -> ModelScanner:
    """Dependency injection for scanner."""
    return ModelScanner(config)

@router.get("", response_model=ModelsListResponse)
async def list_models(
    repository: ModelRepository = Depends(get_repository),
    scanner: ModelScanner = Depends(get_scanner)
) -> ModelsListResponse:
    """
    Get all models from cache. Trigger initial scan if cache is empty.

    Returns:
        ModelsListResponse: List of all models with metadata
    """
    if repository.is_cache_empty():
        logger.info("Cache empty, triggering initial scan")
        models = await scanner.scan()
        repository.update_cache(models)
    else:
        models = repository.get_all()

    return ModelsListResponse(
        success=True,
        models=models,
        total_count=len(models),
        scanned_at=repository._last_scan
    )

@router.post("/scan", response_model=ScanResponse)
async def scan_models(
    repository: ModelRepository = Depends(get_repository),
    scanner: ModelScanner = Depends(get_scanner)
) -> ScanResponse:
    """
    Trigger manual filesystem scan and update cache.

    Returns:
        ScanResponse: Scan results with model count
    """
    try:
        models = await scanner.scan()
        repository.update_cache(models)

        return ScanResponse(
            success=True,
            models=models,
            scanned_count=len(models),
            message=f"Found {len(models)} models"
        )
    except Exception as e:
        logger.error(f"Scan failed: {e}", exc_info=True)
        raise ModelScanError(
            message=f"Filesystem scan failed: {str(e)}",
            code="SCAN_FAILED"
        ) from e

@router.get("/{model_id}", response_model=ModelDetailResponse)
async def get_model(
    model_id: str,
    repository: ModelRepository = Depends(get_repository)
) -> ModelDetailResponse:
    """
    Get detailed information for a specific model.

    Args:
        model_id: Unique model identifier

    Returns:
        ModelDetailResponse: Detailed model metadata

    Raises:
        HTTPException: 404 if model not found
    """
    model = repository.get_by_id(model_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Model not found", "code": "MODEL_NOT_FOUND"}
        )

    return ModelDetailResponse(success=True, model=model)

@router.post("/{model_id}/move", response_model=MoveResponse)
async def move_model(
    model_id: str,
    request: MoveRequest,
    config: Config = Depends(get_config),
    repository: ModelRepository = Depends(get_repository)
) -> MoveResponse:
    """
    Move model file to different category (Active/Archive).

    Args:
        model_id: Model to move
        request: Target category (active/archive)

    Returns:
        MoveResponse: Move result with new path

    Raises:
        HTTPException: 404/409/500 on various failures
    """
    # Get model from cache
    model = repository.get_by_id(model_id)
    if model is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Model not found", "code": "MODEL_NOT_FOUND"}
        )

    # Build destination path
    source_path = Path(model.file_path)
    dest_path = _build_destination_path(source_path, request.category, config)

    # Validate destination
    if dest_path.exists():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": "File already exists in destination",
                "code": "FILE_EXISTS",
                "existing_path": str(dest_path)
            }
        )

    # Perform move operation
    try:
        result = await _move_file(source_path, dest_path)

        # Update cache
        repository.update_model(model_id, {
            "file_path": result.new_path,
            "category": request.category
        })

        return MoveResponse(
            success=True,
            moved_count=1,
            new_path=result.new_path,
            old_path=result.old_path,
            message="Model moved successfully. Press 'r' in ComfyUI to refresh the model list"
        )
    except ModelMoveError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"error": str(e), "code": e.code}
        ) from e

@router.post("/bulk-move", response_model=BulkMoveResponse)
async def bulk_move_models(
    request: BulkMoveRequest,
    config: Config = Depends(get_config),
    repository: ModelRepository = Depends(get_repository)
) -> BulkMoveResponse:
    """
    Move multiple models to different category.

    Args:
        request: Model IDs and target category

    Returns:
        BulkMoveResponse: Results for each model (success/failed)
    """
    results = []
    moved_count = 0
    failed_count = 0

    for model_id in request.model_ids:
        try:
            model = repository.get_by_id(model_id)
            if model is None:
                results.append({
                    "id": model_id,
                    "status": "failed",
                    "error": "Model not found"
                })
                failed_count += 1
                continue

            source_path = Path(model.file_path)
            dest_path = _build_destination_path(source_path, request.category, config)

            if dest_path.exists():
                results.append({
                    "id": model_id,
                    "status": "failed",
                    "error": "File already exists in destination"
                })
                failed_count += 1
                continue

            result = await _move_file(source_path, dest_path)
            repository.update_model(model_id, {
                "file_path": result.new_path,
                "category": request.category
            })

            results.append({
                "id": model_id,
                "status": "success",
                "new_path": result.new_path
            })
            moved_count += 1

        except Exception as e:
            logger.error(f"Failed to move model {model_id}: {e}")
            results.append({
                "id": model_id,
                "status": "failed",
                "error": str(e)
            })
            failed_count += 1

    return BulkMoveResponse(
        success=moved_count > 0,
        moved_count=moved_count,
        failed_count=failed_count,
        details=results,
        message=f"Moved {moved_count} of {len(request.model_ids)} models successfully. Press 'r' in ComfyUI to refresh the model list"
    )

def _build_destination_path(source: Path, category: Category, config: Config) -> Path:
    """Build destination path preserving model type subdirectory."""
    # Detect model type subdirectory (loras/, checkpoints/, vae/, embeddings/)
    parts = source.parts
    type_dir = None
    for part in reversed(parts):
        if part.lower() in {"loras", "checkpoints", "vae", "embeddings"}:
            type_dir = part.lower()
            break

    # Build destination path
    if category == Category.ACTIVE:
        base_dir = Path(config.active_dir)
    else:
        base_dir = Path(config.archive_dir)

    if type_dir:
        dest_path = base_dir / type_dir / source.name
    else:
        dest_path = base_dir / source.name

    return dest_path

async def _move_file(source: Path, dest: Path) -> MoveResult:
    """Move file with validation and error handling (Requirement 12.9)."""
    # Validate paths
    if ".." in str(dest):
        raise ModelMoveError("Path traversal detected", code="INVALID_PATH")

    if not source.exists():
        raise ModelMoveError("Source file not found", code="SOURCE_NOT_FOUND")

    # Check disk space (Requirement 12.9)
    file_size = source.stat().st_size

    # Find first existing parent directory for disk space check
    check_path = dest.parent
    while not check_path.exists():
        check_path = check_path.parent
        if check_path == check_path.parent:  # Reached filesystem root
            check_path = Path("/")  # Use root as fallback
            break

    disk_usage = shutil.disk_usage(check_path)

    if disk_usage.free < file_size:
        raise ModelMoveError(
            f"Insufficient disk space. Required: {file_size} bytes, Available: {disk_usage.free} bytes",
            code="NO_SPACE"
        )

    try:
        # Create destination directory
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Atomic move (same filesystem)
        await asyncio.to_thread(shutil.move, str(source), str(dest))

        return MoveResult(
            success=True,
            old_path=str(source),
            new_path=str(dest)
        )
    except Exception as e:
        raise ModelMoveError(f"Move operation failed: {str(e)}", code="MOVE_FAILED") from e
```

**Pattern Alignment**:
- Dependency injection (like `download.py`)
- Structured error responses (like Phase 2 error handling)
- Pydantic request/response models (V2 syntax)

---

## UI Design

### Design Inspiration & Visual Direction
- Primary inspiration comes from ComfyUI-LoRA-Manager (layout density, card styling) and the grid catalog UI used in `reference_git_clones/civitai-tools/civitai-downloader-v2`.  
- We reuse their high-contrast card layout, soft shadows, and badge-based categorisation while conforming to the existing Tailwind design tokens in this repo.  
- Component naming and spacing follow the Phase 2 download UI to keep typography and elevations consistent across features.

### Page Layout (Requirement 5, 7, 8, 11, 13)
```
┌─────────────────────────────────────────────────────────────┐
│ Top Bar                                                     │
│ ├─ Page Title ("Model Viewer")                              │
│ ├─ Manual Scan Button ("Scan for Models")                   │
│ └─ Last scanned timestamp / status pill                     │
│                                                             │
│ Filter Row                                                  │
│ ├─ SearchBar (full width on mobile, inline on desktop)      │
│ └─ TypeFilter segmented control                             │
│                                                             │
│ BulkActionBar (conditional)                                 │
│ ├─ Selection count                                          │
│ ├─ Move to Active button                                    │
│ ├─ Move to Archive button                                   │
│ └─ Deselect all link                                         │
│                                                             │
│ Content Area                                                │
│ ├─ Loading: skeleton grid + status banner                   │
│ ├─ Error: full-width alert with retry button                │
│ ├─ Empty: illustration + "No models found" guidance         │
│ └─ ModelGrid (responsive Masonry layout)                    │
└─────────────────────────────────────────────────────────────┘

Modal Layer:
- `ModelDetailModal` slides in from the right (desktop) / bottom sheet (mobile) when a card is clicked.
- `BulkMoveSummaryDialog` overlays the grid after a bulk move finishes to show per-model results.
```

### Component Interaction Overview
| Component | Key Interactions | Requirement Coverage |
|-----------|-----------------|----------------------|
| `SearchBar` | Debounced text input, clear button, keyboard focus states | Req. 6 |
| `TypeFilter` | Segmented buttons (`All`, `LoRA`, `Checkpoint`, `VAE`, `Embedding`, `Unknown`) with aria-pressed states | Req. 6 |
| `ManualScanButton` | Disabled + spinner while `/api/models/scan` is running; tooltip with last scan time | Req. 7, 8 |
| `BulkActionBar` | Shown when `selectedIds.size > 0`; move buttons trigger confirmation dialog with source/destination paths | Req. 11, 13 |
| `ModelGrid` | CSS grid: 4 columns ≥1280px, 3 columns 768–1279px, 2 columns <768px; falls back to one column ≤480px | Req. 5 |
| `ModelCard` | Checkbox selection, preview image, badges for type/category, move button with destination preview path; click area opens detail modal | Req. 5, 6, 11 |
| `ModelDetailModal` | Full metadata (tags, trigger words, file stats, absolute paths), CTA buttons for move/delete (future), keyboard-accessible close | Req. 5.7 |
| `BulkMoveProgressToast` | Appears bottom-right showing “Moving X of Y” with live count; converts into summary dialog once complete | Req. 13 |

### State-Driven UI Behaviour
- **Loading (initial or manual scan)**: Display skeleton `ModelCardSkeleton` grid and top-level banner “Scanning models…”, disable search/filter/bulk actions.  
- **Error**: Show `ErrorDisplay` with retry callback. For filesystem errors include error code (e.g., `ACCESS_DENIED`).  
- **Empty results**: If total models=0 use setup guidance card (directories + documentation link). If filtered count=0 show “No models matched your filters” with reset controls.  
- **Selection flow**: Checkbox toggles call `toggleSelection(id)`; selection state synced with BulkActionBar; ESC clears selection.  
- **Bulk move**: Confirmation modal displays current path → target path preview. During move, show progress toast; after completion, summary dialog lists successes/failures using `BulkMoveResponse.details`.  
- **Detail modal**: Triggered via card click or keyboard Enter. Modal traps focus, supports arrow key navigation between models, and renders civitai tags as pill chips.

### Accessibility & Cross-Platform Notes
- Tailwind classes ensure sufficient contrast; badges and buttons meet WCAG AA.  
- All interactive elements expose ARIA roles (`role="dialog"` for modals, `aria-live="polite"` for progress toast).  
- Use CSS logical properties where possible so macOS and Windows renderings stay consistent (font stacks include `Inter`, `Segoe UI`, `system-ui`).  
- Avoid OS-specific scrollbars by wrapping grids in `overflow-auto` containers with padding.  
- Confirmation dialogs use a custom modal instead of `window.confirm` to guarantee consistent look on macOS/Windows and allow path details.

### Wireframe References
- `/reference_git_clones/civitiai-tools/civitai-downloader-v2/docs/ui-wireframes.png` (local copy) is referenced for card composition.
- Annotated screenshots from ComfyUI-LoRA-Manager (saved in `assets/reference/ui/`) are linked in Confluence to justify spacing and iconography choices.

### UI Component Library Integration

**Modern Component Library Adoption**: Radix UI + Framer Motion for professional-grade accessibility and animations.

#### Rationale

1. **Accessibility First**: Radix UI provides WAI-ARIA compliant headless components with built-in keyboard navigation, focus management, and screen reader support.
2. **Animation Quality**: Framer Motion delivers 60fps GPU-accelerated animations with declarative API.
3. **Development Efficiency**: Reduces implementation time by 40-60% for complex UI patterns (modals, dialogs, dropdowns).
4. **Maintenance**: Industry-standard libraries with active maintenance and extensive documentation.
5. **Phase 2 Consistency**: Aligns with existing React 18+ and TypeScript ecosystem.

#### Dependencies

```json
{
  "dependencies": {
    "@radix-ui/react-dialog": "^1.0.5",
    "@radix-ui/react-alert-dialog": "^1.0.5",
    "@radix-ui/react-select": "^2.0.0",
    "framer-motion": "^11.0.0"
  }
}
```

**Bundle Impact**: +50KB gzipped (Dialog + AlertDialog + Motion), tree-shakeable.

#### Component Mapping

| Component | Library | Features | Requirement Coverage |
|-----------|---------|----------|---------------------|
| `ModelDetailModal` | Radix Dialog + Framer Motion | Focus trap, ESC handling, backdrop blur, smooth animations | Req. 5.7, 5.8 |
| Confirmation Dialogs | Radix AlertDialog | Path preview, accessible buttons, keyboard navigation | Req. 11.3 |
| Type Filter (Optional) | Radix Select | Searchable dropdown for large tag sets (future enhancement) | Req. 6.5 |

#### Animation Specifications

**Modal Entry/Exit Animation**:
```typescript
// Entry animation
initial: {
  opacity: 0,
  scale: 0.8,
  filter: "blur(4px)",
  transform: "perspective(500px) rotateY(30deg)"
}
animate: {
  opacity: 1,
  scale: 1,
  filter: "blur(0px)",
  transform: "perspective(500px) rotateY(0deg)"
}
transition: { type: "spring", stiffness: 150, damping: 25 }

// Backdrop animation
backdrop: {
  initial: { opacity: 0, filter: "blur(4px)" },
  animate: { opacity: 1, filter: "blur(0px)" },
  transition: { duration: 0.2, ease: "easeInOut" }
}
```

**Tag/Badge Staggered Animation**:
```typescript
// Trigger words and tags animate with staggered delay
{trigger_words.map((word, idx) => (
  <motion.span
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay: 0.3 + idx * 0.05 }}
  >
    {word}
  </motion.span>
))}
```

#### Performance Considerations

1. **Layout Shift Prevention**: Use `layoutId` for smooth transitions without cumulative layout shift (CLS).
2. **GPU Acceleration**: `transform` and `opacity` animations leverage GPU for 60fps performance.
3. **Lazy Loading**: AnimatePresence ensures animations only run when modal is open.
4. **Tree Shaking**: Import only required Radix primitives to minimize bundle size.

#### Implementation Notes

- **Backward Compatibility**: Basic React implementation remains valid fallback if Radix/Motion are unavailable.
- **Testing**: Radix UI components include built-in ARIA attributes testable with React Testing Library.
- **Dark Mode**: Radix headless components inherit Tailwind dark mode classes seamlessly.

### UI Reference Assets Setup

**Directory Structure**:
```
assets/
└── reference/
    └── ui/
        ├── comfyui-lora-manager-grid.png      # Grid layout reference
        ├── comfyui-lora-manager-card.png      # Card component detail
        ├── civitai-downloader-filters.png     # Filter bar layout
        ├── 21st-dev-dialog-animation.gif      # Modal animation reference
        └── radix-ui-accessibility.png         # ARIA implementation reference
```

**Asset Acquisition**:
1. **ComfyUI-LoRA-Manager Screenshots**: Capture from running instance or reference_git_clones.
2. **21st.dev Components**: Browser screenshots from component demos (Dialog, Item, Select).
3. **Radix UI Documentation**: ARIA patterns and accessibility checklist.

**Asset Purpose**:
- **Grid Layout**: Justify 4-3-2-1 column responsive breakpoints.
- **Card Composition**: Image aspect ratio, badge positioning, hover states.
- **Filter Design**: Search input styling, segmented control spacing.
- **Animation Reference**: Motion curves, timing functions, stagger delays.

**Note**: Assets are for design reference only; implementations use 21st.dev component code and Radix UI primitives, not screenshots.

---

### Frontend Components

#### 1. ModelsPage (Container)

**Location**: `src/sd_model_manager/ui/frontend/src/pages/ModelsPage.tsx`

**Responsibilities**:
- Fetch models from API
- Manage search/filter state
- Coordinate child components

**Interface**:
```typescript
interface BulkMoveProgress {
  current: number;
  total: number;
  result?: BulkMoveResponse;
}

interface ConfirmDialogState {
  open: boolean;
  title: string;
  message: string;
  currentPath?: string;
  destinationPath?: string;
  onConfirm: () => void;
}

interface ModelsPageState {
  models: ModelInfo[];
  filteredModels: ModelInfo[];
  searchQuery: string;
  selectedType: ModelType | "all";
  loading: boolean;
  isScanning: boolean;  // Manual scan in progress (Requirement 8)
  bulkMoveProgress: BulkMoveProgress | null;  // Bulk move progress (Requirement 13.5, 13.6)
  selectedModelId: string | null;  // Model ID for detail modal (Requirement 5.7)
  confirmDialog: ConfirmDialogState | null;  // Radix AlertDialog state (Requirement 11.3)
  error: string | null;
  selectedIds: Set<string>;
}

export const ModelsPage: React.FC = () => {
  const [state, setState] = useState<ModelsPageState>({
    models: [],
    filteredModels: [],
    searchQuery: "",
    selectedType: "all",
    loading: true,
    isScanning: false,
    bulkMoveProgress: null,
    selectedModelId: null,
    confirmDialog: null,
    error: null,
    selectedIds: new Set()
  });

  // Client-side filter function (memoized for performance)
  const applyFilters = useMemo(() => {
    return (models: ModelInfo[], query: string, type: ModelType | "all") => {
      return models.filter(model => {
        const lowerQuery = query.toLowerCase();
        // Search in filename, Civitai name, and tags (Requirement 6.3, 6.4)
        const matchesSearch =
          model.filename.toLowerCase().includes(lowerQuery) ||
          model.civitai_metadata?.name?.toLowerCase()?.includes(lowerQuery) ||
          model.civitai_metadata?.tags?.some(tag => tag.toLowerCase().includes(lowerQuery)) ||
          false;
        const matchesType = type === "all" || model.model_type === type;
        return matchesSearch && matchesType;
      });
    };
  }, []);

  // Fetch models on mount
  useEffect(() => {
    fetchModels();
  }, []);

  // Apply filters when search/type changes
  useEffect(() => {
    const filtered = applyFilters(state.models, state.searchQuery, state.selectedType);
    setState(prev => ({ ...prev, filteredModels: filtered }));
  }, [state.models, state.searchQuery, state.selectedType, applyFilters]);

  const fetchModels = async () => {
    try {
      const response = await fetch("/api/models");
      const data: ModelsListResponse = await response.json();
      setState(prev => ({
        ...prev,
        models: data.models,
        filteredModels: data.models,
        loading: false
      }));
    } catch (err) {
      setState(prev => ({
        ...prev,
        error: err.message,
        loading: false
      }));
    }
  };

  const handleSearch = (query: string) => {
    setState(prev => ({ ...prev, searchQuery: query }));
  };

  const handleTypeFilter = (type: ModelType | "all") => {
    setState(prev => ({ ...prev, selectedType: type }));
  };

  const handleMove = async (modelId: string, category: Category) => {
    // Get model info for confirmation dialog (Requirement 11.3)
    const model = state.models.find(m => m.id === modelId);
    if (!model) return;

    const targetCategory = category === Category.ACTIVE ? "Active" : "Archive";
    const destinationPath = `${category}/${model.model_type}/${model.filename}`;

    // Show Radix AlertDialog with path information (Requirement 11.3)
    setState(prev => ({
      ...prev,
      confirmDialog: {
        open: true,
        title: `Move to ${targetCategory}?`,
        message: "This will move the model file to a different location.",
        currentPath: model.file_path,
        destinationPath: destinationPath,
        onConfirm: async () => {
          setState(prev => ({ ...prev, confirmDialog: null }));
          await executeMove(modelId, category);
        }
      }
    }));
  };

  const executeMove = async (modelId: string, category: Category) => {
    try {
      const response = await fetch(`/api/models/${modelId}/move`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ category })
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || "Move failed");
      }

      const result: MoveResponse = await response.json();
      showNotification(result.message);
      await fetchModels(); // Refresh list
    } catch (err) {
      showError(err.message);
    }
  };

  const handleBulkMove = async (category: Category) => {
    const ids = Array.from(state.selectedIds);
    if (ids.length === 0) return;

    const targetCategory = category === Category.ACTIVE ? "Active" : "Archive";

    // Show Radix AlertDialog for bulk move confirmation
    setState(prev => ({
      ...prev,
      confirmDialog: {
        open: true,
        title: `Move ${ids.length} models to ${targetCategory}?`,
        message: `This will move ${ids.length} model files. Progress will be shown during the operation.`,
        onConfirm: async () => {
          setState(prev => ({ ...prev, confirmDialog: null }));
          await executeBulkMove(ids, category);
        }
      }
    }));
  };

  const executeBulkMove = async (ids: string[], category: Category) => {
    // Show initial progress (Requirement 13.5)
    setState(prev => ({
      ...prev,
      bulkMoveProgress: { current: 0, total: ids.length }
    }));

    // Simulate progress with optimistic UI update (Requirement 13.5: "Moving X of Y")
    const progressInterval = setInterval(() => {
      setState(prev => {
        if (!prev.bulkMoveProgress || prev.bulkMoveProgress.result) {
          return prev;
        }
        const newCurrent = Math.min(
          prev.bulkMoveProgress.current + 1,
          prev.bulkMoveProgress.total - 1  // Keep at N-1 until API responds
        );
        return {
          ...prev,
          bulkMoveProgress: { ...prev.bulkMoveProgress, current: newCurrent }
        };
      });
    }, 100);  // Update every 100ms for smooth visual feedback

    try {
      // Use bulk-move endpoint (Requirement 13.4)
      const response = await fetch("/api/models/bulk-move", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ model_ids: ids, category })
      });

      clearInterval(progressInterval);

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Bulk move failed");
      }

      const result: BulkMoveResponse = await response.json();

      // Show result dialog (Requirement 13.6)
      setState(prev => ({
        ...prev,
        bulkMoveProgress: { current: ids.length, total: ids.length, result },
        selectedIds: new Set()
      }));

      await fetchModels();
    } catch (err) {
      clearInterval(progressInterval);
      setState(prev => ({ ...prev, bulkMoveProgress: null }));
      showError(err instanceof Error ? err.message : "Unknown error");
    }
  };

  const closeBulkMoveResult = () => {
    setState(prev => ({ ...prev, bulkMoveProgress: null }));
  };

  const handleManualScan = async () => {
    // Requirement 8: Manual scan trigger
    setState(prev => ({ ...prev, isScanning: true }));

    try {
      const response = await fetch("/api/models/scan", {
        method: "POST"
      });

      if (!response.ok) {
        throw new Error("Scan failed");
      }

      const result: ScanResponse = await response.json();
      setState(prev => ({
        ...prev,
        models: result.models,
        filteredModels: result.models,
        isScanning: false
      }));
      showNotification(`Found ${result.scanned_count} models`);
    } catch (err) {
      setState(prev => ({ ...prev, isScanning: false }));
      showError(err.message);
    }
  };

  const toggleSelection = (id: string) => {
    setState(prev => {
      const newSelected = new Set(prev.selectedIds);
      if (newSelected.has(id)) {
        newSelected.delete(id);
      } else {
        newSelected.add(id);
      }
      return { ...prev, selectedIds: newSelected };
    });
  };

  const handleShowDetail = (modelId: string) => {
    // Requirement 5.7: Show detail modal on card click
    setState(prev => ({ ...prev, selectedModelId: modelId }));
  };

  const handleCloseDetail = () => {
    setState(prev => ({ ...prev, selectedModelId: null }));
  };

  if (state.loading) return <LoadingSpinner message="Scanning models..." />;
  if (state.error) return <ErrorDisplay error={state.error} onRetry={fetchModels} />;

  return (
    <div className="models-page">
      <div className="toolbar">
        <SearchBar
          query={state.searchQuery}
          onSearch={handleSearch}
        />
        <TypeFilter
          selected={state.selectedType}
          onChange={handleTypeFilter}
        />
        {/* Requirement 8: Manual scan button */}
        <button
          onClick={handleManualScan}
          disabled={state.isScanning}
          className="btn-scan"
        >
          {state.isScanning ? "Scanning..." : "Scan for Models"}
        </button>
      </div>

      {/* Requirement 13.5: Bulk move progress banner */}
      {state.bulkMoveProgress && !state.bulkMoveProgress.result && (
        <div className="bulk-move-progress">
          Moving {state.bulkMoveProgress.current} of {state.bulkMoveProgress.total} models...
        </div>
      )}

      {/* Requirement 13.6: Bulk move result dialog */}
      {state.bulkMoveProgress?.result && (
        <div className="bulk-move-result-dialog">
          <h3>Bulk Move Results</h3>
          <p>{state.bulkMoveProgress.result.message}</p>
          <div className="result-summary">
            <span>✅ Moved: {state.bulkMoveProgress.result.moved_count}</span>
            <span>❌ Failed: {state.bulkMoveProgress.result.failed_count}</span>
          </div>
          <div className="result-details">
            {state.bulkMoveProgress.result.details.map((detail, idx) => (
              <div key={idx} className={`result-item ${detail.status}`}>
                {detail.status === "success" ? "✅" : "❌"} {detail.id}
                {detail.error && <span className="error">{detail.error}</span>}
              </div>
            ))}
          </div>
          <button onClick={closeBulkMoveResult}>Close</button>
        </div>
      )}

      {/* Requirement 5.7: Model detail modal */}
      {state.selectedModelId && (
        <ModelDetailModal
          model={state.models.find(m => m.id === state.selectedModelId)!}
          open={Boolean(state.selectedModelId)}
          onClose={handleCloseDetail}
        />
      )}

      {/* Requirement 11.3: Radix AlertDialog for move confirmation */}
      {state.confirmDialog && (
        <AlertDialog.Root
          open={state.confirmDialog.open}
          onOpenChange={(open) => {
            if (!open) setState(prev => ({ ...prev, confirmDialog: null }));
          }}
        >
          <AlertDialog.Portal>
            <AlertDialog.Overlay className="fixed inset-0 bg-black/50 z-50" />
            <AlertDialog.Content className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                                            w-full max-w-md bg-white dark:bg-gray-900 rounded-lg
                                            shadow-xl p-6 z-50 focus:outline-none">
              <AlertDialog.Title className="text-xl font-bold mb-2">
                {state.confirmDialog.title}
              </AlertDialog.Title>
              <AlertDialog.Description className="text-gray-600 dark:text-gray-400 mb-4">
                {state.confirmDialog.message}
              </AlertDialog.Description>

              {/* Show path information if available (Requirement 11.3) */}
              {state.confirmDialog.currentPath && state.confirmDialog.destinationPath && (
                <div className="mb-4 p-3 bg-gray-100 dark:bg-gray-800 rounded text-sm">
                  <div className="mb-2">
                    <span className="font-semibold">Current:</span>
                    <div className="text-gray-700 dark:text-gray-300 font-mono text-xs mt-1">
                      {state.confirmDialog.currentPath}
                    </div>
                  </div>
                  <div>
                    <span className="font-semibold">Destination:</span>
                    <div className="text-gray-700 dark:text-gray-300 font-mono text-xs mt-1">
                      {state.confirmDialog.destinationPath}
                    </div>
                  </div>
                </div>
              )}

              <div className="flex gap-3 justify-end">
                <AlertDialog.Cancel asChild>
                  <button className="px-4 py-2 rounded bg-gray-200 dark:bg-gray-700
                                     hover:bg-gray-300 dark:hover:bg-gray-600
                                     transition-colors">
                    Cancel
                  </button>
                </AlertDialog.Cancel>
                <AlertDialog.Action asChild>
                  <button
                    className="px-4 py-2 rounded bg-blue-600 text-white
                               hover:bg-blue-700 transition-colors"
                    onClick={state.confirmDialog.onConfirm}
                  >
                    Confirm
                  </button>
                </AlertDialog.Action>
              </div>
            </AlertDialog.Content>
          </AlertDialog.Portal>
        </AlertDialog.Root>
      )}

      {state.selectedIds.size > 0 && (
        <BulkActionBar
          count={state.selectedIds.size}
          onMoveToActive={() => handleBulkMove(Category.ACTIVE)}
          onMoveToArchive={() => handleBulkMove(Category.ARCHIVE)}
        />
      )}
      <ModelGrid
        models={state.filteredModels}
        selectedIds={state.selectedIds}
        onSelect={(id) => toggleSelection(id)}
        onShowDetail={(id) => handleShowDetail(id)}
        onMove={handleMove}
      />
    </div>
  );
};
```

---

#### 2. ModelCard (Presentational)

**Location**: `src/sd_model_manager/ui/frontend/src/components/ModelCard.tsx`

**Responsibilities**:
- Display model thumbnail/placeholder
- Show model metadata (name, type, size)
- Provide move button and selection checkbox

**Interface**:
```typescript
interface ModelCardProps {
  model: ModelInfo;
  selected: boolean;
  onSelect: (id: string) => void;
  onMove: (id: string, category: Category) => void;
}

export const ModelCard: React.FC<ModelCardProps> = ({
  model,
  selected,
  onSelect,
  onMove
}) => {
  const targetCategory = model.category === Category.ACTIVE
    ? Category.ARCHIVE
    : Category.ACTIVE;

  const moveButtonText = model.category === Category.ACTIVE
    ? "Move to Archive"
    : "Move to Active";

  return (
    <div className={`model-card ${selected ? "selected" : ""}`}>
      <input
        type="checkbox"
        checked={selected}
        onChange={() => onSelect(model.id)}
        className="model-checkbox"
      />

      <div className="model-thumbnail">
        {model.preview_url ? (
          <img
            src={model.preview_url}
            alt={model.filename}
            onError={(e) => {
              e.currentTarget.src = getPlaceholderImage(model.model_type);
            }}
          />
        ) : (
          <img src={getPlaceholderImage(model.model_type)} alt="placeholder" />
        )}
      </div>

      <div className="model-info">
        <h3 className="model-name">{model.civitai_metadata?.name || model.filename}</h3>
        <div className="model-badges">
          <span className={`badge badge-${model.model_type.toLowerCase()}`}>
            {model.model_type}
          </span>
          <span className={`badge badge-${model.category.toLowerCase()}`}>
            {model.category}
          </span>
        </div>
        <p className="model-size">{formatFileSize(model.file_size)}</p>
      </div>

      <div className="model-actions">
        <button
          onClick={() => onMove(model.id, targetCategory)}
          className="btn-move"
        >
          {moveButtonText}
        </button>
      </div>
    </div>
  );
};

function getPlaceholderImage(modelType: ModelType): string {
  const placeholders = {
    [ModelType.LORA]: "/assets/placeholder-lora.svg",
    [ModelType.CHECKPOINT]: "/assets/placeholder-checkpoint.svg",
    [ModelType.VAE]: "/assets/placeholder-vae.svg",
    [ModelType.EMBEDDING]: "/assets/placeholder-embedding.svg",
    [ModelType.UNKNOWN]: "/assets/placeholder-unknown.svg"
  };
  return placeholders[modelType];
}

function formatFileSize(bytes: number): string {
  const units = ["B", "KB", "MB", "GB"];
  let size = bytes;
  let unitIndex = 0;

  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024;
    unitIndex++;
  }

  return `${size.toFixed(1)} ${units[unitIndex]}`;
}
```

---

#### 3. ModelDetailModal (Modal Component with Radix UI + Framer Motion)

**Location**: `src/sd_model_manager/ui/frontend/src/components/ModelDetailModal.tsx`

**Responsibilities**:
- Display comprehensive model information with accessible modal
- Show all Civitai metadata (description, tags, trigger words) with animations
- Provide accessible close button, ESC key handling, and focus management

**Dependencies**:
```typescript
import * as Dialog from "@radix-ui/react-dialog";
import { motion, AnimatePresence } from "framer-motion";
import { X } from "lucide-react";
```

**Interface** (Requirement 5.7):
```typescript
interface ModelDetailModalProps {
  model: ModelInfo | null;
  open: boolean;
  onClose: () => void;
}

export const ModelDetailModal: React.FC<ModelDetailModalProps> = ({
  model,
  open,
  onClose
}) => {
  if (!model) return null;

  return (
    <Dialog.Root open={open} onOpenChange={onClose}>
      <AnimatePresence>
        {open && (
          <Dialog.Portal forceMount>
            {/* Backdrop with blur animation */}
            <Dialog.Overlay asChild>
              <motion.div
                className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50"
                initial={{ opacity: 0, filter: "blur(4px)" }}
                animate={{ opacity: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, filter: "blur(4px)" }}
                transition={{ duration: 0.2, ease: "easeInOut" }}
              />
            </Dialog.Overlay>

            {/* Modal content with 3D perspective animation */}
            <Dialog.Content asChild forceMount>
              <motion.div
                className="fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                           w-full max-w-2xl max-h-[90vh] overflow-y-auto z-50
                           bg-white dark:bg-gray-900 rounded-xl shadow-2xl p-6
                           focus:outline-none"
                initial={{
                  opacity: 0,
                  scale: 0.8,
                  filter: "blur(4px)",
                  transform: "perspective(500px) rotateY(30deg) scale(0.8) translate(-50%, -50%)"
                }}
                animate={{
                  opacity: 1,
                  scale: 1,
                  filter: "blur(0px)",
                  transform: "perspective(500px) rotateY(0deg) scale(1) translate(-50%, -50%)"
                }}
                exit={{
                  opacity: 0,
                  scale: 0.8,
                  filter: "blur(4px)",
                  transform: "perspective(500px) rotateY(30deg) scale(0.8) translate(-50%, -50%)"
                }}
                transition={{ type: "spring", stiffness: 150, damping: 25 }}
              >
                {/* Close button with ARIA label */}
                <Dialog.Close
                  className="absolute top-4 right-4 p-2 rounded-full
                             hover:bg-gray-100 dark:hover:bg-gray-800
                             transition-colors focus:outline-none focus:ring-2
                             focus:ring-blue-500 focus:ring-offset-2"
                  aria-label="Close modal"
                >
                  <X className="w-5 h-5" />
                </Dialog.Close>

                {/* Header section */}
                <div className="mb-6">
                  <Dialog.Title className="text-2xl font-bold mb-2 pr-10">
                    {model.civitai_metadata?.name || model.filename}
                  </Dialog.Title>
                  <div className="flex gap-2">
                    <span className={`inline-flex items-center px-3 py-1 rounded-full
                                     text-xs font-medium
                                     ${model.model_type === 'LoRA' ? 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' : ''}
                                     ${model.model_type === 'Checkpoint' ? 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' : ''}
                                     ${model.model_type === 'VAE' ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' : ''}
                                     ${model.model_type === 'Embedding' ? 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200' : ''}`}>
                      {model.model_type}
                    </span>
                    <span className={`inline-flex items-center px-3 py-1 rounded-full
                                     text-xs font-medium
                                     ${model.category === 'Active' ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900 dark:text-emerald-200' : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'}`}>
                      {model.category}
                    </span>
                  </div>
                </div>

                {/* Preview image with fade-in animation */}
                {model.preview_url && (
                  <motion.img
                    src={model.preview_url}
                    alt={model.filename}
                    className="w-full h-auto rounded-lg mb-6 object-cover"
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 }}
                    onError={(e) => {
                      e.currentTarget.src = getPlaceholderImage(model.model_type);
                    }}
                  />
                )}

                {/* Metadata sections with staggered animation */}
                <motion.div
                  className="space-y-6"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.2 }}
                >
                  {/* File Information */}
                  <div>
                    <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
                      File Information
                    </h3>
                    <dl className="grid grid-cols-3 gap-x-4 gap-y-2 text-sm">
                      <dt className="font-medium text-gray-600 dark:text-gray-400">Filename:</dt>
                      <dd className="col-span-2 text-gray-900 dark:text-gray-100 break-all">
                        {model.filename}
                      </dd>
                      <dt className="font-medium text-gray-600 dark:text-gray-400">Path:</dt>
                      <dd className="col-span-2 text-gray-900 dark:text-gray-100 truncate"
                          title={model.file_path}>
                        {model.file_path}
                      </dd>
                      <dt className="font-medium text-gray-600 dark:text-gray-400">Size:</dt>
                      <dd className="col-span-2 text-gray-900 dark:text-gray-100">
                        {formatFileSize(model.file_size)}
                      </dd>
                      <dt className="font-medium text-gray-600 dark:text-gray-400">Created:</dt>
                      <dd className="col-span-2 text-gray-900 dark:text-gray-100">
                        {new Date(model.created_at).toLocaleDateString()}
                      </dd>
                      <dt className="font-medium text-gray-600 dark:text-gray-400">Modified:</dt>
                      <dd className="col-span-2 text-gray-900 dark:text-gray-100">
                        {new Date(model.modified_at).toLocaleDateString()}
                      </dd>
                    </dl>
                  </div>

                  {/* Civitai Metadata */}
                  {model.civitai_metadata && (
                    <>
                      <div>
                        <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
                          Civitai Metadata
                        </h3>
                        <dl className="grid grid-cols-3 gap-x-4 gap-y-2 text-sm">
                          {model.civitai_metadata.version && (
                            <>
                              <dt className="font-medium text-gray-600 dark:text-gray-400">
                                Version:
                              </dt>
                              <dd className="col-span-2 text-gray-900 dark:text-gray-100">
                                {model.civitai_metadata.version}
                              </dd>
                            </>
                          )}
                          {model.civitai_metadata.creator && (
                            <>
                              <dt className="font-medium text-gray-600 dark:text-gray-400">
                                Creator:
                              </dt>
                              <dd className="col-span-2 text-gray-900 dark:text-gray-100">
                                {model.civitai_metadata.creator}
                              </dd>
                            </>
                          )}
                          {model.civitai_metadata.description && (
                            <>
                              <dt className="font-medium text-gray-600 dark:text-gray-400">
                                Description:
                              </dt>
                              <dd className="col-span-2 text-gray-900 dark:text-gray-100 leading-relaxed">
                                {model.civitai_metadata.description}
                              </dd>
                            </>
                          )}
                        </dl>
                      </div>

                      {/* Trigger Words with staggered animation */}
                      {model.civitai_metadata.trigger_words.length > 0 && (
                        <div>
                          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
                            Trigger Words
                          </h3>
                          <div className="flex flex-wrap gap-2">
                            {model.civitai_metadata.trigger_words.map((word, idx) => (
                              <motion.span
                                key={idx}
                                className="px-3 py-1 bg-blue-100 dark:bg-blue-900
                                           text-blue-800 dark:text-blue-200
                                           rounded-full text-sm font-medium"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.3 + idx * 0.05 }}
                              >
                                {word}
                              </motion.span>
                            ))}
                          </div>
                        </div>
                      )}

                      {/* Tags with staggered animation */}
                      {model.civitai_metadata.tags.length > 0 && (
                        <div>
                          <h3 className="text-lg font-semibold mb-3 text-gray-900 dark:text-gray-100">
                            Tags
                          </h3>
                          <div className="flex flex-wrap gap-2">
                            {model.civitai_metadata.tags.map((tag, idx) => (
                              <motion.span
                                key={idx}
                                className="px-3 py-1 bg-gray-100 dark:bg-gray-800
                                           text-gray-800 dark:text-gray-200
                                           rounded-full text-sm"
                                initial={{ opacity: 0, scale: 0.8 }}
                                animate={{ opacity: 1, scale: 1 }}
                                transition={{ delay: 0.4 + idx * 0.03 }}
                              >
                                {tag}
                              </motion.span>
                            ))}
                          </div>
                        </div>
                      )}
                    </>
                  )}
                </motion.div>
              </motion.div>
            </Dialog.Content>
          </Dialog.Portal>
        )}
      </AnimatePresence>
    </Dialog.Root>
  );
};
```

**Accessibility Features**:
- ✅ Focus trap: Tab/Shift+Tab cycles through modal elements
- ✅ ESC key handling: Automatically closes modal
- ✅ ARIA labels: `aria-label` on close button, `Dialog.Title` for screen readers
- ✅ Backdrop click: Closes modal (Radix UI default behavior)
- ✅ Focus restoration: Returns focus to trigger element on close

**Animation Benefits**:
- Smooth 3D perspective entry/exit for professional feel
- Staggered tag animations prevent visual overload
- GPU-accelerated transforms for 60fps performance
- Backdrop blur enhances visual hierarchy

---

## Data Models

### Pydantic Models (Backend)

**Location**: `src/sd_model_manager/registry/models.py`

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator, model_validator

class ModelType(str, Enum):
    """Supported model types."""
    LORA = "lora"
    CHECKPOINT = "checkpoint"
    VAE = "vae"
    EMBEDDING = "embedding"
    UNKNOWN = "unknown"

class Category(str, Enum):
    """Model organization categories."""
    ACTIVE = "active"
    ARCHIVE = "archive"

class CivitaiMetadata(BaseModel):
    """Civitai metadata from .civitai.info files."""

    model_config = {"populate_by_name": True, "str_strip_whitespace": True}

    name: Optional[str] = None
    version: Optional[str] = None
    creator: Optional[str] = Field(None, alias="creatorUsername")
    description: Optional[str] = None
    tags: list[str] = Field(default_factory=list)
    trigger_words: list[str] = Field(default_factory=list, alias="trainedWords")
    preview_url: Optional[str] = Field(None, alias="images")

    @field_validator("preview_url", mode="before")
    @classmethod
    def extract_first_image(cls, v):
        """Extract first image URL from images array."""
        if isinstance(v, list) and len(v) > 0:
            first_image = v[0]
            if isinstance(first_image, dict):
                return first_image.get("url")
            return first_image
        return v

class ModelInfo(BaseModel):
    """Complete model information."""

    model_config = {"populate_by_name": True}

    id: str
    filename: str
    file_path: str
    file_size: int
    model_type: ModelType
    category: Category = Category.ACTIVE
    created_at: datetime
    modified_at: datetime
    civitai_metadata: Optional[CivitaiMetadata] = None
    preview_url: Optional[str] = None

    @model_validator(mode="after")
    def set_preview_from_metadata(self):
        """Set preview_url from Civitai metadata if not set."""
        if self.preview_url is None and self.civitai_metadata:
            self.preview_url = self.civitai_metadata.preview_url
        return self

# API Request/Response Models

class MoveRequest(BaseModel):
    """Request to move model to different category."""
    category: Category

class BulkMoveRequest(BaseModel):
    """Request to move multiple models."""
    model_ids: list[str] = Field(..., min_length=1)
    category: Category

class ModelsListResponse(BaseModel):
    """Response for GET /api/models."""
    success: bool = True
    models: list[ModelInfo]
    total_count: int
    scanned_at: Optional[datetime] = None

class ScanResponse(BaseModel):
    """Response for POST /api/models/scan."""
    success: bool
    models: list[ModelInfo]
    scanned_count: int
    message: str

class ModelDetailResponse(BaseModel):
    """Response for GET /api/models/{id}."""
    success: bool
    model: ModelInfo

class MoveResponse(BaseModel):
    """Response for POST /api/models/{id}/move."""
    success: bool
    moved_count: int
    new_path: str
    old_path: str
    message: str

class BulkMoveResponse(BaseModel):
    """Response for POST /api/models/bulk-move."""
    success: bool
    moved_count: int
    failed_count: int
    details: list[dict]
    message: str
```

**Pattern Alignment**:
- Pydantic V2 syntax (`model_config`, `Field`, validators)
- Enum for type safety (like Phase 2 download schemas)
- Optional metadata handling (graceful degradation)
- Field aliases for Civitai API compatibility

---

### TypeScript Interfaces (Frontend)

**Location**: `src/sd_model_manager/ui/frontend/src/types/models.ts`

```typescript
export enum ModelType {
  LORA = "lora",
  CHECKPOINT = "checkpoint",
  VAE = "vae",
  EMBEDDING = "embedding",
  UNKNOWN = "unknown"
}

export enum Category {
  ACTIVE = "active",
  ARCHIVE = "archive"
}

export interface CivitaiMetadata {
  name?: string;
  version?: string;
  creator?: string;
  description?: string;
  tags: string[];
  trigger_words: string[];
  preview_url?: string;
}

export interface ModelInfo {
  id: string;
  filename: string;
  file_path: string;
  file_size: number;
  model_type: ModelType;
  category: Category;
  created_at: string;
  modified_at: string;
  civitai_metadata?: CivitaiMetadata;
  preview_url?: string;
}

export interface ModelsListResponse {
  success: boolean;
  models: ModelInfo[];
  total_count: number;
  scanned_at?: string;
}

export interface MoveRequest {
  category: Category;
}

export interface MoveResponse {
  success: boolean;
  moved_count: number;
  new_path: string;
  old_path: string;
  message: string;
}

export interface BulkMoveRequest {
  model_ids: string[];
  category: Category;
}

export interface BulkMoveResponse {
  success: boolean;
  moved_count: number;
  failed_count: number;
  details: Array<{
    id: string;
    status: "success" | "failed";
    new_path?: string;
    error?: string;
  }>;
  message: string;
}
```

---

## Error Handling

### Error Hierarchy

**Location**: `src/sd_model_manager/lib/errors.py`

```python
# Extend existing AppError hierarchy

class ModelError(AppError):
    """Base error for model-related operations."""
    code = "MODEL_ERROR"

class ModelScanError(ModelError):
    """Errors during filesystem scanning."""
    code = "SCAN_ERROR"

class ModelMoveError(ModelError):
    """Errors during file movement."""
    code = "MOVE_ERROR"

class ModelNotFoundError(ModelError):
    """Model not found in registry."""
    code = "MODEL_NOT_FOUND"

class FileExistsError(ModelMoveError):
    """Destination file already exists."""
    code = "FILE_EXISTS"

class InvalidPathError(ModelMoveError):
    """Invalid or unsafe file path."""
    code = "INVALID_PATH"
```

### Error Response Format

```json
{
  "success": false,
  "error": "User-friendly error message",
  "code": "ERROR_CODE",
  "details": {
    "field": "additional context"
  }
}
```

**HTTP Status Codes**:
- 200 OK: Success
- 400 Bad Request: Invalid input (validation error)
- 404 Not Found: Model not found
- 409 Conflict: File already exists at destination
- 500 Internal Server Error: Scan/move operation failed

**Pattern Alignment**:
- Follows Phase 2 error handling structure
- Consistent error response format across endpoints
- Specific error codes for client-side handling

---

## Testing Strategy

### Backend Testing

**Test Coverage Target**: >80% for registry module

**Test Structure**:
```
tests/
├── registry/
│   ├── test_scanners.py          # ModelScanner unit tests
│   ├── test_repositories.py      # ModelRepository unit tests
│   └── test_models.py            # Pydantic model validation tests
├── api/
│   ├── test_models_api.py        # API endpoint integration tests
│   └── fixtures/
│       ├── sample_models/        # Test model files
│       └── .civitai.info         # Sample metadata files
└── integration/
    └── test_scan_and_move.py     # End-to-end workflow tests
```

**Unit Tests** (`test_scanners.py`):
```python
import pytest
from pathlib import Path
from sd_model_manager.registry.scanners import ModelScanner

@pytest.fixture
def temp_model_dir(tmp_path):
    """Create temp directory with sample models."""
    lora_dir = tmp_path / "loras"
    lora_dir.mkdir()

    # Create sample model file
    model_file = lora_dir / "test_lora.safetensors"
    model_file.write_bytes(b"fake model data")

    # Create .civitai.info file
    info_file = lora_dir / "test_lora.safetensors.civitai.info"
    info_file.write_text('{"name": "Test LoRA", "tags": ["character"]}')

    return tmp_path

@pytest.mark.asyncio
async def test_scan_discovers_models(temp_model_dir):
    """Test that scanner finds model files."""
    config = Config(model_scan_dir=str(temp_model_dir))
    scanner = ModelScanner(config)

    models = await scanner.scan()

    assert len(models) == 1
    assert models[0].filename == "test_lora.safetensors"
    assert models[0].model_type == ModelType.LORA

@pytest.mark.asyncio
async def test_scan_parses_civitai_metadata(temp_model_dir):
    """Test that scanner parses .civitai.info files."""
    config = Config(model_scan_dir=str(temp_model_dir))
    scanner = ModelScanner(config)

    models = await scanner.scan()

    assert models[0].civitai_metadata is not None
    assert models[0].civitai_metadata.name == "Test LoRA"
    assert "character" in models[0].civitai_metadata.tags

@pytest.mark.asyncio
async def test_scan_handles_invalid_metadata(temp_model_dir):
    """Test graceful handling of invalid .civitai.info."""
    # Create invalid metadata file
    invalid_info = temp_model_dir / "loras" / "test_lora.safetensors.civitai.info"
    invalid_info.write_text("{invalid json}")

    config = Config(model_scan_dir=str(temp_model_dir))
    scanner = ModelScanner(config)

    models = await scanner.scan()

    # Should still find model, but metadata is None
    assert len(models) == 1
    assert models[0].civitai_metadata is None
    assert models[0].filename == "test_lora.safetensors"
```

**Integration Tests** (`test_models_api.py`):
```python
import pytest
from fastapi.testclient import TestClient
from sd_model_manager.ui.api.main import create_app

@pytest.fixture
def client(temp_model_dir):
    """Create test client with temp model directory."""
    config = Config(model_scan_dir=str(temp_model_dir))
    app = create_app(config)
    return TestClient(app)

def test_list_models_triggers_initial_scan(client):
    """Test that GET /api/models triggers scan if cache empty."""
    response = client.get("/api/models")

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["models"]) > 0

def test_move_model_updates_path(client):
    """Test that move operation updates file path."""
    # Get model ID
    response = client.get("/api/models")
    model = response.json()["models"][0]

    # Move to archive
    response = client.post(
        f"/api/models/{model['id']}/move",
        json={"category": "archive"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "archive" in data["new_path"]

def test_move_fails_if_destination_exists(client):
    """Test that move fails with 409 if file exists."""
    # Create destination file
    # ... setup code ...

    response = client.post(
        f"/api/models/{model_id}/move",
        json={"category": "archive"}
    )

    assert response.status_code == 409
    assert "FILE_EXISTS" in response.json()["code"]
```

**E2E Tests** (Playwright):
```typescript
test("user can search and filter models", async ({ page }) => {
  await page.goto("/models");

  // Wait for models to load
  await page.waitForSelector(".model-card");

  // Type in search box
  await page.fill('input[placeholder="Search models..."]', "test");

  // Verify filtering
  const cards = await page.locator(".model-card").all();
  for (const card of cards) {
    const text = await card.textContent();
    expect(text.toLowerCase()).toContain("test");
  }
});

test("user can move model to archive", async ({ page }) => {
  await page.goto("/models");

  // Click move button
  await page.click(".model-card >> text=Move to Archive");

  // Confirm dialog
  page.on("dialog", dialog => dialog.accept());

  // Wait for notification
  await page.waitForSelector("text=/moved successfully/i");

  // Verify badge updated
  const badge = await page.locator(".badge-archive").first();
  expect(badge).toBeVisible();
});
```

---

## Performance & Scalability

### Performance Targets

| Operation | Target | Measurement |
|-----------|--------|-------------|
| Scan 1000 models | <5 seconds | Time from scan start to completion |
| API response (cached) | <200ms | Time to first byte |
| Grid render (initial) | <1 second | Time to interactive |
| Search filtering | <100ms | Debounced input to display update |
| File move operation | <500ms | API call to completion |

### Optimization Strategies

#### Backend Optimizations

1. **Async Filesystem Operations**:
```python
# Use asyncio.to_thread for I/O-bound operations
async def _scan_files(self) -> AsyncIterator[Path]:
    """Async generator for filesystem traversal."""
    loop = asyncio.get_event_loop()

    # Define blocking I/O operation to run in executor
    def scan_sync():
        """Blocking filesystem scan (runs in thread pool)."""
        result = []
        for file_path in self.base_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in self.supported_extensions:
                result.append(file_path)
        return result

    # Execute blocking scan in thread pool, then yield results
    files = await loop.run_in_executor(None, scan_sync)
    for file_path in files:
        yield file_path
```

2. **In-Memory Caching**:
- Dict lookup: O(1) complexity
- No database query overhead
- Cache invalidation on scan/move

3. **Lazy Metadata Parsing**:
- Only parse `.civitai.info` when model is scanned
- Skip metadata parsing for list endpoints (return cached)
- Detailed metadata on demand (GET /api/models/{id})

#### Frontend Optimizations

1. **Client-Side Filtering** (for <1000 models):
- Filter logic implemented in `ModelsPage` component using `useMemo()`
- No API calls on search/filter changes (instant response)
- Searches both filename and Civitai metadata name fields
- <100ms response time for filtering operations

2. **Virtual Scrolling** (Future):
```typescript
// For >100 models, use react-window
import { FixedSizeGrid } from "react-window";

<FixedSizeGrid
  columnCount={4}
  rowCount={Math.ceil(models.length / 4)}
  columnWidth={300}
  rowHeight={400}
  height={800}
  width={1200}
>
  {ModelCardRenderer}
</FixedSizeGrid>
```

3. **Image Lazy Loading**:
```typescript
<img
  src={model.preview_url}
  loading="lazy"  // Native lazy loading
  onError={(e) => e.currentTarget.src = placeholder}
/>
```

### Scalability Considerations

**Phase 1 (Current Design)**: <1000 models
- In-memory caching sufficient
- Client-side filtering performant
- No virtual scrolling needed

**Phase 2 (Database Migration)**: 1000-5000 models
- SQLite persistence with indexed queries
- Server-side pagination (20-50 models per page)
- Virtual scrolling for grid view

**Phase 3 (Enterprise Scale)**: >5000 models
- PostgreSQL or dedicated search (Elasticsearch)
- Server-side search with full-text indexing
- Infinite scroll with API cursor pagination
- CDN for preview images

---

## Migration Path

### Phase 1 → Phase 2: Add Background Scanning

**Changes Required**:
1. Add `BackgroundTasks` parameter to scan endpoint
2. Extend `ProgressManager` for scan progress tracking
3. Add WebSocket endpoint `/ws/scan/{task_id}`
4. Update frontend to poll scan progress

**No Breaking Changes**: Existing sync scan remains compatible

---

### Phase 1 → Database Persistence

**Changes Required**:
1. Add SQLAlchemy dependency
2. Create database models (mirror Pydantic models)
3. Replace `ModelRepository._models` dict with SQLAlchemy session
4. Add database migrations (Alembic)

**Migration Strategy**:
```python
# Pydantic models remain unchanged (API contracts)
# Add SQLAlchemy models as persistence layer

from sqlalchemy import Column, String, Integer, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class ModelRecord(Base):
    """SQLAlchemy model for database persistence."""
    __tablename__ = "models"

    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(Integer)
    model_type = Column(String)
    # ... other fields ...

    def to_pydantic(self) -> ModelInfo:
        """Convert to Pydantic model for API responses."""
        return ModelInfo(
            id=self.id,
            filename=self.filename,
            # ... other fields ...
        )

# Repository update
class ModelRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_all(self) -> list[ModelInfo]:
        records = self.session.query(ModelRecord).all()
        return [r.to_pydantic() for r in records]
```

**No API Changes**: Pydantic models ensure backward compatibility

---

## Security Considerations

### Path Traversal Prevention

```python
def validate_file_path(file_path: Path, base_dir: Path) -> None:
    """Validate that file path is within base directory."""
    resolved_path = file_path.resolve()
    resolved_base = base_dir.resolve()

    if not str(resolved_path).startswith(str(resolved_base)):
        raise InvalidPathError("Path traversal detected")

    if ".." in file_path.parts:
        raise InvalidPathError("Relative path not allowed")
```

### File Operation Safety

1. **No Execution**: Models are never executed, only scanned
2. **Read-Only Scanning**: Scanner has read-only filesystem access
3. **Validated Moves**: Move operations validate destination before execution
4. **Atomic Operations**: `shutil.move()` prevents partial moves
5. **Rollback on Failure**: Exceptions prevent incomplete state

### Input Validation

```python
class MoveRequest(BaseModel):
    category: Category  # Enum ensures only "active"/"archive"

    @field_validator("category")
    @classmethod
    def validate_category(cls, v):
        if v not in {Category.ACTIVE, Category.ARCHIVE}:
            raise ValueError("Invalid category")
        return v
```

---

## Configuration

### Config Extension

**Location**: `src/sd_model_manager/config.py`

```python
class Config(BaseSettings):
    # Existing fields
    civitai_api_key: Optional[str] = None
    download_dir: Path = Path("./downloads")
    host: str = "127.0.0.1"
    port: int = 8188

    # New fields for model viewer
    model_scan_dir: Path = Field(
        default=Path("./models"),
        description="Base directory for model scanning"
    )
    active_dir: Path = Field(
        default=Path("./models/active"),
        description="Directory for active models (loaded by ComfyUI)"
    )
    archive_dir: Path = Field(
        default=Path("./models/archive"),
        description="Directory for archived models (not loaded)"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )
```

**.env Example**:
```
CIVITAI_API_KEY=your_key_here
MODEL_SCAN_DIR=/path/to/models
ACTIVE_DIR=/path/to/models/active
ARCHIVE_DIR=/path/to/models/archive
```

---

## Deployment Considerations

### Directory Structure Setup

```bash
models/
├── active/              # ComfyUI loads from this directory
│   ├── loras/
│   ├── checkpoints/
│   ├── vae/
│   └── embeddings/
└── archive/             # ComfyUI does not load from this directory
    ├── loras/
    ├── checkpoints/
    ├── vae/
    └── embeddings/
```

**Setup Script**:
```python
def setup_model_directories(config: Config) -> None:
    """Create model directory structure if it doesn't exist."""
    for base_dir in [config.active_dir, config.archive_dir]:
        for model_type in ["loras", "checkpoints", "vae", "embeddings"]:
            dir_path = base_dir / model_type
            dir_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {dir_path}")
```

### ComfyUI Integration

**extra_model_paths.yaml** (for ComfyUI):
```yaml
sd_model_manager:
  base_path: /path/to/SD-Model-Manager/models/active/

  loras: loras/
  checkpoints: checkpoints/
  vae: vae/
  embeddings: embeddings/
```

**Refresh Instructions**:
1. Move models via Model Viewer
2. Press `r` in ComfyUI to refresh model list
3. OR use menu: `Edit → Refresh Node Definitions`

---

## Success Criteria

### Functional Completeness
- ✅ Scan discovers all model files (.safetensors, .ckpt, .pt, .pth, .bin)
- ✅ Model types correctly detected from path patterns
- ✅ Civitai metadata parsed and displayed
- ✅ Preview images shown (with fallback placeholders)
- ✅ Search filters by name and tags
- ✅ Type filter works for all model types
- ✅ File movement preserves directory structure
- ✅ Bulk operations handle partial failures gracefully

### Performance Targets
- ✅ Scan <5 seconds for 1000 models
- ✅ API response <200ms (cached)
- ✅ Grid render <1 second
- ✅ Search filter <100ms

### Quality Targets
- ✅ >80% backend test coverage
- ✅ Zero critical bugs in filesystem operations
- ✅ Graceful degradation for missing metadata
- ✅ All error states properly handled

### Architectural Consistency
- ✅ Follows Phase 2 Pydantic V2 patterns
- ✅ Uses FastAPI factory pattern
- ✅ Extends AppError hierarchy
- ✅ Consistent async/await usage
- ✅ Reuses shared infrastructure (Config, logging)

---

## Appendix: Reference Implementations

### Exploration Findings from Existing Codebase

**Key Patterns Identified** (from reference-explorer agent):

1. **Pydantic V2 Models** (`download/schemas.py`):
   - `model_config` instead of `Config` inner class
   - Field validators with `@field_validator`
   - Model validators with `@model_validator`

2. **FastAPI Router Pattern** (`ui/api/download.py`):
   - Factory function `create_app()`
   - Dependency injection with `Depends()`
   - Background tasks for async operations

3. **Error Handling** (`lib/errors.py`):
   - Hierarchical exceptions: `AppError` → `DownloadError`
   - Structured error responses with `code` and `details`

4. **Async Client Pattern** (`download/civitai_client.py`):
   - Lazy initialization of `httpx.AsyncClient`
   - Context manager support (`__aenter__`, `__aexit__`)
   - Async/await throughout

5. **Progress Tracking** (`ui/api/progress.py`):
   - Singleton `ProgressManager`
   - Dataclass models for progress state
   - WebSocket polling pattern

6. **Configuration** (`config.py`):
   - Pydantic `BaseSettings` with `.env` support
   - `SettingsConfigDict` for configuration
   - Path validation and defaults

**Recommendations for Implementation**:
- Extend `AppError` with `ModelError`, `ModelScanError`, `ModelMoveError`
- Use same Pydantic V2 patterns for validation
- Follow FastAPI factory pattern for testability
- Reuse `Config` class with new fields for model directories
- Consider future integration with `ProgressManager` for scan progress

---

## Next Steps

1. **Review and Approve Design** → Update `spec.json` to `design.approved=true`
2. **Generate Tasks** → Run `/kiro:spec-tasks model-viewer -y`
3. **Implementation** → Execute tasks following TDD methodology
4. **Integration** → Test with Phase 2 download functionality
5. **Deployment** → Setup model directories and ComfyUI integration
