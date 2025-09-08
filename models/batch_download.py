"""
批量下载数据模型
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import uuid


class BatchStatus(Enum):
    """批量下载状态枚举"""
    PENDING = "pending"      # 等待中
    DOWNLOADING = "downloading"  # 下载中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    CANCELLED = "cancelled"  # 已取消


class TaskStatus(Enum):
    """单个任务状态枚举"""
    PENDING = "pending"      # 等待中
    DOWNLOADING = "downloading"  # 下载中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 失败
    SKIPPED = "skipped"      # 跳过


@dataclass
class DownloadTask:
    """单个下载任务"""
    id: str
    url: str
    title: str = ""
    artist: str = ""
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    error_message: str = ""
    filename: str = ""
    filepath: str = ""
    duration: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(uuid.uuid4())
    
    @property
    def is_completed(self) -> bool:
        """检查是否已完成"""
        return self.status == TaskStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self.status == TaskStatus.FAILED
    
    @property
    def is_pending(self) -> bool:
        """检查是否等待中"""
        return self.status == TaskStatus.PENDING
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'artist': self.artist,
            'status': self.status.value,
            'progress': self.progress,
            'error_message': self.error_message,
            'filename': self.filename,
            'filepath': self.filepath,
            'duration': self.duration,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DownloadTask':
        """从字典创建实例"""
        task = cls(
            id=data['id'],
            url=data['url'],
            title=data.get('title', ''),
            artist=data.get('artist', ''),
            status=TaskStatus(data.get('status', 'pending')),
            progress=data.get('progress', 0.0),
            error_message=data.get('error_message', ''),
            filename=data.get('filename', ''),
            filepath=data.get('filepath', ''),
            duration=data.get('duration', 0)
        )
        
        if data.get('created_at'):
            task.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('completed_at'):
            task.completed_at = datetime.fromisoformat(data['completed_at'])
        
        return task


@dataclass
class BatchDownload:
    """批量下载任务"""
    id: str
    name: str
    urls: List[str]
    tasks: List[DownloadTask] = field(default_factory=list)
    status: BatchStatus = BatchStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.id:
            self.id = str(uuid.uuid4())
        
        # 初始化任务列表
        if not self.tasks and self.urls:
            self.tasks = [DownloadTask(id=str(uuid.uuid4()), url=url) for url in self.urls]
            self.total_tasks = len(self.tasks)
    
    @property
    def progress(self) -> float:
        """计算整体进度"""
        if self.total_tasks == 0:
            return 0.0
        return (self.completed_tasks + self.failed_tasks) / self.total_tasks * 100
    
    @property
    def is_completed(self) -> bool:
        """检查是否全部完成"""
        return self.status == BatchStatus.COMPLETED
    
    @property
    def is_failed(self) -> bool:
        """检查是否失败"""
        return self.status == BatchStatus.FAILED
    
    @property
    def is_running(self) -> bool:
        """检查是否正在运行"""
        return self.status == BatchStatus.DOWNLOADING
    
    def get_task_by_id(self, task_id: str) -> Optional[DownloadTask]:
        """根据ID获取任务"""
        for task in self.tasks:
            if task.id == task_id:
                return task
        return None
    
    def update_task_status(self, task_id: str, status: TaskStatus, **kwargs):
        """更新任务状态"""
        task = self.get_task_by_id(task_id)
        if task:
            task.status = status
            for key, value in kwargs.items():
                if hasattr(task, key):
                    setattr(task, key, value)
            
            if status == TaskStatus.COMPLETED:
                task.completed_at = datetime.now()
                self.completed_tasks += 1
            elif status == TaskStatus.FAILED:
                self.failed_tasks += 1
            
            # 更新批量任务状态
            self._update_batch_status()
    
    def _update_batch_status(self):
        """更新批量任务状态"""
        if self.completed_tasks + self.failed_tasks >= self.total_tasks:
            if self.failed_tasks == 0:
                self.status = BatchStatus.COMPLETED
            elif self.completed_tasks == 0:
                self.status = BatchStatus.FAILED
            else:
                self.status = BatchStatus.COMPLETED  # 部分成功也算完成
            self.completed_at = datetime.now()
        elif self.status == BatchStatus.PENDING and any(task.status == TaskStatus.DOWNLOADING for task in self.tasks):
            self.status = BatchStatus.DOWNLOADING
            if not self.started_at:
                self.started_at = datetime.now()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取任务摘要"""
        return {
            'total': self.total_tasks,
            'completed': self.completed_tasks,
            'failed': self.failed_tasks,
            'pending': self.total_tasks - self.completed_tasks - self.failed_tasks,
            'progress': self.progress
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'urls': self.urls,
            'tasks': [task.to_dict() for task in self.tasks],
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'total_tasks': self.total_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'progress': self.progress,
            'summary': self.get_summary()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BatchDownload':
        """从字典创建实例"""
        batch = cls(
            id=data['id'],
            name=data['name'],
            urls=data['urls'],
            status=BatchStatus(data.get('status', 'pending')),
            total_tasks=data.get('total_tasks', 0),
            completed_tasks=data.get('completed_tasks', 0),
            failed_tasks=data.get('failed_tasks', 0)
        )
        
        # 恢复任务列表
        if data.get('tasks'):
            batch.tasks = [DownloadTask.from_dict(task_data) for task_data in data['tasks']]
        
        # 恢复时间戳
        if data.get('created_at'):
            batch.created_at = datetime.fromisoformat(data['created_at'])
        if data.get('started_at'):
            batch.started_at = datetime.fromisoformat(data['started_at'])
        if data.get('completed_at'):
            batch.completed_at = datetime.fromisoformat(data['completed_at'])
        
        return batch


@dataclass
class BatchDownloadRequest:
    """批量下载请求"""
    name: str
    urls: List[str]
    auto_edit_tags: bool = True
    default_tags: Dict[str, str] = field(default_factory=dict)
    
    def validate(self) -> tuple[bool, str]:
        """验证请求数据"""
        if not self.name or not self.name.strip():
            return False, "批量下载名称不能为空"
        
        if not self.urls:
            return False, "至少需要提供一个URL"
        
        if len(self.urls) > 50:  # 限制批量下载数量
            return False, "批量下载数量不能超过50个"
        
        # 验证URL格式
        from utils.validators import URLValidator
        validator = URLValidator()
        
        valid_urls = []
        for url in self.urls:
            url = url.strip()
            if not url:
                continue
            
            # 尝试提取URL
            extracted_url = validator.extract_bilibili_url(url)
            if extracted_url:
                valid_urls.append(extracted_url)
            elif validator.is_valid_bilibili_url(url):
                valid_urls.append(url)
        
        if not valid_urls:
            return False, "没有找到有效的Bilibili URL"
        
        self.urls = valid_urls
        return True, ""
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'urls': self.urls,
            'auto_edit_tags': self.auto_edit_tags,
            'default_tags': self.default_tags
        }
