# ログ実装ドキュメント (Logging Implementation)

## 概要

SD-Model-Managerのログ実装は、**標準出力を最小化し、ファイル出力を優先する**戦略を採用しています。開発環境・本番環境の両方で、詳細なログをファイルに記録しながら、コンソール出力をクリーンに保ちます。

## 設計方針

### コアプリンシプル

1. **標準出力最小化**: コンソール出力はuvicorn起動メッセージのみ
2. **ファイル出力優先**: すべてのアプリケーションログは `logs/app.log` に出力
3. **ログローテーション**: 10MB毎に自動ローテーション、最大3ファイル保持
4. **構造化フォーマット**: タイムスタンプ、モジュール名、ログレベル、メッセージを含む
5. **環境変数対応**: `.env` ファイルでログレベル・ディレクトリを設定可能

### ログレベル戦略

| レベル | 用途 | 出力例 |
|--------|------|--------|
| **DEBUG** | 開発環境のみ（詳細なトレース） | 変数の値、関数呼び出し順序 |
| **INFO** | 通常の操作 | ダウンロード開始/完了、API呼び出し、起動処理 |
| **WARNING** | 注意が必要な事象 | リトライ実行、レート制限、アクセス拒否 |
| **ERROR** | エラー | ダウンロード失敗、APIエラー、認証失敗 |
| **CRITICAL** | システム停止レベルのエラー | （現在未使用） |

## 実装詳細

### ファイル構成

```
src/sd_model_manager/
├── lib/
│   └── logging_config.py          # ロギングシステム設定
├── download/
│   ├── download_service.py        # ダウンロード処理ログ
│   └── civitai_client.py          # Civitai API ログ
├── ui/api/
│   └── main.py                    # FastAPI アプリログ
├── lib/
│   └── errors.py                  # エラーハンドラーログ
└── __main__.py                    # 起動処理ログ

tests/sd_model_manager/lib/
└── test_logging_config.py         # ロギングテスト (6 tests)

logs/
├── app.log                        # 現在のログ
├── app.log.1                      # 1つ前のローテーション
├── app.log.2                      # 2つ前のローテーション
└── app.log.3                      # 3つ前のローテーション
```

### コアモジュール: `logging_config.py`

#### `setup_logging()` 関数

```python
def setup_logging(
    log_level: str = "INFO",
    log_dir: Path = Path("./logs"),
    log_max_bytes: int = 10 * 1024 * 1024,  # 10MB
    log_backup_count: int = 3
) -> None:
    """ロギングシステムをセットアップ"""
```

**機能**:
- ログディレクトリ自動作成
- RotatingFileHandler設定（自動ローテーション）
- ログレベル設定
- フォーマット設定: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
- uvicorn/FastAPIのログもファイルに統合

#### `get_logger()` 関数

```python
def get_logger(name: str) -> logging.Logger:
    """モジュール用のロガーを取得"""
    return logging.getLogger(name)
```

**使用例**:
```python
import logging
logger = logging.getLogger(__name__)

logger.info("Processing started")
logger.warning("Retry attempt 2/3")
logger.error("Operation failed: %s", error_message)
```

### 設定ファイル: `config.py`

#### ログ設定項目

```python
class Config(BaseSettings):
    # Logging settings
    log_level: str = "INFO"
    log_dir: Path = Path("./logs")
    log_max_bytes: int = 10 * 1024 * 1024  # 10MB
    log_backup_count: int = 3
```

#### 環境変数 (`.env`)

```env
# Logging Configuration
LOG_LEVEL=INFO                 # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_DIR=./logs                 # ログファイル保存ディレクトリ
LOG_MAX_BYTES=10485760         # 10MB (ローテーションサイズ)
LOG_BACKUP_COUNT=3             # 保持するバックアップファイル数
```

### 起動処理: `__main__.py`

```python
def main():
    config = Config()

    # ロギングをセットアップ（標準出力を最小化）
    setup_logging(
        log_level=config.log_level,
        log_dir=config.log_dir,
        log_max_bytes=config.log_max_bytes,
        log_backup_count=config.log_backup_count
    )

    logger.info("=" * 60)
    logger.info("Starting SD-Model-Manager application")
    logger.info("=" * 60)

    # FastAPIアプリケーションを作成
    app = create_app(config)

    # uvicorn設定（標準出力を最小化）
    log_config = uvicorn.config.LOGGING_CONFIG
    log_config["loggers"]["uvicorn.access"]["handlers"] = []  # アクセスログ無効化
    log_config["loggers"]["uvicorn.error"]["handlers"] = []   # エラーログ無効化

    uvicorn.run(app, host=config.host, port=config.port, log_config=log_config)
```

## ログ出力箇所

### 1. ダウンロードサービス (`download_service.py`)

