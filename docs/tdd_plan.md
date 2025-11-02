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

# TDD 駆動開発計画（Phase 2: ダウンロード機能）

## 概要

Phase 2 では、Civitai.com からモデルをダウンロードする機能を TDD で実装します。

**Phase 2 の目標**:
- Civitai API と連携してモデル情報を取得
- HTTPファイルダウンロードの実装
- プログレス表示機能
- エラーハンドリング（リトライ含む）

---

## タスク一覧

| # | タスク | 種別 | 所要時間 | 状態 |
|---|--------|------|---------|------|
| 2.1 | CivitaiClient のテスト作成 | TDD (RED) | 1h | ✅ 完了 |
| 2.2 | CivitaiClient 実装 | TDD (GREEN) | 1-2h | ✅ 完了 |
| 2.3 | DownloadService のテスト作成 | TDD (RED) | 1h | ✅ 完了 |
| 2.4 | DownloadService 実装 | TDD (GREEN) | 1-2h | ✅ 完了 |
| 2.5 | Meaningful Tests リファクタリング | TDD (REFACTOR) | 1h | ✅ 完了 |
| 2.6 | ダウンロードAPIエンドポイント作成 | TDD (RED) | 1h | ⏳ 未実装 |
| 2.7 | ダウンロードAPI実装 | TDD (GREEN) | 1-2h | ⏳ 未実装 |
| 2.8 | WebSocket プログレス配信実装 | TDD | 2h | ⏳ 未実装 |
| 2.9 | Download タブ UI 実装 | 統合 | 3-4h | ⏳ 未実装 |
| 2.10 | E2Eテスト（Playwright） | TDD | 1-2h | ⏳ 未実装 |

**合計**: 約 13-18 時間

---

## Phase 2.1: CivitaiClient のテスト作成 ✅

**種別**: TDD (RED)
**状態**: ✅ 完了

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/download/test_civitai_client.py`

```python
"""Civitai API クライアントのテスト"""

import pytest
from unittest.mock import AsyncMock, patch
from sd_model_manager.download.civitai_client import CivitaiClient
from sd_model_manager.lib.errors import DownloadError


@pytest.fixture
def civitai_client():
    """CivitaiClient フィクスチャ"""
    return CivitaiClient(api_key="test_api_key")


@pytest.mark.asyncio
async def test_extract_model_id_from_url(civitai_client):
    """Civitai URL からモデル ID を抽出するテスト"""
    url = "https://civitai.com/models/123456/test-lora"
    model_id = civitai_client.extract_model_id(url)
    assert model_id == "123456"


@pytest.mark.asyncio
async def test_extract_model_id_from_direct_id(civitai_client):
    """モデル ID を直接渡した場合のテスト"""
    model_id = civitai_client.extract_model_id("789012")
    assert model_id == "789012"


@pytest.mark.asyncio
async def test_extract_model_id_invalid_url(civitai_client):
    """無効な URL の場合のテスト"""
    with pytest.raises(DownloadError):
        civitai_client.extract_model_id("https://example.com/invalid")


@pytest.mark.asyncio
async def test_get_model_metadata(civitai_client):
    """モデルメタデータ取得のテスト"""
    mock_response = {
        "id": 123456,
        "name": "Test LoRA",
        "type": "LORA",
        "modelVersions": [
            {
                "id": 789012,
                "downloadUrl": "https://civitai.com/api/download/models/789012"
            }
        ]
    }

    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(return_value=mock_response)):
        metadata = await civitai_client.get_model_metadata("123456")
        assert metadata["id"] == 123456
        assert metadata["name"] == "Test LoRA"


@pytest.mark.asyncio
async def test_get_download_url(civitai_client):
    """ダウンロード URL 取得のテスト"""
    mock_response = {
        "id": 123456,
        "modelVersions": [
            {
                "id": 789012,
                "downloadUrl": "https://civitai.com/api/download/models/789012"
            }
        ]
    }

    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(return_value=mock_response)):
        url = await civitai_client.get_download_url("123456")
        assert url == "https://civitai.com/api/download/models/789012"


@pytest.mark.asyncio
async def test_get_model_metadata_api_error(civitai_client):
    """API エラー時のテスト"""
    with patch.object(civitai_client, '_fetch_model_data',
                     new=AsyncMock(side_effect=DownloadError("API Error"))):
        with pytest.raises(DownloadError):
            await civitai_client.get_model_metadata("123456")
```

### テスト実行（RED 確認）

```bash
pytest tests/sd_model_manager/download/test_civitai_client.py -v
```

**期待される結果**: すべてのテストが FAILED（実装がないため）

---

## Phase 2.2: CivitaiClient 実装 ✅

**種別**: TDD (GREEN)
**状態**: ✅ 完了

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/download/civitai_client.py`

```python
"""Civitai API クライアント"""

import logging
import re
from typing import Optional, Any
import httpx

from sd_model_manager.lib.errors import DownloadError

logger = logging.getLogger(__name__)


class CivitaiClient:
    """Civitai API との通信クライアント"""

    BASE_URL = "https://civitai.com/api/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    def extract_model_id(self, url_or_id: str) -> str:
        """URL またはモデル ID からモデル ID を抽出"""
        if url_or_id.isdigit():
            return url_or_id

        pattern = r'civitai\.com/models/(\d+)'
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)

        raise DownloadError(f"Invalid Civitai URL or model ID: {url_or_id}")

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            headers = {}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            self._client = httpx.AsyncClient(
                base_url=self.BASE_URL,
                headers=headers,
                timeout=30.0
            )
        return self._client

    async def _fetch_model_data(self, model_id: str) -> dict[str, Any]:
        """Civitai API からモデルデータを取得"""
        client = await self._get_client()
        logger.info("Fetching model data from Civitai API: model_id=%s", model_id)

        try:
            response = await client.get(f"/models/{model_id}")
            response.raise_for_status()
            logger.info("Successfully fetched model data: model_id=%s", model_id)
            return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            # エラーハンドリング（401, 403, 404, 429）
            # ... (ユーザーフレンドリーなエラーメッセージ)
            raise DownloadError(message, details={"model_id": model_id, "status_code": status_code})
        except httpx.RequestError as e:
            logger.error("Network error: model_id=%s, error=%s", model_id, str(e))
            raise DownloadError(f"Network error: {str(e)}", details={"model_id": model_id})

    async def get_model_metadata(self, url_or_id: str) -> dict[str, Any]:
        """モデルのメタデータを取得"""
        model_id = self.extract_model_id(url_or_id)
        return await self._fetch_model_data(model_id)

    async def get_download_url(self, url_or_id: str) -> str:
        """モデルのダウンロード URL を取得"""
        metadata = await self.get_model_metadata(url_or_id)
        versions = metadata.get("modelVersions", [])

        if not versions:
            raise DownloadError("No model versions found")

        download_url = versions[0].get("downloadUrl")
        if not download_url:
            raise DownloadError("No download URL found")

        return download_url
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/download/test_civitai_client.py -v
```

**期待される結果**:
```
test_extract_model_id_from_url PASSED
test_extract_model_id_from_direct_id PASSED
test_extract_model_id_invalid_url PASSED
test_get_model_metadata PASSED
test_get_download_url PASSED
test_get_model_metadata_api_error PASSED

====== 6 passed in 0.10s ======
```

---

## Phase 2.3: DownloadService のテスト作成 ✅

**種別**: TDD (RED)
**状態**: ✅ 完了

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/download/test_download_service.py`

```python
"""ダウンロードサービスのテスト"""

import pytest
import respx
import httpx
from pathlib import Path
from sd_model_manager.download.download_service import DownloadService
from sd_model_manager.lib.errors import DownloadError


@pytest.fixture
def download_service(tmp_path):
    """DownloadService フィクスチャ"""
    return DownloadService(download_dir=tmp_path)


