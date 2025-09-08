# Bilibili2Navidrome 部署指南

## 部署方式概览

本项目提供多种部署方式，适合不同的使用场景：

1. **独立可执行文件** - 适合个人用户，无需安装Python环境
2. **Docker容器** - 适合服务器部署，环境隔离
3. **源码部署** - 适合开发者和高级用户
4. **一键安装** - 适合快速部署和测试

## 方式一：独立可执行文件部署

### 适用场景
- 个人用户
- 没有Python环境的计算机
- 需要简单部署的场景

### 系统要求
- Windows 10/11 或 Linux/macOS
- 至少 2GB 可用内存
- 至少 1GB 可用磁盘空间
- FFmpeg (必须安装)

### 部署步骤

#### 1. 构建可执行文件
```bash
# 安装构建依赖
pip install pyinstaller

# 运行构建脚本
python build.py
```

#### 2. 分发部署
构建完成后，`release/` 目录包含所有必要文件：
- `Bilibili2Navidrome.exe` (Windows) 或 `Bilibili2Navidrome` (Linux/macOS)
- `启动.bat` (Windows) 或 `启动.sh` (Linux/macOS)
- 配置文件和环境变量示例
- 使用说明文档

#### 3. 目标机器部署
1. 将 `release/` 目录复制到目标机器
2. 安装 FFmpeg 并添加到系统 PATH
3. 运行启动脚本

### 优势
- ✅ 无需安装Python环境
- ✅ 单文件部署
- ✅ 跨平台支持
- ✅ 简单易用

### 劣势
- ❌ 文件体积较大
- ❌ 启动速度较慢
- ❌ 更新需要重新构建

## 方式二：Docker容器部署

### 适用场景
- 服务器部署
- 需要环境隔离
- 生产环境
- 团队协作

### 系统要求
- Docker 20.10+
- Docker Compose 2.0+
- 至少 4GB 可用内存
- 至少 10GB 可用磁盘空间

### 部署步骤

#### 1. 准备Docker环境
```bash
# 安装Docker
# Windows: 下载Docker Desktop
# Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh
# macOS: brew install docker

# 安装Docker Compose
# 通常随Docker Desktop一起安装
```

#### 2. 构建和启动
```bash
# 运行Docker构建脚本
python docker-build.py

# 启动应用
./start-docker.sh  # Linux/macOS
# 或
start-docker.bat   # Windows
```

#### 3. 访问应用
- 应用地址: http://localhost:5000
- 查看日志: `docker-compose logs -f`
- 停止应用: `docker-compose down`

### 优势
- ✅ 环境隔离
- ✅ 易于扩展
- ✅ 版本管理
- ✅ 生产就绪

### 劣势
- ❌ 需要Docker环境
- ❌ 资源占用较高
- ❌ 学习成本

## 方式三：源码部署

### 适用场景
- 开发者
- 需要自定义修改
- 学习研究
- 高级用户

### 系统要求
- Python 3.8+
- pip
- FFmpeg
- 至少 2GB 可用内存
- 至少 1GB 可用磁盘空间

### 部署步骤

#### 1. 一键安装
```bash
# 运行安装脚本
python install.py
```

#### 2. 手动安装
```bash
# 克隆项目
git clone <repository-url>
cd bilibili2navidrome

# 安装依赖
pip install -r requirements.txt

# 创建目录
mkdir -p downloads temp batch_storage logs

# 配置环境变量
cp env.example .env
# 编辑 .env 文件

# 启动应用
python app.py
```

### 优势
- ✅ 完全控制
- ✅ 易于调试
- ✅ 快速更新
- ✅ 自定义修改

### 劣势
- ❌ 需要Python环境
- ❌ 依赖管理复杂
- ❌ 环境配置繁琐

## 方式四：一键安装部署

### 适用场景
- 快速测试
- 临时使用
- 学习体验
- 简单部署

### 系统要求
- Python 3.8+
- 网络连接
- 至少 2GB 可用内存

### 部署步骤

#### 1. 下载项目
```bash
# 下载项目文件
wget <project-url>
# 或
git clone <repository-url>
```

#### 2. 运行安装脚本
```bash
# 运行一键安装
python install.py
```

#### 3. 启动应用
```bash
# 使用启动脚本
./start.sh  # Linux/macOS
# 或
start.bat   # Windows
```

### 优势
- ✅ 自动化安装
- ✅ 依赖自动解决
- ✅ 配置自动生成
- ✅ 快速部署

### 劣势
- ❌ 需要Python环境
- ❌ 网络依赖
- ❌ 权限要求

## 生产环境部署建议

### 1. 服务器配置
```yaml
# 推荐配置
CPU: 2核心以上
内存: 4GB以上
磁盘: 50GB以上
网络: 100Mbps以上
```

### 2. 安全配置
```bash
# 修改默认密码
ADMIN_PASSWORD=your-strong-password

# 启用HTTPS
# 使用反向代理 (Nginx/Apache)
# 配置防火墙
# 定期备份数据
```

### 3. 性能优化
```bash
# 调整并发数
MAX_CONCURRENT_DOWNLOADS=5

# 优化下载超时
DOWNLOAD_TIMEOUT=600

# 配置日志级别
LOG_LEVEL=WARNING
```

### 4. 监控和维护
```bash
# 设置日志轮转
LOG_MAX_SIZE=10485760
LOG_BACKUP_COUNT=10

# 定期清理临时文件
# 监控磁盘空间
# 设置健康检查
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

# 重新安装
# Windows: 下载并添加到PATH
# Linux: sudo apt install ffmpeg
# macOS: brew install ffmpeg
```

#### 2. 端口被占用
```bash
# 检查端口占用
netstat -tulpn | grep :5000  # Linux
netstat -an | grep :5000     # Windows/macOS

# 修改端口
export PORT=8080
# 或修改config.py
```

#### 3. 权限问题
```bash
# Linux/macOS权限
chmod +x start.sh
chmod 755 downloads temp

# Windows权限
# 以管理员身份运行
```

#### 4. 内存不足
```bash
# 检查内存使用
free -h  # Linux
top      # 通用

# 优化配置
# 减少并发下载数
# 清理临时文件
```

### 日志分析
```bash
# 查看应用日志
tail -f app.log

# 查看错误日志
grep ERROR app.log

# 查看下载日志
grep "download" app.log
```

## 更新和维护

### 1. 应用更新
```bash
# 源码更新
git pull origin main
pip install -r requirements.txt

# Docker更新
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 可执行文件更新
# 重新构建和分发
```

### 2. 数据备份
```bash
# 备份重要数据
tar -czf backup-$(date +%Y%m%d).tar.gz downloads batch_storage .env

# 恢复数据
tar -xzf backup-20231201.tar.gz
```

### 3. 性能监控
```bash
# 监控资源使用
htop
iotop
df -h

# 监控应用状态
curl http://localhost:5000/health
```

## 技术支持

### 获取帮助
1. 查看日志文件
2. 检查系统要求
3. 参考故障排除部分
4. 联系技术支持

### 贡献代码
1. Fork项目
2. 创建功能分支
3. 提交代码
4. 创建Pull Request

### 报告问题
1. 描述问题现象
2. 提供错误日志
3. 说明环境信息
4. 提供复现步骤

## 版本信息

- 当前版本: 1.0.0
- 支持平台: Windows, Linux, macOS
- Python版本: 3.8+
- 更新日期: 2024-01-01

---

选择适合你需求的部署方式，开始使用Bilibili2Navidrome吧！
