# 使用官方 Python 基础镜像
FROM python:3.11-slim

# 设置环境变量
ENV DOWNLOAD_PATH=/app/downloads
ENV TEMP_PATH=/app/temp
ENV PYTHONUNBUFFERED=1

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    wget \
    && rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 复制项目文件
COPY . .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建必要的目录
RUN mkdir -p ${DOWNLOAD_PATH} ${TEMP_PATH}

# 暴露端口
EXPOSE 5000

# 设置启动命令
CMD ["python", "app.py"]