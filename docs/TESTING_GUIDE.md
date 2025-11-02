# テストガイド

## 概要

SD-Model-Managerのテストは、ユニットテストと統合テストの2層構造になっています。

## テスト構造

### ユニットテスト
- **目的**: 個別の機能をモックを使用して高速にテスト
- **実行時間**: 3秒程度
- **外部依存**: なし（すべてモック）

### 統合テスト
- **目的**: 実際のCivitai APIとの連携をテスト
- **実行時間**: 14秒程度
- **外部依存**: Civitai API（インターネット接続必須）
- **マーカー**: `@pytest.mark.integration`

## テストの実行

### すべてのテストを実行
```bash
python -m pytest tests/ -v
```

### ユニットテストのみ実行
```bash
python -m pytest tests/ -v -m "not integration"
```

### 統合テストのみ実行
```bash
python -m pytest tests/ -v -m "integration"
```

### 特定のファイルのテスト
```bash
python -m pytest tests/sd_model_manager/ui/api/test_download_endpoint.py -v
```

### カバレッジレポート付き
```bash
python -m pytest tests/ --cov=src/sd_model_manager --cov-report=html
```

## ダウンロードエンドポイントのテスト

### テストURL

実際のCivitai URLを使用してテストを実施しています：

- **LoRA**: `https://civitai.com/models/1998509`
- **Checkpoint**: `https://civitai.com/models/827184?modelVersionId=2167369`
- **テスト用**: `https://civitai.com/models/999999999`（バリデーションテスト用）

### ユニットテスト（12件）

1. **基本機能テスト**
   - `test_download_endpoint_accepts_post`: POSTリクエストを受け付ける
   - `test_download_endpoint_validates_url`: 無効なURLを拒否する
   - `test_download_endpoint_returns_task_id`: タスクIDを返す

2. **セキュリティテスト（Phase 2.11）**
   - `test_download_endpoint_rejects_path_traversal_dotdot`: パストラバーサル攻撃（`..`）を拒否
   - `test_download_endpoint_rejects_absolute_path`: 絶対パスを拒否
   - `test_download_endpoint_rejects_directory_separator`: ディレクトリセパレータを拒否
   - `test_download_endpoint_rejects_windows_path`: Windowsパスを拒否
   - `test_download_endpoint_rejects_empty_filename`: 空のファイル名を拒否
   - `test_download_endpoint_accepts_safe_filename`: 安全なファイル名を受け入れる

3. **メタデータ抽出テスト（Phase 2.12）**
   - `test_download_endpoint_accepts_url_only_request`: URLのみのリクエストを受け付ける
   - `test_download_endpoint_extracts_filename_from_metadata`: メタデータからファイル名を抽出
   - `test_download_endpoint_handles_metadata_extraction_failure`: メタデータ取得失敗時のフォールバック

### 統合テスト（3件）

1. **実際のCivitai URLテスト**
   - `test_download_endpoint_with_real_lora_url`: 実際のLoRA URLでメタデータ抽出
   - `test_download_endpoint_with_real_checkpoint_url`: 実際のCheckpoint URLでメタデータ抽出
   - `test_download_endpoint_with_version_id_parameter`: `modelVersionId`パラメータ付きURLでテスト

## テスト結果

### 最新のテスト結果（2025-10-30）

```
50/50 tests PASSING ✅
- Phase 1: 35 tests
- Phase 2.6-2.7: 3 tests (download endpoint)
- Phase 2.11: 6 tests (security)
- Phase 2.12: 3 tests (metadata extraction)
- Phase 2.14: 3 tests (integration with real Civitai API)
```

### ユニットテスト
- **実行時間**: ~3秒
- **結果**: 12/12 PASSING

### 統合テスト
- **実行時間**: ~14秒
- **結果**: 3/3 PASSING
- **確認項目**:
  - 実際のLoRA URLからメタデータ取得成功
  - 実際のCheckpoint URLからメタデータ取得成功
  - `modelVersionId`パラメータの正常処理

## CI/CDでの実行

### 推奨設定

```yaml
# GitHub Actions example
- name: Run unit tests
  run: pytest tests/ -v -m "not integration"

- name: Run integration tests
  run: pytest tests/ -v -m "integration"
  # インターネット接続が必要
```

### ローカル開発

開発中は統合テストをスキップして高速にテストを実行できます：

```bash
# 高速テスト（ユニットテストのみ）
pytest tests/ -m "not integration"

# 完全テスト（統合テスト含む）
pytest tests/
```

## トラブルシューティング

### 統合テストの失敗

**原因**: インターネット接続またはCivitai APIの一時的な障害

**対処法**:
1. インターネット接続を確認
2. Civitai APIのステータスを確認: https://status.civitai.com
3. 一時的に統合テストをスキップ: `pytest -m "not integration"`

### タイムアウトエラー

**原因**: ネットワークが遅い、またはAPIレスポンスが遅延

**対処法**:
```bash
# タイムアウト時間を延長
pytest tests/ --timeout=60
```

### メタデータ取得エラー

**原因**: Civitai APIの変更、またはモデルが削除された

**対処法**:
1. テストURLが有効か確認
2. 必要に応じて `tests/sd_model_manager/ui/api/test_download_endpoint.py` の `REAL_LORA_URL` と `REAL_CHECKPOINT_URL` を更新

## テストの追加

### 新しいユニットテストの追加

```python
def test_new_feature(test_client):
    """新機能のテスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": TEST_URL,
            # ... test data
        }
    )
    assert response.status_code == 200
```

### 新しい統合テストの追加

```python
@pytest.mark.integration
def test_new_integration(test_client):
    """実際のAPIを使った統合テスト"""
    response = test_client.post(
        "/api/download",
        json={
            "url": REAL_LORA_URL,
            # ... test data
        }
    )
    assert response.status_code == 200
```

## ベストプラクティス

1. **統合テストは最小限に**: ユニットテストで十分カバーできる場合は統合テストを追加しない
2. **実際のURLを使用**: 統合テストでは必ず実際のCivitai URLを使用
3. **テストの独立性**: 各テストは他のテストに依存せず独立して実行可能
4. **明確なテスト名**: テスト名でテスト内容が理解できるようにする
5. **適切なアサーション**: 期待される結果を明確にアサーション

---

**更新日**: 2025-10-30
**バージョン**: Phase 2.14
**ステータス**: 実装済み
