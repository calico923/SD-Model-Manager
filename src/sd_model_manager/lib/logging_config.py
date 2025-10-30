"""ログ設定モジュール"""

import logging
import logging.handlers
from pathlib import Path


def setup_logging(
    log_level: str = "INFO",
    log_dir: Path = Path("./logs"),
    log_max_bytes: int = 10 * 1024 * 1024,  # 10MB
    log_backup_count: int = 3
) -> None:
    """ロギングシステムをセットアップ

    Args:
        log_level: ログレベル（DEBUG, INFO, WARNING, ERROR, CRITICAL）
        log_dir: ログファイル保存ディレクトリ
        log_max_bytes: ログファイルの最大サイズ（バイト）
        log_backup_count: 保持するバックアップファイル数
    """
    # ログディレクトリを作成
    log_dir = Path(log_dir)
    log_dir.mkdir(parents=True, exist_ok=True)

    # ログファイルパス
    log_file = log_dir / "app.log"

    # ログレベルを設定
    level = getattr(logging, log_level.upper(), logging.INFO)

    # ルートロガーを設定
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # 既存のハンドラーをクリア（重複を防ぐ）
    root_logger.handlers.clear()

    # ファイルハンドラー（ローテーション付き）
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=log_max_bytes,
        backupCount=log_backup_count,
        encoding="utf-8"
    )
    file_handler.setLevel(level)

    # ログフォーマット
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    # ハンドラーを追加
    root_logger.addHandler(file_handler)

    # uvicorn/FastAPIのロガーもファイルに出力
    for logger_name in ["uvicorn", "uvicorn.error", "uvicorn.access", "fastapi"]:
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        logger.handlers.clear()
        logger.addHandler(file_handler)
        logger.propagate = False

    logging.info("Logging system initialized (log_level=%s, log_file=%s)", log_level, log_file)


def get_logger(name: str) -> logging.Logger:
    """モジュール用のロガーを取得

    Args:
        name: ロガー名（通常は __name__ を渡す）

    Returns:
        ロガーインスタンス
    """
    return logging.getLogger(name)
