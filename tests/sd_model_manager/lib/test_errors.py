"""エラーハンドリングのテスト"""

import pytest
from sd_model_manager.lib.errors import (
    AppError,
    ConfigurationError,
    DownloadError,
    ModelValidationError
)


def test_app_error_base_class():
    """AppError 基底クラスのテスト"""
    error = AppError("Test error message", code="TEST_ERROR")

    assert str(error) == "Test error message"
    assert error.code == "TEST_ERROR"
    assert error.details is None


def test_configuration_error():
    """ConfigurationError のテスト"""
    error = ConfigurationError(
        "Invalid API key",
        details={"key": "CIVITAI_API_KEY"}
    )

    assert error.code == "CONFIGURATION_ERROR"
    assert error.details["key"] == "CIVITAI_API_KEY"


def test_download_error():
    """DownloadError のテスト"""
    error = DownloadError(
        "Download failed",
        details={"url": "https://example.com/model.safetensors"}
    )

    assert error.code == "DOWNLOAD_ERROR"


def test_model_validation_error():
    """ModelValidationError のテスト"""
    error = ModelValidationError(
        "Invalid model data",
        details={"field": "url", "value": "invalid-url"}
    )

    assert error.code == "MODEL_VALIDATION_ERROR"
