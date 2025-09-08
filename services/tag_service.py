"""
音频标签服务模块
"""
import os
import shutil
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, error
from mutagen.mp3 import MP3

from utils.exceptions import TagEditError, FileError
from config import DOWNLOAD_PATH, DEFAULT_TAGS

logger = logging.getLogger(__name__)


class TagService:
    """音频标签服务类"""
    
    def __init__(self):
        self.download_path = Path(DOWNLOAD_PATH)
        self.default_tags = DEFAULT_TAGS
    
    def get_audio_tags(self, filepath: str) -> Dict[str, str]:
        """获取音频文件的元数据标签"""
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                raise FileError(f"文件不存在: {filepath}")
            
            # 尝试读取ID3标签
            try:
                audio = MP3(str(file_path), ID3=EasyID3)
                tags = {
                    'title': self._get_tag_value(audio, 'title'),
                    'artist': self._get_tag_value(audio, 'artist'),
                    'album': self._get_tag_value(audio, 'album'),
                    'albumartist': self._get_tag_value(audio, 'albumartist'),
                    'date': self._get_tag_value(audio, 'date'),
                    'tracknumber': self._get_track_number(audio),
                    'genre': self._get_tag_value(audio, 'genre')
                }
                return tags
            except error:
                # 如果ID3标签不存在，返回默认值
                logger.warning(f"无法读取ID3标签: {filepath}")
                return self.default_tags.copy()
                
        except Exception as e:
            logger.error(f"读取标签失败: {str(e)}")
            return self.default_tags.copy()
    
    def _get_tag_value(self, audio: MP3, tag_name: str) -> str:
        """安全获取标签值"""
        try:
            value = audio.get(tag_name, [''])[0]
            return str(value) if value else ''
        except (IndexError, TypeError, AttributeError):
            return ''
    
    def _get_track_number(self, audio: MP3) -> str:
        """获取曲目号（只返回数字部分）"""
        try:
            track = audio.get('tracknumber', ['0/0'])[0]
            if isinstance(track, str) and '/' in track:
                return track.split('/')[0]
            return str(track) if track else '0'
        except (IndexError, TypeError, AttributeError):
            return '0'
    
    def has_cover_image(self, filepath: str) -> bool:
        """检查音频文件是否有封面图片"""
        try:
            file_path = Path(filepath)
            
            # 检查外部封面文件
            base_name = file_path.stem
            cover_path = file_path.parent / f"{base_name}.jpg"
            if cover_path.exists():
                return True
            
            # 检查内嵌封面
            try:
                audio = MP3(str(file_path), ID3=ID3)
                return 'APIC:' in audio
            except:
                return False
                
        except Exception as e:
            logger.warning(f"检查封面失败: {str(e)}")
            return False
    
    def update_audio_tags(self, filepath: str, tags: Dict[str, str], cover_path: Optional[str] = None) -> bool:
        """更新音频文件的元数据标签"""
        try:
            file_path = Path(filepath)
            
            if not file_path.exists():
                raise FileError(f"文件不存在: {filepath}")
            
            # 验证必填字段
            if not tags.get('title') or not tags.get('artist'):
                raise TagEditError("标题和艺术家为必填字段")
            
            # 备份原始文件
            backup_path = file_path.with_suffix(file_path.suffix + '.bak')
            shutil.copy2(file_path, backup_path)
            
            try:
                # 使用EasyID3更新简单标签
                audio = MP3(str(file_path), ID3=EasyID3)
                
                # 初始化缺少的标签
                for tag in ['title', 'artist', 'album', 'albumartist', 'date', 'tracknumber', 'genre']:
                    if tag not in audio:
                        audio[tag] = [self.default_tags.get(tag, '')]
                
                # 更新标签
                for tag_name, tag_value in tags.items():
                    if tag_value and tag_name in ['title', 'artist', 'album', 'albumartist', 'date', 'tracknumber', 'genre']:
                        audio[tag_name] = [tag_value]
                
                audio.save()
                
                # 处理封面
                if cover_path and Path(cover_path).exists():
                    self._update_cover_image(str(file_path), cover_path)
                
                # 删除备份
                backup_path.unlink()
                return True
                
            except Exception as e:
                # 恢复备份
                shutil.move(str(backup_path), str(file_path))
                raise TagEditError(f"更新标签失败: {str(e)}")
                
        except TagEditError:
            raise
        except Exception as e:
            logger.error(f"更新标签失败: {str(e)}")
            return False
    
    def _update_cover_image(self, filepath: str, cover_path: str):
        """更新音频文件的封面图片"""
        try:
            audio = ID3(filepath)
            
            # 删除现有封面
            if 'APIC:' in audio:
                del audio['APIC:']
            
            # 添加新封面
            with open(cover_path, 'rb') as f:
                cover_data = f.read()
            
            audio.add(APIC(
                encoding=3,  # UTF-8
                mime='image/jpeg',
                type=3,  # 封面图片
                desc='Cover',
                data=cover_data
            ))
            audio.save()
            
        except Exception as e:
            logger.error(f"更新封面失败: {str(e)}")
            raise TagEditError(f"更新封面失败: {str(e)}")
    
    def get_audio_duration(self, filepath: str) -> float:
        """获取音频时长（秒）"""
        try:
            audio = MP3(filepath)
            return audio.info.length if audio.info else 0.0
        except Exception as e:
            logger.warning(f"获取音频时长失败: {str(e)}")
            return 0.0
    
    def validate_tags(self, tags: Dict[str, str]) -> Dict[str, str]:
        """验证和清理标签数据"""
        cleaned_tags = {}
        
        for key, value in tags.items():
            if isinstance(value, str):
                # 清理字符串
                cleaned_value = value.strip()
                # 限制长度
                if len(cleaned_value) > 200:
                    cleaned_value = cleaned_value[:200]
                cleaned_tags[key] = cleaned_value
            else:
                cleaned_tags[key] = str(value) if value else ''
        
        return cleaned_tags
