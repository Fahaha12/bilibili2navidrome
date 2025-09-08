# Bilibili2Navidrome

一个功能强大的Bilibili音频下载器，支持单个和批量下载，集成Navidrome音乐服务器。

## 功能特性

### 🎵 核心功能
- **单个视频下载** - 支持Bilibili视频音频提取
- **批量下载** - 一次性下载多个视频音频
- **音频标签编辑** - 自动或手动编辑音频元数据
- **Navidrome集成** - 自动触发音乐服务器扫描
- **用户认证** - 安全的登录系统
- **实时进度监控** - 实时查看下载进度

### 🚀 技术特性
- **多格式URL支持** - 完整URL、短链接、BV号、分享文本
- **智能验证** - 自动验证URL有效性
- **异步处理** - 多线程下载，不阻塞界面
- **错误处理** - 完善的异常处理和恢复机制
- **数据持久化** - 任务状态自动保存
- **跨平台支持** - Windows、Linux、macOS

## 快速开始

### 方式一：一键安装（推荐）

```bash
# 下载项目
git clone <repository-url>
cd bilibili2navidrome

# 运行一键安装
python install.py

# 启动应用
./start.sh  # Linux/macOS
# 或
start.bat   # Windows
```

### 方式二：Docker部署

```bash
# 构建和启动
python docker-build.py
./start-docker.sh
```

### 方式三：独立可执行文件

```bash
# 构建可执行文件
python build.py

# 分发到目标机器
# 运行 release/ 目录中的启动脚本
```

## 系统要求

### 基本要求
- Python 3.8+ (源码部署)
- FFmpeg (必须)
- 2GB+ 内存
- 1GB+ 磁盘空间

### 可选要求
- Docker 20.10+ (容器部署)
- Navidrome服务器 (音乐集成)

## 安装FFmpeg

### Windows
1. 下载: https://ffmpeg.org/download.html
2. 解压到任意目录
3. 将bin目录添加到系统PATH

### Linux
```bash
sudo apt install ffmpeg
```

### macOS
```bash
brew install ffmpeg
```

## 配置说明

### 环境变量配置
复制 `env.example` 为 `.env` 并修改配置：

```bash
# 登录配置
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your-password

# Navidrome配置
NAVIDROME_URL=http://localhost:4533
NAVIDROME_API_KEY=your-api-key

# 下载配置
DOWNLOAD_TIMEOUT=300
MAX_DOWNLOAD_SIZE=1073741824
```

### 应用配置
编辑 `config.py` 文件：

```python
# 路径配置
DOWNLOAD_PATH = './downloads'
TEMP_PATH = './temp'

# 登录配置
LOGIN_REQUIRED = True
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin123'
```

## 使用指南

### 1. 单个下载
1. 访问 http://localhost:5000
2. 输入Bilibili视频URL
3. 点击下载
4. 编辑音频标签
5. 保存到音乐库

### 2. 批量下载
1. 点击导航栏"批量下载"
2. 输入任务名称和URL列表
3. 验证URL有效性
4. 创建批量下载任务
5. 启动下载并监控进度

### 3. 音频标签编辑
- 自动提取视频信息作为标签
- 手动编辑标题、艺术家、专辑等
- 上传自定义封面图片
- 支持多种音频格式

## API接口

### 批量下载API
```http
# 创建批量下载任务
POST /api/batch/create
Content-Type: application/json

{
    "name": "我的音乐收藏",
    "urls": "https://www.bilibili.com/video/BV1xxx\nhttps://b23.tv/xxx",
    "auto_edit_tags": true
}

# 获取任务列表
GET /api/batch/list

# 启动任务
POST /api/batch/{batch_id}/start

# 获取任务进度
GET /api/batch/{batch_id}/progress
```

### 其他API
```http
# 检查FFmpeg状态
GET /api/ffmpeg/check

# 上传cookies
POST /api/upload/cookies

# 获取封面图片
GET /cover
```

## 部署方式

### 开发环境
```bash
# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python app.py
```

### 生产环境
```bash
# Docker部署
docker-compose up -d

# 或使用独立可执行文件
./Bilibili2Navidrome
```

### 服务器部署
```bash
# 使用systemd服务
sudo systemctl enable bilibili2navidrome
sudo systemctl start bilibili2navidrome

# 使用Nginx反向代理
# 配置SSL证书
# 设置防火墙规则
```

## 故障排除

### 常见问题

#### 1. FFmpeg未找到
```bash
# 检查安装
ffmpeg -version

# 检查PATH
echo $PATH  # Linux/macOS
echo %PATH% # Windows
```

#### 2. 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :5000

# 修改端口
export PORT=8080
```

#### 3. 下载失败
- 检查网络连接
- 确认URL有效性
- 查看应用日志
- 检查FFmpeg安装

#### 4. 权限问题
```bash
# Linux/macOS
chmod +x start.sh
chmod 755 downloads temp

# Windows
# 以管理员身份运行
```

### 日志查看
```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
grep ERROR app.log

# 查看Docker日志
docker-compose logs -f
```

## 项目结构

```
bilibili2navidrome/
├── app.py                 # 主应用文件
├── config.py              # 配置文件
├── requirements.txt       # Python依赖
├── dockerfile            # Docker配置
├── docker-compose.yml    # Docker Compose配置
├── build.py              # 构建脚本
├── install.py            # 安装脚本
├── models/               # 数据模型
│   ├── audio_file.py
│   ├── user.py
│   └── batch_download.py
├── services/             # 业务逻辑
│   ├── download_service.py
│   ├── tag_service.py
│   ├── navidrome_service.py
│   ├── auth_service.py
│   └── batch_download_service.py
├── controllers/          # 控制器
│   ├── download_controller.py
│   ├── tag_controller.py
│   ├── auth_controller.py
│   └── batch_controller.py
├── utils/                # 工具模块
│   ├── validators.py
│   ├── exceptions.py
│   ├── logger.py
│   ├── downloader.py
│   ├── tag_editor.py
│   └── navidrome.py
└── templates/            # 前端模板
    ├── layout.html
    ├── index.html
    ├── batch_download.html
    └── edit.html
```

## 贡献指南

### 开发环境设置
```bash
# 克隆项目
git clone <repository-url>
cd bilibili2navidrome

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# 或
venv\Scripts\activate     # Windows

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_packaging.py
```

### 代码规范
- 使用Python 3.8+语法
- 遵循PEP 8代码风格
- 添加类型注解
- 编写单元测试
- 更新文档

### 提交代码
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

## 许可证

本项目采用MIT许可证，详见LICENSE文件。

## 技术支持

### 获取帮助
1. 查看文档和FAQ
2. 检查GitHub Issues
3. 联系技术支持

### 报告问题
1. 描述问题现象
2. 提供错误日志
3. 说明环境信息
4. 提供复现步骤

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持单个和批量下载
- 集成Navidrome音乐服务器
- 提供多种部署方式
- 完整的Web界面和API

## 致谢

感谢以下开源项目：
- [Flask](https://flask.palletsprojects.com/) - Web框架
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载
- [mutagen](https://mutagen.readthedocs.io/) - 音频标签处理
- [Bootstrap](https://getbootstrap.com/) - 前端框架

---

**开始使用Bilibili2Navidrome，享受便捷的音频下载体验！**
