"""
音频文件数据模型
"""
from dataclasses import dataclass
from typing import Dict, Any, Optional
from pathlib import Path


@dataclass
class AudioFile:
    """音频文件数据模型"""
    filename: str
    filepath: str
    title: str
    artist: str
    album: str = ""
    albumartist: str = ""
    date: str = ""
    tracknumber: str = ""
    genre: str = ""
    duration: int = 0
    cover_filename: Optional[str] = None
    original_url: str = ""
    
    def __post_init__(self):
        """初始化后处理"""
        # 确保路径是绝对路径
        if not Path(self.filepath).is_absolute():
            self.filepath = str(Path(self.filepath).resolve())
    
    @property
    def file_exists(self) -> bool:
        """检查文件是否存在"""
        return Path(self.filepath).exists()
    
    @property
    def file_size(self) -> int:
        """获取文件大小（字节）"""
        if self.file_exists:
            return Path(self.filepath).stat().st_size
        return 0
    
    @property
    def has_cover(self) -> bool:
        """检查是否有封面"""
        if self.cover_filename:
            cover_path = Path(self.filepath).parent / self.cover_filename
            return cover_path.exists()
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'filename': self.filename,
            'filepath': self.filepath,
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'albumartist': self.albumartist,
            'date': self.date,
            'tracknumber': self.tracknumber,
            'genre': self.genre,
            'duration': self.duration,
            'cover_filename': self.cover_filename,
            'original_url': self.original_url
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'AudioFile':
        """从字典创建实例"""
        return cls(**data)
    
    def get_tags_dict(self) -> Dict[str, str]:
        """获取标签字典"""
        return {
            'title': self.title,
            'artist': self.artist,
            'album': self.album,
            'albumartist': self.albumartist,
            'date': self.date,
            'tracknumber': self.tracknumber,
            'genre': self.genre
        }
    
    def update_tags(self, tags: Dict[str, str]):
        """更新标签"""
        for key, value in tags.items():
            if hasattr(self, key):
                setattr(self, key, value)
    
    def validate(self) -> tuple[bool, str]:
        """验证数据"""
        if not self.filename:
            return False, "文件名不能为空"
        
        if not self.title:
            return False, "标题不能为空"
        
        if not self.artist:
            return False, "艺术家不能为空"
        
        if not self.file_exists:
            return False, "文件不存在"
        
        return True, ""


@dataclass
class DownloadResult:
    """下载结果数据模型"""
    status: str  # 'success' or 'error'
    message: str = ""
    audio_file: Optional[AudioFile] = None
    error_details: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        """检查是否成功"""
        return self.status == 'success'
    
    @property
    def is_error(self) -> bool:
        """检查是否失败"""
        return self.status == 'error'
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            'status': self.status,
            'message': self.message
        }
        
        if self.audio_file:
            result.update(self.audio_file.to_dict())
        
        if self.error_details:
            result['error_details'] = self.error_details
        
        return result
    
    @classmethod
    def success(cls, audio_file: AudioFile, message: str = "下载成功") -> 'DownloadResult':
        """创建成功结果"""
        return cls(status='success', message=message, audio_file=audio_file)
    
    @classmethod
    def error(cls, message: str, error_details: str = None) -> 'DownloadResult':
        """创建错误结果"""
        return cls(status='error', message=message, error_details=error_details)
