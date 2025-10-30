"""ダウンロードAPIルーター"""

import logging
import uuid
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
    # ファイル名をサニタイズ（パストラバーサル攻撃を防ぐ）
    safe_filename = sanitize_filename(request.filename)

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
        await download_service.download_file(url, filename, progress_callback=progress_callback)
        logger.info("Download completed: task_id=%s, filename=%s", task_id, filename)
        progress_manager.complete_task(task_id)
    except Exception as e:
        logger.error("Download failed: task_id=%s, error=%s", task_id, str(e), exc_info=True)
        progress_manager.fail_task(task_id, str(e))
