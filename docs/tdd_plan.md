# TDD 駆動開発計画（Phase 1: 基盤システム構築）

## 概要

wada 式 TDD（テスト駆動開発）で SD-Model-Manager の Phase 1 を実装します。

**TDD の原則**:
- 🔴 **RED**: まずテストを書く（失敗することを確認）
- 🟢 **GREEN**: 最小限の実装でテストをパスさせる
- 🔵 **REFACTOR**: コードを整理・改善（テストは通ったまま）

**タスク粒度**: 各タスク 30分〜2時間程度の最小単位

---

## タスク一覧

| # | タスク | 種別 | 所要時間 |
|---|--------|------|---------|
| 1.1 | プロジェクト環境セットアップ | 環境構築 | 1-2h |
| 1.2 | pytest 環境構築とサンプルテスト | TDD | 30min |
| 1.3 | Pydantic 基本モデル（LoraModel）のテスト作成 | TDD (RED) | 30min |
| 1.4 | LoraModel 実装 | TDD (GREEN) | 30min |
| 1.5 | Config 管理クラスのテスト作成 | TDD (RED) | 30min |
| 1.6 | Config 実装（.env 読み込み） | TDD (GREEN) | 1h |
| 1.7 | FastAPI 最小アプリのテスト作成 | TDD (RED) | 30min |
| 1.8 | FastAPI 実装（health endpoint） | TDD (GREEN) | 1h |
| 1.9 | エラーハンドラーのテスト作成 | TDD (RED) | 30min |
| 1.10 | エラーハンドラー実装 | TDD (GREEN) | 1h |
| 1.11 | API ルータ結合テスト（`/health`） | TDD (REFACTOR) | 30min |

**合計**: 約 8-11 時間

---

## Phase 1.1: プロジェクト環境セットアップ

**種別**: 環境構築（テスト不要）

### 実装内容

1. **pyproject.toml 作成**
```toml
[project]
name = "sd-model-manager"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "pydantic>=2.5.0",
    "pydantic-settings>=2.1.0",
    "httpx>=0.26.0",
    "python-dotenv>=1.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-asyncio>=0.23.0",
    "pytest-cov>=4.1.0",
    "httpx>=0.26.0",
    "ruff>=0.1.0",
]

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.pytest.ini_options]
testpaths = ["tests"]
pythonpath = ["src"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 100
target-version = "py312"
```

2. **ディレクトリ構造作成**
```bash
mkdir -p src/sd_model_manager/{registry,download,ui/{api,frontend,templates},infrastructure,lib,cli}
mkdir -p tests/sd_model_manager/{registry,download,ui/api,lib}
mkdir -p tests/cli
mkdir -p data
```

3. **仮想環境構築**
```bash
python3.12 -m venv .venv
source .venv/bin/activate  # macOS/Linux
pip install -e ".[dev]"
```

4. **.env.example 作成**
```env
# Civitai API Configuration
CIVITAI_API_KEY=your_api_key_here

# Download Configuration
DOWNLOAD_DIR=./downloads
MAX_CONCURRENT_DOWNLOADS=1

# Server Configuration
HOST=127.0.0.1
PORT=8188
```

5. **.gitignore 更新**
```gitignore
# Python
.venv/
__pycache__/
*.pyc
*.pyo
*.egg-info/

# Environment
.env

# Data
data/*.json
downloads/

# Frontend (追加予定)
node_modules/
dist/
```

### 完了条件
- [ ] `pyproject.toml` が存在し、Python 3.12+ を要求
- [ ] ディレクトリ構造が Codex 推奨に従っている
- [ ] 仮想環境が構築され、依存関係がインストール済み
- [ ] `.env.example` が存在

---

## Phase 1.2: pytest 環境構築とサンプルテスト作成

**種別**: TDD（環境確認）

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/test_sample.py`
```python
"""pytest が正しく動作することを確認するサンプルテスト"""


def test_sample_addition():
    """基本的な演算のテスト"""
    assert 1 + 1 == 2


def test_sample_string():
    """文字列操作のテスト"""
    text = "Hello, TDD!"
    assert text.startswith("Hello")
    assert "TDD" in text
```

### 🟢 GREEN: テスト実行

```bash
pytest tests/sd_model_manager/test_sample.py -v
```

**期待される出力**:
```
tests/sd_model_manager/test_sample.py::test_sample_addition PASSED
tests/sd_model_manager/test_sample.py::test_sample_string PASSED