```python
logger.info("Starting download: url=%s, filename=%s", url, filename)
logger.info("Resolving Civitai download URL: %s", url)
logger.info("Resolved download URL: %s", download_url)
logger.info("Download completed: filename=%s, path=%s", filename, result)
logger.warning("Download failed (attempt %d/%d), retrying: %s", attempt + 1, max_retries, str(e))
logger.error("Download failed after %d attempts: url=%s, error=%s", max_retries, url, str(e))
```

### 2. Civitai API クライアント (`civitai_client.py`)

```python
logger.info("Fetching model data from Civitai API: model_id=%s", model_id)
logger.info("Successfully fetched model data: model_id=%s", model_id)
logger.error("API authentication failed: model_id=%s, status=%d", model_id, status_code)
logger.warning("API access forbidden: model_id=%s, status=%d", model_id, status_code)
logger.warning("Model not found: model_id=%s", model_id)
logger.warning("API rate limit exceeded: model_id=%s", model_id)
logger.error("API request failed: model_id=%s, status=%d", model_id, status_code)
logger.error("Network error while fetching model data: model_id=%s, error=%s", model_id, str(e))
```

### 3. FastAPI アプリケーション (`main.py`)

```python
logger.info("Creating FastAPI application")
logger.info("Configuration: host=%s, port=%d, download_dir=%s", config.host, config.port, config.download_dir)
logger.info("CORS middleware configured")
logger.info("Health router registered")
logger.info("Error handlers registered")
logger.info("FastAPI application created successfully")
```

### 4. エラーハンドラー (`errors.py`)

```python
logger.error("Application error: code=%s, message=%s, path=%s, details=%s",
             exc.code, exc.message, request.url.path, exc.details)
logger.warning("Endpoint not found: path=%s", request.url.path)
```

## 使用方法

### 起動

```bash
# デフォルト設定（INFO レベル）
python -m sd_model_manager

# 環境変数でログレベル変更
LOG_LEVEL=DEBUG python -m sd_model_manager

# .envファイルで設定
echo "LOG_LEVEL=DEBUG" >> .env
python -m sd_model_manager
```

### ログ確認

```bash
# リアルタイムログ監視
tail -f logs/app.log

# 最新100行を表示
tail -n 100 logs/app.log

# エラーログのみ表示
grep "ERROR" logs/app.log

# 特定の文字列を含むログを表示
grep "download" logs/app.log

# 全ログファイルから検索
grep -r "civitai" logs/
```

### 開発時のログレベル推奨

| 環境 | LOG_LEVEL | 用途 |
|------|-----------|------|
| **開発** | DEBUG | 詳細なデバッグ情報 |
| **テスト** | INFO | 通常の動作確認 |
| **本番** | INFO または WARNING | 必要最小限のログ |

## ログサンプル

### 起動時

```
2025-01-14 10:30:15 - sd_model_manager.__main__ - INFO - ============================================================
2025-01-14 10:30:15 - sd_model_manager.__main__ - INFO - Starting SD-Model-Manager application
2025-01-14 10:30:15 - sd_model_manager.__main__ - INFO - ============================================================
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - Creating FastAPI application
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - Configuration: host=127.0.0.1, port=8188, download_dir=./downloads
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - CORS middleware configured
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - Health router registered
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - Error handlers registered
2025-01-14 10:30:15 - sd_model_manager.ui.api.main - INFO - FastAPI application created successfully
2025-01-14 10:30:15 - sd_model_manager.__main__ - INFO - Starting uvicorn server at http://127.0.0.1:8188
```

### ダウンロード処理

```
2025-01-14 10:35:20 - sd_model_manager.download.download_service - INFO - Starting download: url=https://civitai.com/models/123456, filename=test-lora.safetensors
2025-01-14 10:35:20 - sd_model_manager.download.download_service - INFO - Resolving Civitai download URL: https://civitai.com/models/123456
2025-01-14 10:35:20 - sd_model_manager.download.civitai_client - INFO - Fetching model data from Civitai API: model_id=123456
2025-01-14 10:35:21 - sd_model_manager.download.civitai_client - INFO - Successfully fetched model data: model_id=123456
2025-01-14 10:35:21 - sd_model_manager.download.download_service - INFO - Resolved download URL: https://civitai.com/api/download/models/123456
2025-01-14 10:35:25 - sd_model_manager.download.download_service - INFO - Download completed: filename=test-lora.safetensors, path=/Users/user/downloads/test-lora.safetensors
```

### エラー発生時（リトライ含む）

```
2025-01-14 10:40:10 - sd_model_manager.download.download_service - INFO - Starting download: url=https://example.com/model.safetensors, filename=test.safetensors
2025-01-14 10:40:11 - sd_model_manager.download.download_service - WARNING - Download failed (attempt 1/3), retrying: Server disconnected
2025-01-14 10:40:13 - sd_model_manager.download.download_service - WARNING - Download failed (attempt 2/3), retrying: Server disconnected
2025-01-14 10:40:16 - sd_model_manager.download.download_service - ERROR - Download failed after 3 attempts: url=https://example.com/model.safetensors, error=Server disconnected
```

