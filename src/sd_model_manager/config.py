"""設定管理モジュール"""

from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """アプリケーション設定クラス"""

    # Civitai API
    civitai_api_key: Optional[str] = None

    # Download settings
    download_dir: Path = Path("./downloads")
    max_concurrent_downloads: int = 1

    # Server settings
    host: str = "127.0.0.1"
    port: int = 8188

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def ensure_download_dir(self) -> None:
        """ダウンロードディレクトリが存在することを保証"""
        self.download_dir.mkdir(parents=True, exist_ok=True)
