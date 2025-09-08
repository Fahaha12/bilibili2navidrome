#!/usr/bin/env python3
"""
一键安装脚本 - 自动安装依赖和配置环境
"""
import os
import sys
import subprocess
import platform
import shutil
from pathlib import Path

def run_command(command, description, check=True):
    """运行命令并处理错误"""
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 完成")
            if result.stdout:
                print(f"输出: {result.stdout}")
            return True
        else:
            print(f"❌ {description} 失败")
            print(f"错误: {result.stderr}")
            return False
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False

def check_python_version():
    """检查Python版本"""
    print("检查Python版本...")
    
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"✅ Python版本: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python版本过低: {version.major}.{version.minor}.{version.micro}")
        print("需要Python 3.8或更高版本")
        return False

def check_pip():
    """检查pip是否安装"""
    print("检查pip安装...")
    
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pip已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ pip未安装")
            return False
    except Exception as e:
        print(f"❌ pip检查失败: {e}")
        return False

def install_python_dependencies():
    """安装Python依赖"""
    print("安装Python依赖...")
    
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt文件不存在")
        return False
    
    command = f"{sys.executable} -m pip install -r requirements.txt"
    
    if not run_command(command, "Python依赖安装"):
        return False
    
    # 安装PyInstaller（用于打包）
    command = f"{sys.executable} -m pip install pyinstaller"
    run_command(command, "PyInstaller安装", check=False)
    
    return True

def check_ffmpeg():
    """检查FFmpeg是否安装"""
    print("检查FFmpeg安装...")
    
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ FFmpeg已安装")
            return True
        else:
            print("❌ FFmpeg未安装")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg未安装")
        return False

def install_ffmpeg():
    """安装FFmpeg"""
    print("安装FFmpeg...")
    
    system = platform.system().lower()
    
    if system == "windows":
        return install_ffmpeg_windows()
    elif system == "linux":
        return install_ffmpeg_linux()
    elif system == "darwin":
        return install_ffmpeg_macos()
    else:
        print(f"❌ 不支持的操作系统: {system}")
        return False

