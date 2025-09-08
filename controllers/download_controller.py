"""
下载控制器模块
"""
import logging
from flask import request, jsonify, redirect, url_for, session
from typing import Dict, Any

from services.download_service import DownloadService
from services.tag_service import TagService
from services.navidrome_service import NavidromeService
from utils.validators import URLValidator, FileValidator
from utils.exceptions import ValidationError, DownloadError, FFmpegError
from models.audio_file import DownloadResult, AudioFile

logger = logging.getLogger(__name__)


class DownloadController:
    """下载控制器类"""
    
    def __init__(self):
        self.download_service = DownloadService()
        self.tag_service = TagService()
        self.navidrome_service = NavidromeService()
        self.url_validator = URLValidator()
        self.file_validator = FileValidator()
    
    def handle_download_request(self) -> Dict[str, Any]:
        """处理下载请求"""
        try:
            # 获取并验证输入
            url = request.form.get('url', '').strip()
            if not url:
                raise ValidationError("请输入URL")
            
            # 尝试从文本中提取URL
            extracted_url = self.url_validator.extract_bilibili_url(url)
            if extracted_url:
                url = extracted_url
            
            # 验证URL格式
            if not self.url_validator.is_valid_bilibili_url(url):
                raise ValidationError("无效的Bilibili URL，请确保URL来自bilibili.com或b23.tv，或输入有效的BV号")
            
            # 提前检查FFmpeg
            if not self.download_service.check_ffmpeg_installed():
                raise FFmpegError("FFmpeg未安装，请安装FFmpeg并添加到系统PATH")
            
            # 执行下载
            result = self.download_service.download_audio(url)
            
            if result['status'] == 'error':
                raise DownloadError(result['message'])
            
            # 验证下载结果
            if 'filename' not in result:
                raise DownloadError("未获取到文件名")
            
            # 创建音频文件对象
            audio_file = AudioFile(
                filename=result['filename'],
                filepath=result['filepath'],
                title=result['title'],
                artist=result['artist'],
                duration=result['duration'],
                cover_filename=result.get('cover_filename'),
                original_url=result['original_url']
            )
            
            # 保存当前文件名到session
            session['current_filename'] = result['filename']
            
            # 返回重定向信息
            return {
                'success': True,
                'redirect_url': url_for('edit_tags', filename=result['filename'])
            }
            
        except ValidationError as e:
            logger.warning(f"验证错误: {str(e)}")
            return {
                'success': False,
                'error': 'validation',
                'message': str(e),
                'status_code': 400
            }
        except FFmpegError as e:
            logger.error(f"FFmpeg错误: {str(e)}")
            return {
                'success': False,
                'error': 'ffmpeg',
                'message': str(e),
                'status_code': 500
            }
        except DownloadError as e:
            logger.error(f"下载错误: {str(e)}")
            return {
                'success': False,
                'error': 'download',
                'message': str(e),
                'status_code': 500
            }
        except Exception as e:
            logger.error(f"下载过程中出错: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': "下载过程中发生错误，请稍后重试",
                'status_code': 500
            }
    
    def check_ffmpeg_status(self) -> Dict[str, Any]:
        """检查FFmpeg状态"""
        try:
            installed = self.download_service.check_ffmpeg_installed()
            return {
                'success': True,
                'installed': installed
            }
        except Exception as e:
            logger.error(f"检查FFmpeg状态失败: {str(e)}")
            return {
                'success': False,
                'installed': False,
                'error': str(e)
            }
    
    def get_download_progress(self, url: str) -> Dict[str, Any]:
        """获取下载进度"""
        try:
            progress = self.download_service.get_download_progress(url)
            return {
                'success': True,
                'progress': progress
            }
        except Exception as e:
            logger.error(f"获取下载进度失败: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
