"""
认证服务模块
"""
import logging
from functools import wraps
from flask import session, redirect, url_for, request, flash
from utils.exceptions import AuthenticationError
from config import LOGIN_REQUIRED, ADMIN_USERNAME, ADMIN_PASSWORD, SESSION_TIMEOUT

logger = logging.getLogger(__name__)


class AuthService:
    """认证服务类"""
    
    def __init__(self):
        self.login_required = LOGIN_REQUIRED
        self.admin_username = ADMIN_USERNAME
        self.admin_password = ADMIN_PASSWORD
        self.session_timeout = SESSION_TIMEOUT
    
    def login_required_decorator(self, f):
        """登录验证装饰器"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if self.login_required and not session.get('logged_in'):
                return redirect(url_for('login', next=request.url))
            return f(*args, **kwargs)
        return decorated_function
    
    def authenticate(self, username: str, password: str) -> bool:
        """验证用户凭据"""
        try:
            # 验证输入
            if not username or not password:
                return False
            
            # 限制用户名长度
            if len(username) > 50:
                return False
            
            # 验证凭据
            if username == self.admin_username and password == self.admin_password:
                # 记录登录成功
                logger.info(f"用户 {username} 登录成功")
                return True
            else:
                # 记录登录失败
                logger.warning(f"登录失败: 用户名={username}")
                return False
                
        except Exception as e:
            logger.error(f"认证过程出错: {str(e)}")
            return False
    
    def create_session(self, username: str):
        """创建用户会话"""
        try:
            session['logged_in'] = True
            session['username'] = username
            session.permanent = True
            return True
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            return False
    
    def destroy_session(self):
        """销毁用户会话"""
        try:
            session.clear()
            return True
        except Exception as e:
            logger.error(f"销毁会话失败: {str(e)}")
            return False
    
    def is_logged_in(self) -> bool:
        """检查用户是否已登录"""
        return session.get('logged_in', False)
    
    def get_current_user(self) -> str:
        """获取当前用户名"""
        return session.get('username', '')
    
    def validate_input(self, username: str, password: str) -> tuple[bool, str]:
        """验证输入数据"""
        if not username or not password:
            return False, "用户名和密码不能为空"
        
        if len(username) > 50:
            return False, "用户名过长"
        
        return True, ""
    
    def get_login_redirect_url(self) -> str:
        """获取登录后的重定向URL"""
        next_page = request.args.get('next')
        return next_page or url_for('index')
