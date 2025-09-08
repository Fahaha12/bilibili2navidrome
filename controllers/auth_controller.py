"""
认证控制器模块
"""
import logging
from flask import request, redirect, url_for, flash, session
from typing import Dict, Any

from services.auth_service import AuthService
from utils.exceptions import AuthenticationError
from models.user import LoginRequest

logger = logging.getLogger(__name__)


class AuthController:
    """认证控制器类"""
    
    def __init__(self):
        self.auth_service = AuthService()
    
    def handle_login_request(self) -> Dict[str, Any]:
        """处理登录请求"""
        try:
            # 获取表单数据
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '')
            
            # 创建登录请求对象
            login_request = LoginRequest(username=username, password=password)
            
            # 验证输入
            is_valid, error_message = login_request.validate()
            if not is_valid:
                return {
                    'success': False,
                    'error': 'validation',
                    'message': error_message,
                    'redirect_url': url_for('login')
                }
            
            # 验证凭据
            if not self.auth_service.authenticate(username, password):
                return {
                    'success': False,
                    'error': 'authentication',
                    'message': '用户名或密码错误',
                    'redirect_url': url_for('login')
                }
            
            # 创建会话
            if not self.auth_service.create_session(username):
                return {
                    'success': False,
                    'error': 'session',
                    'message': '创建会话失败',
                    'redirect_url': url_for('login')
                }
            
            # 获取重定向URL
            redirect_url = self.auth_service.get_login_redirect_url()
            
            return {
                'success': True,
                'message': '登录成功',
                'redirect_url': redirect_url
            }
            
        except Exception as e:
            logger.error(f"登录处理失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '登录过程中发生错误',
                'redirect_url': url_for('login')
            }
    
    def handle_logout_request(self) -> Dict[str, Any]:
        """处理登出请求"""
        try:
            # 销毁会话
            if not self.auth_service.destroy_session():
                return {
                    'success': False,
                    'error': 'session',
                    'message': '销毁会话失败'
                }
            
            return {
                'success': True,
                'message': '登出成功',
                'redirect_url': url_for('index')
            }
            
        except Exception as e:
            logger.error(f"登出处理失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '登出过程中发生错误'
            }
    
    def check_auth_status(self) -> Dict[str, Any]:
        """检查认证状态"""
        try:
            is_logged_in = self.auth_service.is_logged_in()
            current_user = self.auth_service.get_current_user()
            
            return {
                'success': True,
                'is_logged_in': is_logged_in,
                'current_user': current_user,
                'login_required': self.auth_service.login_required
            }
            
        except Exception as e:
            logger.error(f"检查认证状态失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '检查认证状态失败'
            }
    
    def get_login_page_data(self) -> Dict[str, Any]:
        """获取登录页面数据"""
        try:
            # 如果不需要登录，重定向到首页
            if not self.auth_service.login_required:
                return {
                    'success': True,
                    'redirect_url': url_for('index')
                }
            
            # 如果已经登录，重定向到首页
            if self.auth_service.is_logged_in():
                redirect_url = self.auth_service.get_login_redirect_url()
                return {
                    'success': True,
                    'redirect_url': redirect_url
                }
            
            return {
                'success': True,
                'data': {
                    'login_required': self.auth_service.login_required
                }
            }
            
        except Exception as e:
            logger.error(f"获取登录页面数据失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '获取登录页面数据失败'
            }
