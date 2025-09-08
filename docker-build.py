#!/usr/bin/env python3
"""
Docker构建脚本
"""
import os
import sys
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

def check_docker():
    """检查Docker是否安装"""
    print("检查Docker安装...")
    
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker未安装或未启动")
            return False
    except FileNotFoundError:
        print("❌ Docker未安装")
        return False

def check_docker_compose():
    """检查Docker Compose是否安装"""
    print("检查Docker Compose安装...")
    
    try:
        result = subprocess.run(['docker-compose', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker Compose已安装: {result.stdout.strip()}")
            return True
        else:
            print("❌ Docker Compose未安装")
            return False
    except FileNotFoundError:
        print("❌ Docker Compose未安装")
        return False

def create_docker_directories():
    """创建Docker需要的目录"""
    print("创建Docker目录...")
    
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
    
    env_file = '.env'
    if not os.path.exists(env_file):
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✅ 创建环境变量文件: {env_file}")
    else:
        print(f"✅ 环境变量文件已存在: {env_file}")

def build_docker_image():
    """构建Docker镜像"""
    print("构建Docker镜像...")
    
    image_name = "bilibili2navidrome"
    tag = "latest"
    
    command = f"docker build -t {image_name}:{tag} ."
    
    if not run_command(command, "Docker镜像构建"):
        return False
    
    print(f"✅ Docker镜像构建成功: {image_name}:{tag}")
    return True

def create_docker_scripts():
    """创建Docker管理脚本"""
    print("创建Docker管理脚本...")
    
    # Windows启动脚本
    windows_start = '''@echo off
echo 启动 Bilibili2Navidrome Docker 容器...
echo.
docker-compose up -d
echo.
echo 应用已启动，访问地址: http://localhost:5000
echo.
echo 查看日志: docker-compose logs -f
echo 停止应用: docker-compose down
echo.
pause
'''
    
    with open('start-docker.bat', 'w', encoding='utf-8') as f:
        f.write(windows_start)
    print("✅ 创建Windows启动脚本: start-docker.bat")
    
    # Unix启动脚本
    unix_start = '''#!/bin/bash
echo "启动 Bilibili2Navidrome Docker 容器..."
echo ""
docker-compose up -d
echo ""
echo "应用已启动，访问地址: http://localhost:5000"
echo ""
echo "查看日志: docker-compose logs -f"
echo "停止应用: docker-compose down"
echo ""
read -p "按回车键继续..."
'''
    
    with open('start-docker.sh', 'w', encoding='utf-8') as f:
        f.write(unix_start)
    
    os.chmod('start-docker.sh', 0o755)
    print("✅ 创建Unix启动脚本: start-docker.sh")
    
    # 停止脚本
    stop_script = '''#!/bin/bash
echo "停止 Bilibili2Navidrome Docker 容器..."
docker-compose down
echo "应用已停止"
'''
    
    with open('stop-docker.sh', 'w', encoding='utf-8') as f:
        f.write(stop_script)
    
    os.chmod('stop-docker.sh', 0o755)
    print("✅ 创建停止脚本: stop-docker.sh")

def create_docker_readme():
    """创建Docker部署说明"""
    readme_content = '''# Bilibili2Navidrome Docker 部署

## 系统要求

- Docker 20.10+
- Docker Compose 2.0+
- 至少 2GB 可用内存
- 至少 5GB 可用磁盘空间

## 快速开始

### 1. 启动应用

**Windows:**
```bash
start-docker.bat
```

**Linux/macOS:**
```bash
./start-docker.sh
```

**手动启动:**
```bash
docker-compose up -d
```

### 2. 访问应用

应用启动后，在浏览器中访问: http://localhost:5000

### 3. 停止应用

```bash
docker-compose down
```

## 配置说明

### 环境变量

编辑 `.env` 文件来配置应用参数：

```bash
# 应用配置
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-secret-key-here

# 登录配置
LOGIN_REQUIRED=True
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123

# Navidrome配置
NAVIDROME_URL=http://localhost:4533
NAVIDROME_API_KEY=your-api-key-here
```

### 数据持久化

以下目录会被持久化存储：
- `downloads/` - 下载的音频文件
- `temp/` - 临时文件
- `batch_storage/` - 批量下载任务数据
- `logs/` - 应用日志

## 管理命令

### 查看日志
```bash
docker-compose logs -f
```

### 重启应用
```bash
docker-compose restart
```

### 更新应用
```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 清理数据
```bash
docker-compose down -v
```

## 故障排除

### 常见问题

1. **端口被占用**
   - 修改 `docker-compose.yml` 中的端口映射
   - 或停止占用端口的其他服务

2. **权限问题**
   - 确保Docker有足够的权限
   - 检查目录权限设置

3. **内存不足**
   - 增加Docker的内存限制
   - 或关闭其他占用内存的应用

### 查看容器状态
```bash
docker-compose ps
```

### 进入容器调试
```bash
docker-compose exec bilibili2navidrome bash
```

## 生产环境部署

### 使用外部数据库
```yaml
# docker-compose.yml
services:
  bilibili2navidrome:
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/bilibili
    depends_on:
      - db
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=bilibili
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### 使用反向代理
```yaml
# docker-compose.yml
services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - bilibili2navidrome
```

## 安全建议

1. **更改默认密码**
   - 修改 `.env` 中的 `ADMIN_PASSWORD`

2. **使用HTTPS**
   - 配置SSL证书
   - 使用反向代理

3. **限制访问**
   - 使用防火墙限制端口访问
   - 配置IP白名单

4. **定期备份**
   - 备份重要数据
   - 定期更新镜像

## 版本信息

版本: 1.0.0
Docker版本: 20.10+
Python版本: 3.11
'''
    
    with open('DOCKER_README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✅ 创建Docker部署说明: DOCKER_README.md")

def main():
    """主函数"""
    print("=" * 60)
    print("Bilibili2Navidrome Docker 构建脚本")
    print("=" * 60)
    
    # 检查Docker
    if not check_docker():
        print("请先安装Docker: https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    # 检查Docker Compose
    if not check_docker_compose():
        print("请先安装Docker Compose: https://docs.docker.com/compose/install/")
        sys.exit(1)
    
    # 创建目录
    create_docker_directories()
    
    # 创建环境变量文件
    create_env_file()
    
    # 构建Docker镜像
    if not build_docker_image():
        sys.exit(1)
    
    # 创建管理脚本
    create_docker_scripts()
    
    # 创建说明文档
    create_docker_readme()
    
    print("\n" + "=" * 60)
    print("✅ Docker构建完成！")
    print("启动应用: ./start-docker.sh (Linux/macOS) 或 start-docker.bat (Windows)")
    print("访问地址: http://localhost:5000")
    print("=" * 60)

if __name__ == "__main__":
    main()