@pytest.mark.asyncio
@respx.mock
async def test_download_file_success(download_service, tmp_path):
    """ファイルダウンロード成功のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"
    mock_content = b"fake model data for testing"

    respx.get(url).mock(return_value=httpx.Response(
        200,
        content=mock_content,
        headers={"content-length": str(len(mock_content))}
    ))

    result = await download_service.download_file(url, filename)

    assert result.exists()
    assert result.read_bytes() == mock_content


@pytest.mark.asyncio
@respx.mock
async def test_download_file_with_progress_callback(download_service, tmp_path):
    """進捗コールバック付きダウンロードのテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"
    mock_content = b"x" * 16384  # 16KB

    progress_updates = []
    def progress_callback(downloaded: int, total: int):
        progress_updates.append((downloaded, total))

    respx.get(url).mock(return_value=httpx.Response(
        200,
        content=mock_content,
        headers={"content-length": str(len(mock_content))}
    ))

    result = await download_service.download_file(
        url, filename, progress_callback=progress_callback, chunk_size=8192
    )

    assert result.exists()
    assert len(progress_updates) >= 1
    assert progress_updates[-1] == (len(mock_content), len(mock_content))


@pytest.mark.asyncio
@respx.mock
async def test_download_file_http_error(download_service):
    """HTTP エラー時のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"

    respx.get(url).mock(return_value=httpx.Response(404))

    with pytest.raises(DownloadError) as exc_info:
        await download_service.download_file(url, filename)

    assert "Failed to download file after 3 attempts" in str(exc_info.value)


@pytest.mark.asyncio
@respx.mock
async def test_download_with_retry(download_service, tmp_path):
    """リトライ機能のテスト"""
    url = "https://example.com/model.safetensors"
    filename = "test-model.safetensors"
    mock_content = b"fake model data"

    call_count = 0
    def side_effect(request):
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            return httpx.Response(500, text="Internal Server Error")
        return httpx.Response(
            200,
            content=mock_content,
            headers={"content-length": str(len(mock_content))}
        )

    respx.get(url).mock(side_effect=side_effect)

    result = await download_service.download_file(url, filename, max_retries=3)

    assert result.exists()
    assert call_count == 3
```

---

## Phase 2.4: DownloadService 実装 ✅

**種別**: TDD (GREEN)
**状態**: ✅ 完了

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/download/download_service.py`

```python
"""ダウンロードサービス"""

import asyncio
import logging
from pathlib import Path
from typing import Optional, Callable
import httpx

from sd_model_manager.lib.errors import DownloadError
from sd_model_manager.download.civitai_client import CivitaiClient

logger = logging.getLogger(__name__)


class DownloadService:
    """ファイルダウンロードサービス"""

    def __init__(
        self,
        download_dir: Path,
        civitai_client: Optional[CivitaiClient] = None
    ):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)
        self.civitai_client = civitai_client

    async def download_file(
        self,
        url: str,
        filename: str,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        max_retries: int = 3,
        chunk_size: int = 8192
    ) -> Path:
        """ファイルをダウンロード"""
        logger.info("Starting download: url=%s, filename=%s", url, filename)

        # Civitai URL の場合、ダウンロード URL を取得
        download_url = url
        if self._is_civitai_url(url):
            if not self.civitai_client:
                error_msg = "Civitai URL detected but no CivitaiClient configured"
                logger.error(error_msg + ": url=%s", url)
                raise DownloadError(error_msg, details={"url": url})

            logger.info("Resolving Civitai download URL: %s", url)
            download_url = await self.civitai_client.get_download_url(url)
            logger.info("Resolved download URL: %s", download_url)

        output_path = self.download_dir / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)

        last_error = None
        for attempt in range(max_retries):
            try:
                result = await self._download_with_progress(
                    download_url, output_path, progress_callback, chunk_size
                )
                logger.info("Download completed: filename=%s, path=%s", filename, result)
                return result
            except Exception as e:
                last_error = e
                if attempt < max_retries - 1:
                    logger.warning(
                        "Download failed (attempt %d/%d), retrying: %s",
                        attempt + 1, max_retries, str(e)
                    )
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                logger.error(
                    "Download failed after %d attempts: url=%s, error=%s",
                    max_retries, url, str(e)
                )
                break

        raise DownloadError(
            f"Failed to download file after {max_retries} attempts: {str(last_error)}",
            details={"url": url, "filename": filename, "error": str(last_error)}
        )

    def _is_civitai_url(self, url: str) -> bool:
        return "civitai.com" in url.lower()

    async def _download_with_progress(
        self, url: str, output_path: Path,
        progress_callback: Optional[Callable], chunk_size: int
    ) -> Path:
        """進捗付きダウンロード（内部メソッド）"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("GET", url) as response:
                response.raise_for_status()
                total_size = int(response.headers.get("content-length", 0))
                downloaded_size = 0

                with output_path.open("wb") as f:
                    async for chunk in response.aiter_bytes(chunk_size):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded_size, total_size)

                return output_path
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/download/test_download_service.py -v
```

**期待される結果**: すべてのテストが PASSED

---

## Phase 2.5: Meaningful Tests リファクタリング ✅

**種別**: TDD (REFACTOR)
**状態**: ✅ 完了

### 🔵 REFACTOR: テスト品質改善

**問題点**: 初期のテストは内部メソッド（`_download_with_progress`）をモックしていたため、meaningless（意味のないテスト）になっていた。

**改善策**: `respx` ライブラリを導入し、HTTPレイヤーをモックすることで、実際のダウンロードロジックをテストする。

**変更内容**:
1. `pyproject.toml` に `respx>=0.20.0` を追加
2. すべてのテストを `respx.mock` デコレータで書き直し
3. 実際のHTTPリクエスト/レスポンスサイクルをテスト
4. プログレスコールバックの実際の実行をテスト
5. リトライロジックの実際の動作をテスト

**完了条件**:
- ✅ respx を使用してHTTPレイヤーをモック
- ✅ 内部メソッドのモックを廃止
- ✅ 実際のファイル書き込みをテスト
- ✅ プログレスコールバックの複数回実行をテスト
- ✅ すべてのテストがPASS

---

## Phase 2.6: ダウンロードAPIエンドポイント作成 ⏳

**種別**: TDD (RED)
**状態**: ⏳ 未実装

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/ui/api/test_download_endpoint.py`

```python
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
    assert response.status_code == 400


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
```

---

## Phase 2.7: ダウンロードAPI実装 ⏳

**種別**: TDD (GREEN)
**状態**: ⏳ 未実装

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/ui/api/download.py`

```python
"""ダウンロードAPIルーター"""

import logging
import uuid
from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel, HttpUrl

from sd_model_manager.download.download_service import DownloadService
from sd_model_manager.download.civitai_client import CivitaiClient
from sd_model_manager.config import Config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/download", tags=["download"])


class DownloadRequest(BaseModel):
    """ダウンロードリクエスト"""
    url: HttpUrl  # HttpUrl 型で FastAPI がバリデーション
    filename: str


class DownloadResponse(BaseModel):
    """ダウンロードレスポンス"""
    task_id: str
    status: str


@router.post("", response_model=DownloadResponse)
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """ダウンロードを開始"""
    # バックグラウンドタスクでダウンロード実行
    task_id = str(uuid.uuid4())

    background_tasks.add_task(
        execute_download,
        task_id=task_id,
        url=str(request.url),  # HttpUrl を文字列に変換
        filename=request.filename
    )

    return DownloadResponse(
        task_id=task_id,
        status="started"
    )


