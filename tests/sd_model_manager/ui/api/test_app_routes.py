"""アプリケーション全体のルーティング挙動を検証する結合テスト"""

from fastapi.testclient import TestClient

from sd_model_manager.ui.api.main import create_app


def test_health_endpoint_via_app():
    """create_app で組み上げた FastAPI でも /health が動作する"""
    app = create_app()
    client = TestClient(app)

    response = client.get("/health")
    assert response.status_code == 200

    payload = response.json()
    assert payload["status"] == "ok"
    assert "timestamp" in payload
