"""FastAPI アプリケーション構築（ファクトリパターン）"""

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from sd_model_manager.config import Config
from sd_model_manager.ui.api.health import router as health_router
from sd_model_manager.lib.errors import register_error_handlers

logger = logging.getLogger(__name__)


def create_app(config: Config | None = None) -> FastAPI:
    """FastAPI アプリケーション全体を構築するファクトリ関数

    テストと実行時の両方で同じコードパスを通すため、
    ファクトリパターンを採用しています。
    """
    if config is None:
        config = Config()

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

    # エラーハンドラー登録
    register_error_handlers(app)
    logger.info("Error handlers registered")

    logger.info("FastAPI application created successfully")
    return app