====== 2 passed in 0.01s ======
```

### 🔵 REFACTOR: pytest 設定追加

**ファイル**: `pyproject.toml` (既に Phase 1.1 で追加済み)

### 完了条件
- [ ] pytest が正常に実行される
- [ ] サンプルテストが通る
- [ ] カバレッジレポートが生成可能（`pytest --cov`）

---

## Phase 1.3: Pydantic 基本モデル（LoraModel）のテスト作成

**種別**: TDD (RED)

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/registry/test_lora_model.py`
```python
"""Pydantic モデルのテスト"""

import pytest
from datetime import datetime
from sd_model_manager.registry.models import LoraModel


def test_lora_model_creation():
    """LoraModel の基本的な生成テスト"""
    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors"
    )

    assert model.name == "test-lora"
    assert model.url == "https://civitai.com/models/123/test-lora"
    assert model.file_path == "/path/to/models/loras/test-lora.safetensors"


def test_lora_model_with_optional_fields():
    """オプションフィールドを含む LoraModel のテスト"""
    downloaded_at = datetime.now()

    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors",
        description="Test description",
        image_url="https://example.com/image.jpg",
        downloaded_at=downloaded_at
    )

    assert model.description == "Test description"
    assert model.image_url == "https://example.com/image.jpg"
    assert model.downloaded_at == downloaded_at


def test_lora_model_validation_error():
    """必須フィールド欠如時のバリデーションエラーテスト"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LoraModel(name="test-lora")  # url, file_path が欠如


def test_lora_model_url_validation():
    """URL フォーマットバリデーションのテスト"""
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        LoraModel(
            name="test-lora",
            url="invalid-url",  # 不正な URL
            file_path="/path/to/lora.safetensors"
        )


def test_lora_model_supports_safetensors():
    """safetensors 拡張子をサポート"""
    model = LoraModel(
        name="test-lora",
        url="https://civitai.com/models/123/test-lora",
        file_path="/path/to/models/loras/test-lora.safetensors"
    )
    assert model.file_path.endswith('.safetensors')
```

### 実行結果（RED 確認）

```bash
pytest tests/sd_model_manager/registry/test_lora_model.py -v
```

**期待されるエラー**:
```
ModuleNotFoundError: No module named 'sd_model_manager.registry.models'
```

### 完了条件
- [ ] テストファイルが作成されている
- [ ] pytest 実行時にモジュール未実装エラーが出る（RED 状態）

---

## Phase 1.4: LoraModel 実装（テストをパスさせる）

**種別**: TDD (GREEN)

### 🟢 GREEN: 最小実装

**ファイル**: `src/sd_model_manager/registry/__init__.py`
```python
"""Registry モジュール: モデル登録・管理機能"""
```

**ファイル**: `src/sd_model_manager/registry/models.py`
```python
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
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/registry/test_lora_model.py -v
```

**期待される出力**:
```
tests/sd_model_manager/registry/test_lora_model.py::test_lora_model_creation PASSED
tests/sd_model_manager/registry/test_lora_model.py::test_lora_model_with_optional_fields PASSED
tests/sd_model_manager/registry/test_lora_model.py::test_lora_model_validation_error PASSED
tests/sd_model_manager/registry/test_lora_model.py::test_lora_model_url_validation PASSED
tests/sd_model_manager/registry/test_lora_model.py::test_lora_model_supports_safetensors PASSED

====== 5 passed in 0.05s ======
```

### 🔵 REFACTOR: コード改善

- 型ヒントの追加
- docstring の充実
- バリデーションロジックの整理

### 完了条件
- [ ] すべてのテストが通る（GREEN 状態）
- [ ] コードが整理されている（REFACTOR 完了）
- [ ] 型チェックが通る（`mypy` or `pyright`）

---

## Phase 1.5: Config 管理クラスのテスト作成

**種別**: TDD (RED)

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/test_config.py`
```python
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
```

### 実行結果（RED 確認）

```bash
pytest tests/sd_model_manager/test_config.py -v
```

**期待されるエラー**:
```
ModuleNotFoundError: No module named 'sd_model_manager.config'
```

### 完了条件
- [ ] テストファイルが作成されている
- [ ] pytest 実行時にモジュール未実装エラーが出る（RED 状態）

---

## Phase 1.6: Config 実装（.env 読み込み）

**種別**: TDD (GREEN)

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/config.py`
```python
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
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/test_config.py -v
```

### 🔵 REFACTOR: 改善

- バリデーション追加
- 型チェック強化

### 完了条件
- [ ] すべてのテストが通る
- [ ] `.env.example` と一致している

---

## Phase 1.7: FastAPI 最小アプリのテスト作成（GET /health）

