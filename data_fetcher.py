"""
投资顾问系统 - 数据获取模块
负责从各个数据源获取市场数据、基金净值、财经新闻等
"""

import requests
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class DataFetcher:
    """数据获取器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def get_fund_nav(self, fund_code: str) -> Optional[Dict]:
        """
        获取基金净值数据
        
        Args:
            fund_code: 基金代码
            
        Returns:
            {
                'confirmed_nav': 昨日确认净值,
                'confirmed_date': 净值日期,
                'estimated_nav': 今日估算净值,
                'estimated_change': 今日估算涨跌幅（相对昨日净值）,
                'name': 基金名称
            }
        """
        try:
            url = f"https://fundgz.1234567.com.cn/js/{fund_code}.js"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # 解析jsonp格式数据
                json_str = response.text.split('(')[1].split(')')[0]
                data = json.loads(json_str)
                
                # dwjz: 昨日确认净值（单位净值）
                # jzrq: 净值日期
                # gsz: 今日估算净值
                # gszzl: 今日估算涨跌幅（相对于dwjz）
                
                confirmed_nav = float(data.get('dwjz', 0))
                estimated_nav = float(data.get('gsz', confirmed_nav))
                estimated_change = float(data.get('gszzl', 0))
                
                return {
                    'confirmed_nav': confirmed_nav,
                    'confirmed_date': data.get('jzrq', ''),
                    'estimated_nav': estimated_nav,
                    'estimated_change': estimated_change,
                    'name': data.get('name', ''),
                    'update_time': data.get('gztime', '')
                }
        except Exception as e:
            logger.error(f"获取基金{fund_code}净值失败: {e}")
        
        return None
    
    def get_market_news(self, keywords: List[str] = None, limit: int = 10) -> List[Dict]:
        """
        获取财经新闻
        
        Args:
            keywords: 关键词列表
            limit: 返回数量
            
        Returns:
            新闻列表 [{'title': 标题, 'url': 链接, 'source': 来源, 'time': 时间}]
        """
        news_list = []
        
        try:
            # 从东方财富获取新闻
            url = "https://stock.eastmoney.com/a/cdpfx.html"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # 解析新闻列表（简化版，实际需要根据页面结构调整）
                articles = soup.find_all('div', class_='text-area', limit=limit)
                
                for article in articles:
                    try:
                        title_tag = article.find('a')
                        if title_tag:
                            news_list.append({
                                'title': title_tag.get_text(strip=True),
                                'url': title_tag.get('href', ''),
                                'source': '东方财富',
                                'time': datetime.now().strftime('%Y-%m-%d %H:%M')
                            })
                    except Exception as e:
                        continue
        
        except Exception as e:
            logger.error(f"获取市场新闻失败: {e}")
        
        return news_list[:limit]
    
    def get_index_data(self, index_code: str = '000001') -> Optional[Dict]:
        """
        获取指数数据
        
        Args:
            index_code: 指数代码（默认上证指数）
            
        Returns:
            {'price': 点位, 'change': 涨跌幅, 'volume': 成交量}
        """
        try:
            # 简化实现：从新浪财经获取
            url = f"https://hq.sinajs.cn/list=s_sh{index_code}"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.text.split(',')
                if len(data) >= 4:
                    return {
                        'name': data[0].split('"')[1],
                        'price': float(data[1]),
                        'change': float(data[2]),
                        'change_pct': float(data[3]),
                        'volume': data[4] if len(data) > 4 else '0'
                    }
        
        except Exception as e:
            logger.error(f"获取指数{index_code}数据失败: {e}")
        
        return None
    
    def search_industry_trends(self, industries: List[str]) -> Dict[str, str]:
        """
        搜索行业趋势信息
        
        Args:
            industries: 行业列表，如 ['医疗', '新能源', '机器人']
            
        Returns:
            {行业: 趋势描述}
        """
        trends = {}
        
        for industry in industries:
            try:
                # 使用Google搜索最新行业信息
                query = f"{industry} 2026年3月 投资机会 行业趋势"
                # 这里简化处理，实际可以调用搜索API
                trends[industry] = f"正在分析{industry}行业最新趋势..."
                
            except Exception as e:
                logger.error(f"搜索{industry}行业趋势失败: {e}")
                trends[industry] = "暂无数据"
        
        return trends
    
    def get_hot_funds(self, fund_type: str = "股票型", limit: int = 10) -> List[Dict]:
        """
        获取热门基金
        
        Args:
            fund_type: 基金类型
            limit: 返回数量
            
        Returns:
            基金列表
        """
        hot_funds = []
        
        try:
            # 从天天基金网获取热门基金
            url = "https://fund.eastmoney.com/data/fundranking.html"
            response = self.session.get(url, timeout=10)
            
            # 实际需要解析页面或调用API
            # 这里返回空列表，待实际接口接入
            
        except Exception as e:
            logger.error(f"获取热门基金失败: {e}")
        
        return hot_funds
    
    def calculate_holding_days(self, buy_date: str) -> int:
        """
        计算持有天数
        
        Args:
            buy_date: 买入日期 "YYYY-MM-DD"
            
        Returns:
            持有天数
        """
        try:
            buy_dt = datetime.strptime(buy_date, "%Y-%m-%d")
            today = datetime.now()
            return (today - buy_dt).days
        except Exception as e:
            logger.error(f"计算持有天数失败: {e}")
            return 0
