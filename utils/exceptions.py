"""
自定义异常类
"""


class BaseAppException(Exception):
    """应用基础异常类"""
    pass


class BilibiliDownloaderError(BaseAppException):
    """Bilibili下载器基础异常"""
    pass


class DownloadError(BilibiliDownloaderError):
    """下载相关错误"""
    pass


class ValidationError(BilibiliDownloaderError):
    """输入验证错误"""
    pass


class TagEditError(BilibiliDownloaderError):
    """标签编辑错误"""
    pass


class NavidromeError(BilibiliDownloaderError):
    """Navidrome相关错误"""
    pass


class FFmpegError(BilibiliDownloaderError):
    """FFmpeg相关错误"""
    pass


class AuthenticationError(BilibiliDownloaderError):
    """认证相关错误"""
    pass


class FileError(BilibiliDownloaderError):
    """文件操作错误"""
    pass


class FileOperationError(BaseAppException):
    """文件操作错误"""
    pass
