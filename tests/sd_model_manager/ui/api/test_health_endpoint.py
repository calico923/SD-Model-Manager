"""FastAPI エンドポイントのテスト"""

import pytest
from fastapi.testclient import TestClient
from sd_model_manager.ui.api.main import create_app


@pytest.fixture
def client():
    """TestClient フィクスチャ（create_app ファクトリ経由）"""
    app = create_app()
    return TestClient(app)


def test_health_endpoint_returns_200(client):
    """GET /health が 200 を返すテスト"""
    response = client.get("/health")

    assert response.status_code == 200


def test_health_endpoint_returns_correct_json(client):
    """GET /health が正しい JSON を返すテスト"""
    response = client.get("/health")
    data = response.json()

    assert data["status"] == "ok"
    assert "timestamp" in data
