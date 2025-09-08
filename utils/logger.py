"""
日志配置模块
"""
import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path


class Logger:
    """日志管理器"""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """初始化日志配置"""
        self.app = app
        
        # 创建日志目录
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # 配置日志级别
        log_level = getattr(app.config, 'LOG_LEVEL', 'INFO')
        app.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 如果不在调试模式，添加文件处理器
        if not app.debug:
            self._add_file_handler(app)
        
        # 添加控制台处理器（开发环境）
        if app.debug:
            self._add_console_handler(app)
    
    def _add_file_handler(self, app):
        """添加文件日志处理器"""
        log_file = getattr(app.config, 'LOG_FILE', 'logs/app.log')
        max_bytes = getattr(app.config, 'LOG_MAX_SIZE', 10 * 1024 * 1024)  # 10MB
        backup_count = getattr(app.config, 'LOG_BACKUP_COUNT', 5)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(logging.ERROR)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        app.logger.addHandler(file_handler)
    
    def _add_console_handler(self, app):
        """添加控制台日志处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        app.logger.addHandler(console_handler)
    
    def log_error(self, message: str, exception: Exception = None):
        """记录错误日志"""
        if self.app:
            if exception:
                self.app.logger.error(f"{message}: {str(exception)}", exc_info=True)
            else:
                self.app.logger.error(message)
    
    def log_warning(self, message: str):
        """记录警告日志"""
        if self.app:
            self.app.logger.warning(message)
    
    def log_info(self, message: str):
        """记录信息日志"""
        if self.app:
            self.app.logger.info(message)
    
    def log_debug(self, message: str):
        """记录调试日志"""
        if self.app:
            self.app.logger.debug(message)
