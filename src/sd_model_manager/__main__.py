"""エントリポイント"""

import uvicorn
from sd_model_manager.config import Config
from sd_model_manager.ui.api.main import create_app


def main():
    """アプリケーション起動"""
    config = Config()
    app = create_app(config)

    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        reload=True
    )


if __name__ == "__main__":
    main()
