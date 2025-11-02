# Requirements Document

## Introduction

The Model Viewer feature enables Stable Diffusion artists to view, search, and manage their local model collections through a web interface. This feature provides a visual catalog of models stored locally, displaying metadata, preview images, and file information extracted from both filesystem analysis and Civitai metadata files. The viewer operates independently of the download functionality, allowing users to browse and organize existing model collections without requiring internet connectivity or active downloads.

Additionally, the Model Viewer provides category management functionality, allowing users to organize models into Active and Archive categories. This enables users to control which models are loaded by ComfyUI/Stable Diffusion, improving application startup performance by archiving infrequently used models while maintaining them in a searchable catalog.

**Business Value:**
- Reduces time spent locating specific models in large collections (100+ files)
- Provides visual identification through preview images and thumbnails
- Enables efficient organization through search and filtering capabilities
- Preserves and displays Civitai metadata for better model understanding
- Improves workflow efficiency for Stable Diffusion artists
- Optimizes ComfyUI/Stable Diffusion startup performance by controlling which models are loaded
- Maintains archived models in a searchable catalog without requiring deletion

**Scope:** Standard implementation (Phase 1 + 2) with grid view, preview images, basic search functionality, and category management (Active/Archive) with file movement capabilities.

---

## Requirements

### Requirement 1: Filesystem Scanning
**Objective:** As a Stable Diffusion artist, I want the system to automatically discover and catalog all model files in my local directory, so that I can view my complete model collection without manual registration.

#### Acceptance Criteria

1. WHEN the Model Viewer page is loaded for the first time THEN the Model Viewer SHALL scan the configured model directory for all supported file types
2. WHERE a model file has extension `.safetensors`, `.ckpt`, `.pt`, `.pth`, or `.bin` THE Model Viewer SHALL identify the file as a potential model
3. WHEN scanning a model file THEN the Model Viewer SHALL determine the model type based on file path patterns:
   - Files in `*/lora/*` or `*/loras/*` directories SHALL be classified as LoRA
   - Files in `*/checkpoints/*` or `*/models/Stable-diffusion/*` directories SHALL be classified as Checkpoint
   - Files in `*/vae/*` directories SHALL be classified as VAE
   - Files in `*/embeddings/*` directories SHALL be classified as Embedding
4. IF a model file does not match any path pattern THEN the Model Viewer SHALL classify it as "Unknown" type
5. WHEN a model file is discovered THEN the Model Viewer SHALL extract file metadata including filename, file size, creation date, and modification date
6. WHEN the scan completes THEN the Model Viewer SHALL return a list of all discovered models with their metadata

### Requirement 2: Civitai Metadata Integration
**Objective:** As a Stable Diffusion artist, I want to see Civitai metadata for models I've downloaded, so that I can understand model details, usage instructions, and creator information.

#### Acceptance Criteria

1. WHEN scanning a model file THEN the Model Viewer SHALL check for a corresponding `.civitai.info` file in the same directory
2. WHERE a `.civitai.info` file exists with the same base filename as the model THE Model Viewer SHALL parse the JSON metadata
3. IF the `.civitai.info` file contains valid JSON THEN the Model Viewer SHALL extract the following fields:
   - Model name
   - Model version
   - Creator/author information
   - Description
   - Tags
   - Trigger words
   - Preview image URLs
4. WHEN `.civitai.info` metadata is successfully parsed THEN the Model Viewer SHALL associate this metadata with the corresponding model record
5. IF the `.civitai.info` file is missing or contains invalid JSON THEN the Model Viewer SHALL use the filename as the model name and mark metadata as unavailable

### Requirement 3: Preview Image Handling
**Objective:** As a Stable Diffusion artist, I want to see preview images for my models, so that I can visually identify and distinguish between different models at a glance.

#### Acceptance Criteria

1. WHEN Civitai metadata contains preview image URLs THEN the Model Viewer SHALL store the primary preview image URL with the model record
2. WHERE a model has associated preview images THE Model Viewer SHALL select the first image as the primary preview
3. WHEN displaying a model in the grid view THEN the Model Viewer SHALL show the preview image as a thumbnail
4. IF a model has no preview image URL THEN the Model Viewer SHALL display a placeholder image indicating the model type (LoRA, Checkpoint, VAE, or Embedding)
5. WHEN a preview image fails to load THEN the Model Viewer SHALL fall back to the type-specific placeholder image

