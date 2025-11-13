import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Optional


LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FILE = "logs/app.log"


def _resolve_log_level(level: Optional[str]) -> int:
    """Resolve string log level to logging module constant."""
    level = (level or DEFAULT_LOG_LEVEL).upper()
    return getattr(logging, level, logging.INFO)


def _build_formatter() -> logging.Formatter:
    return logging.Formatter(LOG_FORMAT, datefmt=DATE_FORMAT)


def _ensure_log_dir(filepath: str) -> Path:
    path = Path(filepath).expanduser()
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def setup_logging():
    """
    配置全局日志记录器，支持控制台和可选文件日志，避免多次初始化。

    环境变量:
        LOG_LEVEL: 全局日志级别，默认 INFO。
        LOG_FILE:  文件日志路径，默认 logs/app.log；为空则关闭文件日志。
        LOG_MAX_BYTES: 单个日志文件最大字节数（滚动），默认 5_000_000。
        LOG_BACKUP_COUNT: 滚动文件保留数量，默认 3。
    """
    root_logger = logging.getLogger()

    if getattr(root_logger, "_baize_logging_configured", False):
        return root_logger

    log_level = _resolve_log_level(os.environ.get("LOG_LEVEL"))
    root_logger.setLevel(log_level)

    formatter = _build_formatter()

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(log_level)
    root_logger.addHandler(console_handler)

    log_file = os.environ.get("LOG_FILE", DEFAULT_LOG_FILE).strip()
    if log_file:
        max_bytes = int(os.environ.get("LOG_MAX_BYTES", 5_000_000))
        backup_count = int(os.environ.get("LOG_BACKUP_COUNT", 3))
        file_path = _ensure_log_dir(log_file)
        file_handler = RotatingFileHandler(
            file_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        root_logger.addHandler(file_handler)

    root_logger._baize_logging_configured = True  # type: ignore[attr-defined]
    return root_logger


# 在模块导入时配置日志
setup_logging()


def get_logger(name: str) -> logging.Logger:
    """
    获取一个指定名称的日志记录器实例。

    参数:
        name (str): 通常是当前模块的名称 (__name__)。

    返回:
        logging.Logger: 配置好的日志记录器实例。
    """
    logger = logging.getLogger(name)
    if not getattr(logger, "_baize_logger_tagged", False):
        logger._baize_logger_tagged = True  # type: ignore[attr-defined]
    return logger