# セキュリティ修正: パストラバーサル脆弱性対策

## 問題概要

**優先度**: P0（最優先）
**発見日**: 2025-10-30
**修正完了日**: 2025-10-30
**影響範囲**: ダウンロードAPIエンドポイント

## 脆弱性の詳細

### 問題点

`src/sd_model_manager/ui/api/download.py:40-51`で、ユーザーから受信した`filename`をサニタイズせずにそのまま`DownloadService`に渡していました。

**攻撃シナリオ**:
```python
# 悪意あるリクエスト
POST /api/download
{
  "url": "https://civitai.com/models/123456",
  "filename": "../../../../etc/ssh/ssh_config"
}
```

**影響**:
- `DownloadService`は`Path(download_dir) / filename`で単純にパスを結合
- `mkdir(..., parents=True)`と`open()`で任意のファイルシステム位置にアクセス可能
- `..`セグメントが`download_dir`から逸脱し、任意ファイルを上書き可能
- バックエンドプロセスの権限で書き込み可能なすべての場所が危険

## 修正内容

### 1. ファイル名サニタイゼーション関数の追加

`sanitize_filename()`関数を実装し、以下をチェック：

```python
def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズして、パストラバーサル攻撃を防ぐ。

    チェック項目:
    - 空文字
    - ディレクトリセパレータ（/, \）
    - 相対パス（..）
    - 絶対パス（/で始まる）
    - Windowsドライブレター（C:, D:など）
    - NULL文字（\0）

    Raises:
        HTTPException: 不正なファイル名の場合（status_code=400）
    """
```

### 2. エンドポイントでの適用

```python
@router.post("", response_model=DownloadResponse)
async def start_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    # ファイル名をサニタイズ（パストラバーサル攻撃を防ぐ）
    safe_filename = sanitize_filename(request.filename)

    # 以降、safe_filenameのみを使用
    progress_manager.create_task(task_id=task_id, filename=safe_filename, ...)
    background_tasks.add_task(execute_download, ..., filename=safe_filename)
```

### 3. 不正な入力の早期拒否

HTTP 400エラーで即座に拒否：

```python
# 例: パストラバーサル試行
{"detail": "Filename cannot contain '..'"}

# 例: 絶対パス
{"detail": "Filename cannot be an absolute path"}

# 例: ディレクトリセパレータ
{"detail": "Filename cannot contain path separators (/ or \\)"}
```

## テストカバレッジ

### 追加したテスト（6個）

1. `test_download_endpoint_rejects_path_traversal_dotdot`
   - 入力: `../../etc/passwd`
   - 期待: HTTP 400

2. `test_download_endpoint_rejects_absolute_path`
   - 入力: `/etc/passwd`
   - 期待: HTTP 400

3. `test_download_endpoint_rejects_directory_separator`
   - 入力: `path/to/file.safetensors`
   - 期待: HTTP 400

4. `test_download_endpoint_rejects_windows_path`
   - 入力: `C:\\Windows\\System32\\config`
   - 期待: HTTP 400

5. `test_download_endpoint_rejects_empty_filename`
   - 入力: `""`
   - 期待: HTTP 400

6. `test_download_endpoint_accepts_safe_filename`
   - 入力: `my-model_v2.safetensors`
   - 期待: HTTP 200/202（正常）

### テスト結果

```
44/44 tests PASSED ✅
- 既存テスト: 38個（リグレッションなし）
- 新規セキュリティテスト: 6個（すべて合格）
```

## TDD方法論

### RED → GREEN → REFACTOR

1. **RED**: セキュリティテストを追加（5個すべてFAILED）
2. **GREEN**: `sanitize_filename()`関数を実装（すべてPASSED）
3. **REFACTOR**: 必要なし（実装がシンプルで明確）

## セキュリティ改善効果

### Before（脆弱）
```python
# 何もチェックせずに直接使用
filename = request.filename  # "../../../../etc/passwd"
download_service.download_file(url, filename)  # 危険！
```

### After（安全）
```python
# サニタイゼーション + 早期拒否
safe_filename = sanitize_filename(request.filename)  # HTTPException(400)
download_service.download_file(url, safe_filename)  # 安全！
```

## 影響を受けるファイル

### 修正したファイル
- `src/sd_model_manager/ui/api/download.py`
  - `sanitize_filename()`関数追加
  - `start_download()`でサニタイゼーション呼び出し

### 追加したテスト
- `tests/sd_model_manager/ui/api/test_download_endpoint.py`
  - セキュリティテスト6個追加

## 今後の推奨事項

### 1. 二重防御（Defense in Depth）

現在の実装:
- ✅ HTTP層でファイル名検証（`sanitize_filename()`）

追加推奨:
- `DownloadService`内でも最終的な書き込みパスを検証
- `Path.resolve()`で絶対パスに解決し、`download_dir`内にあることを確認

```python
# DownloadServiceに追加推奨
def _validate_download_path(self, filename: str) -> Path:
    target_path = (self.download_dir / filename).resolve()
    download_dir_resolved = self.download_dir.resolve()

    try:
        target_path.relative_to(download_dir_resolved)
    except ValueError:
        raise DownloadError(f"Path escapes download directory: {filename}")

    return target_path
```

### 2. 継続的なセキュリティ監査

- 定期的にCodexレビューを実施
- OWASP Top 10に基づく脆弱性スキャン
- 依存ライブラリのセキュリティ更新

### 3. ロギングとモニタリング

- 不正なファイル名の試行をログに記録（現在未実装）
- セキュリティイベントの監視とアラート

```python
# 推奨: sanitize_filename()でロギング追加
if '..' in filename or '/' in filename:
    logger.warning("Malicious filename attempt detected: %s", filename)
    raise HTTPException(...)
```

## 参考資料

- **OWASP**: [Path Traversal](https://owasp.org/www-community/attacks/Path_Traversal)
- **CWE-22**: Improper Limitation of a Pathname to a Restricted Directory
- **CVSS Score**: 7.5 (HIGH) - 修正前の想定評価

---

**修正者**: Claude Code
**レビュー**: Codex (P0 Priority)
**テスト方法**: TDD (RED → GREEN)
**ステータス**: ✅ 修正完了・検証済み