async def execute_download(task_id: str, url: str, filename: str, download_service: DownloadService | None = None):
    """ダウンロード実行（バックグラウンド）

    注意: テストでは download_service を差し替え可能。
    本番では Config から DownloadService を生成。
    """
    if download_service is None:
        config = Config()
        civitai_client = CivitaiClient(api_key=config.civitai_api_key)
        download_service = DownloadService(
            download_dir=config.download_dir,
            civitai_client=civitai_client
        )

    try:
        await download_service.download_file(url, filename)
        logger.info("Download completed: task_id=%s", task_id)
    except Exception as e:
        logger.error("Download failed: task_id=%s, error=%s", task_id, str(e))
```

---

## Phase 2.8: WebSocket プログレス配信実装 ⏳

**種別**: TDD
**状態**: ⏳ 未実装

### 実装内容

- WebSocketエンドポイント: `/ws/download/{task_id}`
- プログレス更新メッセージ配信
- ダウンロード完了/エラー通知

---

## Phase 2.9: Download タブ UI 実装 ⏳

**種別**: 統合
**状態**: ⏳ 未実装

### 🎯 実装目標

Phase 2 のバックエンド（API + WebSocket）と連携し、ユーザーが Web UI から Civitai モデルをダウンロードできるようにする。

### 📦 技術スタック

- **フロントエンド**: Vite + React 18 (TypeScript)
- **ルーティング**: react-router-dom
- **スタイリング**: Tailwind CSS
- **アイコン**: lucide-react
- **状態管理**: @tanstack/react-query（API連携）
- **WebSocket**: native WebSocket API

### 📁 プロジェクト構成

```
src/sd_model_manager/ui/frontend/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── index.html
└── src/
    ├── main.tsx
    ├── App.tsx
    ├── components/
    │   ├── layout/
    │   │   ├── Sidebar.tsx        # 左サイドバー（タブナビゲーション）
    │   │   └── MainLayout.tsx     # メインレイアウト
    │   ├── download/
    │   │   ├── DownloadForm.tsx   # URL入力フォーム
    │   │   └── ProgressBar.tsx    # ダウンロード進捗表示
    │   └── common/
    │       └── Button.tsx
    ├── pages/
    │   └── DownloadPage.tsx       # Download タブメインページ
    ├── hooks/
    │   └── useDownload.ts         # ダウンロードロジック
    └── api/
        └── client.ts              # API クライアント
```

### 🔨 実装ステップ

#### Step 1: フロントエンド環境セットアップ

```bash
cd src/sd_model_manager/ui/frontend
npm init -y
npm install react react-dom react-router-dom
npm install -D @vitejs/plugin-react vite typescript @types/react @types/react-dom
npm install tailwindcss lucide-react @tanstack/react-query
```

#### Step 2: 基本レイアウト実装

**参考**: `reference_git_clones/civitiai-tools/civitai-downloader-v2/src/web/components/layout/Sidebar.tsx`

```tsx
// src/components/layout/Sidebar.tsx
import { Download, History, Settings } from 'lucide-react';

export const Sidebar = () => {
  return (
    <nav className="w-64 bg-gray-900 text-white h-screen p-4">
      <h1 className="text-xl font-bold mb-8">SD Model Manager</h1>
      <ul className="space-y-2">
        <li>
          <a href="/download" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
            <Download size={20} />
            <span>Download</span>
          </a>
        </li>
        <li>
          <a href="/history" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
            <History size={20} />
            <span>History</span>
          </a>
        </li>
        {/* Phase 3+ で追加: LoRA, Checkpoint, VAE, Embedding タブ */}
      </ul>
    </nav>
  );
};
```

#### Step 3: Download ページ実装

```tsx
// src/pages/DownloadPage.tsx
import { useState } from 'react';
import { useDownload } from '../hooks/useDownload';
import { DownloadForm } from '../components/download/DownloadForm';
import { ProgressBar } from '../components/download/ProgressBar';

export const DownloadPage = () => {
  const { startDownload, progress, isDownloading } = useDownload();

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Download Model</h2>

      <DownloadForm onSubmit={startDownload} disabled={isDownloading} />

      {isDownloading && (
        <div className="mt-6">
          <ProgressBar progress={progress} />
        </div>
      )}
    </div>
  );
};
```

#### Step 4: API連携 + WebSocket

```tsx
// src/hooks/useDownload.ts
import { useState, useEffect } from 'react';

export const useDownload = () => {
  const [progress, setProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [taskId, setTaskId] = useState<string | null>(null);

  const startDownload = async (url: string, filename: string) => {
    setIsDownloading(true);

    // POST /api/download
    const response = await fetch('http://localhost:8000/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url, filename })
    });

    const { task_id } = await response.json();
    setTaskId(task_id);
  };

  useEffect(() => {
    if (!taskId) return;

    // WebSocket で進捗を受信
    const ws = new WebSocket(`ws://localhost:8000/ws/download/${taskId}`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'progress') {
        setProgress(data.percentage);
      } else if (data.type === 'completed') {
        setProgress(100);
        setIsDownloading(false);
        ws.close();
      }
    };

    return () => ws.close();
  }, [taskId]);

  return { startDownload, progress, isDownloading };
};
```

### 📋 テスト方針

React Testing Library でコンポーネント単体テスト：
- サイドバーのリンク表示
- フォーム入力とバリデーション
- プログレスバーの表示

E2E テストは Phase 2.10 で実施。

### 🎯 完了条件

- ✅ Web UI から Civitai URL を入力してダウンロード開始できる
- ✅ リアルタイムでプログレスが表示される
- ✅ ダウンロード完了通知が表示される
- ✅ 左サイドバーで Download / History タブが切り替えられる

---

## Phase 2.10: E2Eテスト（Playwright） ⏳

**種別**: TDD
**状態**: ⏳ 未実装

### 実装内容

- Playwright によるブラウザテスト
- ダウンロードフロー全体のテスト（UI → API → WebSocket → 完了）
- プログレス表示の確認
- エラーハンドリングの確認

### テストシナリオ

```typescript
// tests/e2e/download-flow.spec.ts
import { test, expect } from '@playwright/test';

test('Civitai からモデルをダウンロード', async ({ page }) => {
  await page.goto('http://localhost:5173/download');

  // URL 入力
  await page.fill('input[name="url"]', 'https://civitai.com/models/12345/test-lora');
  await page.fill('input[name="filename"]', 'test-lora.safetensors');

  // ダウンロード開始
  await page.click('button[type="submit"]');

  // プログレス表示を確認
  await expect(page.locator('.progress-bar')).toBeVisible();

  // 完了を待つ（最大30秒）
  await expect(page.locator('.download-complete')).toBeVisible({ timeout: 30000 });
});
```

---

## Phase 2.11: セキュリティ修正（パストラバーサル脆弱性） ✅

**種別**: TDD (RED → GREEN)
**状態**: ✅ 完了

### 問題

Codex レビューで検出された P0（最優先）セキュリティ脆弱性：
- ファイル名をサニタイズせずに直接使用
- パストラバーサル攻撃（`../../etc/passwd`）が可能
- 任意のファイルシステム位置への書き込みが可能

### 🔴 RED: セキュリティテスト作成

```python
# tests/sd_model_manager/ui/api/test_download_endpoint.py

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

def test_download_endpoint_rejects_directory_separator(test_client):
    """ディレクトリセパレータを拒否するテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": "https://civitai.com/models/123456",
            "filename": "path/to/file.safetensors"
        }
    )
    assert response.status_code == 400

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
```

### 🟢 GREEN: セキュリティ実装

```python
# src/sd_model_manager/ui/api/download.py

from fastapi import HTTPException

def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズして、パストラバーサル攻撃を防ぐ。

    Raises:
        HTTPException: 不正なファイル名の場合（status_code=400）
    """
    # 空文字チェック
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="Filename cannot be empty")

    filename = filename.strip()

    # ディレクトリセパレータをチェック
    if '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Filename cannot contain path separators (/ or \\)"
        )

    # 相対パス（..）をチェック
    if '..' in filename:
        raise HTTPException(status_code=400, detail="Filename cannot contain '..'")

    # 絶対パスをチェック
    if filename.startswith('/'):
        raise HTTPException(status_code=400, detail="Filename cannot be an absolute path")

    # Windowsドライブレター（C:, D:など）をチェック
    if len(filename) > 1 and filename[1] == ':':
        raise HTTPException(status_code=400, detail="Filename cannot contain drive letters")

    # NULL文字をチェック
    if '\0' in filename:
        raise HTTPException(status_code=400, detail="Filename cannot contain null characters")

    return filename