### Requirement 4: Model Registry API
**Objective:** As a frontend developer, I want REST API endpoints to retrieve model data, so that the React UI can display and interact with the model collection.

#### Acceptance Criteria

1. WHEN a GET request is made to `/api/models` THEN the API SHALL return a JSON array of all scanned models with their metadata
2. WHEN a POST request is made to `/api/models/scan` THEN the API SHALL trigger a new filesystem scan and return the updated model list
3. WHEN a GET request is made to `/api/models/{id}` THEN the API SHALL return detailed metadata for the specified model
4. IF the requested model ID does not exist THEN the API SHALL return a 404 Not Found response with an error message
5. WHEN the API returns model data THEN the response SHALL include:
   - Model ID (unique identifier)
   - Filename
   - File path
   - File size
   - Model type (LoRA, Checkpoint, VAE, Embedding, Unknown)
   - Creation date
   - Modification date
   - Civitai metadata (if available)
   - Preview image URL (if available)
6. WHEN any API endpoint encounters an error THEN the API SHALL return an appropriate HTTP status code and a structured error response

### Requirement 5: Grid View Display
**Objective:** As a Stable Diffusion artist, I want to view my models in a visual grid layout, so that I can quickly browse and identify models using their preview images.

#### Acceptance Criteria

1. WHEN the Models page is loaded THEN the Model Viewer SHALL display all models in a responsive grid layout
2. WHERE the viewport width is ≥1280px (desktop) THE Model Viewer SHALL display 4 model cards per row
3. WHERE the viewport width is between 768px and 1279px (tablet) THE Model Viewer SHALL display 3 model cards per row
4. WHERE the viewport width is <768px (mobile) THE Model Viewer SHALL display 2 model cards per row
5. WHEN displaying a model card THEN the Model Viewer SHALL show:
   - Preview image or type placeholder
   - Model name
   - Model type badge
   - File size
6. WHEN a user hovers over a model card THEN the Model Viewer SHALL highlight the card with a visual indicator
7. WHEN a user clicks on a model card THEN the Model Viewer SHALL display detailed model information in an expanded view or modal

### Requirement 6: Search and Filter
**Objective:** As a Stable Diffusion artist, I want to search and filter my model collection, so that I can quickly find specific models in large collections.

#### Acceptance Criteria

1. WHEN the Models page is loaded THEN the Model Viewer SHALL display a search input field above the grid
2. WHEN a user types in the search field THEN the Model Viewer SHALL filter the displayed models in real-time
3. WHERE the search query matches a model name (case-insensitive partial match) THE Model Viewer SHALL include that model in the filtered results
4. WHERE the search query matches any model tag (case-insensitive) THE Model Viewer SHALL include that model in the filtered results
5. WHEN the search field is cleared THEN the Model Viewer SHALL display all models again
6. WHEN the Models page is loaded THEN the Model Viewer SHALL display filter controls for model type
7. WHEN a user selects a model type filter (LoRA, Checkpoint, VAE, Embedding) THEN the Model Viewer SHALL display only models of that type
8. WHEN multiple filters are active THEN the Model Viewer SHALL apply both search and type filters (AND logic)
9. IF no models match the current filters THEN the Model Viewer SHALL display a "No models found" message

### Requirement 7: Loading and Error States
**Objective:** As a Stable Diffusion artist, I want clear feedback during scanning and error conditions, so that I understand the system state and any issues that occur.

#### Acceptance Criteria

1. WHEN the initial scan is in progress THEN the Model Viewer SHALL display a loading indicator with "Scanning models..." message
2. WHEN models are being loaded from the API THEN the Model Viewer SHALL display a loading spinner or skeleton grid
3. IF the filesystem scan fails THEN the Model Viewer SHALL display an error message with the failure reason
4. IF the API request fails THEN the Model Viewer SHALL display an error message and provide a retry button
5. WHEN a user clicks the retry button THEN the Model Viewer SHALL attempt to reload the model data
6. WHEN the scan completes with zero models found THEN the Model Viewer SHALL display a message indicating the model directory is empty or not configured

