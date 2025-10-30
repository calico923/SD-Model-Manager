"""ダウンロードAPIエンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient
from sd_model_manager.config import Config
from sd_model_manager.ui.api.main import create_app


@pytest.fixture
def test_client():
    config = Config()
    app = create_app(config)
    return TestClient(app)


def test_download_endpoint_accepts_post(test_client):
    """ダウンロードエンドポイントがPOSTを受け付けるテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "test-model.safetensors"
        }
    )
    assert response.status_code in [200, 202]


def test_download_endpoint_validates_url(test_client):
    """無効なURLの場合のバリデーションテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "invalid-url",
            "filename": "test-model.safetensors"
        }
    )
    assert response.status_code == 422


def test_download_endpoint_returns_task_id(test_client):
    """ダウンロードタスクIDを返すテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "test-model.safetensors"
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data


# セキュリティテスト: パストラバーサル攻撃の防止
def test_download_endpoint_rejects_path_traversal_dotdot(test_client):
    """パストラバーサル攻撃（..）を拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "../../etc/passwd"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_download_endpoint_rejects_absolute_path(test_client):
    """絶対パスを拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "/etc/passwd"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_download_endpoint_rejects_directory_separator(test_client):
    """ディレクトリセパレータを含むファイル名を拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "path/to/file.safetensors"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_download_endpoint_rejects_windows_path(test_client):
    """Windowsパスを拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "C:\\Windows\\System32\\config"
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_download_endpoint_rejects_empty_filename(test_client):
    """空のファイル名を拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": ""
        }
    )
    assert response.status_code == 400
    assert "detail" in response.json()


def test_download_endpoint_accepts_safe_filename(test_client):
    """安全なファイル名を受け入れるテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "my-model_v2.safetensors"
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data