@router.post("", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """ダウンロードを開始"""
    # ファイル名をサニタイズ（パストラバーサル攻撃を防ぐ）
    safe_filename = sanitize_filename(request.filename)

    # 以降、safe_filename のみを使用
    ...
```

### 完了条件

- ✅ 6個のセキュリティテストが全て合格
- ✅ 既存テスト（38個）にリグレッションなし
- ✅ 総テスト数: 44/44 passing

---

## Phase 2.12: ファイル名自動決定機能（ComfyUI-LoRA-Manager 方式） ⏳

**種別**: TDD (RED → GREEN → REFACTOR)
**状態**: ⏳ 未実装

### 背景

**ComfyUI-LoRA-Manager の実装分析結果**:
- ✅ ユーザーはファイル名を入力しない
- ✅ Civitai API のメタデータから自動的にファイル名を取得
- ✅ 重複時はハッシュベースでユニーク化
- ✅ UX改善: 入力項目が減る（2つ→1つ）

### 実装内容

**現在の設計**:
```json
POST /api/download
{
  "url": "https://civitai.com/models/12345",
  "filename": "model.safetensors"  // ← ユーザー手動入力
}
```

**新設計（Phase 2.12）**:
```json
POST /api/download
{
  "url": "https://civitai.com/models/12345"  // URLのみ！
}
```

**処理フロー**:
```
1. URL受信
   ↓
2. Civitai API からメタデータ取得
   ↓
3. file_info['name'] でファイル名を抽出
   ↓
4. sanitize_filename() でセキュリティチェック
   ↓
5. 重複時はタイムスタンプ等で対応
   ↓
6. ダウンロード実行
```

### 🔴 RED: テスト作成（失敗させる）

```python
# tests/sd_model_manager/ui/api/test_download_endpoint.py

import pytest
from unittest.mock import AsyncMock, patch

def test_download_endpoint_accepts_url_only(test_client):
    """filename なしのリクエストを受け付けるテスト"""
    response = test_client.post(
        "/api/download",
        json={"url": "https://civitai.com/models/134605/yaemiko-lora"}
    )
    # filename が必須でなくなったので 200/202 を期待
    assert response.status_code in [200, 202]
    data = response.json()
    assert "task_id" in data


@pytest.mark.asyncio
async def test_extract_filename_from_metadata(test_client):
    """メタデータからファイル名を抽出するテスト"""
    # モックのメタデータ
    mock_metadata = {
        "modelVersions": [{
            "files": [{
                "name": "yaemiko-lora-nochekaiser.safetensors",
                "type": "Model"
            }]
        }]
    }

    with patch('sd_model_manager.download.civitai_client.CivitaiClient.get_model_metadata') as mock_get:
        mock_get.return_value = mock_metadata

        response = test_client.post(
            "/api/download",
            json={"url": "https://civitai.com/models/134605"}
        )

        assert response.status_code in [200, 202]
        # 実際のダウンロードでファイル名が使われることを確認
        # （ログまたはプログレスマネージャーで検証）


def test_filename_sanitization_on_metadata(test_client):
    """メタデータのファイル名もサニタイズされることを確認"""
    # 悪意あるメタデータを想定
    with patch('sd_model_manager.download.civitai_client.CivitaiClient.get_model_metadata') as mock_get:
        mock_get.return_value = {
            "modelVersions": [{
                "files": [{
                    "name": "../../etc/passwd",  # 悪意あるファイル名
                    "type": "Model"
                }]
            }]
        }

        response = test_client.post(
            "/api/download",
            json={"url": "https://civitai.com/models/134605"}
        )

        # セキュリティエラーを期待
        assert response.status_code == 400
        assert "path" in response.json()["detail"].lower()
```

### 🟢 GREEN: 実装

**1. DownloadRequest モデルを更新**

```python
# src/sd_model_manager/ui/api/download.py

class DownloadRequest(BaseModel):
    """ダウンロードリクエスト"""
    url: HttpUrl  # filename フィールドを削除！
```

**2. ファイル名抽出ロジックを追加**

```python
# src/sd_model_manager/ui/api/download.py

async def extract_filename_from_metadata(url: str, civitai_client: CivitaiClient) -> str:
    """
    Civitai API のメタデータからファイル名を抽出

    Args:
        url: Civitai URL
        civitai_client: CivitaiClient インスタンス

    Returns:
        抽出されたファイル名

    Raises:
        HTTPException: メタデータ取得失敗時
    """
    try:
        metadata = await civitai_client.get_model_metadata(url)

        # modelVersions[0].files[0].name を取得
        if not metadata.get("modelVersions"):
            raise HTTPException(
                status_code=400,
                detail="No model versions found in metadata"
            )

        files = metadata["modelVersions"][0].get("files", [])
        if not files:
            raise HTTPException(
                status_code=400,
                detail="No files found in model version"
            )

        # 最初のファイル名を取得
        filename = files[0].get("name")
        if not filename:
            raise HTTPException(
                status_code=400,
                detail="Filename not found in metadata"
            )

        return filename

    except Exception as e:
        logger.error("Failed to extract filename from metadata: %s", str(e))
        # フォールバック: モデルIDベースのファイル名
        model_id = civitai_client.extract_model_id(url)
        return f"model-{model_id}.safetensors"
```

**3. start_download を更新**

```python
@router.post("", response_model=DownloadResponse)
async def start_download(
    request: DownloadRequest,
    background_tasks: BackgroundTasks
):
    """ダウンロードを開始"""

    # Civitai クライアントを初期化
    config = Config()
    civitai_client = CivitaiClient(api_key=config.civitai_api_key)

    # メタデータからファイル名を自動取得
    filename = await extract_filename_from_metadata(str(request.url), civitai_client)

    # ファイル名をサニタイズ（パストラバーサル攻撃を防ぐ）
    safe_filename = sanitize_filename(filename)

    # バックグラウンドタスクでダウンロード実行
    task_id = str(uuid.uuid4())
    progress_manager = get_progress_manager()

    progress_manager.create_task(
        task_id=task_id,
        filename=safe_filename,
        total_bytes=0
    )

    background_tasks.add_task(
        execute_download,
        task_id=task_id,
        url=str(request.url),
        filename=safe_filename
    )

    logger.info("Download task created: task_id=%s, url=%s, filename=%s (auto-detected)",
                task_id, request.url, safe_filename)

    return DownloadResponse(
        task_id=task_id,
        status="started"
    )
```

**4. フロントエンド更新**

```tsx
// src/sd_model_manager/ui/frontend/src/components/download/DownloadForm.tsx

export default function DownloadForm({ onSubmit, disabled = false }: DownloadFormProps) {
  const [url, setUrl] = useState('')
  // filename state を削除！
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    if (!url.trim()) {
      setError('URL is required')
      return
    }

    // URL バリデーション
    try {
      new URL(url)
    } catch {
      setError('Invalid URL format')
      return
    }

    // filename を渡さない！
    onSubmit(url)
    setUrl('')
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4 bg-white p-6 rounded shadow">
      <div>
        <label htmlFor="url" className="block text-sm font-medium text-gray-700 mb-1">
          Civitai Model URL
        </label>
        <input
          type="text"
          id="url"
          name="url"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={disabled}
          placeholder="https://civitai.com/models/12345/model-name"
          className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
        />
      </div>

      {/* filename 入力欄を削除！ */}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded text-sm">
          {error}
        </div>
      )}

      <button
        type="submit"
        disabled={disabled}
        className="w-full px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition"
      >
        {disabled ? 'Downloading...' : 'Start Download'}
      </button>
    </form>
  )
}
```

```typescript
// src/sd_model_manager/ui/frontend/src/hooks/useDownload.ts

