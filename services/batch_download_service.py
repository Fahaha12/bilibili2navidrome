"""
批量下载服务模块
"""
import os
import json
import logging
import threading
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from models.batch_download import BatchDownload, DownloadTask, BatchStatus, TaskStatus, BatchDownloadRequest
from services.download_service import DownloadService
from services.tag_service import TagService
from services.navidrome_service import NavidromeService
from utils.exceptions import ValidationError, DownloadError
from utils.validators import URLValidator
from config import DOWNLOAD_PATH, TEMP_PATH

logger = logging.getLogger(__name__)


class BatchDownloadService:
    """批量下载服务类"""
    
    def __init__(self):
        self.download_service = DownloadService()
        self.tag_service = TagService()
        self.navidrome_service = NavidromeService()
        self.url_validator = URLValidator()
        
        # 存储活跃的批量下载任务
        self.active_batches: Dict[str, BatchDownload] = {}
        self.batch_storage_path = Path("batch_storage")
        self.batch_storage_path.mkdir(exist_ok=True)
        
        # 线程锁
        self.lock = threading.Lock()
    
    def create_batch_download(self, request: BatchDownloadRequest) -> BatchDownload:
        """创建批量下载任务"""
        try:
            # 验证请求
            is_valid, error_message = request.validate()
            if not is_valid:
                raise ValidationError(error_message)
            
            # 创建批量下载任务
            batch = BatchDownload(
                id="",  # 会自动生成
                name=request.name,
                urls=request.urls
            )
            
            # 保存到存储
            self._save_batch(batch)
            
            # 添加到活跃任务
            with self.lock:
                self.active_batches[batch.id] = batch
            
            logger.info(f"创建批量下载任务: {batch.id}, 包含 {len(batch.urls)} 个URL")
            
            return batch
            
        except Exception as e:
            logger.error(f"创建批量下载任务失败: {str(e)}")
            raise
    
    def start_batch_download(self, batch_id: str) -> bool:
        """启动批量下载任务"""
        try:
            batch = self.get_batch_download(batch_id)
            if not batch:
                raise ValidationError("批量下载任务不存在")
            
            if batch.status != BatchStatus.PENDING:
                raise ValidationError("批量下载任务状态不正确")
            
            # 更新状态
            batch.status = BatchStatus.DOWNLOADING
            batch.started_at = datetime.now()
            self._save_batch(batch)
            
            # 启动下载线程
            download_thread = threading.Thread(
                target=self._download_batch_worker,
                args=(batch_id,),
                daemon=True
            )
            download_thread.start()
            
            logger.info(f"启动批量下载任务: {batch_id}")
            return True
            
        except Exception as e:
            logger.error(f"启动批量下载任务失败: {str(e)}")
            return False
    
    def _download_batch_worker(self, batch_id: str):
        """批量下载工作线程"""
        try:
            batch = self.get_batch_download(batch_id)
            if not batch:
                return
            
            logger.info(f"开始执行批量下载任务: {batch_id}")
            
            for task in batch.tasks:
                if batch.status == BatchStatus.CANCELLED:
                    break
                
                try:
                    # 更新任务状态为下载中
                    batch.update_task_status(task.id, TaskStatus.DOWNLOADING)
                    self._save_batch(batch)
                    
                    # 执行下载
                    result = self.download_service.download_audio(task.url)
                    
                    if result['status'] == 'success':
                        # 下载成功
                        task.title = result.get('title', '')
                        task.artist = result.get('artist', '')
                        task.filename = result['filename']
                        task.filepath = result['filepath']
                        task.duration = result.get('duration', 0)
                        
                        batch.update_task_status(task.id, TaskStatus.COMPLETED)
                        logger.info(f"任务下载成功: {task.id} - {task.title}")
                    else:
                        # 下载失败
                        task.error_message = result.get('message', '下载失败')
                        batch.update_task_status(task.id, TaskStatus.FAILED)
                        logger.error(f"任务下载失败: {task.id} - {task.error_message}")
                    
                except Exception as e:
                    # 任务执行异常
                    task.error_message = str(e)
                    batch.update_task_status(task.id, TaskStatus.FAILED)
                    logger.error(f"任务执行异常: {task.id} - {str(e)}")
                
                # 保存进度
                self._save_batch(batch)
            
            # 批量下载完成
            if batch.status == BatchStatus.DOWNLOADING:
                if batch.completed_tasks > 0:
                    batch.status = BatchStatus.COMPLETED
                else:
                    batch.status = BatchStatus.FAILED
                batch.completed_at = datetime.now()
                self._save_batch(batch)
                
                # 触发Navidrome扫描
                if batch.completed_tasks > 0:
                    self.navidrome_service.trigger_scan()
                
                logger.info(f"批量下载任务完成: {batch_id}, 成功: {batch.completed_tasks}, 失败: {batch.failed_tasks}")
            
        except Exception as e:
            logger.error(f"批量下载工作线程异常: {str(e)}")
            # 更新批量任务状态为失败
            batch = self.get_batch_download(batch_id)
            if batch:
                batch.status = BatchStatus.FAILED
                batch.completed_at = datetime.now()
                self._save_batch(batch)
    
    def cancel_batch_download(self, batch_id: str) -> bool:
        """取消批量下载任务"""
        try:
            batch = self.get_batch_download(batch_id)
            if not batch:
                return False
            
            if batch.status not in [BatchStatus.PENDING, BatchStatus.DOWNLOADING]:
                return False
            
            batch.status = BatchStatus.CANCELLED
            batch.completed_at = datetime.now()
            self._save_batch(batch)
            
            logger.info(f"取消批量下载任务: {batch_id}")
            return True
            
        except Exception as e:
            logger.error(f"取消批量下载任务失败: {str(e)}")
            return False
    
    def get_batch_download(self, batch_id: str) -> Optional[BatchDownload]:
        """获取批量下载任务"""
        try:
            # 先从内存中查找
            with self.lock:
                if batch_id in self.active_batches:
                    return self.active_batches[batch_id]
            
            # 从存储中加载
            batch_file = self.batch_storage_path / f"{batch_id}.json"
            if batch_file.exists():
                with open(batch_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    batch = BatchDownload.from_dict(data)
                    
                    # 如果任务还在进行中，添加到活跃任务
                    if batch.status in [BatchStatus.PENDING, BatchStatus.DOWNLOADING]:
                        with self.lock:
                            self.active_batches[batch_id] = batch
                    
                    return batch
            
            return None
            
        except Exception as e:
            logger.error(f"获取批量下载任务失败: {str(e)}")
            return None
    
    def get_all_batches(self) -> List[BatchDownload]:
        """获取所有批量下载任务"""
        try:
            batches = []
            
            # 从存储中加载所有任务
            for batch_file in self.batch_storage_path.glob("*.json"):
                try:
                    with open(batch_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        batch = BatchDownload.from_dict(data)
                        batches.append(batch)
                except Exception as e:
                    logger.warning(f"加载批量任务文件失败: {batch_file} - {str(e)}")
            
            # 按创建时间倒序排列
            batches.sort(key=lambda x: x.created_at, reverse=True)
            
            return batches
            
        except Exception as e:
            logger.error(f"获取所有批量下载任务失败: {str(e)}")
            return []
    
    def delete_batch_download(self, batch_id: str) -> bool:
        """删除批量下载任务"""
        try:
            # 从内存中移除
            with self.lock:
                if batch_id in self.active_batches:
                    del self.active_batches[batch_id]
            
            # 删除存储文件
            batch_file = self.batch_storage_path / f"{batch_id}.json"
            if batch_file.exists():
                batch_file.unlink()
            
            logger.info(f"删除批量下载任务: {batch_id}")
            return True
            
        except Exception as e:
            logger.error(f"删除批量下载任务失败: {str(e)}")
            return False
    
    def get_batch_progress(self, batch_id: str) -> Dict[str, Any]:
        """获取批量下载进度"""
        try:
            batch = self.get_batch_download(batch_id)
            if not batch:
                return {
                    'success': False,
                    'message': '批量下载任务不存在'
                }
            
            return {
                'success': True,
                'data': {
                    'id': batch.id,
                    'name': batch.name,
                    'status': batch.status.value,
                    'progress': batch.progress,
                    'summary': batch.get_summary(),
                    'tasks': [task.to_dict() for task in batch.tasks]
                }
            }
            
        except Exception as e:
            logger.error(f"获取批量下载进度失败: {str(e)}")
            return {
                'success': False,
                'message': str(e)
            }
    
    def _save_batch(self, batch: BatchDownload):
        """保存批量下载任务到存储"""
        try:
            batch_file = self.batch_storage_path / f"{batch.id}.json"
            with open(batch_file, 'w', encoding='utf-8') as f:
                json.dump(batch.to_dict(), f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存批量下载任务失败: {str(e)}")
    
    def cleanup_old_batches(self, days: int = 7):
        """清理旧的批量下载任务"""
        try:
            cutoff_time = datetime.now().timestamp() - (days * 24 * 3600)
            deleted_count = 0
            
            for batch_file in self.batch_storage_path.glob("*.json"):
                try:
                    # 检查文件修改时间
                    if batch_file.stat().st_mtime < cutoff_time:
                        batch_file.unlink()
                        deleted_count += 1
                except Exception as e:
                    logger.warning(f"清理批量任务文件失败: {batch_file} - {str(e)}")
            
            logger.info(f"清理了 {deleted_count} 个旧的批量下载任务")
            
        except Exception as e:
            logger.error(f"清理旧批量下载任务失败: {str(e)}")
    
    def get_batch_statistics(self) -> Dict[str, Any]:
        """获取批量下载统计信息"""
        try:
            batches = self.get_all_batches()
            
            total_batches = len(batches)
            completed_batches = len([b for b in batches if b.status == BatchStatus.COMPLETED])
            failed_batches = len([b for b in batches if b.status == BatchStatus.FAILED])
            running_batches = len([b for b in batches if b.status == BatchStatus.DOWNLOADING])
            
            total_tasks = sum(b.total_tasks for b in batches)
            completed_tasks = sum(b.completed_tasks for b in batches)
            failed_tasks = sum(b.failed_tasks for b in batches)
            
            return {
                'total_batches': total_batches,
                'completed_batches': completed_batches,
                'failed_batches': failed_batches,
                'running_batches': running_batches,
                'total_tasks': total_tasks,
                'completed_tasks': completed_tasks,
                'failed_tasks': failed_tasks,
                'success_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"获取批量下载统计信息失败: {str(e)}")
            return {}
