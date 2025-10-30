"""ログ設定のテスト"""

import logging
from pathlib import Path
import pytest
from sd_model_manager.lib.logging_config import setup_logging, get_logger


def test_setup_logging_creates_log_directory(tmp_path):
    """ログディレクトリが作成されることを確認"""
    log_dir = tmp_path / "logs"

    setup_logging(log_dir=log_dir)

    assert log_dir.exists()
    assert log_dir.is_dir()


def test_setup_logging_creates_log_file(tmp_path):
    """ログファイルが作成されることを確認"""
    log_dir = tmp_path / "logs"

    setup_logging(log_dir=log_dir)

    log_file = log_dir / "app.log"
    # ロガーに何かログを出力
    logger = logging.getLogger("test_logger")
    logger.info("Test log message")

    assert log_file.exists()
    assert log_file.is_file()


def test_setup_logging_sets_correct_log_level(tmp_path):
    """ログレベルが正しく設定されることを確認"""
    log_dir = tmp_path / "logs"

    setup_logging(log_level="DEBUG", log_dir=log_dir)

    root_logger = logging.getLogger()
    assert root_logger.level == logging.DEBUG


def test_setup_logging_with_info_level(tmp_path):
    """INFO レベルのログが出力されることを確認"""
    log_dir = tmp_path / "logs"

    setup_logging(log_level="INFO", log_dir=log_dir)

    logger = logging.getLogger("test_info")
    logger.info("Info message")
    logger.debug("Debug message")  # これは出力されないはず

    log_file = log_dir / "app.log"
    content = log_file.read_text()

    assert "Info message" in content
    assert "Debug message" not in content


def test_get_logger_returns_logger():
    """get_logger が正しくロガーを返すことを確認"""
    logger = get_logger("test_module")

    assert isinstance(logger, logging.Logger)
    assert logger.name == "test_module"


def test_setup_logging_writes_to_file(tmp_path):
    """ログがファイルに書き込まれることを確認"""
    log_dir = tmp_path / "logs"

    setup_logging(log_dir=log_dir)

    logger = logging.getLogger("test_file_write")
    test_message = "This is a test log message"
    logger.info(test_message)

    log_file = log_dir / "app.log"
    content = log_file.read_text()

    assert test_message in content
    assert "test_file_write" in content
    assert "INFO" in content