const startDownload = async (url: string) => {  // filename パラメータ削除！
  setIsDownloading(true)
  setProgress(0)
  setStatus('downloading')
  setError(null)

  try {
    const response = await fetch('http://localhost:8000/api/download', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })  // filename を送信しない！
    })

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }

    const { task_id } = await response.json()
    setTaskId(task_id)
    console.log('Download started with task_id:', task_id)
  } catch (err) {
    setError(err instanceof Error ? err.message : 'Failed to start download')
    setStatus('failed')
    setIsDownloading(false)
  }
}
```

### 🔵 REFACTOR: エラーハンドリング改善

```python
# src/sd_model_manager/ui/api/download.py

async def extract_filename_from_metadata(
    url: str,
    civitai_client: CivitaiClient,
    fallback_to_model_id: bool = True
) -> str:
    """
    Civitai API のメタデータからファイル名を抽出

    Args:
        url: Civitai URL
        civitai_client: CivitaiClient インスタンス
        fallback_to_model_id: メタデータ取得失敗時にモデルIDベースのファイル名を使用するか

    Returns:
        抽出されたファイル名
    """
    try:
        metadata = await civitai_client.get_model_metadata(url)

        # 最新バージョンのファイルを取得
        versions = metadata.get("modelVersions", [])
        if not versions:
            if fallback_to_model_id:
                return _generate_fallback_filename(url, civitai_client)
            raise HTTPException(status_code=400, detail="No model versions found")

        # 最新バージョンの最初のファイルを取得
        files = versions[0].get("files", [])
        if not files:
            if fallback_to_model_id:
                return _generate_fallback_filename(url, civitai_client)
            raise HTTPException(status_code=400, detail="No files found in model version")

        # Type="Model" のファイルを優先
        model_file = next((f for f in files if f.get("type") == "Model"), files[0])
        filename = model_file.get("name")

        if not filename:
            if fallback_to_model_id:
                return _generate_fallback_filename(url, civitai_client)
            raise HTTPException(status_code=400, detail="Filename not found in metadata")

        logger.info("Extracted filename from metadata: %s", filename)
        return filename

    except HTTPException:
        raise
    except Exception as e:
        logger.error("Failed to extract filename from metadata: %s", str(e))
        if fallback_to_model_id:
            return _generate_fallback_filename(url, civitai_client)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to extract filename: {str(e)}"
        )


def _generate_fallback_filename(url: str, civitai_client: CivitaiClient) -> str:
    """フォールバック用のファイル名を生成"""
    model_id = civitai_client.extract_model_id(url)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"model-{model_id}-{timestamp}.safetensors"
    logger.warning("Using fallback filename: %s", filename)
    return filename
```

### 完了条件

- ✅ DownloadRequest から filename フィールドを削除
- ✅ メタデータからファイル名を自動抽出
- ✅ sanitize_filename() は引き続き適用
- ✅ フォールバック機能（メタデータ取得失敗時）
- ✅ フロントエンドから filename 入力欄を削除
- ✅ 既存テストの更新（filename なし）
- ✅ 新規テスト: メタデータ抽出、セキュリティ検証
- ✅ すべてのテストが合格

---

---

# TDD 駆動開発計画（Phase 3: 履歴管理 & 仕上げ）

## 概要

Phase 3 では、ダウンロード履歴管理機能と全体の仕上げを TDD で実装します。

**Phase 3 の目標**:
- ダウンロード履歴のJSON保存・読み込み
- 履歴APIエンドポイント実装
- 履歴削除・再ダウンロード機能
- UI/UX 仕上げ

---

## タスク一覧

| # | タスク | 種別 | 所要時間 | 状態 |
|---|--------|------|---------|------|
| 3.1 | DownloadHistory モデルのテスト作成 | TDD (RED) | 30min | ⏳ 未実装 |
| 3.2 | DownloadHistory モデル実装 | TDD (GREEN) | 30min | ⏳ 未実装 |
| 3.3 | HistoryService のテスト作成 | TDD (RED) | 1h | ⏳ 未実装 |
| 3.4 | HistoryService 実装 | TDD (GREEN) | 1-2h | ⏳ 未実装 |
| 3.5 | 履歴APIエンドポイントのテスト作成 | TDD (RED) | 1h | ⏳ 未実装 |
| 3.6 | 履歴APIエンドポイント実装 | TDD (GREEN) | 1h | ⏳ 未実装 |
| 3.7 | ダウンロード完了時の履歴自動保存 | TDD | 1h | ⏳ 未実装 |
| 3.8 | 履歴削除機能のテスト・実装 | TDD | 30min | ⏳ 未実装 |
| 3.9 | History タブ UI 実装 | 統合 | 2-3h | ⏳ 未実装 |
| 3.10 | E2Eテスト（履歴フロー全体） | TDD | 1-2h | ⏳ 未実装 |

**合計**: 約 10-13 時間

---

## Phase 3.1: DownloadHistory モデルのテスト作成 ⏳

**種別**: TDD (RED)
**状態**: ⏳ 未実装

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/registry/test_download_history.py`

```python
"""ダウンロード履歴モデルのテスト"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from sd_model_manager.registry.models import DownloadHistory


def test_download_history_creation():
    """ダウンロード履歴モデルの作成テスト"""
    history = DownloadHistory(
        id="test-uuid-1234",
        model_type="lora",
        name="Test LoRA",
        civitai_model_id="123456",
        civitai_version_id="789012",
        url="https://civitai.com/api/download/models/789012",
        file_name="test-lora.safetensors",
        file_path="/models/loras/test-lora.safetensors",
        file_size=1024000,
        downloaded_at=datetime.now()
    )

    assert history.id == "test-uuid-1234"
    assert history.model_type == "lora"
    assert history.name == "Test LoRA"
    assert history.file_size == 1024000


def test_download_history_with_optional_fields():
    """オプションフィールド付きダウンロード履歴のテスト"""
    history = DownloadHistory(
        id="test-uuid-1234",
        model_type="checkpoint",
        name="Test Checkpoint",
        civitai_model_id="123456",
        civitai_version_id="789012",
        url="https://civitai.com/api/download/models/789012",
        file_name="checkpoint.safetensors",
        file_path="/models/checkpoints/checkpoint.safetensors",
        file_size=2048000,
        downloaded_at=datetime.now(),
        description="Test description",
        preview_image_url="https://example.com/preview.jpg",
        downloaded_by_version="0.1.0"
    )

    assert history.description == "Test description"
    assert history.preview_image_url == "https://example.com/preview.jpg"
    assert history.downloaded_by_version == "0.1.0"


def test_download_history_model_type_validation():
    """モデルタイプのバリデーションテスト"""
    with pytest.raises(ValidationError):
        DownloadHistory(
            id="test-uuid",
            model_type="invalid_type",  # 無効なモデルタイプ
            name="Test",
            civitai_model_id="123456",
            civitai_version_id="789012",
            url="https://civitai.com/api/download/models/789012",
            file_name="test.safetensors",
            file_path="/models/test.safetensors",
            file_size=1024,
            downloaded_at=datetime.now()
        )


def test_download_history_to_dict():
    """辞書変換のテスト"""
    history = DownloadHistory(
        id="test-uuid-1234",
        model_type="lora",
        name="Test LoRA",
        civitai_model_id="123456",
        civitai_version_id="789012",
        url="https://civitai.com/api/download/models/789012",
        file_name="test-lora.safetensors",
        file_path="/models/loras/test-lora.safetensors",
        file_size=1024000,
        downloaded_at=datetime.now()
    )

    data = history.model_dump()

    assert data["id"] == "test-uuid-1234"
    assert data["model_type"] == "lora"
    assert "downloaded_at" in data


def test_download_history_from_dict():
    """辞書からの復元テスト"""
    data = {
        "id": "test-uuid-1234",
        "model_type": "vae",
        "name": "Test VAE",
        "civitai_model_id": "123456",
        "civitai_version_id": "789012",
        "url": "https://civitai.com/api/download/models/789012",
        "file_name": "vae.safetensors",
        "file_path": "/models/vae/vae.safetensors",
        "file_size": 512000,
        "downloaded_at": "2024-10-29T10:30:00Z"
    }

    history = DownloadHistory(**data)

    assert history.id == "test-uuid-1234"
    assert history.model_type == "vae"
```

