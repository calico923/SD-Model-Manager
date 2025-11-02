"""FastAPI アプリケーション構築（ファクトリパターン）"""

import logging
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sd_model_manager.config import Config
from sd_model_manager.ui.api.health import router as health_router
from sd_model_manager.ui.api.download import router as download_router
from sd_model_manager.ui.api.websocket import router as websocket_router
from sd_model_manager.lib.errors import register_error_handlers
from sd_model_manager.lib.logging_config import setup_logging

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> FastAPI:
    """FastAPI アプリケーション全体を構築するファクトリ関数

    テストと実行時の両方で同じコードパスを通すため、
    ファクトリパターンを採用しています。
    """
    if config is None:
        config = Config()

    # uvicorn 直接起動時など、ファイルハンドラーが未設定ならログを初期化
    log_file = (config.log_dir / "app.log").resolve()
    root_logger = logging.getLogger()
    has_app_log_handler = any(
        getattr(handler, "baseFilename", None)
        and Path(handler.baseFilename).resolve() == log_file
        for handler in root_logger.handlers
    )

    if not has_app_log_handler:
        setup_logging(
            log_level=config.log_level,
            log_dir=config.log_dir,
            log_max_bytes=config.log_max_bytes,
            log_backup_count=config.log_backup_count
        )

    logger.info("Creating FastAPI application")
    logger.info("Configuration: host=%s, port=%d, download_dir=%s", config.host, config.port, config.download_dir)

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
    logger.info("CORS middleware configured")

    # ルーター登録
    app.include_router(health_router)
    logger.info("Health router registered")

    app.include_router(download_router)
    logger.info("Download router registered")

    app.include_router(websocket_router)
    logger.info("WebSocket router registered")

    # エラーハンドラー登録
    register_error_handlers(app)
    logger.info("Error handlers registered")

    logger.info("FastAPI application created successfully")
    return app
