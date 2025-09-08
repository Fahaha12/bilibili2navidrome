"""
标签控制器模块
"""
import logging
from flask import request, jsonify, session
from typing import Dict, Any

from services.tag_service import TagService
from services.navidrome_service import NavidromeService
from utils.validators import FileValidator
from utils.exceptions import ValidationError, TagEditError, FileError
from models.audio_file import AudioFile

logger = logging.getLogger(__name__)


class TagController:
    """标签控制器类"""
    
    def __init__(self):
        self.tag_service = TagService()
        self.navidrome_service = NavidromeService()
        self.file_validator = FileValidator()
    
    def get_edit_page_data(self, filename: str) -> Dict[str, Any]:
        """获取编辑页面数据"""
        try:
            # 验证文件名安全性
            if not filename or not self.file_validator.is_safe_filename(filename):
                raise ValidationError("无效的文件名")
            
            # 防止路径遍历攻击
            if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
                raise ValidationError("不安全的文件名")
            
            # 验证文件类型
            if not filename.lower().endswith('.mp3'):
                raise ValidationError("只支持MP3文件")
            
            # 获取文件路径
            from config import DOWNLOAD_PATH
            import os
            filepath = os.path.join(DOWNLOAD_PATH, filename)
            
            if not os.path.exists(filepath):
                raise FileError(f"文件不存在: {filename}")
            
            # 获取标签信息
            tags = self.tag_service.get_audio_tags(filepath)
            
            # 检查封面
            has_cover = self.tag_service.has_cover_image(filepath)
            
            # 保存当前文件名到session
            session['current_filename'] = filename
            
            return {
                'success': True,
                'data': {
                    'filename': filename,
                    'tags': tags,
                    'has_cover': has_cover
                }
            }
            
        except ValidationError as e:
            logger.warning(f"验证错误: {str(e)}")
            return {
                'success': False,
                'error': 'validation',
                'message': str(e),
                'status_code': 400
            }
        except FileError as e:
            logger.warning(f"文件错误: {str(e)}")
            return {
                'success': False,
                'error': 'file',
                'message': str(e),
                'status_code': 404
            }
        except Exception as e:
            logger.error(f"获取编辑页面数据失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': "加载编辑页面时出错",
                'status_code': 500
            }
    
    def save_tags(self) -> Dict[str, Any]:
        """保存标签"""
        try:
            # 获取并验证文件名
            filename = request.form.get('filename', '').strip()
            if not filename:
                raise ValidationError("文件名不能为空")
            
            # 验证文件名安全性
            if not self.file_validator.is_safe_filename(filename):
                raise ValidationError("无效的文件名")
            
            # 防止路径遍历攻击
            if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
                raise ValidationError("不安全的文件名")
            
            # 验证文件类型
            if not filename.lower().endswith('.mp3'):
                raise ValidationError("只支持MP3文件")
            
            # 获取文件路径
            from config import DOWNLOAD_PATH
            import os
            filepath = os.path.join(DOWNLOAD_PATH, filename)
            
            if not os.path.exists(filepath):
                raise FileError("文件不存在")
            
            # 获取并验证表单数据
            tags = {
                'title': request.form.get('title', '').strip(),
                'artist': request.form.get('artist', '').strip(),
                'album': request.form.get('album', '').strip(),
                'albumartist': request.form.get('albumartist', '').strip(),
                'date': request.form.get('date', '').strip(),
                'tracknumber': request.form.get('tracknumber', '').strip(),
                'genre': request.form.get('genre', '').strip()
            }
            
            # 验证必填字段
            if not tags['title'] or not tags['artist']:
                raise ValidationError("标题和艺术家为必填字段")
            
            # 限制字段长度
            for key, value in tags.items():
                if len(value) > 200:
                    tags[key] = value[:200]
            
            # 处理封面图片
            cover_file = request.files.get('cover')
            cover_path = None
            
            if cover_file and cover_file.filename:
                # 验证文件类型
                if not self.file_validator.is_valid_image(cover_file.filename):
                    raise ValidationError("不支持的图片格式")
                
                # 验证文件大小（限制为5MB）
                if hasattr(cover_file, 'content_length') and cover_file.content_length > 5 * 1024 * 1024:
                    raise ValidationError("图片文件过大，请选择小于5MB的图片")
                
                # 保存到临时目录
                from config import TEMP_PATH
                cover_path = os.path.join(TEMP_PATH, "new_cover.jpg")
                cover_file.save(cover_path)
            
            # 更新标签
            success = self.tag_service.update_audio_tags(filepath, tags, cover_path)
            
            if not success:
                raise TagEditError("标签更新失败")
            
            # 触发Navidrome扫描
            scan_success = self.navidrome_service.trigger_scan()
            scan_message = "，曲库更新成功" if scan_success else "，但曲库更新失败"
            
            return {
                'success': True,
                'message': f"标签更新成功{scan_message}"
            }
            
        except ValidationError as e:
            logger.warning(f"验证错误: {str(e)}")
            return {
                'success': False,
                'error': 'validation',
                'message': str(e),
                'status_code': 400
            }
        except TagEditError as e:
            logger.error(f"标签编辑错误: {str(e)}")
            return {
                'success': False,
                'error': 'tag_edit',
                'message': str(e),
                'status_code': 500
            }
        except FileError as e:
            logger.warning(f"文件错误: {str(e)}")
            return {
                'success': False,
                'error': 'file',
                'message': str(e),
                'status_code': 404
            }
        except Exception as e:
            logger.error(f"保存标签失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': "保存失败，请稍后重试",
                'status_code': 500
            }
    
    def get_cover_image(self) -> Dict[str, Any]:
        """获取封面图片"""
        try:
            filename = session.get('current_filename')
            if not filename:
                return {
                    'success': False,
                    'error': 'no_file',
                    'message': "未找到当前文件"
                }
            
            from config import DOWNLOAD_PATH
            import os
            import time
            from flask import send_file
            from mutagen.mp3 import MP3
            from mutagen.id3 import ID3
            from io import BytesIO
            
            filepath = os.path.join(DOWNLOAD_PATH, filename)
            cover_path = os.path.splitext(filepath)[0] + '.jpg'
            
            if os.path.exists(cover_path):
                timestamp = int(time.time())
                return {
                    'success': True,
                    'type': 'file',
                    'path': cover_path,
                    'timestamp': timestamp
                }
            
            # 尝试从音频文件内嵌封面获取
            audio = MP3(filepath, ID3=ID3)
            if 'APIC:' in audio:
                cover_data = audio['APIC:'].data
                timestamp = int(time.time())
                return {
                    'success': True,
                    'type': 'embedded',
                    'data': cover_data,
                    'timestamp': timestamp
                }
            
            return {
                'success': False,
                'error': 'no_cover',
                'message': "未找到封面图片"
            }
            
        except Exception as e:
            logger.error(f"获取封面失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': "获取封面失败"
            }
