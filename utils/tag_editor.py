import shutil
from venv import logger
from mutagen.easyid3 import EasyID3
from mutagen.id3 import ID3, APIC, TIT2, TPE1, TALB, TDRC, TRCK, TPE2, error
from mutagen.mp3 import MP3
import os
import logging
from config import DOWNLOAD_PATH, DEFAULT_TAGS
import traceback  # 添加导入

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
                'title': audio.get('title', [''])[0],
                'artist': audio.get('artist', [''])[0],
                'album': audio.get('album', [''])[0],
                'albumartist': audio.get('albumartist', [''])[0],
                'date': audio.get('date', [''])[0],
                'tracknumber': audio.get('tracknumber', ['0/0'])[0].split('/')[0],
                'genre': audio.get('genre', [''])[0]
            }
            return tags
        except error:
            # 如果ID3标签不存在，返回默认值
            return DEFAULT_TAGS
    except Exception as e:
        logger.error(f"读取标签失败: {str(e)}\n{traceback.format_exc()}")
        return DEFAULT_TAGS

def update_audio_tags(filepath, tags, cover_path=None):
    """更新音频文件的元数据标签"""
    try:
        # 确保文件存在
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"文件不存在: {filepath}")
        
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
            
            # 设置标签
            if tags.get('title'):
                audio['title'] = tags['title']
            if tags.get('artist'):
                audio['artist'] = tags['artist']
            if tags.get('album'):
                audio['album'] = tags['album']
            if tags.get('albumartist'):
                audio['albumartist'] = tags['albumartist']
            if tags.get('date'):
                audio['date'] = tags['date']
            if tags.get('tracknumber'):
                audio['tracknumber'] = tags['tracknumber']
            if tags.get('genre'):
                audio['genre'] = tags['genre']
            
            audio.save()
            
            # 处理封面（需要直接使用ID3接口）
            if cover_path and os.path.exists(cover_path):
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