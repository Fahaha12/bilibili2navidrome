"""
Navidrome服务模块
"""
import requests
import logging
from typing import Dict, Any, Optional
from utils.exceptions import NavidromeError
from config import NAVIDROME_URL, NAVIDROME_API_KEY

logger = logging.getLogger(__name__)


class NavidromeService:
    """Navidrome音乐库服务类"""
    
    def __init__(self):
        self.base_url = NAVIDROME_URL
        self.api_key = NAVIDROME_API_KEY
        self.timeout = 10
    
    def trigger_scan(self) -> bool:
        """触发Navidrome扫描"""
        try:
            if not self.base_url or not self.api_key:
                logger.info("Navidrome配置未设置，跳过扫描")
                return True
            
            # 构建API URL
            scan_url = f"{self.base_url.rstrip('/')}/api/scan"
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # 发送扫描请求
            response = requests.post(
                scan_url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                logger.info("Navidrome扫描触发成功")
                return True
            else:
                logger.warning(f"Navidrome扫描失败: {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Navidrome扫描请求失败: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Navidrome扫描出错: {str(e)}")
            return False
    
    def get_library_status(self) -> Dict[str, Any]:
        """获取音乐库状态"""
        try:
            if not self.base_url or not self.api_key:
                return {"status": "not_configured", "message": "Navidrome未配置"}
            
            # 构建API URL
            status_url = f"{self.base_url.rstrip('/')}/api/status"
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                status_url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"获取状态失败: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "message": f"请求失败: {str(e)}"
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取状态出错: {str(e)}"
            }
    
    def test_connection(self) -> bool:
        """测试Navidrome连接"""
        try:
            status = self.get_library_status()
            return status.get("status") != "error"
        except Exception:
            return False
    
    def get_scan_status(self) -> Dict[str, Any]:
        """获取扫描状态"""
        try:
            if not self.base_url or not self.api_key:
                return {"status": "not_configured"}
            
            # 构建API URL
            status_url = f"{self.base_url.rstrip('/')}/api/scan/status"
            
            headers = {
                'X-API-Key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            response = requests.get(
                status_url,
                headers=headers,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {
                    "status": "error",
                    "message": f"获取扫描状态失败: {response.status_code}"
                }
                
        except Exception as e:
            return {
                "status": "error",
                "message": f"获取扫描状态出错: {str(e)}"
            }
