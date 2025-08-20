import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config import config

def setup_logging() -> logging.Logger:
    """设置日志配置"""
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 创建主日志器
    logger = logging.getLogger("babyagi")
    logger.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建格式器
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
    )
    simple_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # 文件处理器 - 详细日志
    file_handler = RotatingFileHandler(
        log_dir / config.LOG_FILE,
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(detailed_formatter)
    logger.addHandler(file_handler)
    
    # 控制台处理器 - 简洁日志
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL.upper()))
    console_handler.setFormatter(simple_formatter)
    logger.addHandler(console_handler)
    
    # 错误日志文件处理器
    error_handler = RotatingFileHandler(
        log_dir / "error.log",
        maxBytes=5 * 1024 * 1024,  # 5MB
        backupCount=3,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(detailed_formatter)
    logger.addHandler(error_handler)
    
    return logger

def get_logger(name: str = None) -> logging.Logger:
    """获取日志器实例"""
    if name:
        return logging.getLogger(f"babyagi.{name}")
    return logging.getLogger("babyagi")

# 初始化日志系统
logger = setup_logging()