"""
Server酱微信推送通知
"""

import os
import json
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def send_wechat_notification():
    """发送微信推送"""
    sendkey = os.getenv('SERVERCHAN_KEY')
    
    if not sendkey:
        logger.warning("⚠️  未配置Server酱Key，跳过推送")
        return
    
    try:
        # 读取最新分析结果
        result_file = Path('docs/latest.json')
        if not result_file.exists():
            logger.error("❌ 分析结果不存在")
            return
        
        with open(result_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        metrics = data['portfolio_metrics']
        recs = data['recommendations']
        
        # 构建推送内容
        title = f"📊 每日投资分析报告"
        
        content = f"""
## 💼 组合概览

- **持仓总值**: ¥{metrics['total_value']:,.2f}
- **持有收益**: {'+'if metrics['total_profit'] >= 0 else ''}¥{metrics['total_profit']:,.2f}
- **总收益率**: {'+'if metrics['total_return'] >= 0 else ''}{metrics['total_return']:.2f}%

## 💡 今日建议（共{len(recs)}条）

"""
        
        for i, rec in enumerate(recs[:5], 1):  # 只推送前5条
            content += f"""
### {i}. [{rec['type']}] {rec['fund_name']}

- **紧急度**: {rec['urgency']}
- **原因**: {rec['reason'][:100]}...
- **建议**: {rec['action'][:100]}...

"""
        
        content += f"\n📈 [查看完整报告](https://litianyu03.github.io/investment-advisor/)"
        
        # 调用Server酱API
        url = f"https://sctapi.ftqq.com/{sendkey}.send"
        
        response = requests.post(url, data={
            'title': title,
            'desp': content
        }, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('code') == 0:
                logger.info("✅ 微信推送成功")
            else:
                logger.error(f"❌ 推送失败: {result.get('message')}")
        else:
            logger.error(f"❌ 推送失败: HTTP {response.status_code}")
            
    except Exception as e:
        logger.error(f"❌ 推送异常: {e}", exc_info=True)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    send_wechat_notification()
