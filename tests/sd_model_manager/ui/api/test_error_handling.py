"""FastAPI エラーハンドリングのテスト"""

import pytest
from fastapi.testclient import TestClient
from sd_model_manager.ui.api.main import create_app


@pytest.fixture
def client():
    """TestClient フィクスチャ（create_app ファクトリ経由）"""
    app = create_app()
    return TestClient(app)


def test_404_error_handler(client):
    """存在しないエンドポイントのテスト"""
    response = client.get("/nonexistent")

    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "NOT_FOUND"
