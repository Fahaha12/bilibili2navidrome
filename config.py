import os
from pathlib import Path

# 基础配置
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', 'your_secret_key_here_change_this')

# 文件路径配置
MUSIC_LIBRARY = os.getenv('MUSIC_LIBRARY', str(Path.home() / 'Downloads'))

# 下载配置
DOWNLOAD_PATH = os.path.join(MUSIC_LIBRARY, "Bilibili")
ALLOWED_DOMAINS = ["bilibili.com", "b23.tv"]
TEMP_PATH = os.getenv('TEMP_PATH', 'temp')

# 安全配置
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
UPLOAD_FOLDER = TEMP_PATH

# 标签编辑默认值
DEFAULT_TAGS = {
    "genre": "Bilibili",
    "publisher": "Bilibili"
}

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = os.getenv('LOG_FILE', 'app.log')
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
LOG_BACKUP_COUNT = 5

# 认证配置
LOGIN_REQUIRED = os.getenv('LOGIN_REQUIRED', 'True').lower() == 'true'
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')
SESSION_TIMEOUT = int(os.getenv('SESSION_TIMEOUT', '3600'))

# Navidrome配置
NAVIDROME_URL = os.getenv('NAVIDROME_URL')
NAVIDROME_API_KEY = os.getenv('NAVIDROME_API_KEY')

# 下载配置
DOWNLOAD_TIMEOUT = int(os.getenv('DOWNLOAD_TIMEOUT', '300'))  # 5分钟
MAX_DOWNLOAD_SIZE = int(os.getenv('MAX_DOWNLOAD_SIZE', '500'))  # 500MB

# 文件验证配置
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
ALLOWED_COOKIES_EXTENSIONS = {'.txt'}
MAX_FILENAME_LENGTH = 255