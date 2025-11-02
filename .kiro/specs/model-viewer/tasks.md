# Implementation Tasks: Model Viewer

## Overview
Implement web-based model viewer for browsing, searching, and managing local Stable Diffusion model collections with Active/Archive category management.

## Task List

- [ ] 1. Build model scanning and type detection system
- [ ] 1.1 Implement filesystem scanner for model files
  - Scan model directory recursively for supported extensions (.safetensors, .ckpt, .pt, .bin, .pth)
  - Detect model type (LoRA, Checkpoint, VAE, Embedding) based on file path patterns
  - Detect category (Active, Archive) based on directory structure
  - Extract file metadata (size, timestamps)
  - Handle scanning errors gracefully with detailed logging
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [ ] 1.2 Integrate Civitai metadata extraction
  - Read and parse `.civitai.info` JSON files adjacent to model files
  - Extract model name, version, creator, description from metadata
  - Parse trigger words and tags arrays
  - Store preview image URLs from Civitai metadata
  - Handle missing or malformed metadata files gracefully
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ] 1.3 Implement preview image handling from Civitai metadata
  - Extract preview image URLs from Civitai metadata
  - Select primary preview image (first image in array)
  - Implement type-specific placeholder images (LoRA, Checkpoint, VAE, Embedding)
  - Handle missing preview URLs with appropriate placeholders
  - Implement fallback to placeholder on image load failure
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_

- [ ] 2. Create backend API endpoints for model data
- [ ] 2.1 Build model listing and scanning endpoints
  - Implement GET /api/models endpoint to return all scanned models
  - Implement POST /api/models/scan endpoint to trigger manual scan
  - Return complete model data (ID, filename, path, size, type, dates, metadata, preview URL)
  - Handle API errors with appropriate HTTP status codes and structured responses
  - Implement in-memory cache with automatic initial scan
  - _Requirements: 4.1, 4.2, 4.5, 4.6, 10.1, 10.2, 10.3, 10.4_

- [ ] 2.2 Build model detail endpoint
  - Implement GET /api/models/{id} endpoint for individual model details
  - Return complete model information including all metadata fields
  - Handle non-existent model IDs with 404 Not Found response
  - Validate model ID format and security
  - _Requirements: 4.3, 4.4_

- [ ] 2.3 Implement single model movement endpoint
  - Create POST /api/models/{id}/move endpoint for category changes
  - Validate source file existence and destination path (no path traversal)
  - Check available disk space before moving files
  - Move files atomically preserving model type subdirectory structure
  - Update model registry cache after successful move
  - Return move result with new/old paths and success message
  - Handle move failures with rollback and error details (FILE_EXISTS, etc.)
  - _Requirements: 11.2, 11.3, 11.4, 11.6, 11.7, 11.8, 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7, 12.8, 12.9_

- [ ] 2.4 Implement bulk operations endpoint
  - Create POST /api/models/bulk-move endpoint for moving multiple models
  - Accept array of model IDs and target category
  - Process moves sequentially continuing on failures
  - Return detailed results for each model (success/failure with reasons)
  - Provide summary statistics (moved count, failed count)
  - Include ComfyUI refresh instructions in success message
  - _Requirements: 13.4, 13.6, 13.7_

- [ ] 3. Build frontend model viewer page and layout
- [ ] 3.1 Create models page structure with navigation
  - Implement ModelsPage component as main container
  - Add navigation between Download and Models pages
  - Set up page layout with header, filters, and content area
  - Initialize state management for models, filters, and selections
  - _Requirements: 5.1_

- [ ] 3.2 Implement responsive model grid display
  - Create ModelGrid component with responsive grid layout (4-3-2 columns)
  - Implement ModelCard component for individual model thumbnails
  - Show preview image or type placeholder
  - Display model name, type badge, and file size
  - Add hover effect with visual indicator
  - Handle empty state when no models found
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 3.3 Add model detail modal with Radix UI
  - Create ModelDetailModal component using Radix Dialog + Framer Motion
  - Show full-size preview image with fallback for missing images
  - Display complete file information (filename, path, size, dates)
  - Show Civitai metadata (name, version, creator, description)
  - Display trigger words as animated chips
  - Display tags as animated chips
  - Implement accessible close behavior (ESC, backdrop click, close button)
  - _Requirements: 5.7, 3.1, 3.2, 3.3, 3.4, 3.5, 2.3, 2.4, 2.5_

- [ ] 4. Implement search and filtering functionality
- [ ] 4.1 Build real-time search functionality
  - Add search input field in page header
  - Implement real-time search across filename and model name (case-insensitive)
  - Implement tag search (case-insensitive)
  - Update grid display as user types
  - Show "No models found" message for empty results
  - Clear search to display all models
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.9_

- [ ] 4.2 Add model type filtering
  - Create type filter dropdown (All, LoRA, Checkpoint, VAE, Embedding)
  - Implement filter logic to show only selected type
  - Combine type filter with search query (AND logic)
  - Update filter UI to show active selection
  - _Requirements: 6.6, 6.7, 6.8_