### Requirement 8: Manual Scan Trigger
**Objective:** As a Stable Diffusion artist, I want to manually trigger a rescan of my model directory, so that newly added or removed models are reflected in the viewer without reloading the page.

#### Acceptance Criteria

1. WHEN the Models page is displayed THEN the Model Viewer SHALL show a "Scan for Models" button
2. WHEN a user clicks the "Scan for Models" button THEN the Model Viewer SHALL trigger a new filesystem scan via the API
3. WHILE a scan is in progress THE Model Viewer SHALL disable the scan button and show "Scanning..." text
4. WHEN the scan completes successfully THEN the Model Viewer SHALL update the grid with the new model list
5. IF the scan fails THEN the Model Viewer SHALL display an error message and re-enable the scan button

### Requirement 9: Performance and Scalability
**Objective:** As a Stable Diffusion artist with a large model collection, I want the viewer to remain responsive, so that I can browse hundreds of models without performance degradation.

#### Acceptance Criteria

1. WHEN the model directory contains up to 1000 models THEN the filesystem scan SHALL complete within 5 seconds
2. WHEN displaying the grid view THEN the Model Viewer SHALL render the initial viewport within 1 second
3. WHEN scrolling through the grid THEN the Model Viewer SHALL maintain 60fps scrolling performance
4. WHERE the model list contains more than 100 models THE Model Viewer SHALL implement virtual scrolling or pagination
5. WHEN filtering or searching THEN the Model Viewer SHALL update the displayed results within 100ms

### Requirement 10: Data Persistence
**Objective:** As a system administrator, I want model scan results to be stored efficiently, so that subsequent page loads don't require full directory rescans.

#### Acceptance Criteria

1. WHEN a filesystem scan completes THEN the Model Registry SHALL store the scan results in memory
2. WHEN the API receives a `/api/models` request THEN the Model Registry SHALL return cached results if a scan has been performed
3. IF no scan has been performed since server startup THEN the Model Registry SHALL automatically trigger an initial scan
4. WHEN the server restarts THEN the Model Registry SHALL perform a fresh scan on the first API request
5. (Future) WHERE the model directory is large (>500 models) THE Model Registry SHALL persist scan results to a database for faster startup

### Requirement 11: Model Category Management and File Movement
**Objective:** As a Stable Diffusion artist, I want to categorize models into Active and Archive groups, so that I can control which models ComfyUI loads and improve startup performance by archiving unused models.

#### Acceptance Criteria

1. WHEN the Models page is loaded THEN the Model Viewer SHALL display a category badge (Active or Archive) on each model card
2. WHEN displaying a model card THEN the Model Viewer SHALL provide a "Move to Archive" button for Active models and a "Move to Active" button for Archived models
3. WHEN a user clicks a move button THEN the Model Viewer SHALL display a confirmation dialog showing the current and destination paths
4. WHEN the user confirms the move operation THEN the Model Viewer SHALL send an API request to move the file
5. WHEN the file move completes successfully THEN the Model Viewer SHALL update the model's category and file path in the UI
6. IF the destination directory does not exist THEN the Model Viewer SHALL create it automatically maintaining the same subdirectory structure (loras/, checkpoints/, vae/, embeddings/)
7. WHEN a file move operation is initiated THEN the Model Viewer SHALL prevent duplicate moves of the same file until the operation completes
8. IF a file with the same name already exists at the destination THEN the Model Viewer SHALL display an error message and cancel the move operation

**Directory Structure:**
```
models/
├── active/           # ComfyUI loads from this directory
│   ├── loras/
│   ├── checkpoints/
│   └── vae/
└── archive/          # ComfyUI does not load from this directory
    ├── loras/
    ├── checkpoints/
    └── vae/
```

### Requirement 12: File Movement API
**Objective:** As a backend developer, I want a REST API endpoint to safely move model files between Active and Archive directories, so that the frontend can perform category management operations.

#### Acceptance Criteria