**種別**: TDD (RED)

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/ui/api/test_health_endpoint.py`
```python
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
```

**注**: CORS ヘッダーテストは削除。TestClient がプリフライト（OPTIONS）リクエストに対応しないため、
Phase 3（React UI 統合テスト）での実際のブラウザベースのテストで検証します。

### 実行結果（RED 確認）

```bash
pytest tests/sd_model_manager/ui/api/test_health_endpoint.py -v
```

**期待されるエラー**:
```
ModuleNotFoundError: No module named 'sd_model_manager.ui.api.routes'
```

### 完了条件
- [ ] テストファイルが作成されている
- [ ] pytest 実行時にモジュール未実装エラーが出る（RED 状態）

---

## Phase 1.8: FastAPI 実装（health endpoint）

**種別**: TDD (GREEN)

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/ui/__init__.py`
```python
"""UI モジュール"""
```

**ファイル**: `src/sd_model_manager/ui/api/__init__.py`
```python
"""API ルーター"""
```

**ファイル**: `src/sd_model_manager/ui/api/health.py`
```python
"""ヘルスチェックルーター"""

from datetime import datetime
from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    """ヘルスチェックエンドポイント"""
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat()
    }
```

**ファイル**: `src/sd_model_manager/ui/api/main.py`（新規作成）
```python
"""FastAPI アプリケーション構築（ファクトリパターン）"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sd_model_manager.config import Config
from sd_model_manager.ui.api.health import router as health_router
from sd_model_manager.lib.errors import AppError, register_error_handlers


def create_app(config: Config | None = None) -> FastAPI:
    """FastAPI アプリケーション全体を構築するファクトリ関数

    テストと実行時の両方で同じコードパスを通すため、
    ファクトリパターンを採用しています。
    """
    if config is None:
        config = Config()

    app = FastAPI(
        title="SD-Model-Manager API",
        version="0.1.0",
        description="Stable Diffusion Model Manager API"
    )

    # CORS 設定
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],  # Vite default port
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ルーター登録
    app.include_router(health_router)

    # エラーハンドラー登録
    register_error_handlers(app)

    return app
```

**ファイル**: `src/sd_model_manager/__main__.py`
```python
"""エントリポイント"""

import uvicorn
from sd_model_manager.config import Config
from sd_model_manager.ui.api.main import create_app


def main():
    """アプリケーション起動"""
    config = Config()
    app = create_app(config)

    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=True
    )


if __name__ == "__main__":
    main()
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/ui/api/test_health_endpoint.py -v
```

### 手動確認

```bash
python -m sd_model_manager
# ブラウザで http://127.0.0.1:8188/health にアクセス
```

### 完了条件
- [ ] すべてのテストが通る
- [ ] サーバーが起動する
- [ ] `/health` にアクセスできる

---

## Phase 1.9: エラーハンドラーのテスト作成

**種別**: TDD (RED)

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/lib/test_errors.py`
```python
"""エラーハンドリングのテスト"""

import pytest
from sd_model_manager.lib.errors import (
    AppError,
    ConfigurationError,
    DownloadError,
    ModelValidationError
)


def test_app_error_base_class():
    """AppError 基底クラスのテスト"""
    error = AppError("Test error message", code="TEST_ERROR")

    assert str(error) == "Test error message"
    assert error.code == "TEST_ERROR"
    assert error.details is None


def test_configuration_error():
    """ConfigurationError のテスト"""
    error = ConfigurationError(
        "Invalid API key",
        details={"key": "CIVITAI_API_KEY"}
    )

    assert error.code == "CONFIGURATION_ERROR"
    assert error.details["key"] == "CIVITAI_API_KEY"


def test_download_error():
    """DownloadError のテスト"""
    error = DownloadError(
        "Download failed",
        details={"url": "https://example.com/model.safetensors"}
    )

    assert error.code == "DOWNLOAD_ERROR"


def test_model_validation_error():
    """ModelValidationError のテスト"""
    error = ModelValidationError(
        "Invalid model data",
        details={"field": "url", "value": "invalid-url"}
    )

    assert error.code == "MODEL_VALIDATION_ERROR"
```

**ファイル**: `tests/sd_model_manager/ui/api/test_error_handling.py`
```python
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
```

**注**: `/api/download` エンドポイントはPhase 2 で実装予定のため、バリデーションエラーハンドリングテストは削除。
Phase 2 で `ModelValidationError` が実際に発生するエンドポイントをテストします。

### 実行結果（RED 確認）

```bash
pytest tests/sd_model_manager/lib/test_errors.py tests/sd_model_manager/ui/api/test_error_handling.py -v
```

### 完了条件
- [ ] テストが失敗する（モジュール未実装）

---

## Phase 1.10: エラーハンドラー実装

**種別**: TDD (GREEN)

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/lib/__init__.py`
```python
"""共通ライブラリ"""
```

