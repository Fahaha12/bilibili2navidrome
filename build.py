#!/usr/bin/env python3
"""
构建脚本 - 用于打包应用程序
"""
import os
import sys
import shutil
import subprocess
import platform
from pathlib import Path

def run_command(command, description):
    """运行命令并处理错误"""
    print(f"正在执行: {description}")
    print(f"命令: {command}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} 完成")
        if result.stdout:
            print(f"输出: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} 失败")
        print(f"错误: {e.stderr}")
        return False

def check_dependencies():
    """检查构建依赖"""
    print("检查构建依赖...")
    
    dependencies = ['pyinstaller', 'flask', 'mutagen', 'yt-dlp', 'python-dotenv']
    missing = []
    
    for dep in dependencies:
        try:
            __import__(dep.replace('-', '_'))
            print(f"✅ {dep}")
        except ImportError:
            missing.append(dep)
            print(f"❌ {dep}")
    
    if missing:
        print(f"\n缺少依赖: {', '.join(missing)}")
        print("请运行: pip install " + " ".join(missing))
        return False
    
    return True

def create_build_directories():
    """创建构建目录"""
    print("创建构建目录...")
    
    dirs = ['build', 'dist', 'temp']
    for dir_name in dirs:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
        os.makedirs(dir_name, exist_ok=True)
        print(f"✅ 创建目录: {dir_name}")

def copy_assets():
    """复制资源文件"""
    print("复制资源文件...")
    
    assets = [
        ('templates', 'templates'),
        ('static', 'static'),
        ('config.py', '.'),
        ('requirements.txt', '.'),
        ('env.example', '.'),
        ('BATCH_DOWNLOAD_GUIDE.md', '.'),
        ('PROJECT_STRUCTURE.md', '.'),
    ]
    
    for src, dst in assets:
        if os.path.exists(src):
            if os.path.isdir(src):
                shutil.copytree(src, dst, dirs_exist_ok=True)
            else:
                shutil.copy2(src, dst)
            print(f"✅ 复制: {src} -> {dst}")
        else:
            print(f"⚠️  文件不存在: {src}")

def build_executable():
    """构建可执行文件"""
    print("开始构建可执行文件...")
    
    # 使用PyInstaller构建
    command = "pyinstaller --clean app.spec"
    
    if not run_command(command, "PyInstaller构建"):
        return False
    
    # 检查构建结果
    exe_name = "Bilibili2Navidrome.exe" if platform.system() == "Windows" else "Bilibili2Navidrome"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        print(f"✅ 可执行文件构建成功: {exe_path}")
        return True
    else:
        print(f"❌ 可执行文件构建失败: {exe_path}")
        return False

def create_installer():
    """创建安装包"""
    print("创建安装包...")
    
    # 创建发布目录
    release_dir = "release"
    if os.path.exists(release_dir):
        shutil.rmtree(release_dir)
    os.makedirs(release_dir, exist_ok=True)
    
    # 复制可执行文件
    exe_name = "Bilibili2Navidrome.exe" if platform.system() == "Windows" else "Bilibili2Navidrome"
    exe_path = os.path.join("dist", exe_name)
    
    if os.path.exists(exe_path):
        shutil.copy2(exe_path, release_dir)
        print(f"✅ 复制可执行文件到发布目录")
    
    # 复制必要文件
    files_to_copy = [
        'config.py',
        'env.example',
        'BATCH_DOWNLOAD_GUIDE.md',
        'PROJECT_STRUCTURE.md',
        'README.md',
    ]
    
    for file_name in files_to_copy:
        if os.path.exists(file_name):
            shutil.copy2(file_name, release_dir)
            print(f"✅ 复制: {file_name}")
    
    # 创建启动脚本
    if platform.system() == "Windows":
        create_windows_launcher(release_dir)
    else:
        create_unix_launcher(release_dir)
    
    print(f"✅ 安装包创建完成: {release_dir}")

