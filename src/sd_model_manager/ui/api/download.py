"""ダウンロードAPIルーター"""

import logging
import time
import uuid
from pathlib import Path
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel, HttpUrl

from sd_model_manager.download.download_service import DownloadService
from sd_model_manager.download.civitai_client import CivitaiClient
from sd_model_manager.config import Config
from sd_model_manager.ui.api.progress import get_progress_manager

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/download", tags=["download"])


def sanitize_filename(filename: str) -> str:
    """
    ファイル名をサニタイズして、パストラバーサル攻撃を防ぐ。

    Args:
        filename: サニタイズするファイル名

    Returns:
        サニタイズされたファイル名

    Raises:
        HTTPException: 不正なファイル名の場合（status_code=400）
    """
    # 空文字チェック
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="Filename cannot be empty")

    filename = filename.strip()

    # ディレクトリセパレータをチェック（Unix/Windows両対応）
    if '/' in filename or '\\' in filename:
        raise HTTPException(
            status_code=400,
            detail="Filename cannot contain path separators (/ or \\)"
        )

    # 相対パス（..）をチェック
    if '..' in filename:
        raise HTTPException(
            status_code=400,
            detail="Filename cannot contain '..'"
        )

    # 絶対パスをチェック（Windowsドライブレター含む）
    if filename.startswith('/'):
        raise HTTPException(
            status_code=400,
            detail="Filename cannot be an absolute path"
        )

    # Windowsドライブレター（C:, D:など）をチェック
    if len(filename) > 1 and filename[1] == ':':
        raise HTTPException(
            status_code=400,
            detail="Filename cannot contain drive letters"
        )

    # NULL文字をチェック
    if '\0' in filename:
        raise HTTPException(
            status_code=400,
            detail="Filename cannot contain null characters"
        )

    return filename


async def extract_filename_from_metadata(url: str, civitai_client: CivitaiClient) -> str:
    """
    Civitai APIメタデータからファイル名を抽出する（Phase 2.12）

    Args:
        url: Civitai URL
        civitai_client: CivitaiClientインスタンス

    Returns:
        抽出されたファイル名

    Raises:
        DownloadError: メタデータ取得失敗時
    """
    try:
        # メタデータを取得
        metadata = await civitai_client.get_model_metadata(url)

        # modelVersions[0].files[0].name からファイル名を抽出
        model_versions = metadata.get("modelVersions", [])
        if not model_versions:
            raise ValueError("No model versions found")

        files = model_versions[0].get("files", [])
        if not files:
            raise ValueError("No files found in model version")

        filename = files[0].get("name")
        if not filename:
            raise ValueError("File name not found in metadata")

        logger.info("Extracted filename from metadata: %s", filename)
        return filename

    except Exception as e:
        # フォールバック: モデルIDから生成
        logger.warning("Failed to extract filename from metadata: %s. Using fallback.", str(e))
        model_id = civitai_client.extract_model_id(url)
        fallback_filename = f"model-{model_id}.safetensors"
        logger.info("Using fallback filename: %s", fallback_filename)
        return fallback_filename


class DownloadRequest(BaseModel):
    """ダウンロードリクエスト"""
    url: HttpUrl  # HttpUrl 型で FastAPI がバリデーション
    filename: str | None = None  # Phase 2.12: オプショナルに変更（メタデータから自動抽出）


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
    # Phase 2.12: filenameが指定されていない場合、メタデータから抽出
    if request.filename is None:
        logger.info("Extracting filename from metadata: url=%s", request.url)
        config = Config()
        civitai_client = CivitaiClient(api_key=config.civitai_api_key)
        try:
            filename = await extract_filename_from_metadata(str(request.url), civitai_client)
            logger.info("Filename extracted successfully: filename=%s, url=%s", filename, request.url)
        finally:
            await civitai_client.close()
    else:
        filename = request.filename
        logger.info("Using user-provided filename: filename=%s", filename)

    # ファイル名をサニタイズ（パストラバーサル攻撃を防ぐ）
    safe_filename = sanitize_filename(filename)

    # バックグラウンドタスクでダウンロード実行
    task_id = str(uuid.uuid4())
    progress_manager = get_progress_manager()

    # プログレス情報を初期化
    progress_manager.create_task(
        task_id=task_id,
        filename=safe_filename,
        total_bytes=0
    )

    background_tasks.add_task(
        execute_download,
        task_id=task_id,
        url=str(request.url),  # HttpUrl を文字列に変換
        filename=safe_filename
    )

    logger.info("Download task created: task_id=%s, url=%s, filename=%s", task_id, request.url, safe_filename)

    return DownloadResponse(
        task_id=task_id,
        status="started"
    )


async def execute_download(task_id: str, url: str, filename: str, download_service: DownloadService | None = None):
    """ダウンロード実行（バックグラウンド）

    注意: テストでは download_service を差し替え可能。
    本番では Config から DownloadService を生成。

    プログレスコールバックを定義してダウンロード中にプログレス情報を更新。
    """
    progress_manager = get_progress_manager()
    start_time = time.time()  # ダウンロード開始時刻

    def progress_callback(downloaded: int, total: int) -> None:
        """ダウンロード進捗コールバック"""
        progress_manager.update_progress(task_id, downloaded, total)

    if download_service is None:
        config = Config()
        civitai_client = CivitaiClient(api_key=config.civitai_api_key)
        download_service = DownloadService(
            download_dir=config.download_dir,
            civitai_client=civitai_client
        )

    try:
        logger.info("Starting download: task_id=%s, url=%s, filename=%s", task_id, url, filename)

        # ダウンロード実行
        downloaded_path = await download_service.download_file(url, filename, progress_callback=progress_callback)

        # ダウンロード完了後の情報収集
        elapsed_time = time.time() - start_time
        file_size = downloaded_path.stat().st_size
        absolute_path = downloaded_path.resolve()

        # 詳細ログ出力
        logger.info(
            "Download completed successfully: task_id=%s, filename=%s, "
            "absolute_path=%s, file_size=%d bytes (%.2f MB), elapsed_time=%.2f seconds",
            task_id, filename, absolute_path, file_size, file_size / (1024 * 1024), elapsed_time
        )

        progress_manager.complete_task(task_id)
    except Exception as e:
        elapsed_time = time.time() - start_time
        logger.error(
            "Download failed: task_id=%s, filename=%s, url=%s, error=%s, elapsed_time=%.2f seconds",
            task_id, filename, url, str(e), elapsed_time, exc_info=True
        )
        progress_manager.fail_task(task_id, str(e))
