"""Civitai API クライアントのテスト"""

import pytest
from unittest.mock import AsyncMock, patch
from sd_model_manager.download.civitai_client import CivitaiClient
from sd_model_manager.lib.errors import DownloadError


@pytest.fixture
def civitai_client():
    """CivitaiClient フィクスチャ"""
    return CivitaiClient(api_key=None)


@pytest.mark.asyncio
async def test_extract_model_id_from_url(civitai_client):
    """Civitai URL からモデル ID を抽出するテスト"""
    url = "https://civitai.com/models/123456/test-lora"
    model_id = civitai_client.extract_model_id(url)

    assert model_id == "123456"


@pytest.mark.asyncio
async def test_extract_model_id_from_direct_id(civitai_client):
    """直接モデル ID を渡した場合のテスト"""
    model_id = civitai_client.extract_model_id("123456")

    assert model_id == "123456"


@pytest.mark.asyncio
async def test_extract_model_id_invalid_url(civitai_client):
    """無効な URL の場合のテスト"""
    with pytest.raises(DownloadError):
        civitai_client.extract_model_id("invalid-url")


@pytest.mark.asyncio
async def test_get_model_metadata(civitai_client):
    """モデルメタデータ取得のテスト"""
    # モックレスポンス
    mock_response = {
        "id": 123456,
        "name": "Test LoRA",
        "description": "Test description",
        "type": "LORA",
        "modelVersions": [
            {
                "id": 1,
                "name": "v1.0",
                "downloadUrl": "https://civitai.com/api/download/models/1",
                "files": [
                    {
                        "name": "test-lora.safetensors",
                        "sizeKB": 144000,
                        "type": "Model"
                    }
                ],
                "images": [
                    {
                        "url": "https://example.com/image.jpg"
                    }
                ]
            }
        ]
    }

    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(return_value=mock_response)):
        metadata = await civitai_client.get_model_metadata("123456")

        assert metadata["id"] == 123456
        assert metadata["name"] == "Test LoRA"
        assert metadata["type"] == "LORA"
        assert len(metadata["modelVersions"]) > 0


@pytest.mark.asyncio
async def test_get_download_url(civitai_client):
    """ダウンロード URL 取得のテスト"""
    # Phase 2.16: files配列内にdownloadUrlを配置（実際のCivitai APIレスポンスに合わせて修正）
    mock_response = {
        "modelVersions": [
            {
                "files": [
                    {
                        "name": "test-lora.safetensors",
                        "type": "Model",
                        "primary": True,
                        "downloadUrl": "https://civitai.com/api/download/models/1"
                    }
                ]
            }
        ]
    }

    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(return_value=mock_response)):
        download_url = await civitai_client.get_download_url("123456")

        assert download_url == "https://civitai.com/api/download/models/1"


@pytest.mark.asyncio
async def test_get_model_metadata_api_error(civitai_client):
    """API エラー時のテスト"""
    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(side_effect=DownloadError("API Error"))):
        with pytest.raises(DownloadError):
            await civitai_client.get_model_metadata("123456")
