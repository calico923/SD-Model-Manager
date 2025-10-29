"""Pydantic データモデル定義"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator


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
