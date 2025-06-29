import os

# 基础配置
DEBUG = True
SECRET_KEY = 'your_secret_key_here'

# Navidrome配置
MUSIC_LIBRARY = r"D:\Downloads"

# 下载配置
DOWNLOAD_PATH = os.path.join(MUSIC_LIBRARY, "Bilibili")
ALLOWED_DOMAINS = ["bilibili.com", "b23.tv"]
TEMP_PATH = "temp"

# 标签编辑默认值
DEFAULT_TAGS = {
    "genre": "Bilibili",
    "publisher": "Bilibili"
}

# 日志配置
LOG_LEVEL = "DEBUG"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "app.log"