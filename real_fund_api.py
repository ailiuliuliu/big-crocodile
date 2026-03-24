"""
真实基金数据获取模块
从东方财富、天天基金等渠道获取实时基金数据
"""

import requests
import json
import re
from typing import Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class RealFundDataAPI:
    """真实基金数据API"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_fund_info(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金实时信息
        
        Args:
            fund_code: 基金代码（6位数字）
        
        Returns:
            基金信息字典
        """
        try:
            # 使用天天基金API
            url = f"http://fundgz.1234567.com.cn/js/{fund_code}.js"
            response = self.session.get(url, timeout=5)
            
            if response.status_code != 200:
                logger.warning(f"获取基金{fund_code}数据失败: {response.status_code}")
                return None
            
            # 解析jsonp返回
            content = response.text
            json_str = re.search(r'jsonpgz\((.*?)\);?$', content)
            if not json_str:
                logger.warning(f"解析基金{fund_code}数据失败")
                return None
            
            data = json.loads(json_str.group(1))
            
            return {
                'fund_code': data.get('fundcode'),
                'fund_name': data.get('name'),
                'confirmed_nav': float(data.get('dwjz', 0)),  # 昨日净值
                'confirmed_date': data.get('jzrq'),  # 净值日期
                'estimated_nav': float(data.get('gsz', 0)),  # 今日估算净值
                'estimated_change': float(data.get('gszzl', 0)),  # 今日估算涨跌幅
                'estimated_time': data.get('gztime'),  # 估值时间
            }
            
        except Exception as e:
            logger.error(f"获取基金{fund_code}数据异常: {e}")
            return None
    
    def get_fund_history(self, fund_code: str, days: int = 30) -> Optional[Dict]:
        """
        获取基金历史净值数据
        
        Args:
            fund_code: 基金代码
            days: 查询天数
        
        Returns:
            历史数据
        """
        try:
            # 东方财富历史净值接口
            url = f"http://api.fund.eastmoney.com/f10/lsjz"
            params = {
                'fundCode': fund_code,
                'pageIndex': 1,
                'pageSize': days,
                'startDate': '',
                'endDate': ''
            }
            
            response = self.session.get(url, params=params, timeout=5)
            
            if response.status_code != 200:
                return None
            
            data = response.json()
            
            if data.get('ErrCode') != 0:
                return None
            
            ls_data = data.get('Data', {}).get('LSJZList', [])
            
            if not ls_data:
                return None
            
            # 计算统计指标
            nav_list = [float(item['DWJZ']) for item in ls_data if item.get('DWJZ')]
            
            if len(nav_list) < 2:
                return None
            
            # 计算涨跌幅
            latest_nav = nav_list[0]
            oldest_nav = nav_list[-1]
            period_return = ((latest_nav - oldest_nav) / oldest_nav * 100)
            
            # 计算波动率（简化版）
            returns = []
            for i in range(len(nav_list) - 1):
                daily_return = (nav_list[i] - nav_list[i+1]) / nav_list[i+1]
                returns.append(daily_return)
            
            import statistics
            volatility = statistics.stdev(returns) * 100 if len(returns) > 1 else 0
            
            return {
                'fund_code': fund_code,
                'period_days': len(nav_list),
                'latest_nav': latest_nav,
                'oldest_nav': oldest_nav,
                'period_return': round(period_return, 2),
                'volatility': round(volatility, 2),
                'max_nav': max(nav_list),
                'min_nav': min(nav_list),
                'history_data': ls_data[:10]  # 只返回最近10条
            }
            
        except Exception as e:
            logger.error(f"获取基金{fund_code}历史数据异常: {e}")
            return None
    
    def get_fund_manager_info(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金经理信息
        
        Args:
            fund_code: 基金代码
        
        Returns:
            基金经理信息
        """
        try:
            url = f"http://fundf10.eastmoney.com/jjjl_{fund_code}.html"
            response = self.session.get(url, timeout=5)
            
            if response.status_code != 200:
                return None
            
            # 这里需要解析HTML，简化处理
            # 实际项目中可以使用BeautifulSoup
            content = response.text
            
            # 简单提取基金经理姓名（仅示例）
            manager_match = re.search(r'基金经理：(.*?)</a>', content)
            manager_name = manager_match.group(1) if manager_match else "未知"
            
            return {
                'fund_code': fund_code,
                'manager_name': manager_name,
                'source': 'eastmoney'
            }
            
        except Exception as e:
            logger.error(f"获取基金{fund_code}经理信息异常: {e}")
            return None
    
    def enrich_holdings_data(self, holdings: list) -> list:
        """
        为持仓数据补充实时信息
        
        Args:
            holdings: 持仓列表
        
        Returns:
            补充后的持仓列表
        """
        enriched = []
        
        for holding in holdings:
            fund_code = holding.get('code')
            
            # 获取实时数据
            fund_info = self.get_fund_info(fund_code)
            
            if fund_info:
                # 更新实时数据
                holding['real_time'] = {
                    'confirmed_nav': fund_info['confirmed_nav'],
                    'confirmed_date': fund_info['confirmed_date'],
                    'estimated_nav': fund_info['estimated_nav'],
                    'estimated_change': fund_info['estimated_change'],
                    'estimated_time': fund_info['estimated_time']
                }
                
                # 获取历史数据
                history = self.get_fund_history(fund_code, days=30)
                if history:
                    holding['performance'] = {
                        'monthly_return': history['period_return'],
                        'volatility': history['volatility'],
                        'max_nav': history['max_nav'],
                        'min_nav': history['min_nav']
                    }
                
                logger.info(f"✅ 已获取{holding['name']}实时数据")
            else:
                logger.warning(f"⚠️  未能获取{holding['name']}实时数据")
            
            enriched.append(holding)
        
        return enriched


# 测试代码
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    api = RealFundDataAPI()
    
    # 测试获取单只基金信息
    test_code = "004851"  # 广发医疗保健
    
    print(f"\n测试获取基金 {test_code} 实时信息:")
    print("=" * 50)
    info = api.get_fund_info(test_code)
    if info:
        print(json.dumps(info, indent=2, ensure_ascii=False))
    
    print(f"\n测试获取基金 {test_code} 历史数据:")
    print("=" * 50)
    history = api.get_fund_history(test_code, days=30)
    if history:
        print(json.dumps(history, indent=2, ensure_ascii=False))
    
    print("\n测试补充持仓数据:")
    print("=" * 50)
    test_holdings = [
        {
            "name": "广发医疗保健股票A",
            "code": "004851",
            "amount": 9069.40,
            "cost": 14000.00,
            "return_rate": -35.22
        }
    ]
    
    enriched = api.enrich_holdings_data(test_holdings)
    print(json.dumps(enriched, indent=2, ensure_ascii=False))