**ファイル**: `src/sd_model_manager/lib/errors.py`
```python
"""カスタム例外クラス定義とエラーハンドラー登録"""

from typing import Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppError(Exception):
    """アプリケーション基底例外"""

    def __init__(
        self,
        message: str,
        code: str = "APP_ERROR",
        details: Optional[dict[str, Any]] = None
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details


class ConfigurationError(AppError):
    """設定エラー"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="CONFIGURATION_ERROR", details=details)


class DownloadError(AppError):
    """ダウンロードエラー"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="DOWNLOAD_ERROR", details=details)


class ModelValidationError(AppError):
    """バリデーションエラー"""

    def __init__(self, message: str, details: Optional[dict[str, Any]] = None):
        super().__init__(message, code="MODEL_VALIDATION_ERROR", details=details)


def register_error_handlers(app: FastAPI) -> None:
    """FastAPI アプリケーションにエラーハンドラーを登録"""

    @app.exception_handler(AppError)
    async def app_error_handler(request: Request, exc: AppError):
        """AppError のハンドラー"""
        return JSONResponse(
            status_code=400,
            content={
                "error": {
                    "code": exc.code,
                    "message": exc.message,
                    "details": exc.details
                }
            }
        )

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc):
        """404 エラーハンドラー"""
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Endpoint not found: {request.url.path}"
                }
            }
        )
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/lib/test_errors.py tests/sd_model_manager/ui/api/test_error_handling.py -v
```

### 完了条件
- [ ] すべてのテストが通る
- [ ] エラーレスポンスが統一されている

---

## Phase 1.11: API ルータ結合テスト整備

**種別**: TDD (REFACTOR)

Phase 1 で整備した設定・エラーハンドリング・ヘルスチェックを FastAPI アプリケーションに束ね、ルータ単体テストだけでなくアプリ境界での挙動を保証します。

### 🔴 RED: テスト拡張

**ファイル**: `tests/sd_model_manager/ui/api/test_app_routes.py`
```python
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
```

### 🟢 GREEN: 実装/調整

1. `sd_model_manager/ui/api/main.py` に `create_app` 関数を追加し、FastAPI インスタンス生成・ルータ登録・エラーハンドラ登録処理を集約する。  
2. 既存のテストや CLI エントリからも `create_app` を経由するように変更し、起動パスを統一する。

**例**: `sd_model_manager/ui/api/main.py`
```python
from fastapi import FastAPI

from sd_model_manager.config import AppConfig, get_settings
from sd_model_manager.ui.api.errors import register_error_handlers
from sd_model_manager.ui.api.health import router as health_router


def create_app(config: AppConfig | None = None) -> FastAPI:
    """アプリケーション全体を構築するファクトリ関数"""
    settings = config or get_settings()
    app = FastAPI()

    app.include_router(health_router)
    register_error_handlers(app)

    @app.get("/config")
    def read_config():
        """デバッグ用途: 実際に読まれた設定の一部を返す"""
        return {"host": settings.host, "port": settings.port}

    return app
```

3. `sd_model_manager/__main__.py` など起動スクリプトでは `uvicorn.run(create_app(), ...)` の形をとる。

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/ui/api/test_app_routes.py -v
```

### 完了条件
- [ ] `create_app` を利用した結合テストが追加されている
- [ ] `/health` がアプリ経由でも正常応答する
- [ ] CLI/起動コードが `create_app` を共通利用する

---

## 次のステップ

Phase 1 完了後:

1. **Phase 2: ダウンロード機能**
   - Civitai API クライアントのテスト作成
   - ダウンロードサービスのテスト作成
   - 履歴管理のテスト作成

2. **Phase 3: Web UI（ダウンロード & 履歴表示）**
   - ダウンロードフォームコンポーネント
   - 進捗表示コンポーネント
   - 履歴一覧コンポーネント

---

## 付録: TDD のベストプラクティス

### テスト命名規則
```python
def test_<対象>_<条件>_<期待結果>():
    """日本語での説明"""
    pass
```

### テストの構造（AAA パターン）
```python
def test_example():
    # Arrange（準備）
    input_data = "test"

    # Act（実行）
    result = function_under_test(input_data)

    # Assert（検証）
    assert result == expected_value
```

### コミットメッセージ規約
```
test: Add test for LoraModel creation (RED)
feat: Implement LoraModel with validation (GREEN)
refactor: Improve LoraModel type hints (REFACTOR)
```

### カバレッジ目標
- **Unit tests**: ≥80%
- **Integration tests**: ≥70%
- **E2E tests**: 主要ユーザーフロー
