"""
下载服务模块
"""
import os
import re
import shutil
import subprocess
import logging
from pathlib import Path
from typing import Dict, Any, Optional
import yt_dlp

from utils.exceptions import DownloadError, FFmpegError
from utils.validators import InputSanitizer
from config import DOWNLOAD_PATH, TEMP_PATH

logger = logging.getLogger(__name__)


class DownloadService:
    """下载服务类"""
    
    def __init__(self):
        self.download_path = Path(DOWNLOAD_PATH)
        self.temp_path = Path(TEMP_PATH)
        self._ensure_directories()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        self.download_path.mkdir(parents=True, exist_ok=True)
        self.temp_path.mkdir(parents=True, exist_ok=True)
    
    def check_ffmpeg_installed(self) -> bool:
        """检查FFmpeg是否安装"""
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=5
            )
            return 'ffmpeg version' in result.stdout or 'ffmpeg version' in result.stderr
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception):
            return False
    
    def _clean_temp_files(self):
        """清理临时文件"""
        if self.temp_path.exists():
            shutil.rmtree(self.temp_path)
        self.temp_path.mkdir(exist_ok=True)
    
    def _get_ydl_opts(self) -> Dict[str, Any]:
        """获取yt-dlp配置选项"""
        cookies_path = self.temp_path / 'cookies.txt'
        
        return {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_path / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'writethumbnail': True,
            'postprocessor_args': [
                '-metadata', 'comment=Downloaded from Bilibili'
            ],
            'ignoreerrors': True,
            'logger': logger,
            'format_sort': ['res:720', 'ext:mp4'],
            'cookies': str(cookies_path) if cookies_path.exists() else None,
            'extract_flat': False,
            'no_warnings': False,
        }
    
    def _download_thumbnail(self, url: str, base_name: str) -> Optional[str]:
        """下载缩略图"""
        try:
            cover_filename = f"{base_name}.jpg"
            cover_path = self.download_path / cover_filename
            
            if cover_path.exists():
                return cover_filename
            
            thumbnail_ydl_opts = {
                'outtmpl': str(cover_path),
                'skip_download': True,
                'writethumbnail': True,
            }
            
            with yt_dlp.YoutubeDL(thumbnail_ydl_opts) as ydl:
                ydl.download([url])
            
            return cover_filename if cover_path.exists() else None
        except Exception as e:
            logger.warning(f"缩略图下载失败: {str(e)}")
            return None
    
    def download_audio(self, url: str) -> Dict[str, Any]:
        """下载Bilibili音频"""
        try:
            # 检查FFmpeg
            if not self.check_ffmpeg_installed():
                raise FFmpegError("FFmpeg未安装，请安装FFmpeg并添加到系统PATH")
            
            # 清理临时文件
            self._clean_temp_files()
            
            # 配置yt-dlp
            ydl_opts = self._get_ydl_opts()
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 提取视频信息
                info = ydl.extract_info(url, download=False)
                
                if not info or 'title' not in info:
                    raise DownloadError("无法获取视频信息")
                
                # 清理标题作为文件名
                safe_title = InputSanitizer.sanitize_filename(info['title'])
                if not safe_title:
                    safe_title = "未知标题"
                
                # 设置输出模板
                ydl_opts['outtmpl'] = str(self.download_path / f"{safe_title}.%(ext)s")
                
                # 重新创建yt-dlp实例并下载
                with yt_dlp.YoutubeDL(ydl_opts) as download_ydl:
                    download_ydl.download([url])
                
                # 查找生成的MP3文件
                mp3_files = list(self.download_path.glob(f"{safe_title}.mp3"))
                if not mp3_files:
                    raise DownloadError("文件转换失败，未生成MP3文件")
                
                final_file = mp3_files[0]
                final_filename = final_file.name
                
                # 下载缩略图
                cover_filename = self._download_thumbnail(url, safe_title)
                
                return {
                    "status": "success",
                    "filename": final_filename,
                    "filepath": str(final_file),
                    "title": info.get('title', '未知标题'),
                    "artist": info.get('uploader', '未知艺术家'),
                    "duration": info.get('duration', 0),
                    "cover_filename": cover_filename,
                    "original_url": url
                }
                
        except FFmpegError:
            raise
        except Exception as e:
            logger.error(f"下载失败: {str(e)}")
            # 清理可能的部分下载文件
            if 'final_file' in locals() and final_file.exists():
                final_file.unlink()
            raise DownloadError(f"下载失败: {str(e)}")
    
    def get_download_progress(self, url: str) -> Dict[str, Any]:
        """获取下载进度（用于实时更新）"""
        # 这里可以实现进度回调
        # 由于yt-dlp的进度回调比较复杂，暂时返回基础信息
        return {
            "status": "downloading",
            "progress": 0,
            "message": "正在下载..."
        }
