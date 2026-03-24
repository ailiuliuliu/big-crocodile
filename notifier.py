"""
投资顾问系统 - 推送模块
负责将分析报告推送到微信
"""

import requests
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class Notifier:
    """消息推送器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.serverchan_config = config.get('serverchan', {})
        self.wechat_work_config = config.get('wechat_work', {})
    
    def send_report(self, title: str, content: str) -> bool:
        """
        发送报告
        
        Args:
            title: 标题
            content: 内容
            
        Returns:
            是否成功
        """
        success = False
        
        # 尝试Server酱
        if self.serverchan_config.get('enabled', False):
            success = self._send_via_serverchan(title, content)
            if success:
                return True
        
        # 尝试企业微信
        if self.wechat_work_config.get('enabled', False):
            success = self._send_via_wechat_work(title, content)
            if success:
                return True
        
        if not success:
            logger.error("所有推送渠道均失败")
        
        return success
    
    def _send_via_serverchan(self, title: str, content: str) -> bool:
        """
        通过Server酱推送
        
        文档：https://sct.ftqq.com/
        """
        try:
            sendkey = self.serverchan_config.get('sendkey', '')
            
            if not sendkey or sendkey == 'YOUR_SENDKEY_HERE':
                logger.warning("Server酱SendKey未配置")
                return False
            
            url = f"https://sctapi.ftqq.com/{sendkey}.send"
            
            data = {
                'title': title,
                'desp': content
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    logger.info("Server酱推送成功")
                    return True
                else:
                    logger.error(f"Server酱推送失败: {result.get('message')}")
            else:
                logger.error(f"Server酱推送失败: HTTP {response.status_code}")
        
        except Exception as e:
            logger.error(f"Server酱推送异常: {e}")
        
        return False
    
    def _send_via_wechat_work(self, title: str, content: str) -> bool:
        """
        通过企业微信Webhook推送
        
        文档：https://work.weixin.qq.com/api/doc/90000/90136/91770
        """
        try:
            webhook_url = self.wechat_work_config.get('webhook_url', '')
            
            if not webhook_url or webhook_url == 'YOUR_WEBHOOK_URL_HERE':
                logger.warning("企业微信Webhook URL未配置")
                return False
            
            # 格式化为markdown
            markdown_content = f"### {title}\n\n{content}"
            
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "content": markdown_content
                }
            }
            
            response = requests.post(webhook_url, json=data, timeout=10)
            
            if response.status_code == 200:
                result = response.json()
                if result.get('errcode') == 0:
                    logger.info("企业微信推送成功")
                    return True
                else:
                    logger.error(f"企业微信推送失败: {result.get('errmsg')}")
            else:
                logger.error(f"企业微信推送失败: HTTP {response.status_code}")
        
        except Exception as e:
            logger.error(f"企业微信推送异常: {e}")
        
        return False
    
    def send_alert(self, message: str) -> bool:
        """
        发送紧急提醒
        
        Args:
            message: 提醒内容
            
        Returns:
            是否成功
        """
        title = "🚨 投资组合紧急提醒"
        return self.send_report(title, message)
    
    def test_connection(self) -> Dict[str, bool]:
        """
        测试推送连接
        
        Returns:
            各渠道测试结果
        """
        results = {}
        
        test_title = "投资顾问系统测试"
        test_content = "这是一条测试消息，如果你收到了，说明推送配置成功！"
        
        if self.serverchan_config.get('enabled', False):
            results['serverchan'] = self._send_via_serverchan(test_title, test_content)
        
        if self.wechat_work_config.get('enabled', False):
            results['wechat_work'] = self._send_via_wechat_work(test_title, test_content)
        
        return results
