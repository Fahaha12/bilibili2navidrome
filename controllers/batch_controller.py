"""
批量下载控制器模块
"""
import logging
from flask import request, jsonify, render_template
from typing import Dict, Any

from services.batch_download_service import BatchDownloadService
from models.batch_download import BatchDownloadRequest, BatchStatus
from utils.exceptions import ValidationError, DownloadError
from utils.validators import URLValidator

logger = logging.getLogger(__name__)


class BatchController:
    """批量下载控制器类"""
    
    def __init__(self):
        self.batch_service = BatchDownloadService()
        self.url_validator = URLValidator()
    
    def get_batch_page(self) -> Dict[str, Any]:
        """获取批量下载页面数据"""
        try:
            # 获取所有批量下载任务
            batches = self.batch_service.get_all_batches()
            
            # 获取统计信息
            statistics = self.batch_service.get_batch_statistics()
            
            return {
                'success': True,
                'data': {
                    'batches': [batch.to_dict() for batch in batches],
                    'statistics': statistics
                }
            }
            
        except Exception as e:
            logger.error(f"获取批量下载页面数据失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '获取页面数据失败'
            }
    
    def create_batch_download(self) -> Dict[str, Any]:
        """创建批量下载任务"""
        try:
            # 获取请求数据
            data = request.get_json() or {}
            
            name = data.get('name', '').strip()
            urls_text = data.get('urls', '')
            auto_edit_tags = data.get('auto_edit_tags', True)
            default_tags = data.get('default_tags', {})
            
            # 验证输入
            if not name:
                return {
                    'success': False,
                    'error': 'validation',
                    'message': '批量下载名称不能为空'
                }
            
            if not urls_text:
                return {
                    'success': False,
                    'error': 'validation',
                    'message': '请输入要下载的URL列表'
                }
            
            # 解析URL列表
            urls = self._parse_urls(urls_text)
            if not urls:
                return {
                    'success': False,
                    'error': 'validation',
                    'message': '没有找到有效的Bilibili URL'
                }
            
            # 创建批量下载请求
            batch_request = BatchDownloadRequest(
                name=name,
                urls=urls,
                auto_edit_tags=auto_edit_tags,
                default_tags=default_tags
            )
            
            # 创建批量下载任务
            batch = self.batch_service.create_batch_download(batch_request)
            
            return {
                'success': True,
                'data': batch.to_dict(),
                'message': f'批量下载任务创建成功，包含 {len(urls)} 个URL'
            }
            
        except ValidationError as e:
            logger.warning(f"批量下载验证错误: {str(e)}")
            return {
                'success': False,
                'error': 'validation',
                'message': str(e)
            }
        except Exception as e:
            logger.error(f"创建批量下载任务失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '创建批量下载任务失败'
            }
    
    def start_batch_download(self, batch_id: str) -> Dict[str, Any]:
        """启动批量下载任务"""
        try:
            success = self.batch_service.start_batch_download(batch_id)
            
            if success:
                return {
                    'success': True,
                    'message': '批量下载任务已启动'
                }
            else:
                return {
                    'success': False,
                    'error': 'start_failed',
                    'message': '启动批量下载任务失败'
                }
                
        except Exception as e:
            logger.error(f"启动批量下载任务失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '启动批量下载任务失败'
            }
    
    def cancel_batch_download(self, batch_id: str) -> Dict[str, Any]:
        """取消批量下载任务"""
        try:
            success = self.batch_service.cancel_batch_download(batch_id)
            
            if success:
                return {
                    'success': True,
                    'message': '批量下载任务已取消'
                }
            else:
                return {
                    'success': False,
                    'error': 'cancel_failed',
                    'message': '取消批量下载任务失败'
                }
                
        except Exception as e:
            logger.error(f"取消批量下载任务失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '取消批量下载任务失败'
            }
    
    def get_batch_progress(self, batch_id: str) -> Dict[str, Any]:
        """获取批量下载进度"""
        try:
            result = self.batch_service.get_batch_progress(batch_id)
            return result
            
        except Exception as e:
            logger.error(f"获取批量下载进度失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '获取批量下载进度失败'
            }
    
    def get_batch_detail(self, batch_id: str) -> Dict[str, Any]:
        """获取批量下载详情"""
        try:
            batch = self.batch_service.get_batch_download(batch_id)
            
            if not batch:
                return {
                    'success': False,
                    'error': 'not_found',
                    'message': '批量下载任务不存在'
                }
            
            return {
                'success': True,
                'data': batch.to_dict()
            }
            
        except Exception as e:
            logger.error(f"获取批量下载详情失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '获取批量下载详情失败'
            }
    
    def delete_batch_download(self, batch_id: str) -> Dict[str, Any]:
        """删除批量下载任务"""
        try:
            success = self.batch_service.delete_batch_download(batch_id)
            
            if success:
                return {
                    'success': True,
                    'message': '批量下载任务已删除'
                }
            else:
                return {
                    'success': False,
                    'error': 'delete_failed',
                    'message': '删除批量下载任务失败'
                }
                
        except Exception as e:
            logger.error(f"删除批量下载任务失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '删除批量下载任务失败'
            }
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """获取批量下载统计信息"""
        try:
            statistics = self.batch_service.get_batch_statistics()
            
            return {
                'success': True,
                'data': statistics
            }
            
        except Exception as e:
            logger.error(f"获取批量下载统计信息失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '获取统计信息失败'
            }
    
    def _parse_urls(self, urls_text: str) -> list:
        """解析URL文本"""
        try:
            urls = []
            
            # 按行分割
            lines = urls_text.strip().split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # 尝试提取URL
                extracted_url = self.url_validator.extract_bilibili_url(line)
                if extracted_url:
                    urls.append(extracted_url)
                elif self.url_validator.is_valid_bilibili_url(line):
                    urls.append(line)
            
            # 去重
            return list(set(urls))
            
        except Exception as e:
            logger.error(f"解析URL失败: {str(e)}")
            return []
    
    def validate_urls(self, urls_text: str) -> Dict[str, Any]:
        """验证URL列表"""
        try:
            urls = self._parse_urls(urls_text)
            
            valid_urls = []
            invalid_lines = []
            
            lines = urls_text.strip().split('\n')
            for i, line in enumerate(lines, 1):
                line = line.strip()
                if not line:
                    continue
                
                extracted_url = self.url_validator.extract_bilibili_url(line)
                if extracted_url:
                    valid_urls.append(extracted_url)
                elif self.url_validator.is_valid_bilibili_url(line):
                    valid_urls.append(line)
                else:
                    invalid_lines.append({
                        'line_number': i,
                        'content': line,
                        'reason': '不是有效的Bilibili URL'
                    })
            
            return {
                'success': True,
                'data': {
                    'valid_urls': valid_urls,
                    'invalid_lines': invalid_lines,
                    'total_valid': len(valid_urls),
                    'total_invalid': len(invalid_lines)
                }
            }
            
        except Exception as e:
            logger.error(f"验证URL列表失败: {str(e)}")
            return {
                'success': False,
                'error': 'internal',
                'message': '验证URL列表失败'
            }
