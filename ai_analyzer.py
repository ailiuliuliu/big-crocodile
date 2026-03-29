"""
AI驱动的投资分析引擎
使用GPT-4进行深度投资分析和建议生成
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime

try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  未安装openai库，将使用规则引擎")

from real_fund_api import RealFundDataAPI

logger = logging.getLogger(__name__)


class AIInvestmentAnalyzer:
    """AI投资分析器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.openai_config = config.get('openai', {})
        self.fund_api = RealFundDataAPI()
        
        # 初始化OpenAI客户端
        if HAS_OPENAI and self.openai_config.get('api_key'):
            self.client = OpenAI(
                api_key=self.openai_config['api_key'],
                base_url=self.openai_config.get('base_url', 'https://api.openai.com/v1')
            )
            self.use_ai = True
            logger.info("✅ 使用GPT-4进行投资分析")
        else:
            self.use_ai = False
            logger.warning("⚠️  未配置OpenAI API，使用规则引擎")
    
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict:
        """
        分析投资组合
        
        Args:
            holdings: 持仓列表
        
        Returns:
            完整的分析报告
        """
        # 1. 补充真实基金数据
        logger.info("📊 正在获取实时基金数据...")
        enriched_holdings = self.fund_api.enrich_holdings_data(holdings)
        
        # 2. 计算组合指标
        portfolio_metrics = self._calculate_portfolio_metrics(enriched_holdings)
        
        # 3. 生成AI建议（或规则建议）
        if self.use_ai:
            logger.info("🤖 正在使用GPT-4生成投资建议...")
            recommendations = self._generate_ai_recommendations(
                enriched_holdings, 
                portfolio_metrics
            )
        else:
            logger.info("📋 使用规则引擎生成建议...")
            recommendations = self._generate_rule_based_recommendations(
                enriched_holdings,
                portfolio_metrics
            )
        
        # 4. 生成市场分析
        if self.use_ai:
            market_analysis = self._generate_market_analysis(enriched_holdings)
        else:
            market_analysis = "未启用AI分析，请配置OpenAI API Key获取深度市场洞察"
        
        return {
            'portfolio_metrics': portfolio_metrics,
            'holdings': enriched_holdings,
            'recommendations': recommendations,
            'market_analysis': market_analysis,
            'analyzed_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _calculate_portfolio_metrics(self, holdings: List[Dict]) -> Dict:
        """计算组合指标"""
        total_value = sum(h['amount'] for h in holdings)
        total_cost = sum(h['cost'] for h in holdings)
        total_profit = total_value - total_cost
        total_return = (total_profit / total_cost * 100) if total_cost > 0 else 0
        
        # 计算各个资产类别占比
        asset_allocation = {}
        for h in holdings:
            name = h['name']
            if '黄金' in name:
                category = '黄金'
            elif '医疗' in name or '医药' in name:
                category = '医疗'
            elif '新能源' in name or '光伏' in name:
                category = '新能源'
            elif '机器人' in name or 'AI' in name:
                category = '科技'
            elif '红利' in name or '价值' in name:
                category = '红利价值'
            else:
                category = '其他'
            
            ratio = (h['amount'] / total_value * 100) if total_value > 0 else 0
            asset_allocation[category] = asset_allocation.get(category, 0) + ratio
        
        return {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_return': total_return,
            'fund_count': len(holdings),
            'asset_allocation': asset_allocation
        }
    
    def _generate_ai_recommendations(self, holdings: List[Dict], 
                                    portfolio_metrics: Dict) -> List[Dict]:
        """使用GPT-4生成智能建议"""
        try:
            # 构建prompt
            prompt = self._build_analysis_prompt(holdings, portfolio_metrics)
            
            # 调用GPT-4
            response = self.client.chat.completions.create(
                model=self.openai_config.get('model', 'gpt-4o'),
                messages=[
                    {
                        "role": "system",
                        "content": "你是专业投资顾问。分析基金持仓，提供具体建议：止损、止盈、加仓、持有、减仓。每条建议50-80字，聚焦操作要点。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.openai_config.get('max_tokens', 4000),
                temperature=self.openai_config.get('temperature', 0.7),
                response_format={"type": "json_object"}
            )
            
            # 解析返回结果
            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)
            
            recommendations = result_json.get('recommendations', [])
            
            logger.info(f"✅ GPT-4生成了{len(recommendations)}条建议")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"❌ GPT-4分析失败: {e}")
            # 降级到规则引擎
            return self._generate_rule_based_recommendations(holdings, portfolio_metrics)
    
    def _build_analysis_prompt(self, holdings: List[Dict], 
                              portfolio_metrics: Dict) -> str:
        """构建分析prompt"""
        
        # 简化持仓数据（避免token过多）
        simplified_holdings = []
        for h in holdings:
            item = {
                'name': h['name'],
                'code': h['code'],
                'amount': h['amount'],
                'cost': h['cost'],
                'return_rate': h['return_rate'],
                'position_ratio': (h['amount'] / portfolio_metrics['total_value'] * 100)
            }
            
            # 添加实时数据
            if 'real_time' in h:
                item['real_time'] = h['real_time']
            
            # 添加历史表现
            if 'performance' in h:
                item['performance'] = h['performance']
            
            simplified_holdings.append(item)
        
        prompt = f"""分析投资组合，提供4-5条核心建议：

总市值¥{portfolio_metrics['total_value']:.2f} | 成本¥{portfolio_metrics['total_cost']:.2f} | 收益率{portfolio_metrics['total_return']:.2f}%

持仓明细：
{json.dumps(simplified_holdings, indent=2, ensure_ascii=False)}

返回JSON格式（每条建议50-80字）：
{{
  "recommendations": [
    {{
      "type": "止损|止盈|加仓|持有|减仓",
      "fund_name": "基金名称",
      "urgency": "高|中|低",
      "reason": "核心理由（聚焦操作要点）",
      "action": "具体操作"
    }}
  ]
}}
"""
        
        return prompt
    
    def _generate_rule_based_recommendations(self, holdings: List[Dict],
                                            portfolio_metrics: Dict) -> List[Dict]:
        """规则引擎生成建议（降级方案）"""
        recommendations = []
        total_value = portfolio_metrics['total_value']
        
        for h in holdings:
            fund_name = h['name']
            return_rate = h['return_rate']
            current_amount = h['amount']
            position_ratio = (current_amount / total_value * 100) if total_value > 0 else 0
            
            # 规则1：深度亏损止损
            if return_rate < -30:
                recommendations.append({
                    'type': '止损',
                    'fund_name': fund_name,
                    'urgency': '高',
                    'reason': f'深度亏损{return_rate:.1f}%，建议止损',
                    'action': f'建议减仓50%或清仓',
                    'details': {
                        '建议金额': f'¥{int(current_amount * 0.5)}',
                        '风险提示': '继续持有可能加剧损失'
                    }
                })
            
            # 规则2：高收益止盈
            elif return_rate > 30:
                recommendations.append({
                    'type': '止盈',
                    'fund_name': fund_name,
                    'urgency': '中',
                    'reason': f'收益率{return_rate:.1f}%较高，建议锁定利润',
                    'action': '建议减仓30-40%',
                    'details': {
                        '建议金额': f'¥{int(current_amount * 0.35)}',
                        '预期收益': '锁定部分利润'
                    }
                })
            
            # 规则3：黄金仓位优化
            elif '黄金' in fund_name and position_ratio < 15:
                add_amount = int(total_value * 0.17 - current_amount)
                if add_amount > 500:
                    recommendations.append({
                        'type': '加仓',
                        'fund_name': fund_name,
                        'urgency': '中',
                        'reason': f'黄金仓位{position_ratio:.1f}%偏低，建议提升至15-20%',
                        'action': f'建议加仓至17%仓位',
                        'details': {
                            '建议金额': f'¥{add_amount}',
                            '目标仓位': '17%'
                        }
                    })
            
            # 规则4：成本摊薄
            elif -25 < return_rate < -10:
                add_amount = min(2000, int(current_amount * 0.25))
                recommendations.append({
                    'type': '加仓',
                    'fund_name': fund_name,
                    'urgency': '低',
                    'reason': f'亏损{return_rate:.1f}%，可考虑摊低成本',
                    'action': f'如看好长期，建议加仓{add_amount}元',
                    'details': {
                        '建议金额': f'¥{add_amount}',
                        '预期收益': '降低持仓成本'
                    }
                })
        
        return recommendations
    
    def _generate_market_analysis(self, holdings: List[Dict]) -> str:
        """生成市场分析"""
        try:
            # 提取行业信息
            industries = set()
            for h in holdings:
                name = h['name']
                if '医疗' in name or '医药' in name:
                    industries.add('医疗医药')
                if '新能源' in name or '光伏' in name:
                    industries.add('新能源')
                if '黄金' in name:
                    industries.add('黄金')
                if '机器人' in name or 'AI' in name:
                    industries.add('科技AI')
            
            prompt = f"""请简要分析当前市场环境对以下行业的影响：

持仓行业：{', '.join(industries)}

请从以下角度分析（200字以内）：
1. 宏观经济环境（降息预期、政策方向）
2. 行业景气度判断
3. 未来1-3个月趋势预判

请用专业但易懂的语言回答。"""
            
            response = self.client.chat.completions.create(
                model=self.openai_config.get('model', 'gpt-4o'),
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深的市场分析师，擅长宏观经济和行业趋势分析。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            analysis = response.choices[0].message.content
            
            return analysis
            
        except Exception as e:
            logger.error(f"市场分析生成失败: {e}")
            return "市场分析功能暂时不可用"


# 测试代码
if __name__ == '__main__':
    import yaml
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 测试持仓
    test_holdings = [
        {
            "name": "广发医疗保健股票A",
            "code": "004851",
            "amount": 9069.40,
            "cost": 14000.00,
            "return_rate": -35.22
        },
        {
            "name": "国泰黄金ETF联接A",
            "code": "000218",
            "amount": 4110.88,
            "cost": 4800.00,
            "return_rate": -14.36
        },
        {
            "name": "信澳新能源产业股票A",
            "code": "001410",
            "amount": 6568.53,
            "cost": 4819.98,
            "return_rate": 36.28
        }
    ]
    
    # 创建分析器
    analyzer = AIInvestmentAnalyzer(config)
    
    print("\n" + "="*60)
    print("🤖 AI投资分析引擎测试")
    print("="*60)
    
    # 执行分析
    result = analyzer.analyze_portfolio(test_holdings)
    
    print("\n📊 组合指标:")
    print(json.dumps(result['portfolio_metrics'], indent=2, ensure_ascii=False))
    
    print("\n💡 投资建议:")
    for i, rec in enumerate(result['recommendations'], 1):
        print(f"\n{i}. [{rec['type']}] {rec['fund_name']} (紧急度: {rec['urgency']})")
        print(f"   理由: {rec['reason']}")
        print(f"   建议: {rec['action']}")
        if rec.get('details'):
            print(f"   详情: {rec['details']}")
    
    print("\n📈 市场分析:")
    print(result['market_analysis'])
