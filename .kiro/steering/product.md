# Product Steering Document

## Product Overview

**SD-Model-Manager** is a comprehensive tool for managing Stable Diffusion models with integrated download, viewing, and organization capabilities.

## Core Features

### 1. Model Viewer (Phase 3 - Current Focus)
- Display local model files (LoRA, Checkpoint, VAE, Embedding)
- Show metadata, preview images, and file information
- Search and filter capabilities
- Grid view with thumbnails
- Detailed model information view

### 2. Download Management (Phase 2 - Completed)
- Download models from Civitai
- Real-time progress tracking via WebSocket
- Resume capability for interrupted downloads
- Automatic metadata extraction

### 3. Model Registry
- Local filesystem scanning
- Model metadata storage
- Relationship tracking between models
- Version management

## Target Use Case

**Primary Users**: Stable Diffusion artists and creators who need to:
- Organize large collections of models (100+ files)
- Track model metadata and relationships
- Download models from Civitai efficiently
- Preview models before use
- Find specific models quickly

**Workflow**: Download → Scan → View → Organize → Use in SD workflows

## Key Value Proposition

1. **Unified Interface**: Single tool for download and local model management
2. **Metadata Preservation**: Keeps Civitai metadata with local files
3. **Visual Organization**: Preview images and grid views for quick identification
4. **Search Efficiency**: Fast search across large model collections
5. **Web-Based UI**: Cross-platform, no desktop app installation needed

## Architecture Philosophy

- **Backend**: Python FastAPI for robust API and file handling
- **Frontend**: React for responsive, modern UI
- **API-First**: RESTful design for potential future integrations
- **WebSocket**: Real-time updates for long-running operations
- **Local-First**: Works offline for viewing local models

## Development Approach

- **Spec-Driven**: Kiro methodology with requirements → design → tasks → implementation
- **TDD**: Test-driven development with pytest
- **Incremental**: Phased rollout (CLI → Download → Viewer → Advanced features)
- **Quality Focus**: Type safety, comprehensive testing, error handling
