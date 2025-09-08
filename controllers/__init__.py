"""
控制器模块初始化
"""
from .download_controller import DownloadController
from .tag_controller import TagController
from .auth_controller import AuthController
from .batch_controller import BatchController

__all__ = [
    'DownloadController',
    'TagController',
    'AuthController',
    'BatchController'
]