### テスト実行（RED 確認）

```bash
pytest tests/sd_model_manager/registry/test_download_history.py -v
```

**期待される結果**: すべてのテストが FAILED（実装がないため）

---

## Phase 3.2: DownloadHistory モデル実装 ⏳

**種別**: TDD (GREEN)
**状態**: ⏳ 未実装

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/registry/models.py`（既存ファイルに追加）

```python
from datetime import datetime
from typing import Optional, Literal
from pydantic import BaseModel, Field
import uuid


class DownloadHistory(BaseModel):
    """ダウンロード履歴のデータモデル"""

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    model_type: Literal["lora", "checkpoint", "vae", "embedding"]
    name: str
    civitai_model_id: str
    civitai_version_id: str
    description: Optional[str] = None
    url: str
    file_name: str
    file_path: str
    file_size: int
    preview_image_url: Optional[str] = None
    downloaded_at: datetime
    downloaded_by_version: Optional[str] = None

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": "550e8400-e29b-41d4-a716-446655440000",
                    "model_type": "lora",
                    "name": "Example LoRA",
                    "civitai_model_id": "123456",
                    "civitai_version_id": "789012",
                    "description": "Example LoRA model",
                    "url": "https://civitai.com/api/download/models/789012",
                    "file_name": "example-lora.safetensors",
                    "file_path": "/models/loras/example-lora.safetensors",
                    "file_size": 2147483648,
                    "preview_image_url": "https://example.com/preview.jpg",
                    "downloaded_at": "2024-10-29T10:30:00Z",
                    "downloaded_by_version": "0.1.0"
                }
            ]
        }
    }
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/registry/test_download_history.py -v
```

**期待される結果**:
```
test_download_history_creation PASSED
test_download_history_with_optional_fields PASSED
test_download_history_model_type_validation PASSED
test_download_history_to_dict PASSED
test_download_history_from_dict PASSED

====== 5 passed in 0.05s ======
```

---

## Phase 3.3: HistoryService のテスト作成 ⏳

**種別**: TDD (RED)
**状態**: ⏳ 未実装

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/registry/test_history_service.py`

```python
"""履歴サービスのテスト"""

import pytest
from pathlib import Path
from datetime import datetime
from sd_model_manager.registry.history_service import HistoryService
from sd_model_manager.registry.models import DownloadHistory


@pytest.fixture
def history_service(tmp_path):
    """HistoryService フィクスチャ"""
    history_file = tmp_path / "test_history.json"
    return HistoryService(history_file=history_file)


@pytest.fixture
def sample_history():
    """サンプル履歴データ"""
    return DownloadHistory(
        id="test-uuid-1234",
        model_type="lora",
        name="Test LoRA",
        civitai_model_id="123456",
        civitai_version_id="789012",
        url="https://civitai.com/api/download/models/789012",
        file_name="test-lora.safetensors",
        file_path="/models/loras/test-lora.safetensors",
        file_size=1024000,
        downloaded_at=datetime.now()
    )


def test_history_service_initialization(history_service):
    """HistoryService 初期化のテスト"""
    assert history_service.history_file.exists()


def test_add_history(history_service, sample_history):
    """履歴追加のテスト"""
    history_service.add(sample_history)

    histories = history_service.get_all()
    assert len(histories) == 1
    assert histories[0].id == "test-uuid-1234"


def test_get_all_histories(history_service, sample_history):
    """全履歴取得のテスト"""
    # 複数の履歴を追加
    history_service.add(sample_history)

    history2 = DownloadHistory(
        id="test-uuid-5678",
        model_type="checkpoint",
        name="Test Checkpoint",
        civitai_model_id="234567",
        civitai_version_id="890123",
        url="https://civitai.com/api/download/models/890123",
        file_name="checkpoint.safetensors",
        file_path="/models/checkpoints/checkpoint.safetensors",
        file_size=2048000,
        downloaded_at=datetime.now()
    )
    history_service.add(history2)

    histories = history_service.get_all()
    assert len(histories) == 2


def test_get_history_by_id(history_service, sample_history):
    """ID指定で履歴取得のテスト"""
    history_service.add(sample_history)

    result = history_service.get_by_id("test-uuid-1234")
    assert result is not None
    assert result.id == "test-uuid-1234"
    assert result.name == "Test LoRA"


def test_get_history_by_id_not_found(history_service):
    """存在しないIDで履歴取得のテスト"""
    result = history_service.get_by_id("nonexistent-id")
    assert result is None


def test_delete_history(history_service, sample_history):
    """履歴削除のテスト"""
    history_service.add(sample_history)

    deleted = history_service.delete("test-uuid-1234")
    assert deleted is True

    histories = history_service.get_all()
    assert len(histories) == 0


def test_delete_history_not_found(history_service):
    """存在しないIDで削除のテスト"""
    deleted = history_service.delete("nonexistent-id")
    assert deleted is False


def test_history_persistence(tmp_path):
    """履歴の永続化テスト"""
    history_file = tmp_path / "test_history.json"

    # 1つ目のサービスで履歴追加
    service1 = HistoryService(history_file=history_file)
    history = DownloadHistory(
        id="test-uuid-1234",
        model_type="lora",
        name="Test LoRA",
        civitai_model_id="123456",
        civitai_version_id="789012",
        url="https://civitai.com/api/download/models/789012",
        file_name="test-lora.safetensors",
        file_path="/models/loras/test-lora.safetensors",
        file_size=1024000,
        downloaded_at=datetime.now()
    )
    service1.add(history)

    # 2つ目のサービスで読み込み
    service2 = HistoryService(history_file=history_file)
    histories = service2.get_all()

    assert len(histories) == 1
    assert histories[0].id == "test-uuid-1234"


def test_search_histories_by_name(history_service, sample_history):
    """名前で履歴検索のテスト"""
    history_service.add(sample_history)

    results = history_service.search(query="Test LoRA")
    assert len(results) == 1
    assert results[0].name == "Test LoRA"


def test_filter_histories_by_model_type(history_service, sample_history):
    """モデルタイプでフィルタリングのテスト"""
    history_service.add(sample_history)

    # checkpointを追加
    checkpoint_history = DownloadHistory(
        id="test-uuid-5678",
        model_type="checkpoint",
        name="Test Checkpoint",
        civitai_model_id="234567",
        civitai_version_id="890123",
        url="https://civitai.com/api/download/models/890123",
        file_name="checkpoint.safetensors",
        file_path="/models/checkpoints/checkpoint.safetensors",
        file_size=2048000,
        downloaded_at=datetime.now()
    )
    history_service.add(checkpoint_history)

    # loraでフィルタ
    lora_histories = history_service.filter_by_type("lora")
    assert len(lora_histories) == 1
    assert lora_histories[0].model_type == "lora"
```

### テスト実行（RED 確認）

```bash
pytest tests/sd_model_manager/registry/test_history_service.py -v
```