1. WHEN a POST request is made to `/api/models/{id}/move` with `{"category": "active"}` or `{"category": "archive"}` THEN the API SHALL move the model file to the corresponding directory
2. WHEN moving a file THEN the API SHALL preserve the model type subdirectory structure (e.g., `active/loras/model.safetensors` → `archive/loras/model.safetensors`)
3. WHEN the move operation succeeds THEN the API SHALL return a 200 response with:
   - `success: true`
   - `moved_count: 1`
   - `new_path`: Full path to the moved file
   - `old_path`: Original file path
   - `message`: "Model moved successfully. Press 'r' in ComfyUI to refresh the model list"
4. IF the destination file already exists THEN the API SHALL return a 409 Conflict response with error code "FILE_EXISTS"
5. IF the model ID does not exist THEN the API SHALL return a 404 Not Found response
6. IF the file move operation fails THEN the API SHALL return a 500 Internal Server Error response with the failure reason
7. WHEN a file move fails THEN the API SHALL ensure the original file remains in its original location (rollback on failure)
8. WHEN a file move completes THEN the API SHALL update the model registry cache with the new file path and category
9. WHEN processing a move request THEN the API SHALL validate:
   - Destination path does not contain path traversal sequences (`..`, absolute paths)
   - Category parameter is either "active" or "archive"
   - Source file exists and is readable
   - Sufficient disk space exists at destination

**API Response Examples:**

Success:
```json
{
  "success": true,
  "moved_count": 1,
  "new_path": "/models/archive/loras/model.safetensors",
  "old_path": "/models/active/loras/model.safetensors",
  "message": "Model moved successfully. Press 'r' in ComfyUI to refresh the model list"
}
```

Error (File Exists):
```json
{
  "success": false,
  "error": "File already exists in destination",
  "code": "FILE_EXISTS",
  "details": {
    "existing_path": "/models/archive/loras/model.safetensors"
  }
}
```

### Requirement 13: Bulk Movement Operations
**Objective:** As a Stable Diffusion artist, I want to move multiple models at once, so that I can efficiently reorganize my model collection without performing individual moves.

#### Acceptance Criteria

1. WHEN displaying the model grid THEN the Model Viewer SHALL provide checkboxes for selecting multiple models
2. WHEN one or more models are selected THEN the Model Viewer SHALL display a "Move Selected to Archive" or "Move Selected to Active" button depending on the current category
3. WHEN a user clicks the bulk move button THEN the Model Viewer SHALL display a confirmation dialog showing the number of models to be moved
4. WHEN the user confirms the bulk move THEN the Model Viewer SHALL send a POST request to `/api/models/bulk-move` with the model IDs and target category
5. WHILE the bulk move is in progress THE Model Viewer SHALL display a progress indicator showing "Moving X of Y models..."
6. WHEN the bulk move API responds THEN the Model Viewer SHALL display a summary showing:
   - Number of successfully moved models
   - Number of failed moves (if any)
   - List of any errors that occurred
7. WHEN any model in a bulk move fails THEN the Model Viewer SHALL continue moving the remaining models and report all results
8. WHEN the bulk move completes THEN the Model Viewer SHALL update the UI to reflect the new categories for all successfully moved models

**Bulk Move API Endpoint:**

Request: `POST /api/models/bulk-move`
```json
{
  "model_ids": ["id1", "id2", "id3"],
  "category": "archive"
}
```

Response:
```json
{
  "success": true,
  "moved_count": 2,
  "failed_count": 1,
  "details": [
    {"id": "id1", "status": "success", "new_path": "/models/archive/loras/model1.safetensors"},
    {"id": "id2", "status": "success", "new_path": "/models/archive/loras/model2.safetensors"},
    {"id": "id3", "status": "failed", "error": "File already exists in destination"}
  ],
  "message": "Moved 2 of 3 models successfully. Press 'r' in ComfyUI to refresh the model list"
}
```

### Requirement 14: ComfyUI Integration Guidance
**Objective:** As a Stable Diffusion artist using ComfyUI, I want clear instructions on how to configure ComfyUI and refresh the model list after moving files, so that I can seamlessly integrate the Model Viewer with my existing ComfyUI workflow.

#### Acceptance Criteria