def install_ffmpeg_windows():
    """Windows安装FFmpeg"""
    print("Windows系统FFmpeg安装...")
    
    # 检查是否有Chocolatey
    try:
        result = subprocess.run(['choco', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("使用Chocolatey安装FFmpeg...")
            command = "choco install ffmpeg -y"
            return run_command(command, "Chocolatey安装FFmpeg")
    except FileNotFoundError:
        pass
    
    # 检查是否有Scoop
    try:
        result = subprocess.run(['scoop', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("使用Scoop安装FFmpeg...")
            command = "scoop install ffmpeg"
            return run_command(command, "Scoop安装FFmpeg")
    except FileNotFoundError:
        pass
    
    print("请手动安装FFmpeg:")
    print("1. 访问: https://ffmpeg.org/download.html")
    print("2. 下载Windows版本")
    print("3. 解压到任意目录")
    print("4. 将bin目录添加到系统PATH")
    print("5. 重启命令行")
    
    return False

def install_ffmpeg_linux():
    """Linux安装FFmpeg"""
    print("Linux系统FFmpeg安装...")
    
    # 尝试不同的包管理器
    package_managers = [
        ("apt", "sudo apt update && sudo apt install -y ffmpeg"),
        ("yum", "sudo yum install -y ffmpeg"),
        ("dnf", "sudo dnf install -y ffmpeg"),
        ("pacman", "sudo pacman -S ffmpeg"),
        ("zypper", "sudo zypper install ffmpeg")
    ]
    
    for pm, command in package_managers:
        try:
            result = subprocess.run([pm, '--version'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print(f"使用{pm}安装FFmpeg...")
                return run_command(command, f"{pm}安装FFmpeg")
        except FileNotFoundError:
            continue
    
    print("请手动安装FFmpeg:")
    print("Ubuntu/Debian: sudo apt install ffmpeg")
    print("CentOS/RHEL: sudo yum install ffmpeg")
    print("Arch Linux: sudo pacman -S ffmpeg")
    
    return False

def install_ffmpeg_macos():
    """macOS安装FFmpeg"""
    print("macOS系统FFmpeg安装...")
    
    # 检查是否有Homebrew
    try:
        result = subprocess.run(['brew', '--version'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("使用Homebrew安装FFmpeg...")
            command = "brew install ffmpeg"
            return run_command(command, "Homebrew安装FFmpeg")
    except FileNotFoundError:
        pass
    
    print("请手动安装FFmpeg:")
    print("1. 安装Homebrew: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    print("2. 安装FFmpeg: brew install ffmpeg")
    
    return False

def create_directories():
    """创建必要的目录"""
    print("创建必要的目录...")
    
    directories = [
        'downloads',
        'temp',
        'batch_storage',
        'logs'
    ]
    
    for dir_name in directories:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            print(f"✅ 创建目录: {dir_name}")
        else:
            print(f"✅ 目录已存在: {dir_name}")

def create_env_file():
    """创建环境变量文件"""
    print("创建环境变量文件...")
    
    env_file = '.env'
    if os.path.exists(env_file):
        print(f"✅ 环境变量文件已存在: {env_file}")
        return True
    
    env_content = '''# Bilibili2Navidrome 环境配置

# 应用配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# 路径配置
DOWNLOAD_PATH=./downloads
TEMP_PATH=./temp

# 登录配置
LOGIN_REQUIRED=True
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# 会话配置
SESSION_TIMEOUT=3600

# 文件上传配置
MAX_CONTENT_LENGTH=10485760
UPLOAD_FOLDER=./temp

# 日志配置
LOG_LEVEL=INFO
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=5

# Navidrome配置
NAVIDROME_URL=http://localhost:4533
NAVIDROME_API_KEY=your-api-key-here

# 下载配置
DOWNLOAD_TIMEOUT=300
MAX_DOWNLOAD_SIZE=1073741824

# 文件验证配置
ALLOWED_IMAGE_EXTENSIONS=.jpg,.jpeg,.png,.gif,.bmp,.webp
ALLOWED_COOKIES_EXTENSIONS=.txt
MAX_FILENAME_LENGTH=255
'''
    
    with open(env_file, 'w', encoding='utf-8') as f:
        f.write(env_content)
    
    print(f"✅ 创建环境变量文件: {env_file}")
    return True

def create_startup_scripts():
    """创建启动脚本"""
    print("创建启动脚本...")
    
    # Windows启动脚本
    windows_start = '''@echo off
echo 启动 Bilibili2Navidrome...
echo.
echo 请确保已安装 FFmpeg 并添加到系统 PATH
echo 如果没有安装 FFmpeg，请访问: https://ffmpeg.org/download.html
echo.
pause
python app.py
pause
'''
    
    with open('start.bat', 'w', encoding='utf-8') as f:
        f.write(windows_start)
    print("✅ 创建Windows启动脚本: start.bat")
    
    # Unix启动脚本
    unix_start = '''#!/bin/bash
echo "启动 Bilibili2Navidrome..."
echo ""
echo "请确保已安装 FFmpeg 并添加到系统 PATH"
echo "如果没有安装 FFmpeg，请运行: sudo apt install ffmpeg"
echo ""
read -p "按回车键继续..."
python3 app.py
'''
    
    with open('start.sh', 'w', encoding='utf-8') as f:
        f.write(unix_start)
    
    os.chmod('start.sh', 0o755)
    print("✅ 创建Unix启动脚本: start.sh")

def test_installation():
    """测试安装"""
    print("测试安装...")
    
    # 测试Python导入
    try:
        import flask
        import mutagen
        import yt_dlp
        import dotenv
        print("✅ Python依赖导入成功")
    except ImportError as e:
        print(f"❌ Python依赖导入失败: {e}")
        return False
    
    # 测试FFmpeg
    if check_ffmpeg():
        print("✅ FFmpeg测试成功")
    else:
        print("⚠️  FFmpeg未安装，请手动安装")
    
    return True

def create_install_readme():
    """创建安装说明"""
    readme_content = '''# Bilibili2Navidrome 安装完成

## 安装状态

✅ Python依赖已安装
✅ 项目目录已创建
✅ 环境配置文件已创建
✅ 启动脚本已创建

## 启动应用

### Windows
```bash
start.bat
```

### Linux/macOS
```bash
./start.sh
```

### 手动启动
```bash
python app.py
```

## 访问应用

应用启动后，在浏览器中访问: http://localhost:5000

## 配置说明

### 1. 修改环境配置
编辑 `.env` 文件来配置应用参数：

```bash
# 登录配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password

# Navidrome配置
NAVIDROME_URL=http://localhost:4533
NAVIDROME_API_KEY=your-api-key
```

### 2. 安装FFmpeg
如果FFmpeg未安装，请根据操作系统安装：

**Windows:**
- 下载: https://ffmpeg.org/download.html
- 解压到任意目录
- 将bin目录添加到系统PATH

**Linux:**
```bash
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

## 功能特性

- 单个视频下载
- 批量视频下载
- 音频标签编辑
- Navidrome集成
- 用户认证
- 实时进度监控

## 故障排除

### 常见问题

1. **FFmpeg未找到**
   - 确保FFmpeg已正确安装
   - 检查系统PATH环境变量
   - 重启命令行/终端

2. **端口被占用**
   - 修改config.py中的端口设置
   - 或使用环境变量PORT=8080

3. **下载失败**
   - 检查网络连接
   - 确认Bilibili URL有效
   - 查看应用日志

### 日志文件

应用日志保存在 `app.log` 文件中，可以查看详细的错误信息。

## 技术支持

如果遇到问题，请：
1. 查看日志文件
2. 检查系统要求
3. 联系技术支持

## 版本信息

版本: 1.0.0
安装时间: {install_time}
安装平台: {platform}
'''
    
    import datetime
    install_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    platform_info = platform.platform()
    
    with open('INSTALL_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content.format(install_time=install_time, platform=platform_info))
    
    print("✅ 创建安装说明: INSTALL_README.md")

def main():
    """主函数"""
    print("=" * 60)
    print("Bilibili2Navidrome 一键安装脚本")
    print("=" * 60)
    
    # 检查Python版本
    if not check_python_version():
        sys.exit(1)
    
    # 检查pip
    if not check_pip():
        print("请先安装pip")
        sys.exit(1)
    
    # 安装Python依赖
    if not install_python_dependencies():
        print("Python依赖安装失败")
        sys.exit(1)
    
    # 检查FFmpeg
    if not check_ffmpeg():
        print("FFmpeg未安装，尝试自动安装...")
        if not install_ffmpeg():
            print("FFmpeg自动安装失败，请手动安装")
    
    # 创建目录
    create_directories()
    
    # 创建环境变量文件
    create_env_file()
    
    # 创建启动脚本
    create_startup_scripts()
    
    # 测试安装
    test_installation()
    
    # 创建安装说明
    create_install_readme()
    
    print("\n" + "=" * 60)
    print("✅ 安装完成！")
    print("启动应用: ./start.sh (Linux/macOS) 或 start.bat (Windows)")
    print("访问地址: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()
