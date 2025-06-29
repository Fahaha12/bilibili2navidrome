import requests
import logging
import traceback

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def trigger_navidrome_scan():
    """空函数，不再触发扫描"""
    logger.info("跳过 Navidrome 扫描（未启用）")
    return True  # 始终返回成功