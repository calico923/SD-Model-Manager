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
        """
        Args:
            download_dir: ダウンロード先ディレクトリ
            civitai_client: Civitai API クライアント（オプション）
        """
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
        """ファイルをダウンロード

        Args:
            url: ダウンロード URL（Civitai URL または直接ダウンロード URL）
            filename: 保存ファイル名（相対パスも可）
            progress_callback: 進捗コールバック関数 (downloaded_bytes, total_bytes)
            max_retries: 最大リトライ回数
            chunk_size: チャンクサイズ（バイト）

        Returns:
            ダウンロードしたファイルのパス

        Raises:
            DownloadError: ダウンロード失敗時
        """
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
                    # リトライ前に少し待機
                    await asyncio.sleep(1.0 * (attempt + 1))
                    continue
                # 最後のリトライも失敗した場合
                logger.error(
                    "Download failed after %d attempts: url=%s, error=%s",
                    max_retries, url, str(e)
                )
                break

        # すべてのリトライが失敗
        raise DownloadError(
            f"Failed to download file after {max_retries} attempts: {str(last_error)}",
            details={"url": url, "filename": filename, "error": str(last_error)}
        )

    def _is_civitai_url(self, url: str) -> bool:
        """Civitai URL かどうかを判定

        Args:
            url: 判定する URL

        Returns:
            Civitai URL の場合 True
        """
        return "civitai.com" in url.lower()

    async def _download_with_progress(
        self,
        url: str,
        output_path: Path,
        progress_callback: Optional[Callable[[int, int], None]],
        chunk_size: int
    ) -> Path:
        """進捗付きダウンロード（内部メソッド）

        Args:
            url: ダウンロード URL
            output_path: 保存先パス
            progress_callback: 進捗コールバック
            chunk_size: チャンクサイズ

        Returns:
            ダウンロードしたファイルのパス

        Raises:
            Exception: ダウンロード失敗時
        """
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
