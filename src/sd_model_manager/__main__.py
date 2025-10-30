"""エントリポイント"""

import logging
import uvicorn
from sd_model_manager.config import Config
from sd_model_manager.lib.logging_config import setup_logging
from sd_model_manager.ui.api.main import create_app

logger = logging.getLogger(__name__)


def main():
    """アプリケーション起動"""
    # 設定を読み込み
    config = Config()

    # ロギングをセットアップ（標準出力を最小化）
    setup_logging(
        log_level=config.log_level,
        log_dir=config.log_dir,
        log_max_bytes=config.log_max_bytes,
        log_backup_count=config.log_backup_count
    )

    logger.info("=" * 60)
    logger.info("Starting SD-Model-Manager application")
    logger.info("=" * 60)

    # FastAPIアプリケーションを作成
    app = create_app(config)

    # uvicorn設定（標準出力を最小化）
    log_config = uvicorn.config.LOGGING_CONFIG
    # アクセスログを無効化（ファイルのみに出力）
    log_config["loggers"]["uvicorn.access"]["handlers"] = []
    # エラーログをファイルのみに（起動メッセージは標準出力に出る）
    log_config["loggers"]["uvicorn.error"]["handlers"] = []

    logger.info("Starting uvicorn server at http://%s:%d", config.host, config.port)

    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=True,
        log_config=log_config
    )


if __name__ == "__main__":
    main()
