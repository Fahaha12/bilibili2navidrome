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

# 密码配置
LOGIN_REQUIRED = True  # 是否启用登录验证
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'admin')  # 管理员用户名
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'password')  # 管理员密码
SESSION_TIMEOUT = 3600  # 会话超时时间(秒)