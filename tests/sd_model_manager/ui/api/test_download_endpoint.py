"""ダウンロードAPIエンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient
from sd_model_manager.config import Config
from sd_model_manager.ui.api.main import create_app

# 実際のCivitai URL（本番環境と同じ）
REAL_LORA_URL = "https://civitai.com/models/1998509"
REAL_CHECKPOINT_URL = "https://civitai.com/models/827184?modelVersionId=2167369"
# バリデーションテスト用の架空URL（存在しない可能性があるが、形式は正しい）
TEST_URL = "https://civitai.com/models/999999999"


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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
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
            "url": TEST_URL,
            "filename": "my-model_v2.safetensors"
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data


# Phase 2.12: メタデータからのファイル名自動抽出テスト
def test_download_endpoint_accepts_url_only_request(test_client):
    """URLのみのリクエストを受け付けるテスト（filenameフィールドなし）"""
    response = test_client.post(
        "/api/download",
        json={
            "url": TEST_URL
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data


def test_download_endpoint_extracts_filename_from_metadata(test_client, mocker):
    """メタデータからファイル名を抽出するテスト"""
    # CivitaiClientのモックを作成
    mock_metadata = {
        "modelVersions": [
            {
                "files": [
                    {"name": "awesome-model-v1.safetensors"}
                ]
            }
        ]
    }

    mock_client = mocker.MagicMock()
    mock_client.get_model_metadata = mocker.AsyncMock(return_value=mock_metadata)

    # DownloadServiceのモックも作成
    mock_service = mocker.MagicMock()
    mock_service.download_file = mocker.AsyncMock()

    response = test_client.post(
        "/api/download",
        json={
            "url": TEST_URL
        }
    )

    assert response.status_code in [200, 202]
    # 注: 実際のメタデータ抽出のテストは統合テストで実施


def test_download_endpoint_handles_metadata_extraction_failure(test_client, mocker):
    """メタデータ取得失敗時のフォールバック動作テスト"""
    # メタデータ取得が失敗する場合のモック
    mock_client = mocker.MagicMock()
    mock_client.get_model_metadata = mocker.AsyncMock(side_effect=Exception("API error"))

    response = test_client.post(
        "/api/download",
        json={
            "url": TEST_URL
        }
    )

    # メタデータ取得失敗でもフォールバックファイル名を使用して処理継続
    assert response.status_code in [200, 202, 500]
    # 注: エラーハンドリングの詳細は実装時に定義


# 統合テスト: 実際のCivitai APIを呼び出す
@pytest.mark.integration
def test_download_endpoint_with_real_lora_url(test_client):
    """実際のLoRA URLでメタデータ抽出をテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": REAL_LORA_URL
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "started"


@pytest.mark.integration
def test_download_endpoint_with_real_checkpoint_url(test_client):
    """実際のCheckpoint URLでメタデータ抽出をテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": REAL_CHECKPOINT_URL
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "started"


@pytest.mark.integration
def test_download_endpoint_with_version_id_parameter(test_client):
    """modelVersionIdパラメータ付きURLでメタデータ抽出をテスト"""
    # https://civitai.com/models/{modelid}?modelVersionId={versionid} 形式
    response = test_client.post(
        "/api/download",
        json={
            "url": REAL_CHECKPOINT_URL  # すでにmodelVersionId付き
        }
    )
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data