def create_windows_launcher(release_dir):
    """创建Windows启动脚本"""
    launcher_content = '''@echo off
echo 启动 Bilibili2Navidrome...
echo.
echo 请确保已安装 FFmpeg 并添加到系统 PATH
echo 如果没有安装 FFmpeg，请访问: https://ffmpeg.org/download.html
echo.
pause
Bilibili2Navidrome.exe
pause
'''
    
    launcher_path = os.path.join(release_dir, "启动.bat")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    print(f"✅ 创建Windows启动脚本: {launcher_path}")

def create_unix_launcher(release_dir):
    """创建Unix启动脚本"""
    launcher_content = '''#!/bin/bash
echo "启动 Bilibili2Navidrome..."
echo ""
echo "请确保已安装 FFmpeg 并添加到系统 PATH"
echo "如果没有安装 FFmpeg，请运行: sudo apt install ffmpeg"
echo ""
read -p "按回车键继续..."
./Bilibili2Navidrome
'''
    
    launcher_path = os.path.join(release_dir, "启动.sh")
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # 设置执行权限
    os.chmod(launcher_path, 0o755)
    print(f"✅ 创建Unix启动脚本: {launcher_path}")

def create_readme():
    """创建发布说明"""
    readme_content = '''# Bilibili2Navidrome 发布包

## 系统要求

- Windows 10/11 或 Linux/macOS
- FFmpeg (必须安装并添加到系统PATH)
- 至少 2GB 可用内存
- 至少 1GB 可用磁盘空间

## 安装说明

### 1. 安装 FFmpeg

**Windows:**
1. 下载 FFmpeg: https://ffmpeg.org/download.html
2. 解压到任意目录 (如 C:\\ffmpeg)
3. 将 FFmpeg 的 bin 目录添加到系统 PATH
4. 在命令行运行 `ffmpeg -version` 验证安装

**Linux:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

### 2. 运行应用

**Windows:**
- 双击 `启动.bat` 文件
- 或直接运行 `Bilibili2Navidrome.exe`

**Linux/macOS:**
- 运行 `./启动.sh`
- 或直接运行 `./Bilibili2Navidrome`

### 3. 访问应用

应用启动后，在浏览器中访问: http://localhost:5000

## 配置说明

1. 复制 `env.example` 为 `.env`
2. 根据需要修改配置参数
3. 重启应用使配置生效

## 功能特性

- 单个视频下载
- 批量视频下载
- 音频标签编辑
- Navidrome 集成
- 用户认证
- 实时进度监控

## 故障排除

### 常见问题

1. **FFmpeg 未找到**
   - 确保 FFmpeg 已正确安装
   - 检查系统 PATH 环境变量
   - 重启命令行/终端

2. **端口被占用**
   - 修改 config.py 中的端口设置
   - 或使用环境变量 PORT=8080

3. **下载失败**
   - 检查网络连接
   - 确认 Bilibili URL 有效
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
构建时间: {build_time}
构建平台: {platform}
'''
    
    build_time = subprocess.run(['date'], capture_output=True, text=True).stdout.strip()
    platform_info = platform.platform()
    
    readme_path = os.path.join("release", "README.md")
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content.format(build_time=build_time, platform=platform_info))
    
    print(f"✅ 创建发布说明: {readme_path}")

def main():
    """主函数"""
    print("=" * 60)
    print("Bilibili2Navidrome 构建脚本")
    print("=" * 60)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 创建构建目录
    create_build_directories()
    
    # 复制资源文件
    copy_assets()
    
    # 构建可执行文件
    if not build_executable():
        sys.exit(1)
    
    # 创建安装包
    create_installer()
    
    # 创建发布说明
    create_readme()
    
    print("\n" + "=" * 60)
    print("✅ 构建完成！")
    print("发布文件位于: release/ 目录")
    print("=" * 60)

if __name__ == "__main__":
    main()
