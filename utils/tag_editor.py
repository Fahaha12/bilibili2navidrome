import shutil
import logging
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TRCK, TPE2, error
from mutagen.mp3 import MP3
import os
from config import DOWNLOAD_PATH, DEFAULT_TAGS
import traceback

# 设置日志
logger = logging.getLogger(__name__)

def get_audio_tags(filepath):
    """获取音频文件的元数据标签"""
    try:
        # 确保文件存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 尝试读取ID3标签
        try:
            audio = MP3(filepath, ID3=EasyID3)
            tags = {
                'title': _get_tag_value(audio, 'title'),
                'artist': _get_tag_value(audio, 'artist'),
                'album': _get_tag_value(audio, 'album'),
                'albumartist': _get_tag_value(audio, 'albumartist'),
                'date': _get_tag_value(audio, 'date'),
                'tracknumber': _get_track_number(audio),
                'genre': _get_tag_value(audio, 'genre')
            }
            return tags
        except error:
            # 如果ID3标签不存在，返回默认值
            logger.warning(f"无法读取ID3标签: {filepath}")
            return DEFAULT_TAGS.copy()
    except Exception as e:
        logger.error(f"读取标签失败: {str(e)}\n{traceback.format_exc()}")
        return DEFAULT_TAGS.copy()

def _get_tag_value(audio, tag_name):
    """安全获取标签值"""
    try:
        value = audio.get(tag_name, [''])[0]
        return str(value) if value else ''
    except (IndexError, TypeError, AttributeError):
        return ''

def _get_track_number(audio):
    """获取曲目号（只返回数字部分）"""
    try:
        track = audio.get('tracknumber', ['0/0'])[0]
        if isinstance(track, str) and '/' in track:
            return track.split('/')[0]
        return str(track) if track else '0'
    except (IndexError, TypeError, AttributeError):
        return '0'

def update_audio_tags(filepath, tags, cover_path=None):
    """更新音频文件的元数据标签"""
    try:
        # 确保文件存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
        # 验证必填字段
        if not tags.get('title') or not tags.get('artist'):
            logger.error("标题和艺术家为必填字段")
            return False
        
        # 备份原始文件
        backup_path = filepath + ".bak"
        shutil.copyfile(filepath, backup_path)
        
        try:
            # 使用EasyID3更新简单标签
            audio = MP3(filepath, ID3=EasyID3)
            
            # 初始化缺少的标签
            for tag in ['title', 'artist', 'album', 'albumartist', 'date', 'tracknumber', 'genre']:
                if tag not in audio:
                    audio[tag] = [DEFAULT_TAGS.get(tag, '')]
            
            # 设置标签（只设置非空值）
            for tag_name, tag_value in tags.items():
                if tag_value and tag_name in ['title', 'artist', 'album', 'albumartist', 'date', 'tracknumber', 'genre']:
                    audio[tag_name] = [tag_value]
            
            audio.save()
            
            # 处理封面（需要直接使用ID3接口）
            if cover_path and os.path.exists(cover_path):
                _update_cover_image(filepath, cover_path)
            
            # 删除备份
            os.remove(backup_path)
            return True
        except Exception as e:
            # 恢复备份
            shutil.move(backup_path, filepath)
            logger.error(f"更新标签失败: {str(e)}\n{traceback.format_exc()}")
            return False
    except Exception as e:
        logger.error(f"更新标签失败: {str(e)}\n{traceback.format_exc()}")
        return False

def _update_cover_image(filepath, cover_path):
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
        raise