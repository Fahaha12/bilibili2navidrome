"""
输入验证工具模块
"""
import re
import os
from pathlib import Path
from typing import List, Optional


class URLValidator:
    """URL验证器"""
    
    BILIBILI_PATTERNS = [
        r'^https?://(www\.)?bilibili\.com/video/((BV|bv)[a-zA-Z0-9]{10})',
        r'^https?://b23\.tv/[a-zA-Z0-9]+',
        r'^(BV|bv)[a-zA-Z0-9]{10}$',
        r'^(av|AV)\d+$'
    ]
    
    def __init__(self):
        self.compiled_patterns = [re.compile(pattern) for pattern in self.BILIBILI_PATTERNS]
    
    def is_valid_bilibili_url(self, url: str) -> bool:
        """验证是否为有效的Bilibili URL"""
        if not url or not isinstance(url, str):
            return False
        
        url = url.strip()
        
        # 检查是否匹配任何Bilibili模式
        for pattern in self.compiled_patterns:
            if pattern.match(url):
                return True
        
        return False
    
    def extract_bilibili_url(self, text: str) -> str:
        """从文本中提取Bilibili URL"""
        if not text:
            return ""
        
        # 分享文本模式
        share_patterns = [
            r'【.*?】\s*(https?://(www\.)?(bilibili\.com|b23\.tv)[^\s]+)',
            r'\[.*?\]\s*(https?://(www\.)?(bilibili\.com|b23\.tv)[^\s]+)'
        ]
        
        for pattern in share_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).split('?')[0].split('#')[0]
        
        # 直接检查是否为URL
        if self.is_valid_bilibili_url(text):
            return text
        
        return ""


class FileValidator:
    """文件验证器"""
    
    ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp'}
    ALLOWED_COOKIES_EXTENSIONS = {'.txt'}
    DANGEROUS_EXTENSIONS = {'.exe', '.bat', '.cmd', '.scr', '.pif', '.com', '.vbs', '.js'}
    
    def __init__(self):
        self.max_filename_length = 255
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def is_safe_filename(self, filename: str) -> bool:
        """检查文件名是否安全"""
        if not filename or not isinstance(filename, str):
            return False
        
        filename = filename.strip()
        
        # 检查长度
        if len(filename) > self.max_filename_length:
            return False
        
        # 检查危险字符
        dangerous_chars = r'[\\/*?:"<>|]'
        if re.search(dangerous_chars, filename):
            return False
        
        # 检查路径遍历
        if '..' in filename or filename.startswith('/') or filename.startswith('\\'):
            return False
        
        # 检查危险扩展名
        ext = Path(filename).suffix.lower()
        if ext in self.DANGEROUS_EXTENSIONS:
            return False
        
        return True
    
    def is_valid_image(self, filename: str) -> bool:
        """检查是否为有效的图片文件"""
        if not self.is_safe_filename(filename):
            return False
        
        ext = Path(filename).suffix.lower()
        return ext in self.ALLOWED_IMAGE_EXTENSIONS
    
    def is_valid_cookies_file(self, filename: str) -> bool:
        """检查是否为有效的cookies文件"""
        if not self.is_safe_filename(filename):
            return False
        
        ext = Path(filename).suffix.lower()
        return ext in self.ALLOWED_COOKIES_EXTENSIONS
    
    def validate_file_size(self, file_size: int) -> bool:
        """验证文件大小"""
        return 0 < file_size <= self.max_file_size


class InputSanitizer:
    """输入清理器"""
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """清理字符串输入"""
        if not value:
            return ""
        
        # 移除控制字符
        cleaned = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', str(value))
        
        # 限制长度
        if len(cleaned) > max_length:
            cleaned = cleaned[:max_length]
        
        return cleaned.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """清理文件名"""
        if not filename:
            return ""
        
        # 移除危险字符
        cleaned = re.sub(r'[\\/*?:"<>|]', '', filename)
        
        # 移除多余的空格和点
        cleaned = re.sub(r'\s+', ' ', cleaned).strip()
        cleaned = cleaned.strip('.')
        
        return cleaned
