"""
生成收益趋势图表（可选功能）
"""

import json
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def generate_charts():
    """生成历史趋势图表"""
    try:
        history_dir = Path('docs/history')
        
        if not history_dir.exists():
            logger.warning("⚠️  历史数据不存在，跳过图表生成")
            return
        
        # 读取所有历史数据
        history_files = sorted(history_dir.glob('*.json'))
        
        if len(history_files) < 2:
            logger.warning("⚠️  历史数据不足，跳过图表生成")
            return
        
        # 提取时间序列数据
        dates = []
        values = []
        returns = []
        
        for file in history_files:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            date = file.stem  # 文件名就是日期
            total_value = data['portfolio_metrics']['total_value']
            total_return = data['portfolio_metrics']['total_return']
            
            dates.append(date)
            values.append(total_value)
            returns.append(total_return)
        
        # 生成ECharts数据
        chart_data = {
            'dates': dates,
            'values': values,
            'returns': returns
        }
        
        # 保存图表数据
        with open('docs/chart_data.json', 'w', encoding='utf-8') as f:
            json.dump(chart_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"✅ 图表数据已生成，共{len(dates)}个数据点")
        
    except Exception as e:
        logger.error(f"❌ 图表生成失败: {e}")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    generate_charts()