1. WHEN a file move operation completes successfully THEN the Model Viewer SHALL display a notification message with ComfyUI refresh instructions
2. WHERE models have been moved THE notification SHALL include the following information:
   - Success message: "✅ X model(s) moved to [Active/Archive]"
   - ComfyUI refresh method 1: "Press 'r' in ComfyUI to refresh the model list"
   - ComfyUI refresh method 2: "Or use menu: Edit → Refresh Node Definitions"
   - Directory information: "Active models: models/active/ | Archived models: models/archive/"
3. WHEN a user clicks a "Setup Guide" link in the interface THEN the Model Viewer SHALL display documentation explaining:
   - How to configure ComfyUI's `extra_model_paths.yaml` to point to the `models/active/` directory
   - How ComfyUI automatically detects file changes when the refresh command is executed
   - Troubleshooting steps if models don't appear in ComfyUI after refresh
4. WHEN displaying the setup guide THEN the documentation SHALL include an example `extra_model_paths.yaml` configuration:

```yaml
sd_model_manager:
  base_path: /path/to/SD-Model-Manager/models/active/

  loras: loras/
  checkpoints: checkpoints/
  vae: vae/
```

5. WHEN the bulk move notification is displayed THEN the message SHALL remind users that a single 'r' key press in ComfyUI will refresh all moved models at once

**Notification Message Example:**
```
✅ 3 model(s) moved to Archive

💡 ComfyUI Refresh:
Press "r" in ComfyUI to refresh the model list

OR

Menu: Edit → Refresh Node Definitions

Note:
- Active models: models/active/
- Archived models: models/archive/

[Setup Guide]
```

---

## Non-Functional Requirements

### Performance
- Initial scan: <5 seconds for 1000 models
- API response time: <200ms for model list queries
- UI rendering: <1 second for initial grid display
- Search filtering: <100ms response time

### Usability
- Responsive design supporting desktop, tablet, and mobile viewports
- Keyboard navigation support for accessibility
- Clear visual feedback for all user actions
- Intuitive search and filter controls

### Reliability
- Graceful handling of missing or corrupted `.civitai.info` files
- Fallback to filename-based display when metadata unavailable
- Error recovery with retry capabilities
- Robust file type detection

### Maintainability
- Clear separation between scanning logic, data storage, and API layers
- Comprehensive test coverage (>80% for backend)
- Type safety with Pydantic models and TypeScript interfaces
- Consistent error handling patterns

### Security
- Controlled filesystem write access limited to moving files within the configured model directory
- Path traversal protection for all file operations (read and write)
- Validation of destination paths to prevent moving files outside the model directory
- Input validation for all API parameters including category names and model IDs
- Atomic file move operations with rollback on failure
- Prevention of overwriting existing files without explicit user confirmation
- No execution of arbitrary model files
- Read-only access for model scanning and metadata extraction

---

## Technical Constraints

### Backend
- Python 3.11+ with FastAPI framework
- Async/await for non-blocking I/O operations
- Pydantic V2 for data validation
- Pytest for test coverage

### Frontend
- React 18 with TypeScript
- Vite for build and development
- Tailwind CSS for styling
- React hooks for state management

### Integration
- RESTful API design following existing patterns
- JSON response format for all endpoints
- CORS configuration for local development
- Consistent error response structure

### File System
- Configurable model directory path (default: `./models`)
- Support for nested directory structures
- Read-only access to model files
- `.civitai.info` JSON format as defined by Civitai API

---

## Dependencies

### Existing System Components
- Configuration system (`src/sd_model_manager/config.py`)
- Logging infrastructure (`src/sd_model_manager/lib/logging_config.py`)
- Error handling framework (`src/sd_model_manager/lib/errors.py`)
- FastAPI application structure (`src/sd_model_manager/ui/api/main.py`)
- React frontend base (`src/sd_model_manager/ui/frontend/`)

### External Dependencies
- No new external API dependencies required
- Filesystem access via Python standard library (`pathlib`, `os`)
- JSON parsing via Python standard library (`json`)
- Frontend image loading via browser APIs

### Phase 2 Independence
- Viewer functionality operates independently of download system
- Can display models regardless of download source
- Shares configuration and logging infrastructure
- Follows same architectural patterns for consistency