### API エラー（レート制限）

```
2025-01-14 11:00:45 - sd_model_manager.download.civitai_client - INFO - Fetching model data from Civitai API: model_id=789012
2025-01-14 11:00:46 - sd_model_manager.download.civitai_client - WARNING - API rate limit exceeded: model_id=789012
```

## トラブルシューティング

### ログファイルが作成されない

**原因**: ログディレクトリの書き込み権限がない

**解決策**:
```bash
# ディレクトリの権限を確認
ls -ld logs/

# 権限を付与
chmod 755 logs/
```

### ログが出力されない

**原因**: ログレベルが高すぎる

**解決策**:
```bash
# .envファイルを確認
cat .env | grep LOG_LEVEL

# ログレベルをDEBUGに変更
echo "LOG_LEVEL=DEBUG" >> .env
```

### ログファイルが肥大化する

**原因**: ログローテーションが動作していない、またはログ出力が多すぎる

**解決策**:
```bash
# ログローテーション設定を確認
cat .env | grep LOG_MAX_BYTES
cat .env | grep LOG_BACKUP_COUNT

# 古いログを手動削除
rm logs/app.log.*

# ログレベルを上げる（INFOまたはWARNING）
echo "LOG_LEVEL=WARNING" >> .env
```

### 標準出力にログが出る

**原因**: `setup_logging()` が正しく呼ばれていない、またはuvicorn設定が正しくない

**解決策**:
```python
# __main__.py で setup_logging() が呼ばれているか確認
# uvicorn の log_config が正しく設定されているか確認
```

## テスト

### ログ機能のテスト

```bash
# ログ設定テストを実行
python -m pytest tests/sd_model_manager/lib/test_logging_config.py -v

# 全テストを実行（ログテスト含む）
python -m pytest tests/ -v
```

### テストカバレッジ

- `test_setup_logging_creates_log_directory`: ログディレクトリ作成
- `test_setup_logging_creates_log_file`: ログファイル作成
- `test_setup_logging_sets_correct_log_level`: ログレベル設定
- `test_setup_logging_with_info_level`: ログレベルフィルタリング
- `test_get_logger_returns_logger`: ロガー取得
- `test_setup_logging_writes_to_file`: ファイル書き込み

## ベストプラクティス

### ログメッセージの書き方

✅ **Good**:
```python
logger.info("Starting download: url=%s, filename=%s", url, filename)
logger.error("API request failed: model_id=%s, status=%d", model_id, status_code)
```

❌ **Bad**:
```python
logger.info(f"Starting download: url={url}, filename={filename}")  # f-string は非効率
logger.info("Starting download")  # コンテキスト情報が不足
```

### 機密情報の除外

❌ **絶対にログに出力してはいけない情報**:
- API キー (`CIVITAI_API_KEY`)
- ユーザートークン
- パスワード
- 個人情報（PII）

✅ **安全なログ出力**:
```python
# API キーの最初の4文字のみ
logger.info("API key configured: %s****", api_key[:4] if api_key else "None")

# URLからクエリパラメータを除外
from urllib.parse import urlparse
parsed = urlparse(url)
safe_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
logger.info("Fetching from: %s", safe_url)
```

### ログレベルの使い分け

```python
# DEBUG: 開発時のデバッグ情報
logger.debug("Variable value: x=%d, y=%d", x, y)

# INFO: 通常の操作・フロー
logger.info("Download started: filename=%s", filename)

# WARNING: 注意が必要だが処理は継続
logger.warning("Retry attempt %d/%d", attempt, max_retries)

# ERROR: エラーが発生したが処理は継続可能
logger.error("Failed to fetch data: %s", error_message)

# CRITICAL: システム停止レベルのエラー
logger.critical("Database connection lost, shutting down")
```

## 今後の拡張予定

### Phase 3以降で検討

1. **構造化ログ (JSON形式)**
   - `structlog` ライブラリの導入
   - ELK Stack / CloudWatch との連携
   - リクエストID によるトレーシング

2. **ログ分析・監視**
   - ログ集約ツール（Fluentd, Logstash）
   - ダッシュボード（Kibana, Grafana）
   - アラート設定

3. **パフォーマンスログ**
   - レスポンスタイム計測
   - スループット監視
   - リソース使用状況

## まとめ

- ✅ 標準出力を最小化し、ファイル出力を優先
- ✅ 自動ログローテーション（10MB毎、最大3ファイル）
- ✅ 環境変数で設定可能（LOG_LEVEL, LOG_DIR）
- ✅ uvicorn/FastAPI のログもファイルに統合
- ✅ 6つのテストで品質保証
- ✅ 開発環境で `tail -f logs/app.log` で確認可能

**実装完了**: Phase 2終了時点（2025-01-14）
