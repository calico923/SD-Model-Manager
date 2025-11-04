"""Filesystem scanner for Stable Diffusion model files"""

import asyncio
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import AsyncIterator

from sd_model_manager.config import Config
from sd_model_manager.lib.errors import AppError
from sd_model_manager.registry.models import ModelInfo

logger = logging.getLogger(__name__)


class ModelScanError(AppError):
    """Model scanning error"""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message, code="MODEL_SCAN_ERROR", details=details)


class ModelScanner:
    """Scans filesystem for Stable Diffusion model files"""

    def __init__(self, config: Config):
        """Initialize scanner with configuration

        Args:
            config: Application configuration with model_scan_dir
        """
        self.config = config
        self.base_path = Path(config.model_scan_dir)
        self.supported_extensions = {".safetensors", ".ckpt", ".pt", ".pth", ".bin"}

        # Model type detection patterns (case-insensitive)
        self.type_patterns = {
            "LoRA": ["loras", "lora"],
            "Checkpoint": ["checkpoints", "stable-diffusion"],
            "VAE": ["vae"],
            "Embedding": ["embeddings"],
        }

        # Category detection patterns (case-insensitive)
        self.category_patterns = {
            "Active": ["active"],
            "Archive": ["archive"],
        }

    async def scan(self) -> list[ModelInfo]:
        """Scan model directory and return list of discovered models

        Returns:
            List of ModelInfo objects for all discovered model files

        Raises:
            ModelScanError: If directory does not exist or cannot be accessed
        """
        if not self.base_path.exists():
            raise ModelScanError(
                f"Model directory not found: {self.base_path}",
                details={"path": str(self.base_path)}
            )

        logger.info("Starting model scan in directory: %s", self.base_path)

        models = []
        async for file_path in self._scan_files():
            try:
                model_info = await self._process_file(file_path)
                models.append(model_info)
            except Exception as e:
                # Log error but continue scanning
                logger.error(
                    "Error processing file %s: %s",
                    file_path,
                    str(e),
                    exc_info=True
                )

        logger.info("Model scan completed. Found %d models", len(models))
        return models

    async def _scan_files(self) -> AsyncIterator[Path]:
        """Async generator for filesystem traversal

        Yields:
            Path objects for files matching supported extensions
        """

        def scan_sync():
            """Synchronous filesystem traversal"""
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
        """Process a single model file and extract metadata

        Args:
            file_path: Path to model file

        Returns:
            ModelInfo object with extracted metadata
        """
        # Get file stats
        stat = file_path.stat()
        file_size = stat.st_size
        modified_time = datetime.fromtimestamp(stat.st_mtime)

        # Try to get created time (platform-dependent)
        try:
            created_time = datetime.fromtimestamp(stat.st_birthtime)
        except AttributeError:
            # birthtime not available on this platform (e.g., Linux)
            created_time = None

        # Detect model type and category from path
        model_type = self._detect_model_type(file_path)
        category = self._detect_category(file_path)

        # Parse Civitai metadata if available
        civitai_metadata = await self._parse_civitai_metadata(file_path)

        # Extract preview image URL from metadata
        preview_image_url = self._extract_preview_image_url(civitai_metadata)

        return ModelInfo.from_file_path(
            file_path=str(file_path),
            model_type=model_type,
            category=category,
            file_size=file_size,
            modified_time=modified_time,
            created_time=created_time,
            civitai_metadata=civitai_metadata,
            preview_image_url=preview_image_url
        )

    def _detect_model_type(self, file_path: Path) -> str:
        """Detect model type from file path patterns

        Args:
            file_path: Path to model file

        Returns:
            Model type string (LoRA, Checkpoint, VAE, Embedding, Unknown)
        """
        path_str = str(file_path).lower()

        # Check patterns in specific order to avoid false positives
        # More specific patterns should be checked first

        # Split path into parts for more accurate matching
        path_parts = path_str.split("/")

        # Check for exact directory name matches
        for model_type, patterns in self.type_patterns.items():
            for pattern in patterns:
                # Check if pattern appears as a complete directory name
                if pattern in path_parts:
                    return model_type
                # Also check for pattern at end of directory name (e.g., "my_loras" contains "loras")
                for part in path_parts:
                    if part.endswith(pattern):
                        return model_type

        return "Unknown"

    def _detect_category(self, file_path: Path) -> str:
        """Detect category from directory structure

        Args:
            file_path: Path to model file

        Returns:
            Category string (Active or Archive)
        """
        path_str = str(file_path).lower()
        path_parts = path_str.split("/")

        # Check for archive first (more specific)
        # Use exact directory name match to avoid false positives
        for pattern in self.category_patterns["Archive"]:
            if pattern in path_parts:
                return "Archive"

        # Check for active
        for pattern in self.category_patterns["Active"]:
            if pattern in path_parts:
                return "Active"

        # Default to Active if no pattern matches
        return "Active"

    async def _parse_civitai_metadata(self, file_path: Path) -> dict | None:
        """Parse .civitai.info metadata file if it exists

        Args:
            file_path: Path to model file

        Returns:
            Parsed JSON metadata dict or None if file doesn't exist or is invalid
        """
        # Construct .civitai.info file path
        metadata_path = file_path.parent / f"{file_path.name}.civitai.info"

        if not metadata_path.exists():
            return None

        try:
            # Read and parse JSON
            loop = asyncio.get_event_loop()
            content = await loop.run_in_executor(None, metadata_path.read_text, "utf-8")
            metadata = json.loads(content)
            return metadata
        except (json.JSONDecodeError, OSError) as e:
            # Log warning but don't fail the scan
            logger.warning(
                "Failed to parse Civitai metadata for %s: %s",
                file_path.name,
                str(e)
            )
            return None

    def _extract_preview_image_url(self, civitai_metadata: dict | None) -> str | None:
        """Extract primary preview image URL from Civitai metadata

        Args:
            civitai_metadata: Parsed Civitai metadata dict

        Returns:
            URL string of first preview image or None
        """
        if not civitai_metadata:
            return None

        # Try to get first image URL
        images = civitai_metadata.get("images", [])
        if images and len(images) > 0:
            first_image = images[0]
            if isinstance(first_image, dict):
                return first_image.get("url")

        return None
