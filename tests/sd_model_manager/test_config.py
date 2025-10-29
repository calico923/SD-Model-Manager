"""Config 管理クラスのテスト"""

import pytest
from pathlib import Path
from sd_model_manager.config import Config


def test_config_loads_from_env_file(tmp_path):
    """環境変数ファイルから設定を読み込むテスト"""
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CIVITAI_API_KEY=test_api_key_12345\n"
        "DOWNLOAD_DIR=/custom/download/path\n"
        "MAX_CONCURRENT_DOWNLOADS=3\n"
    )

    config = Config(_env_file=env_file)

    assert config.civitai_api_key == "test_api_key_12345"
    assert config.download_dir == Path("/custom/download/path")
    assert config.max_concurrent_downloads == 3


def test_config_default_values():
    """デフォルト値が正しく設定されるテスト"""
    config = Config(_env_file=None)  # .env なし

    assert config.download_dir == Path("./downloads")
    assert config.max_concurrent_downloads == 1
    assert config.host == "127.0.0.1"
    assert config.port == 8188


def test_config_validates_download_dir(tmp_path):
    """download_dir が存在しない場合は作成されるテスト"""
    env_file = tmp_path / ".env"
    download_dir = tmp_path / "new_downloads"

    env_file.write_text(f"DOWNLOAD_DIR={download_dir}\n")

    config = Config(_env_file=env_file)
    config.ensure_download_dir()

    assert download_dir.exists()
    assert download_dir.is_dir()
