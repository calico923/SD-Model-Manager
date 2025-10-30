"""カスタム例外クラス定義とエラーハンドラー登録"""

import logging
from typing import Any, Optional
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

logger = logging.getLogger(__name__)


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
        logger.error(
            "Application error: code=%s, message=%s, path=%s, details=%s",
            exc.code, exc.message, request.url.path, exc.details
        )
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
        logger.warning("Endpoint not found: path=%s", request.url.path)
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "NOT_FOUND",
                    "message": f"Endpoint not found: {request.url.path}"
                }
            }
        )