---

## Reference Repositories

### Implementation References
The following repositories provide proven implementations and patterns that can be leveraged during design and implementation phases:

#### ComfyUI-Lora-Manager (Reference Only - GPL-3.0)
- **Location**: `reference_git_clones/ComfyUI-Lora-Manager`
- **URL**: https://github.com/willmiao/ComfyUI-Lora-Manager
- **License**: GPL-3.0 (Reference only, no direct code reuse)
- **Relevant Features**:
  - File movement and organization patterns
  - Category management UI design
  - Grid view layout and interactions
  - Bulk operations workflow
  - Auto-organization logic with path templates
  - Duplicate detection and conflict resolution
  - Folder sidebar and breadcrumb navigation
- **Usage Strategy**: Study implementation patterns and UI/UX design; reimplement independently to avoid GPL contamination

#### civitai-downloader-v2 (Full Reuse - Own Development)
- **Location**: `reference_git_clones/civitai-tools/civitai-downloader-v2`
- **License**: Owned by developer (full reuse permitted)
- **Relevant Features**:
  - SQLite database schema for model metadata
  - `.civitai.info` file format and generation
  - Duplicate detection logic using database records
  - Metadata collection and storage patterns
  - Category-based file organization (`type/base-model/category/[id]name/version`)
  - Download history tracking
  - Performance optimization patterns
- **Integration Strategy**: Reuse database schema, metadata formats, and duplicate detection logic; adapt for Model Registry implementation

#### paperspace-civitiai-downloader (Full Reuse - Own Development)
- **Location**: `reference_git_clones/paperspace-civitiai-downloader`
- **License**: Owned by developer (full reuse permitted)
- **Relevant Features**:
  - SHA256-based model identification
  - Metadata scanner implementation for existing files
  - Civitai API integration patterns
  - Batch processing for bulk operations
  - CSV/JSON export functionality
  - Resume-capable download logic
- **Integration Strategy**: Reuse metadata scanning logic for existing model collections; adapt SHA256 identification for model registry

#### startpack (Full Reuse - Purchased)
- **Location**: `reference_git_clones/startpack`
- **License**: Purchased (full reuse permitted)
- **Relevant Features**:
  - Next.js + TypeScript SaaS architecture patterns
  - React component structures
  - UI/UX design patterns
  - Authentication and authorization patterns (if applicable)
  - API design patterns
  - Build and deployment configurations
- **Integration Strategy**: Reference React component patterns and UI design for frontend implementation; adapt TypeScript patterns for type safety

### Code Reuse Guidelines
1. **GPL-3.0 Compliance**: ComfyUI-Lora-Manager code cannot be directly copied; only study and reimplement independently
2. **Attribution**: Provide attribution in code comments for patterns inspired by reference repositories
3. **Adaptation**: Modify all reused code to fit FastAPI/React architecture and project conventions
4. **Testing**: Add comprehensive tests for all reused or adapted components
5. **Documentation**: Document origin and modifications in code comments and architecture docs
6. **License Headers**: Include appropriate license headers for code from owned repositories

### Integration Priorities for Design Phase
1. **High Priority**:
   - civitai-downloader-v2 database schema and metadata formats
   - paperspace-civitiai-downloader metadata scanning logic
   - ComfyUI-Lora-Manager UI/UX patterns (reference only)
2. **Medium Priority**:
   - startpack React component patterns
   - civitai-downloader-v2 duplicate detection logic
3. **Low Priority**:
   - ComfyUI-Lora-Manager bulk operations workflow (reference)
   - paperspace-civitiai-downloader CSV export patterns

---

## Success Metrics

### Functional Completeness
- All supported model types (LoRA, Checkpoint, VAE, Embedding) correctly identified
- Civitai metadata successfully parsed and displayed
- Search and filter operations work across all models
- Grid view responsive across all target viewports

### Performance Targets
- Scan completion time meets <5 second target for 1000 models
- UI remains responsive during filtering and scrolling
- API response times under 200ms threshold

### Quality Targets
- >80% test coverage for backend components
- Zero critical bugs in filesystem scanning
- Graceful degradation when metadata unavailable
- All error states properly handled and displayed