- [ ] 5. Implement model selection and movement with category management
- [ ] 5.1 Add model selection functionality
  - Implement checkbox selection on model cards
  - Track selected model IDs in component state
  - Add "Select All" / "Deselect All" controls
  - Show selected count in UI
  - Disable selection during move operations
  - _Requirements: 13.1, 13.2_

- [ ] 5.2 Display category badges and implement single model movement
  - Display category badge (Active or Archive) on each model card
  - Add context-aware move button ("Move to Archive" / "Move to Active")
  - Show Radix AlertDialog confirmation with current and destination paths
  - Call move API endpoint with selected category
  - Update UI after successful move
  - Show error message if move fails
  - Prevent duplicate moves during operation
  - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.7_

- [ ] 5.3 Implement bulk model movement with progress tracking
  - Add bulk move controls for selected models (context-aware button)
  - Show Radix AlertDialog confirmation with number of models
  - Display progress indicator showing "Moving X of Y models..."
  - Display move results dialog with success/failure details
  - Show summary statistics (moved count, failed count)
  - Clear selection after successful bulk move
  - Handle partial failures gracefully
  - _Requirements: 13.1, 13.2, 13.3, 13.4, 13.5, 13.6, 13.7, 13.8_

- [ ] 6. Add manual scan trigger and state management
- [ ] 6.1 Implement manual scan button
  - Add "Scan for Models" button to page header
  - Trigger POST /api/models/scan on button click
  - Show scanning state in button UI ("Scanning...")
  - Disable button during scan operation
  - Update model list after scan completes
  - Show notification with scan results
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 6.2 Add loading and error states
  - Show loading spinner during initial page load
  - Display loading state with "Scanning models..." message
  - Show error messages for API failures
  - Implement retry mechanism for failed requests
  - Provide user-friendly error descriptions
  - Display message for empty model directory
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6_

- [ ] 7. Implement ComfyUI integration guidance
- [ ] 7.1 Add move success notifications with ComfyUI refresh instructions
  - Display notification after successful file move showing success count
  - Include ComfyUI refresh method 1: "Press 'r' in ComfyUI"
  - Include ComfyUI refresh method 2: "Menu: Edit → Refresh Node Definitions"
  - Show directory information (Active: models/active/, Archive: models/archive/)
  - Remind users that single 'r' press refreshes all moved models
  - _Requirements: 14.1, 14.2, 14.5_

- [ ] 7.2 Create ComfyUI setup guide documentation
  - Add "Setup Guide" link in interface
  - Display modal/page with extra_model_paths.yaml configuration instructions
  - Include example configuration pointing to models/active/ directory
  - Explain how ComfyUI detects file changes on refresh
  - Provide troubleshooting steps for models not appearing
  - _Requirements: 14.3, 14.4_

- [ ] 8. Implement performance optimizations
- [ ] 8.1 Optimize frontend rendering performance
  - Memoize filter functions to prevent unnecessary recalculation
  - Optimize grid re-rendering with proper key props
  - Implement efficient state updates
  - Implement virtual scrolling or pagination for collections over 100 models
  - Ensure search filtering updates within 100ms
  - Maintain 60fps scrolling performance
  - _Requirements: 9.2, 9.3, 9.4, 9.5_

- [ ] 8.2 Optimize backend scanning performance
  - Use single-pass filesystem scan with case-insensitive extension filtering
  - Implement async I/O for file operations
  - Cache scan results in memory to avoid repeated filesystem access
  - Ensure scan completes within 5 seconds for 1000 models
  - Trigger automatic initial scan on first API request
  - _Requirements: 9.1, 10.1, 10.3_

- [ ] 9. Integration and end-to-end testing
- [ ] 9.1 Test complete user workflows
  - Test scan → view → search → filter workflow
  - Test model selection → move workflow
  - Test bulk operations workflow
  - Verify metadata display with various model types
  - Test error scenarios (missing files, insufficient space, file exists)
  - _Requirements: All requirements integration_

- [ ] 9.2 Validate cross-platform compatibility
  - Test path handling on Windows and Unix systems
  - Verify category detection works with different path separators
  - Test file operations across different filesystems
  - Validate preview image loading on various platforms
  - _Requirements: 1.2, 1.3, 11.6, 12.2_

- [ ] 9.3 Verify security and safety measures
  - Test path traversal protection in move operations
  - Verify disk space validation prevents failures
  - Confirm atomic file operations prevent corruption
  - Validate input sanitization in all API endpoints
  - Test concurrent operation handling
  - _Requirements: 12.9, 12.3, 12.4, 12.5, 12.6, 12.7_

## Implementation Notes

### Technology Stack
- Backend: Python 3.11+, FastAPI, Pydantic V2
- Frontend: React 18.2+, TypeScript 5.0+, Tailwind CSS, Radix UI, Framer Motion
- Testing: pytest with async support

### Development Approach
- Follow TDD methodology with comprehensive test coverage
- Implement backend endpoints before frontend integration
- Test each component independently before integration
- Use design.md as reference for implementation details

### Success Criteria
- All 14 requirements fully implemented and tested
- Cross-platform compatibility verified
- Performance targets met (scan <5s for 1000 models, API <200ms, search <100ms)
- Security measures validated (path traversal, disk space, atomic operations)
- Complete error handling and user feedback
- ComfyUI integration guidance provided
