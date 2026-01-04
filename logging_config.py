"""
日志配置模块 / Logging Configuration Module

本模块提供统一的日志配置和管理功能
This module provides unified logging configuration and management
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import os


# ============================================================================
# 日志级别映射 / Log Level Mapping
# ============================================================================

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}


# ============================================================================
# 自定义日志格式器 / Custom Log Formatter
# ============================================================================

class ColoredFormatter(logging.Formatter):
    """
    带颜色的日志格式器（用于控制台输出）
    Colored log formatter for console output
    """

    # ANSI颜色代码 / ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # 青色 Cyan
        'INFO': '\033[32m',       # 绿色 Green
        'WARNING': '\033[33m',    # 黄色 Yellow
        'ERROR': '\033[31m',      # 红色 Red
        'CRITICAL': '\033[35m',   # 紫色 Magenta
        'RESET': '\033[0m',       # 重置 Reset
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录"""
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"

        return super().format(record)


class ChineseFormatter(logging.Formatter):
    """
    中文友好的日志格式器
    Chinese-friendly log formatter
    """

    LEVEL_NAMES = {
        'DEBUG': '调试',
        'INFO': '信息',
        'WARNING': '警告',
        'ERROR': '错误',
        'CRITICAL': '严重',
    }

    def format(self, record: logging.LogRecord) -> str:
        """格式化日志记录，使用中文级别名称"""
        original_levelname = record.levelname
        if record.levelname in self.LEVEL_NAMES:
            record.levelname = self.LEVEL_NAMES[record.levelname]

        result = super().format(record)
        record.levelname = original_levelname  # 恢复原始级别名称
        return result


# ============================================================================
# 日志配置函数 / Logging Configuration Functions
# ============================================================================

