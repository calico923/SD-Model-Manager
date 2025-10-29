"""Pydantic モデルのテスト"""

import pytest
from datetime import datetime
from sd_model_manager.registry.models import LoraModel


def test_lora_model_creation():
    """LoraModel の基本的な生成テスト"""
    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors"
    )

    assert model.name == "test-lora"
    assert str(model.url) == "https://civitai.com/models/123/test-lora"
    assert model.file_path == "/path/to/models/loras/test-lora.safetensors"


def test_lora_model_with_optional_fields():
    """オプションフィールドを含む LoraModel のテスト"""
    downloaded_at = datetime.now()

    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors",
        description="Test description",
        image_url="https://example.com/image.jpg",
        downloaded_at=downloaded_at
    )

    assert model.description == "Test description"
    assert str(model.image_url) == "https://example.com/image.jpg"
    assert model.downloaded_at == downloaded_at


def test_lora_model_validation_error():
    """必須フィールド欠如時のバリデーションエラーテスト"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LoraModel(name="test-lora")  # url, file_path が欠如


def test_lora_model_url_validation():
    """URL フォーマットバリデーションのテスト"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LoraModel(
            name="test-lora",
            url="invalid-url",  # 不正な URL
            file_path="/path/to/lora.safetensors"
        )


def test_lora_model_supports_safetensors():
    """safetensors 拡張子をサポート"""
    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors"
    )
    assert model.file_path.endswith('.safetensors')