**期待される結果**: すべてのテストが FAILED（実装がないため）

---

## Phase 3.4: HistoryService 実装 ⏳

**種別**: TDD (GREEN)
**状態**: ⏳ 未実装

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/registry/history_service.py`

```python
"""履歴管理サービス"""

import json
import logging
from pathlib import Path
from typing import List, Optional
from datetime import datetime

from sd_model_manager.registry.models import DownloadHistory

logger = logging.getLogger(__name__)


class HistoryService:
    """ダウンロード履歴管理サービス"""

    def __init__(self, history_file: Path):
        """
        Args:
            history_file: 履歴JSONファイルのパス
        """
        self.history_file = Path(history_file)
        self._ensure_history_file()

    def _ensure_history_file(self):
        """履歴ファイルが存在することを保証"""
        self.history_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.history_file.exists():
            self._save([])
            logger.info("Created new history file: %s", self.history_file)

    def _load(self) -> List[DownloadHistory]:
        """履歴を読み込み"""
        try:
            with self.history_file.open("r", encoding="utf-8") as f:
                data = json.load(f)
                return [DownloadHistory(**item) for item in data]
        except json.JSONDecodeError as e:
            logger.error("Failed to load history: %s", str(e))
            return []

    def _save(self, histories: List[DownloadHistory]):
        """履歴を保存"""
        with self.history_file.open("w", encoding="utf-8") as f:
            data = [h.model_dump(mode="json") for h in histories]
            json.dump(data, f, indent=2, ensure_ascii=False)

    def add(self, history: DownloadHistory):
        """履歴を追加"""
        histories = self._load()
        histories.append(history)
        self._save(histories)
        logger.info("Added history: id=%s, name=%s", history.id, history.name)

    def get_all(self) -> List[DownloadHistory]:
        """全履歴を取得"""
        return self._load()

    def get_by_id(self, history_id: str) -> Optional[DownloadHistory]:
        """IDで履歴を取得"""
        histories = self._load()
        for history in histories:
            if history.id == history_id:
                return history
        return None

    def delete(self, history_id: str) -> bool:
        """履歴を削除"""
        histories = self._load()
        original_count = len(histories)

        histories = [h for h in histories if h.id != history_id]

        if len(histories) < original_count:
            self._save(histories)
            logger.info("Deleted history: id=%s", history_id)
            return True

        logger.warning("History not found for deletion: id=%s", history_id)
        return False

    def search(self, query: str) -> List[DownloadHistory]:
        """名前で履歴を検索"""
        histories = self._load()
        query_lower = query.lower()
        return [h for h in histories if query_lower in h.name.lower()]

    def filter_by_type(self, model_type: str) -> List[DownloadHistory]:
        """モデルタイプでフィルタリング"""
        histories = self._load()
        return [h for h in histories if h.model_type == model_type]