def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    log_dir: Optional[Path] = None,
    enable_console: bool = True,
    enable_file: bool = True,
    use_colors: bool = True,
    use_chinese: bool = True,
    rotation: bool = True,
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    配置日志系统 / Configure logging system

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: 日志文件路径（如果指定，将覆盖log_dir）
        log_dir: 日志目录路径（如果不指定log_file，则在此目录创建日志文件）
        enable_console: 是否启用控制台输出
        enable_file: 是否启用文件输出
        use_colors: 控制台输出是否使用颜色
        use_chinese: 是否使用中文日志级别名称
        rotation: 是否启用日志文件轮转
        max_bytes: 单个日志文件最大字节数（启用轮转时）
        backup_count: 保留的备份文件数量（启用轮转时）

    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    # 获取根日志记录器
    root_logger = logging.getLogger()

    # 清除现有的处理器
    root_logger.handlers.clear()

    # 设置日志级别
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)
    root_logger.setLevel(log_level)

    # 创建格式器
    if use_chinese:
        # 中文格式
        console_format = '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s'
        file_format = '%(asctime)s - [%(levelname)s] - %(name)s - %(filename)s:%(lineno)d - %(message)s'
    else:
        # 英文格式
        console_format = '%(asctime)s - %(levelname)-8s - %(name)s - %(message)s'
        file_format = '%(asctime)s - %(levelname)-8s - %(name)s - %(filename)s:%(lineno)d - %(message)s'

    date_format = '%Y-%m-%d %H:%M:%S'

    # 添加控制台处理器
    if enable_console:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)

        if use_colors and use_chinese:
            # 不支持同时使用颜色和中文（颜色代码会干扰）
            formatter = ChineseFormatter(console_format, datefmt=date_format)
        elif use_colors:
            formatter = ColoredFormatter(console_format, datefmt=date_format)
        elif use_chinese:
            formatter = ChineseFormatter(console_format, datefmt=date_format)
        else:
            formatter = logging.Formatter(console_format, datefmt=date_format)

        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # 添加文件处理器
    if enable_file:
        # 确定日志文件路径
        if log_file:
            log_file_path = Path(log_file)
        elif log_dir:
            log_dir_path = Path(log_dir)
            log_dir_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file_path = log_dir_path / f"moviemaker_{timestamp}.log"
        else:
            # 默认日志目录
            log_dir_path = Path("logs")
            log_dir_path.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d')
            log_file_path = log_dir_path / f"moviemaker_{timestamp}.log"

        # 确保日志文件所在目录存在
        log_file_path.parent.mkdir(parents=True, exist_ok=True)

        # 选择处理器类型
        if rotation:
            from logging.handlers import RotatingFileHandler
            file_handler = RotatingFileHandler(
                log_file_path,
                maxBytes=max_bytes,
                backupCount=backup_count,
                encoding='utf-8'
            )
        else:
            file_handler = logging.FileHandler(
                log_file_path,
                encoding='utf-8'
            )

        file_handler.setLevel(log_level)

        # 文件输出使用详细格式
        file_formatter = logging.Formatter(file_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        root_logger.addHandler(file_handler)

        # 记录日志文件位置
        root_logger.info(f"日志文件: {log_file_path.absolute()}")

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的日志记录器 / Get logger with specified name

    Args:
        name: 日志记录器名称（通常使用 __name__）

    Returns:
        logging.Logger: 日志记录器实例
    """
    return logging.getLogger(name)


def set_log_level(level: str, logger_name: Optional[str] = None) -> None:
    """
    动态设置日志级别 / Dynamically set log level

    Args:
        level: 日志级别 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        logger_name: 日志记录器名称（如果为None，则设置根日志记录器）
    """
    log_level = LOG_LEVELS.get(level.upper(), logging.INFO)

    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    logger.setLevel(log_level)
    for handler in logger.handlers:
        handler.setLevel(log_level)


def disable_logging(logger_name: Optional[str] = None) -> None:
    """
    禁用日志输出 / Disable logging

    Args:
        logger_name: 日志记录器名称（如果为None，则禁用根日志记录器）
    """
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    logger.disabled = True


def enable_logging(logger_name: Optional[str] = None) -> None:
    """
    启用日志输出 / Enable logging

    Args:
        logger_name: 日志记录器名称（如果为None，则启用根日志记录器）
    """
    if logger_name:
        logger = logging.getLogger(logger_name)
    else:
        logger = logging.getLogger()

    logger.disabled = False


# ============================================================================
# 日志上下文管理器 / Logging Context Manager
# ============================================================================

class LogContext:
    """
    日志上下文管理器 / Logging context manager
    用于临时修改日志级别
    """

    def __init__(self, level: str, logger_name: Optional[str] = None):
        """
        初始化日志上下文

        Args:
            level: 临时日志级别
            logger_name: 日志记录器名称
        """
        self.level = level
        self.logger_name = logger_name
        self.original_level = None
        self.logger = None

    def __enter__(self):
        """进入上下文"""
        if self.logger_name:
            self.logger = logging.getLogger(self.logger_name)
        else:
            self.logger = logging.getLogger()

        self.original_level = self.logger.level
        set_log_level(self.level, self.logger_name)
        return self.logger

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出上下文"""
        if self.logger and self.original_level is not None:
            self.logger.setLevel(self.original_level)
            for handler in self.logger.handlers:
                handler.setLevel(self.original_level)


# ============================================================================
# 进度日志记录器 / Progress Logger
# ============================================================================

class ProgressLogger:
    """
    进度日志记录器 / Progress logger
    用于记录长时间运行任务的进度
    """

    def __init__(self, total: int, logger: Optional[logging.Logger] = None,
                 task_name: str = "任务"):
        """
        初始化进度日志记录器

        Args:
            total: 总任务数
            logger: 日志记录器（如果为None，使用根日志记录器）
            task_name: 任务名称
        """
        self.total = total
        self.current = 0
        self.logger = logger or logging.getLogger()
        self.task_name = task_name
        self.start_time = datetime.now()

    def update(self, increment: int = 1, message: str = "") -> None:
        """
        更新进度

        Args:
            increment: 增量
            message: 附加消息
        """
        self.current += increment
        percentage = (self.current / self.total) * 100 if self.total > 0 else 0

        elapsed = datetime.now() - self.start_time
        elapsed_seconds = elapsed.total_seconds()

        if self.current > 0 and elapsed_seconds > 0:
            rate = self.current / elapsed_seconds
            remaining_seconds = (self.total - self.current) / rate if rate > 0 else 0
            eta = f"预计剩余: {int(remaining_seconds)}秒"
        else:
            eta = "预计剩余: 计算中..."

        log_message = f"{self.task_name} 进度: {self.current}/{self.total} ({percentage:.1f}%) - {eta}"
        if message:
            log_message += f" - {message}"

        self.logger.info(log_message)

    def finish(self, message: str = "完成") -> None:
        """
        完成任务

        Args:
            message: 完成消息
        """
        elapsed = datetime.now() - self.start_time
        self.logger.info(f"{self.task_name} {message}！总耗时: {elapsed}")


# ============================================================================
# 默认配置 / Default Configuration
# ============================================================================

def setup_default_logging() -> logging.Logger:
    """
    设置默认日志配置 / Setup default logging configuration
    从环境变量读取配置，如果未设置则使用默认值

    Returns:
        logging.Logger: 配置好的根日志记录器
    """
    log_level = os.getenv("MOVIEMAKER_LOG_LEVEL", "INFO")
    log_dir = os.getenv("MOVIEMAKER_LOG_DIR", "logs")
    use_colors = os.getenv("MOVIEMAKER_LOG_COLORS", "true").lower() == "true"
    use_chinese = os.getenv("MOVIEMAKER_LOG_CHINESE", "true").lower() == "true"

    return setup_logging(
        level=log_level,
        log_dir=Path(log_dir),
        use_colors=use_colors,
        use_chinese=use_chinese
    )


# ============================================================================
# 模块级别初始化 / Module Level Initialization
# ============================================================================

# 如果作为模块导入，可以自动设置默认日志配置
# 注释掉以避免自动初始化，让用户手动调用
# setup_default_logging()
