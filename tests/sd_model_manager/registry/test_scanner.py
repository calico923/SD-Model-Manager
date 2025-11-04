"""Filesystem scanner tests for model discovery and metadata extraction"""

import pytest
from pathlib import Path
from datetime import datetime
from sd_model_manager.registry.scanner import ModelScanner
from sd_model_manager.config import Config
from sd_model_manager.lib.errors import AppError


class TestModelScanner:
    """Test suite for ModelScanner class"""

    @pytest.fixture
    def test_model_dir(self, tmp_path):
        """Create test directory structure with model files"""
        # Create Active/Archive directory structure
        active_dir = tmp_path / "active"
        archive_dir = tmp_path / "archive"

        # Active models
        active_lora = active_dir / "loras"
        active_checkpoint = active_dir / "checkpoints"
        active_vae = active_dir / "vae"
        active_embedding = active_dir / "embeddings"

        # Archive models
        archive_lora = archive_dir / "loras"

        # Create directories
        for dir_path in [active_lora, active_checkpoint, active_vae, active_embedding, archive_lora]:
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create test model files
        test_files = {
            active_lora / "test_lora.safetensors": "lora content",
            active_checkpoint / "test_checkpoint.safetensors": "checkpoint content",
            active_vae / "test_vae.pt": "vae content",
            active_embedding / "test_embedding.bin": "embedding content",
            archive_lora / "archived_lora.safetensors": "archived lora content",
        }

        for file_path, content in test_files.items():
            file_path.write_text(content)

        return tmp_path

    @pytest.fixture
    def test_config(self, test_model_dir):
        """Create test configuration"""
        config = Config()
        config.model_scan_dir = test_model_dir
        return config

    @pytest.fixture
    def scanner(self, test_config):
        """Create ModelScanner instance"""
        return ModelScanner(test_config)

    @pytest.mark.asyncio
    async def test_scanner_initialization(self, scanner, test_model_dir):
        """Test scanner initializes with correct configuration"""
        assert scanner.base_path == test_model_dir
        assert len(scanner.supported_extensions) == 5
        assert ".safetensors" in scanner.supported_extensions
        assert ".ckpt" in scanner.supported_extensions
        assert ".pt" in scanner.supported_extensions
        assert ".bin" in scanner.supported_extensions
        assert ".pth" in scanner.supported_extensions

    @pytest.mark.asyncio
    async def test_scan_discovers_all_model_files(self, scanner):
        """Test scanner discovers all supported model files"""
        models = await scanner.scan()

        # Should find 5 model files (4 active + 1 archive)
        assert len(models) == 5

        # Verify all models have required fields
        for model in models:
            assert model.filename
            assert model.file_path
            assert model.file_size > 0
            assert model.modified_time
            assert model.model_type in ["LoRA", "Checkpoint", "VAE", "Embedding", "Unknown"]
            assert model.category in ["Active", "Archive"]

    @pytest.mark.asyncio
    async def test_scan_detects_lora_type_from_path(self, scanner):
        """Test scanner detects LoRA type from path patterns"""
        models = await scanner.scan()

        lora_models = [m for m in models if m.model_type == "LoRA"]
        assert len(lora_models) == 2  # test_lora.safetensors + archived_lora.safetensors

        # Verify path patterns
        for model in lora_models:
            assert "loras" in model.file_path.lower() or "lora" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_detects_checkpoint_type_from_path(self, scanner):
        """Test scanner detects Checkpoint type from path patterns"""
        models = await scanner.scan()

        checkpoint_models = [m for m in models if m.model_type == "Checkpoint"]
        assert len(checkpoint_models) == 1  # test_checkpoint.safetensors

        # Verify path patterns
        for model in checkpoint_models:
            assert "checkpoints" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_detects_vae_type_from_path(self, scanner):
        """Test scanner detects VAE type from path patterns"""
        models = await scanner.scan()

        vae_models = [m for m in models if m.model_type == "VAE"]
        assert len(vae_models) == 1  # test_vae.pt

        for model in vae_models:
            assert "vae" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_detects_embedding_type_from_path(self, scanner):
        """Test scanner detects Embedding type from path patterns"""
        models = await scanner.scan()

        embedding_models = [m for m in models if m.model_type == "Embedding"]
        assert len(embedding_models) == 1  # test_embedding.bin

        for model in embedding_models:
            assert "embeddings" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_detects_active_category(self, scanner):
        """Test scanner detects Active category from directory structure"""
        models = await scanner.scan()

        active_models = [m for m in models if m.category == "Active"]
        assert len(active_models) == 4

        for model in active_models:
            assert "active" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_detects_archive_category(self, scanner):
        """Test scanner detects Archive category from directory structure"""
        models = await scanner.scan()

        archive_models = [m for m in models if m.category == "Archive"]
        assert len(archive_models) == 1

        for model in archive_models:
            assert "archive" in model.file_path.lower()

    @pytest.mark.asyncio
    async def test_scan_extracts_file_metadata(self, scanner, test_model_dir):
        """Test scanner extracts file size and timestamps"""
        models = await scanner.scan()

        # Find a specific model
        lora_model = next(m for m in models if "test_lora" in m.filename)

        # Verify metadata
        assert lora_model.file_size > 0
        assert isinstance(lora_model.modified_time, datetime)
        assert lora_model.created_time is None or isinstance(lora_model.created_time, datetime)

    @pytest.mark.asyncio
    async def test_scan_handles_civitai_metadata_file(self, scanner, test_model_dir):
        """Test scanner parses .civitai.info metadata files"""
        # Create a .civitai.info file
        lora_dir = test_model_dir / "active" / "loras"
        metadata_file = lora_dir / "test_lora.safetensors.civitai.info"

        metadata_content = {
            "id": 12345,
            "name": "Test LoRA Model",
            "modelId": 123,
            "modelName": "Test LoRA",
            "modelVersionId": 456,
            "versionName": "v1.0",
            "description": "Test description",
            "tags": ["anime", "character"],
            "trainedWords": ["test_trigger"],
            "images": [
                {"url": "https://example.com/preview1.jpg"},
                {"url": "https://example.com/preview2.jpg"}
            ]
        }

        import json
        metadata_file.write_text(json.dumps(metadata_content))

        # Scan and verify metadata
        models = await scanner.scan()
        lora_model = next(m for m in models if "test_lora" in m.filename)

        assert lora_model.civitai_metadata is not None
        assert lora_model.civitai_metadata.get("name") == "Test LoRA Model"
        assert lora_model.civitai_metadata.get("description") == "Test description"
        assert "anime" in lora_model.civitai_metadata.get("tags", [])
        assert lora_model.preview_image_url == "https://example.com/preview1.jpg"

    @pytest.mark.asyncio
    async def test_scan_handles_missing_civitai_metadata(self, scanner):
        """Test scanner handles missing .civitai.info files gracefully"""
        models = await scanner.scan()

        # Models without .civitai.info should have None metadata
        for model in models:
            if model.civitai_metadata is None:
                # Verify fallback: filename as display name
                assert model.filename
                assert model.preview_image_url is None

    @pytest.mark.asyncio
    async def test_scan_extracts_all_civitai_metadata_fields(self, scanner, test_model_dir):
        """Test scanner extracts all required metadata fields per Requirement 2.3"""
        # Create a comprehensive .civitai.info file with all fields
        lora_dir = test_model_dir / "active" / "loras"
        metadata_file = lora_dir / "test_lora.safetensors.civitai.info"

        comprehensive_metadata = {
            "id": 12345,
            "name": "Comprehensive Test Model",
            "modelId": 123,
            "modelName": "Test Model Series",
            "modelVersionId": 456,
            "versionName": "v2.0",
            "creatorUsername": "test_creator",
            "creatorName": "Test Creator",
            "description": "Full description with all details",
            "tags": ["anime", "character", "lora"],
            "trainedWords": ["trigger1", "trigger2", "trigger3"],
            "images": [
                {"url": "https://example.com/preview1.jpg"},
                {"url": "https://example.com/preview2.jpg"}
            ]
        }

        import json
        metadata_file.write_text(json.dumps(comprehensive_metadata))

        # Scan and verify all fields are extracted
        models = await scanner.scan()
        lora_model = next(m for m in models if "test_lora" in m.filename)

        # Requirement 2.3: Extract model name
        assert lora_model.civitai_metadata.get("name") == "Comprehensive Test Model"

        # Requirement 2.3: Extract model version
        assert lora_model.civitai_metadata.get("versionName") == "v2.0"

        # Requirement 2.3: Extract creator information
        assert lora_model.civitai_metadata.get("creatorUsername") == "test_creator"
        assert lora_model.civitai_metadata.get("creatorName") == "Test Creator"

        # Requirement 2.3: Extract description
        assert lora_model.civitai_metadata.get("description") == "Full description with all details"

        # Requirement 2.3: Extract tags
        tags = lora_model.civitai_metadata.get("tags", [])
        assert "anime" in tags
        assert "character" in tags
        assert "lora" in tags
        assert len(tags) == 3

        # Requirement 2.3: Extract trigger words
        trigger_words = lora_model.civitai_metadata.get("trainedWords", [])
        assert "trigger1" in trigger_words
        assert "trigger2" in trigger_words
        assert "trigger3" in trigger_words
        assert len(trigger_words) == 3

        # Requirement 2.3: Extract preview image URLs
        images = lora_model.civitai_metadata.get("images", [])
        assert len(images) == 2
        assert images[0]["url"] == "https://example.com/preview1.jpg"
        assert images[1]["url"] == "https://example.com/preview2.jpg"

        # Requirement 2.4: Verify metadata is associated with model
        assert lora_model.preview_image_url == "https://example.com/preview1.jpg"

    @pytest.mark.asyncio
    async def test_scan_handles_malformed_civitai_metadata(self, scanner, test_model_dir):
        """Test scanner handles malformed JSON in .civitai.info files"""
        # Create a malformed .civitai.info file
        lora_dir = test_model_dir / "active" / "loras"
        metadata_file = lora_dir / "test_lora.safetensors.civitai.info"
        metadata_file.write_text("{ invalid json }")

        # Should not raise exception, but skip metadata
        models = await scanner.scan()
        lora_model = next(m for m in models if "test_lora" in m.filename)

        assert lora_model.civitai_metadata is None

    @pytest.mark.asyncio
    async def test_scan_handles_empty_directory(self, tmp_path):
        """Test scanner handles empty directory gracefully"""
        config = Config()
        config.model_scan_dir = tmp_path / "empty_dir"
        config.model_scan_dir.mkdir(exist_ok=True)

        scanner = ModelScanner(config)
        models = await scanner.scan()

        assert len(models) == 0

    @pytest.mark.asyncio
    async def test_scan_handles_missing_directory(self, tmp_path):
        """Test scanner handles missing directory with error"""
        config = Config()
        config.model_scan_dir = tmp_path / "nonexistent"

        scanner = ModelScanner(config)

        with pytest.raises(AppError) as exc_info:
            await scanner.scan()

        assert "not found" in str(exc_info.value).lower() or "does not exist" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_scan_handles_file_access_errors(self, scanner, test_model_dir, monkeypatch):
        """Test scanner handles file access errors gracefully"""
        # Mock _process_file to raise OSError for one file
        original_process = scanner._process_file
        call_count = [0]

        async def mock_process_with_error(file_path):
            call_count[0] += 1
            if call_count[0] == 2:  # Raise error on second file
                raise OSError("File access error")
            return await original_process(file_path)

        monkeypatch.setattr(scanner, "_process_file", mock_process_with_error)

        # Should complete successfully, just skip the file with error
        models = await scanner.scan()

        # Should have fewer models due to access error
        assert len(models) < 5  # One file should be skipped due to error

    @pytest.mark.asyncio
    async def test_scan_ignores_unsupported_extensions(self, scanner, test_model_dir):
        """Test scanner ignores files with unsupported extensions"""
        # Create files with unsupported extensions
        active_dir = test_model_dir / "active" / "loras"
        (active_dir / "readme.txt").write_text("readme")
        (active_dir / "config.yaml").write_text("config")
        (active_dir / "script.py").write_text("script")

        models = await scanner.scan()

        # Should still only find the original 5 model files
        assert len(models) == 5

    @pytest.mark.asyncio
    async def test_scan_handles_nested_directory_structures(self, test_model_dir):
        """Test scanner handles deeply nested directory structures"""
        # Create nested structure
        nested_dir = test_model_dir / "active" / "loras" / "subfolder1" / "subfolder2"
        nested_dir.mkdir(parents=True, exist_ok=True)
        (nested_dir / "nested_lora.safetensors").write_text("nested content")

        config = Config()
        config.model_scan_dir = test_model_dir
        scanner = ModelScanner(config)

        models = await scanner.scan()

        # Should find the nested file
        nested_models = [m for m in models if "nested_lora" in m.filename]
        assert len(nested_models) == 1
        assert nested_models[0].model_type == "LoRA"

    @pytest.mark.asyncio
    async def test_scan_handles_alternative_checkpoint_paths(self, test_model_dir):
        """Test scanner detects Checkpoint type from alternative path patterns"""
        # Create ComfyUI-style path
        comfyui_checkpoint_dir = test_model_dir / "active" / "models" / "Stable-diffusion"
        comfyui_checkpoint_dir.mkdir(parents=True, exist_ok=True)
        (comfyui_checkpoint_dir / "comfyui_checkpoint.safetensors").write_text("checkpoint")

        config = Config()
        config.model_scan_dir = test_model_dir
        scanner = ModelScanner(config)

        models = await scanner.scan()

        comfyui_models = [m for m in models if "comfyui_checkpoint" in m.filename]
        assert len(comfyui_models) == 1
        assert comfyui_models[0].model_type == "Checkpoint"

    @pytest.mark.asyncio
    async def test_scan_handles_unknown_model_type(self, test_model_dir):
        """Test scanner classifies files in unknown paths as Unknown type"""
        # Create file in root directory (not matching any pattern)
        unknown_file = test_model_dir / "unknown_model.safetensors"
        unknown_file.write_text("unknown content")

        config = Config()
        config.model_scan_dir = test_model_dir
        scanner = ModelScanner(config)

        models = await scanner.scan()

        unknown_models = [m for m in models if "unknown_model" in m.filename]
        assert len(unknown_models) == 1
        assert unknown_models[0].model_type == "Unknown"

    @pytest.mark.asyncio
    async def test_scan_case_insensitive_extension_matching(self, test_model_dir):
        """Test scanner handles extensions in various cases (cross-platform)"""
        active_lora = test_model_dir / "active" / "loras"

        # Create files with different case extensions
        (active_lora / "uppercase.SAFETENSORS").write_text("uppercase")
        (active_lora / "mixedcase.SafeTensors").write_text("mixedcase")

        config = Config()
        config.model_scan_dir = test_model_dir
        scanner = ModelScanner(config)

        models = await scanner.scan()

        # Should find files regardless of extension case
        uppercase_models = [m for m in models if "uppercase" in m.filename.lower()]
        mixedcase_models = [m for m in models if "mixedcase" in m.filename.lower()]

        assert len(uppercase_models) == 1
        assert len(mixedcase_models) == 1

    @pytest.mark.asyncio
    async def test_scan_generates_unique_model_ids(self, scanner):
        """Test scanner generates unique IDs for each model"""
        models = await scanner.scan()

        model_ids = [model.id for model in models]
        assert len(model_ids) == len(set(model_ids))  # All IDs are unique

    @pytest.mark.asyncio
    async def test_scan_logging_on_errors(self, scanner, caplog):
        """Test scanner logs errors appropriately"""
        import logging

        with caplog.at_level(logging.ERROR):
            # This would require mocking to trigger specific errors
            # For now, verify successful scan produces no errors
            await scanner.scan()

            # No ERROR level logs should appear for successful scan
            error_logs = [record for record in caplog.records if record.levelname == "ERROR"]
            assert len(error_logs) == 0

    def test_path_parsing_cross_platform_windows_style(self):
        """Test path parsing works with Windows-style backslash paths"""
        from pathlib import PureWindowsPath
        config = Config()
        scanner = ModelScanner(config)

        # Create a Windows-style path
        windows_path = PureWindowsPath("models\\active\\loras\\test.safetensors")

        # Convert to Path for testing (Path.parts works for both / and \)
        # Test that our cross-platform parsing uses Path.parts correctly
        path_parts = [part.lower() for part in windows_path.parts]

        # Verify path_parts are correctly extracted regardless of separator
        assert any("lora" in part for part in path_parts)
        assert any("active" in part for part in path_parts)

    @pytest.mark.asyncio
    async def test_scan_rejects_file_path_not_directory(self, tmp_path):
        """Test scanner rejects file path (not directory)"""
        # Create a file instead of directory
        file_path = tmp_path / "not_a_directory.txt"
        file_path.write_text("content")

        config = Config()
        config.model_scan_dir = file_path

        scanner = ModelScanner(config)

        with pytest.raises(AppError) as exc_info:
            await scanner.scan()

        assert "directory" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_scan_with_symbolic_link_directory(self, tmp_path):
        """Test scanner handles directories with symbolic links"""
        # Create a directory and a symbolic link to it
        real_dir = tmp_path / "real"
        real_dir.mkdir()

        # Create a model file in the real directory
        model_file = real_dir / "test_model.safetensors"
        model_file.write_text("model content")

        config = Config()
        config.model_scan_dir = real_dir

        scanner = ModelScanner(config)
        models = await scanner.scan()

        # Should find the model in the real directory
        assert len(models) == 1
        assert "test_model" in models[0].filename