```

### テスト実行（GREEN 確認）

```bash
pytest tests/sd_model_manager/registry/test_history_service.py -v
```

**期待される結果**: すべてのテストが PASSED

---

## Phase 3.5: 履歴APIエンドポイントのテスト作成 ⏳

**種別**: TDD (RED)
**状態**: ⏳ 未実装

### 🔴 RED: テスト作成

**ファイル**: `tests/sd_model_manager/ui/api/test_history_endpoint.py`

```python
"""履歴APIエンドポイントのテスト"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sd_model_manager.config import Config
from sd_model_manager.ui.api.main import create_app
from sd_model_manager.registry.models import DownloadHistory


@pytest.fixture
def test_client():
    config = Config()
    app = create_app(config)
    return TestClient(app)


@pytest.fixture
def sample_history():
    """テスト用サンプル履歴データ"""
    return DownloadHistory(
        task_id="test-uuid-1234",
        model_name="example-lora",
        model_url="https://civitai.com/models/12345/example-lora",
        file_path="/models/loras/example-lora.safetensors",
        file_size=512000000,
        status="completed",
        downloaded_at=datetime.now()
    )


def test_get_all_histories_endpoint(test_client, sample_history):
    """全履歴取得エンドポイントのテスト"""
    # HistoryService をモック化してテストデータを返す
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.get_all.return_value = [sample_history]
        mock_service_getter.return_value = mock_service

        response = test_client.get("/api/history")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["task_id"] == "test-uuid-1234"
    assert data[0]["model_name"] == "example-lora"


def test_get_history_by_id_endpoint(test_client, sample_history):
    """ID指定履歴取得エンドポイントのテスト"""
    # テストデータを投入
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = sample_history
        mock_service_getter.return_value = mock_service

        response = test_client.get(f"/api/history/{sample_history.task_id}")

    assert response.status_code == 200
    data = response.json()
    assert data["task_id"] == "test-uuid-1234"
    assert data["model_name"] == "example-lora"
    assert data["status"] == "completed"


def test_get_history_not_found_endpoint(test_client):
    """存在しない履歴の取得テスト"""
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.get_by_id.return_value = None
        mock_service_getter.return_value = mock_service

        response = test_client.get("/api/history/nonexistent-uuid")

    assert response.status_code == 404


def test_delete_history_endpoint(test_client, sample_history):
    """履歴削除エンドポイントのテスト"""
    # テストデータを投入してから削除
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.delete.return_value = True
        mock_service_getter.return_value = mock_service

        response = test_client.delete(f"/api/history/{sample_history.task_id}")

    assert response.status_code == 204
    mock_service.delete.assert_called_once_with(sample_history.task_id)


def test_search_histories_endpoint(test_client, sample_history):
    """履歴検索エンドポイントのテスト"""
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.search.return_value = [sample_history]
        mock_service_getter.return_value = mock_service

        response = test_client.get("/api/history/search?q=example")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["model_name"] == "example-lora"


def test_filter_histories_by_type_endpoint(test_client, sample_history):
    """モデルタイプフィルタエンドポイントのテスト"""
    with patch('sd_model_manager.ui.api.history.get_history_service') as mock_service_getter:
        mock_service = MagicMock()
        mock_service.filter_by_type.return_value = [sample_history]
        mock_service_getter.return_value = mock_service

        response = test_client.get("/api/history?model_type=lora")

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["model_name"] == "example-lora"
    mock_service.filter_by_type.assert_called_once_with("lora")
```

---

## Phase 3.6: 履歴APIエンドポイント実装 ⏳

**種別**: TDD (GREEN)
**状態**: ⏳ 未実装

### 🟢 GREEN: 実装

**ファイル**: `src/sd_model_manager/ui/api/history.py`

```python
"""履歴APIルーター"""

import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from pathlib import Path

from sd_model_manager.registry.history_service import HistoryService
from sd_model_manager.registry.models import DownloadHistory
from sd_model_manager.config import Config

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["history"])

# グローバルに履歴サービスを保持
_history_service: Optional[HistoryService] = None


def get_history_service() -> HistoryService:
    """履歴サービスのシングルトン取得"""
    global _history_service
    if _history_service is None:
        config = Config()
        history_file = Path("data") / "download_history.json"
        _history_service = HistoryService(history_file=history_file)
    return _history_service


@router.get("", response_model=List[DownloadHistory])
async def get_all_histories(
    model_type: Optional[str] = Query(None, description="モデルタイプでフィルタ")
):
    """全履歴を取得"""
    service = get_history_service()

    if model_type:
        histories = service.filter_by_type(model_type)
    else:
        histories = service.get_all()

    logger.info("Retrieved %d histories (filter=%s)", len(histories), model_type)
    return histories


@router.get("/search", response_model=List[DownloadHistory])
async def search_histories(q: str = Query(..., description="検索クエリ")):
    """履歴を検索"""
    service = get_history_service()
    results = service.search(q)

    logger.info("Search query=%s, found=%d", q, len(results))
    return results


@router.get("/{history_id}", response_model=DownloadHistory)
async def get_history_by_id(history_id: str):
    """IDで履歴を取得"""
    service = get_history_service()
    history = service.get_by_id(history_id)

    if not history:
        logger.warning("History not found: id=%s", history_id)
        raise HTTPException(status_code=404, detail="History not found")

    return history


@router.delete("/{history_id}")
async def delete_history(history_id: str):
    """履歴を削除"""
    service = get_history_service()
    deleted = service.delete(history_id)

    if not deleted:
        logger.warning("History not found for deletion: id=%s", history_id)
        raise HTTPException(status_code=404, detail="History not found")

    logger.info("Deleted history: id=%s", history_id)
    return {"status": "deleted", "id": history_id}
```

**ファイル**: `src/sd_model_manager/ui/api/main.py`（履歴ルーターを登録）

```python
from sd_model_manager.ui.api.history import router as history_router

def create_app(config: Config | None = None) -> FastAPI:
    # ... 既存のコード ...

    # ルーター登録
    app.include_router(health_router)
    app.include_router(history_router)  # 追加
    logger.info("History router registered")

    # ... 既存のコード ...
```

---

## Phase 3.7: ダウンロード完了時の履歴自動保存 ⏳

**種別**: TDD
**状態**: ⏳ 未実装

### 実装内容

- DownloadService に履歴保存機能を統合
- ダウンロード完了時に自動的に HistoryService.add() を呼び出し
- Civitai API から取得したメタデータを履歴に保存

---

## Phase 3.8: 履歴削除機能のテスト・実装 ⏳

**種別**: TDD
**状態**: ⏳ 未実装

### 実装内容

- 履歴削除エンドポイントのテスト
- 削除時のバリデーション
- エラーハンドリング

---

## Phase 3.9: History タブ UI 実装 ⏳

**種別**: 統合
**状態**: ⏳ 未実装

### 🎯 実装目標

ダウンロード履歴を視覚的に管理できる UI を提供し、モデルの検索・フィルタリング・削除・再ダウンロードを可能にする。

### 📦 追加コンポーネント

Phase 2.9 の基本レイアウト（Sidebar, MainLayout）を拡張：

```
src/sd_model_manager/ui/frontend/src/
├── components/
│   ├── history/
│   │   ├── HistoryList.tsx        # 履歴一覧表示
│   │   ├── HistoryCard.tsx        # 各履歴カード（グリッド表示用）
│   │   ├── HistoryRow.tsx         # 各履歴行（リスト表示用）
│   │   └── FilterBar.tsx          # カテゴリ・検索フィルタ
│   └── common/
│       ├── SearchBar.tsx          # 検索バー
│       └── ViewToggle.tsx         # グリッド/リスト切替
├── pages/
│   └── HistoryPage.tsx            # History タブメインページ
└── hooks/
    └── useHistory.ts              # 履歴取得・削除ロジック
```

### 🔨 実装ステップ

#### Step 1: 履歴一覧コンポーネント

**参考**: `reference_git_clones/civitiai-tools/civitai-downloader-v2/src/web/pages/LocalModels.tsx`

```tsx
// src/pages/HistoryPage.tsx
import { useState } from 'react';
import { useHistory } from '../hooks/useHistory';
import { HistoryList } from '../components/history/HistoryList';
import { FilterBar } from '../components/history/FilterBar';
import { SearchBar } from '../components/common/SearchBar';

export const HistoryPage = () => {
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState<string>('');

  const { data: histories, isLoading } = useHistory({
    modelType: categoryFilter !== 'all' ? categoryFilter : undefined,
    search: searchQuery
  });

  return (
    <div className="p-8">
      <h2 className="text-2xl font-bold mb-6">Download History</h2>

      <div className="flex gap-4 mb-6">
        <FilterBar
          category={categoryFilter}
          onCategoryChange={setCategoryFilter}
        />
        <SearchBar
          value={searchQuery}
          onChange={setSearchQuery}
        />
        <ViewToggle mode={viewMode} onModeChange={setViewMode} />
      </div>

      {isLoading ? (
        <div>Loading...</div>
      ) : (
        <HistoryList histories={histories} viewMode={viewMode} />
      )}
    </div>
  );
};
```

#### Step 2: API連携（react-query）

```tsx
// src/hooks/useHistory.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

interface UseHistoryOptions {
  modelType?: string;
  search?: string;
}

export const useHistory = (options: UseHistoryOptions = {}) => {
  const { modelType, search } = options;

  return useQuery({
    queryKey: ['histories', modelType, search],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (modelType) params.append('model_type', modelType);
      if (search) params.append('q', search);

      const response = await fetch(
        `http://localhost:8000/api/history?${params}`
      );
      return response.json();
    }
  });
};

export const useDeleteHistory = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (taskId: string) => {
      await fetch(`http://localhost:8000/api/history/${taskId}`, {
        method: 'DELETE'
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['histories'] });
    }
  });
};
```

#### Step 3: 左サイドバー拡張（カテゴリタブ）

Phase 2.9 で作成した Sidebar.tsx を拡張し、LoRA / Checkpoint / VAE / Embedding タブを追加：

```tsx
// src/components/layout/Sidebar.tsx（拡張版）
import { Download, History, Sparkles, Box, Layers, FileText } from 'lucide-react';

export const Sidebar = () => {
  return (
    <nav className="w-64 bg-gray-900 text-white h-screen p-4">
      <h1 className="text-xl font-bold mb-8">SD Model Manager</h1>

      {/* メインナビゲーション */}
      <ul className="space-y-2 mb-8">
        <li>
          <a href="/download" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
            <Download size={20} />
            <span>Download</span>
          </a>
        </li>
        <li>
          <a href="/history" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
            <History size={20} />
            <span>History</span>
          </a>
        </li>
      </ul>

      {/* カテゴリナビゲーション */}
      <div className="border-t border-gray-700 pt-4">
        <h3 className="text-sm text-gray-400 mb-2">Categories</h3>
        <ul className="space-y-2">
          <li>
            <a href="/history?category=lora" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
              <Sparkles size={18} />
              <span>LoRA</span>
            </a>
          </li>
          <li>
            <a href="/history?category=checkpoint" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
              <Box size={18} />
              <span>Checkpoint</span>
            </a>
          </li>
          <li>
            <a href="/history?category=vae" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
              <Layers size={18} />
              <span>VAE</span>
            </a>
          </li>
          <li>
            <a href="/history?category=embedding" className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded">
              <FileText size={18} />
              <span>Embedding</span>
            </a>
          </li>
        </ul>
      </div>
    </nav>
  );
};
```

### 📋 テスト方針

React Testing Library でコンポーネント単体テスト：
- 履歴一覧の表示
- カテゴリフィルタの動作
- 検索機能の動作
- 削除ボタンの動作
- グリッド/リスト表示の切替

E2E テストは Phase 3.10 で実施。

### 🎯 完了条件

- ✅ 履歴一覧がグリッド/リスト形式で表示される
- ✅ カテゴリ（LoRA / Checkpoint / VAE / Embedding）でフィルタできる
- ✅ 検索機能が動作する
- ✅ 削除ボタンで履歴を削除できる
- ✅ 左サイドバーのカテゴリタブが動作する

---

## Phase 3.10: E2Eテスト（履歴フロー全体） ⏳

**種別**: TDD
**状態**: ⏳ 未実装

### 実装内容

- Playwright によるブラウザテスト
- ダウンロード → 履歴自動保存 → 履歴表示の一連のフロー
- 履歴検索・フィルタリングのテスト
- 履歴削除のテスト

---

## 次のステップ

Phase 3 完了後:

1. **MVP 完了確認**
   - 全機能動作確認
   - バグ修正
   - ドキュメント整備

2. **Phase 4: 新着LoRA 自動検出機能**
   - Civitai API ポーリング
   - 新着検出アルゴリズム
   - 新着タブ UI

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
