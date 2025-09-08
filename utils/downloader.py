import os
import re
import traceback
import yt_dlp
import logging
from config import DOWNLOAD_PATH, TEMP_PATH
import shutil
import subprocess

# 设置日志
logger = logging.getLogger(__name__)

def sanitize_filename(filename):
    """移除文件名中的非法字符"""
    if not filename:
        return ""
    # 移除危险字符
    cleaned = re.sub(r'[\\/*?:"<>|]', "", filename)
    # 移除多余空格
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # 移除开头和结尾的点
    cleaned = cleaned.strip('.')
    return cleaned

def download_bilibili_audio(url):
    """下载B站音频并返回文件信息"""
    try:
        # 检查FFmpeg是否安装
        if not check_ffmpeg_installed():
            raise Exception("FFmpeg未安装，请安装FFmpeg并添加到系统PATH")
        
        # 清理之前的临时文件
        if os.path.exists(TEMP_PATH):
            shutil.rmtree(TEMP_PATH)
        os.makedirs(TEMP_PATH, exist_ok=True)
        os.makedirs(DOWNLOAD_PATH, exist_ok=True)
        
        # 构建输出文件名模板
        safe_title_template = sanitize_filename('%(title)s')
        if not safe_title_template:
            safe_title_template = 'Bilibili_Audio'
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(DOWNLOAD_PATH, f'{safe_title_template}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,  # 确保下载封面
            'postprocessor_args': [
                '-metadata', 'comment=Downloaded from Bilibili'
            ],
            'ignoreerrors': True,
            'logger': logger,
            # 添加以下配置以解决会员视频问题
            'format_sort': ['res:720', 'ext:mp4'],  # 优先选择720p格式
            'cookies': os.path.join(TEMP_PATH, 'cookies.txt') if os.path.exists(os.path.join(TEMP_PATH, 'cookies.txt')) else None,
            'extract_flat': False,
            'no_warnings': False,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            
            # 确保下载成功
            if not info or 'title' not in info:
                raise Exception("无法获取视频信息")
            
            # 准备返回的文件信息
            filename = ydl.prepare_filename(info)
            final_filename = filename.replace('.webm', '.mp3').replace('.m4a', '.mp3')
            
            # 确保文件存在
            if not os.path.exists(final_filename):
                raise Exception("文件转换失败，未生成MP3文件")
            
            # 获取基础文件名（不带扩展名）并清理
            base_name = os.path.splitext(os.path.basename(final_filename))[0]
            base_name = sanitize_filename(base_name)
            
            # 处理封面 - 直接保存到下载目录
            cover_filename = None
            if 'thumbnail' in info and info['thumbnail']:
                try:
                    # 获取原始封面路径（yt-dlp下载的封面在下载目录）
                    original_cover_path = os.path.join(DOWNLOAD_PATH, f"{base_name}.jpg")
                    
                    # 如果yt-dlp没有自动保存封面，尝试手动下载
                    if not os.path.exists(original_cover_path):
                        # 尝试从视频信息中下载封面
                        cover_filename = f"{base_name}.jpg"
                        cover_path = os.path.join(DOWNLOAD_PATH, cover_filename)
                        
                        thumbnail_ydl_opts = {
                            'outtmpl': cover_path,
                            'skip_download': True,
                            'writethumbnail': True,
                        }
                        with yt_dlp.YoutubeDL(thumbnail_ydl_opts) as thumbnail_ydl:
                            thumbnail_ydl.download([url])
                    else:
                        cover_filename = os.path.basename(original_cover_path)
                except Exception as e:
                    logger.warning(f"封面下载失败: {str(e)}")
            
            return {
                "status": "success",
                "filename": os.path.basename(final_filename),
                "filepath": final_filename,
                "title": info.get('title', '未知标题'),
                "artist": info.get('uploader', '未知艺术家'),
                "duration": info.get('duration', 0),
                "cover_filename": cover_filename,  # 添加封面文件名
                "original_url": url
            }
    except Exception as e:
        logger.error(f"下载失败: {str(e)}\n{traceback.format_exc()}")
        # 清理可能的部分下载文件
        if 'final_filename' in locals() and os.path.exists(final_filename):
            os.remove(final_filename)
        return {
            "status": "error",
            "message": f"下载失败: {str(e)}"
        }
    
def check_ffmpeg_installed():
    """检查FFmpeg是否安装"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-version'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        return 'ffmpeg version' in result.stdout
    except Exception:
        return False