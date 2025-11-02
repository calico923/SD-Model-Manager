# ログ戦略ドキュメント

## 概要

SD-Model-Managerのログシステムは、ダウンロード処理の追跡、デバッグ、監査を目的として設計されています。

## ログ設定

### 基本設定

**設定ファイル**: `src/sd_model_manager/lib/logging_config.py`

- **ログレベル**: INFO（設定可能）
- **ログファイル**: `./logs/app.log`
- **ローテーション**: 10MB/ファイル、最大3ファイル保持
- **エンコーディング**: UTF-8
- **フォーマット**: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

### ログディレクトリ

デフォルトで `./logs/` ディレクトリにログファイルが保存されます。ディレクトリは自動作成されます。

## ダウンロードログの詳細

### 1. ダウンロードタスク作成時

```
INFO - sd_model_manager.ui.api.download - Download task created: task_id=<uuid>, url=<civitai_url>, filename=<filename>
```

**含まれる情報**:
- `task_id`: ダウンロードタスクの一意識別子
- `url`: ダウンロード元URL
- `filename`: サニタイズ後の安全なファイル名

### 2. メタデータからのファイル名抽出（Phase 2.12）

#### 抽出開始
```
INFO - sd_model_manager.ui.api.download - Extracting filename from metadata: url=<civitai_url>
```

#### 抽出成功
```
INFO - sd_model_manager.ui.api.download - Filename extracted successfully: filename=<extracted_filename>, url=<civitai_url>
```

#### ユーザー指定ファイル名使用
```
INFO - sd_model_manager.ui.api.download - Using user-provided filename: filename=<user_filename>
```

### 3. ダウンロード開始

```
INFO - sd_model_manager.ui.api.download - Starting download: task_id=<uuid>, url=<civitai_url>, filename=<filename>
```

### 4. ダウンロード完了

```
INFO - sd_model_manager.ui.api.download - Download completed successfully: task_id=<uuid>, filename=<filename>, absolute_path=<full_path>, file_size=<bytes> bytes (<MB> MB), elapsed_time=<seconds> seconds
```

**含まれる情報**:
- `task_id`: タスク識別子
- `filename`: ファイル名
- `absolute_path`: 保存先の絶対パス
- `file_size`: ダウンロードされたファイルサイズ（バイトとMB）
- `elapsed_time`: ダウンロード所要時間（秒）

**例**:
```
INFO - sd_model_manager.ui.api.download - Download completed successfully: task_id=a1b2c3d4-e5f6-7890-abcd-ef1234567890, filename=awesome-model-v1.safetensors, absolute_path=/Users/user/Code/SD-Model-Manager/downloads/awesome-model-v1.safetensors, file_size=2147483648 bytes (2048.00 MB), elapsed_time=127.45 seconds
```

### 5. ダウンロード失敗

```
ERROR - sd_model_manager.ui.api.download - Download failed: task_id=<uuid>, filename=<filename>, url=<url>, error=<error_message>, elapsed_time=<seconds> seconds
Traceback (most recent call last):
  ...
```

**含まれる情報**:
- `task_id`: タスク識別子
- `filename`: ファイル名
- `url`: ダウンロード元URL
- `error`: エラーメッセージ
- `elapsed_time`: 失敗までの所要時間
- スタックトレース（`exc_info=True`）

## DownloadServiceのログ

### Civitai URL解決

```
INFO - sd_model_manager.download.download_service - Resolving Civitai download URL: <civitai_url>
INFO - sd_model_manager.download.download_service - Resolved download URL: <direct_download_url>
```

### リトライ処理

```
WARNING - sd_model_manager.download.download_service - Download failed (attempt <n>/<max>), retrying: <error>
```

## ログの活用

### ダウンロード監査

特定のタスクIDで検索：
```bash
grep "task_id=a1b2c3d4" logs/app.log
```

### パフォーマンス分析

ダウンロード時間の確認：
```bash
grep "elapsed_time=" logs/app.log | grep "Download completed"
```

### ファイル保存先の確認

絶対パスの検索：
```bash
grep "absolute_path=" logs/app.log
```

### エラー分析

失敗したダウンロードの確認：
```bash
grep "Download failed" logs/app.log
```

## セキュリティログ（Phase 2.11）

パストラバーサル攻撃の試行は、HTTP 400エラーとして記録されます：

```
WARNING - uvicorn.access - 400 Bad Request - POST /api/download
```

詳細はアプリケーションログに記録されます。

## ログローテーション

### 自動ローテーション

- ファイルサイズが10MBに達すると自動的にローテーション
- 最大3世代のバックアップファイルを保持
- 古いファイルは自動削除

### ファイル名規則

```
logs/app.log        # 現在のログファイル
logs/app.log.1      # 1世代前
logs/app.log.2      # 2世代前
logs/app.log.3      # 3世代前（これ以上古いものは削除）
```

## ベストプラクティス

### 運用推奨事項

1. **定期的なログ確認**: 週次でログを確認し、異常なパターンを検出
2. **ディスク容量監視**: ログディレクトリの容量を監視
3. **長期保存**: 監査目的で、重要なログは外部ストレージにバックアップ
4. **ログレベル調整**: 開発時はDEBUG、本番環境はINFO推奨

### トラブルシューティング

#### ダウンロードが完了しているか確認

```bash
grep "Download completed successfully" logs/app.log | tail -n 10
```

#### 特定ファイルのダウンロード状況

```bash
grep "filename=my-model.safetensors" logs/app.log
```

#### メタデータ抽出の成否

```bash
grep "Filename extracted" logs/app.log
```

## 今後の拡張予定

### Phase 3以降

- ダウンロード履歴のデータベース記録
- ダッシュボードでのログ可視化
- 統計情報の集計（平均ダウンロード時間、成功率など）
- アラート機能（失敗率が一定以上の場合）

---

**更新日**: 2025-10-30
**バージョン**: Phase 2.12
**ステータス**: 実装済み
