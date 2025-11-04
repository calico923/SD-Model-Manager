"""Pydantic データモデル定義"""

from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, HttpUrl, field_validator
import uuid


class LoraModel(BaseModel):
    """LoRA モデルのデータモデル"""

    name: str
    url: HttpUrl
    file_path: str
    description: Optional[str] = None
    image_url: Optional[HttpUrl] = None
    downloaded_at: Optional[datetime] = None

    @field_validator('file_path')
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """ファイルパスが有効な拡張子で終わることを検証

        MVP では .safetensors のみをサポート。
        将来的に .ckpt, .pt, .bin 等を追加予定（Phase 2+）
        """
        supported_extensions = ('.safetensors',)  # 将来拡張用

        if not any(v.endswith(ext) for ext in supported_extensions):
            raise ValueError(
                f'LoRA file must have one of {supported_extensions} extension'
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "name": "example-lora",
                    "url": "https://civitai.com/models/12345/example-lora",
                    "file_path": "/models/loras/example-lora.safetensors",
                    "description": "Example LoRA model",
                    "image_url": "https://example.com/preview.jpg"
                }
            ]
        }
    }


class ModelInfo(BaseModel):
    """Model file information from filesystem scan"""

    id: str
    filename: str
    file_path: str
    file_size: int  # bytes
    model_type: Literal["LoRA", "Checkpoint", "VAE", "Embedding", "Unknown"]
    category: Literal["Active", "Archive"]
    modified_time: datetime
    created_time: Optional[datetime] = None
    civitai_metadata: Optional[dict] = None
    preview_image_url: Optional[str] = None

    @classmethod
    def from_file_path(
        cls,
        file_path: str,
        model_type: str,
        category: str,
        file_size: int,
        modified_time: datetime,
        created_time: Optional[datetime] = None,
        civitai_metadata: Optional[dict] = None,
        preview_image_url: Optional[str] = None
    ) -> "ModelInfo":
        """Create ModelInfo from file path and metadata"""
        from pathlib import Path

        path = Path(file_path)
        filename = path.name

        return cls(
            id=str(uuid.uuid4()),
            filename=filename,
            file_path=str(file_path),
            file_size=file_size,
            model_type=model_type,
            category=category,
            modified_time=modified_time,
            created_time=created_time,
            civitai_metadata=civitai_metadata,
            preview_image_url=preview_image_url
        )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "123e4567-e89b-12d3-a456-426614174000",
                    "filename": "example-lora.safetensors",
                    "file_path": "/models/active/loras/example-lora.safetensors",
                    "file_size": 144000000,
                    "model_type": "LoRA",
                    "category": "Active",
                    "modified_time": "2024-01-01T12:00:00",
                    "created_time": "2024-01-01T10:00:00",
                    "civitai_metadata": {
                        "name": "Example LoRA",
                        "description": "Test model"
                    },
                    "preview_image_url": "https://example.com/preview.jpg"
                }
            ]
        }
    }
