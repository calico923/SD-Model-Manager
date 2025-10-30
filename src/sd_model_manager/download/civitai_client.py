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
        """
        Args:
            api_key: Civitai API キー（オプション）
        """
        self.api_key = api_key
        self._client: Optional[httpx.AsyncClient] = None

    def extract_model_id(self, url_or_id: str) -> str:
        """URL またはモデル ID からモデル ID を抽出

        Args:
            url_or_id: Civitai URL またはモデル ID

        Returns:
            モデル ID（文字列）

        Raises:
            DownloadError: URL が無効な場合
        """
        # 数字のみの場合は直接モデル ID として扱う
        if url_or_id.isdigit():
            return url_or_id

        # URL からモデル ID を抽出
        # 例: https://civitai.com/models/123456/test-lora
        pattern = r'civitai\.com/models/(\d+)'
        match = re.search(pattern, url_or_id)

        if match:
            return match.group(1)

        raise DownloadError(
            f"Invalid Civitai URL or model ID: {url_or_id}",
            details={"input": url_or_id}
        )

    async def _get_client(self) -> httpx.AsyncClient:
        """HTTP クライアントの取得（遅延初期化）"""
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
        """Civitai API からモデルデータを取得

        Args:
            model_id: モデル ID

        Returns:
            モデルデータ（辞書）

        Raises:
            DownloadError: API エラー時
        """
        client = await self._get_client()
        logger.info("Fetching model data from Civitai API: model_id=%s", model_id)

        try:
            response = await client.get(f"/models/{model_id}")
            response.raise_for_status()
            logger.info("Successfully fetched model data: model_id=%s", model_id)
            return response.json()
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code

            # ユーザーフレンドリーなエラーメッセージを生成
            if status_code == 401:
                message = (
                    "Unauthorized: Invalid API key. "
                    "Please check your CIVITAI_API_KEY in .env file."
                )
                logger.error("API authentication failed: model_id=%s, status=%d", model_id, status_code)
            elif status_code == 403:
                message = (
                    "Access forbidden: This model may require Early Access. "
                    "Please ensure you have a valid API key and proper permissions."
                )
                logger.warning("API access forbidden: model_id=%s, status=%d", model_id, status_code)
            elif status_code == 404:
                message = f"Model not found: Model ID {model_id} does not exist."
                logger.warning("Model not found: model_id=%s", model_id)
            elif status_code == 429:
                message = (
                    "Rate limit exceeded. "
                    "Consider adding a CIVITAI_API_KEY to increase rate limits "
                    "(60/min with API key vs 10/min without)."
                )
                logger.warning("API rate limit exceeded: model_id=%s", model_id)
            else:
                message = f"Failed to fetch model data: HTTP {status_code}"
                logger.error("API request failed: model_id=%s, status=%d", model_id, status_code)

            raise DownloadError(
                message,
                details={"model_id": model_id, "status_code": status_code}
            )
        except httpx.RequestError as e:
            logger.error("Network error while fetching model data: model_id=%s, error=%s", model_id, str(e))
            raise DownloadError(
                f"Network error while fetching model data: {str(e)}",
                details={"model_id": model_id}
            )

    async def get_model_metadata(self, url_or_id: str) -> dict[str, Any]:
        """モデルのメタデータを取得

        Args:
            url_or_id: Civitai URL またはモデル ID

        Returns:
            モデルメタデータ（辞書）

        Raises:
            DownloadError: 取得失敗時
        """
        model_id = self.extract_model_id(url_or_id)
        return await self._fetch_model_data(model_id)

    async def get_download_url(self, url_or_id: str, version_index: int = 0) -> str:
        """ダウンロード URL を取得

        Args:
            url_or_id: Civitai URL またはモデル ID
            version_index: モデルバージョンのインデックス（デフォルト: 0 = 最新）

        Returns:
            ダウンロード URL

        Raises:
            DownloadError: 取得失敗時
        """
        metadata = await self.get_model_metadata(url_or_id)

        if "modelVersions" not in metadata or not metadata["modelVersions"]:
            raise DownloadError(
                "No model versions found",
                details={"model_id": url_or_id}
            )

        versions = metadata["modelVersions"]
        if version_index >= len(versions):
            raise DownloadError(
                f"Version index {version_index} out of range",
                details={"model_id": url_or_id, "available_versions": len(versions)}
            )

        version = versions[version_index]
        if "downloadUrl" not in version:
            raise DownloadError(
                "Download URL not found in model version",
                details={"model_id": url_or_id, "version_index": version_index}
            )

        return version["downloadUrl"]

    async def close(self):
        """HTTP クライアントをクローズ"""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def __aenter__(self):
        """非同期コンテキストマネージャー: 開始"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー: 終了"""
        await self.close()
