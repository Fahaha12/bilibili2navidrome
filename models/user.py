"""
用户数据模型
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class User:
    """用户数据模型"""
    username: str
    is_admin: bool = True
    last_login: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.last_login:
            self.last_login = datetime.now()
    
    @property
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return bool(self.username and self.session_id)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login = datetime.now()
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'username': self.username,
            'is_admin': self.is_admin,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'session_id': self.session_id
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'User':
        """从字典创建实例"""
        last_login = None
        if data.get('last_login'):
            last_login = datetime.fromisoformat(data['last_login'])
        
        return cls(
            username=data['username'],
            is_admin=data.get('is_admin', True),
            last_login=last_login,
            session_id=data.get('session_id')
        )


@dataclass
class LoginRequest:
    """登录请求数据模型"""
    username: str
    password: str
    
    def validate(self) -> tuple[bool, str]:
        """验证登录请求"""
        if not self.username or not self.password:
            return False, "用户名和密码不能为空"
        
        if len(self.username) > 50:
            return False, "用户名过长"
        
        if len(self.password) > 100:
            return False, "密码过长"
        
        return True, ""
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'username': self.username,
            'password': '***'  # 不返回真实密码
        }


@dataclass
class SessionInfo:
    """会话信息数据模型"""
    user_id: str
    username: str
    is_logged_in: bool
    session_timeout: int
    created_at: datetime
    
    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now()
    
    @property
    def is_expired(self) -> bool:
        """检查会话是否过期"""
        from datetime import timedelta
        expiry_time = self.created_at + timedelta(seconds=self.session_timeout)
        return datetime.now() > expiry_time
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            'user_id': self.user_id,
            'username': self.username,
            'is_logged_in': self.is_logged_in,
            'session_timeout': self.session_timeout,
            'created_at': self.created_at.isoformat()
        }
