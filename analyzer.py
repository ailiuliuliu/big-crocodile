"""
投资顾问系统 - 分析模块
负责分析持仓、生成调仓建议
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

logger = logging.getLogger(__name__)


class Analyzer:
    """投资分析器"""
    
    def __init__(self, config: dict, data_fetcher):
        self.config = config
        self.data_fetcher = data_fetcher
        self.trading_rules = config.get('trading_rules', {})
        
    def analyze_portfolio(self, holdings: List[Dict]) -> Dict:
        """
        分析持仓组合
        
        Args:
            holdings: 持仓列表
            
        Returns:
            分析结果
        """
        total_value = sum(h['amount'] for h in holdings)
        total_cost = sum(h.get('cost', h['amount'] / (1 + h['return_rate']/100)) for h in holdings)
        total_profit = sum(h.get('profit', 0) for h in holdings)
        total_return = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        # 分析每只基金
        fund_analysis = []
        for holding in holdings:
            analysis = self._analyze_single_fund(holding)
            fund_analysis.append(analysis)
        
        # 组合层面分析
        portfolio_analysis = {
            'total_value': total_value,
            'total_cost': total_cost,
            'total_profit': total_profit,
            'total_return': total_return,
            'fund_count': len(holdings),
            'fund_analysis': fund_analysis,
            'risk_alerts': self._check_portfolio_risks(holdings),
            'recommendations': self._generate_recommendations(fund_analysis)
        }
        
        return portfolio_analysis
    
    def _analyze_single_fund(self, holding: Dict) -> Dict:
        """
        分析单只基金
        
        逻辑：
        1. config.yaml的amount是上次更新的持仓金额
        2. 获取昨日确认净值，计算昨日实际涨跌
        3. 更新amount为最新值
        4. 获取今日估算涨跌
        5. 显示今日估算涨跌（相对于昨日净值）
        """
        fund_code = holding['code']
        fund_name = holding['name']
        last_amount = holding['amount']  # config里的金额（可能是过时的）
        return_rate = holding['return_rate']
        cost = holding.get('cost', last_amount / (1 + return_rate/100))
        profit = holding.get('profit', last_amount - cost)
        
        # 获取最新净值数据
        nav_data = self.data_fetcher.get_fund_nav(fund_code)
        
        # 默认值
        current_amount = last_amount
        today_change = 0.0
        
        if nav_data:
            # 今日估算涨跌幅（相对于昨日确认净值）
            today_change = nav_data.get('estimated_change', 0)
            
            # 如果有昨日净值和今日估算净值，可以计算当前估算金额
            # 但这需要知道持有份额，暂时先用config里的amount
            # TODO: 后续可以优化为存储份额，动态计算金额
            
        # 判断是否可以赎回
        can_redeem = True
        redemption_fee = 0.0
        
        analysis = {
            'fund_code': fund_code,
            'fund_name': fund_name,
            'current_amount': current_amount,
            'cost': cost,
            'profit': profit,
            'return_rate': return_rate,
            'can_redeem': can_redeem,
            'redemption_fee': redemption_fee,
            'confirmed_nav': nav_data.get('confirmed_nav', 0) if nav_data else 0,
            'confirmed_date': nav_data.get('confirmed_date', '') if nav_data else '',
            'today_change': today_change,
            'status': self._judge_fund_status(return_rate)
        }
        
        return analysis
    
    def _calculate_redemption_fee(self, holding_days: int) -> float:
        """
        计算赎回费率
        
        Args:
            holding_days: 持有天数
            
        Returns:
            费率（%）
        """
        if holding_days < 7:
            return 1.5
        elif holding_days < 30:
            return 0.5
        elif holding_days < 365:
            return 0.5
        elif holding_days < 730:
            return 0.0
        else:
            return 0.0
    
    def _judge_fund_status(self, return_rate: float) -> str:
        """
        判断基金状态
        
        Args:
            return_rate: 收益率
            
        Returns:
            状态描述
        """
        if return_rate < -20:
            return "深度亏损"
        elif return_rate < -10:
            return "亏损"
        elif return_rate < 0:
            return "轻微亏损"
        elif return_rate < 5:
            return "微盈"
        elif return_rate < 15:
            return "盈利"
        elif return_rate < 30:
            return "良好盈利"
        else:
            return "优秀盈利"
    
    def _check_portfolio_risks(self, holdings: List[Dict]) -> List[str]:
        """检查组合风险"""
        alerts = []
        
        total_value = sum(h['amount'] for h in holdings)
        
        # 检查单一持仓过高
        max_position_ratio = self.trading_rules.get('max_position_ratio', 30)
        for holding in holdings:
            ratio = (holding['amount'] / total_value * 100) if total_value > 0 else 0
            if ratio > max_position_ratio:
                alerts.append(
                    f"⚠️ {holding['name']}仓位过高（{ratio:.1f}%），建议不超过{max_position_ratio}%"
                )
        
        # 检查深度亏损
        for holding in holdings:
            if holding['return_rate'] < -20:
                alerts.append(
                    f"⚠️ {holding['name']}深度亏损（{holding['return_rate']:.1f}%），建议关注止损"
                )
        
        # 检查过度集中
        if len(holdings) < 3:
            alerts.append("⚠️ 持仓品种过少，建议增加分散度")
        
        return alerts
    
    def _generate_recommendations(self, fund_analysis: List[Dict]) -> List[Dict]:
        """
        生成调仓建议（优化版）
        
        新增逻辑：
        1. 超跌反弹机会识别
        2. 仓位配置优化建议
        3. 成本摊薄机会
        4. 长期趋势判断
        
        Args:
            fund_analysis: 基金分析结果
            
        Returns:
            建议列表
        """
        recommendations = []
        
        # 计算总仓位用于仓位分析
        total_value = sum(f['current_amount'] for f in fund_analysis)
        
        for analysis in fund_analysis:
            fund_name = analysis['fund_name']
            fund_code = analysis['fund_code']
            return_rate = analysis['return_rate']
            can_redeem = analysis['can_redeem']
            redemption_fee = analysis['redemption_fee']
            current_amount = analysis['current_amount']
            today_change = analysis.get('today_change', 0)
            
            # 计算仓位占比
            position_ratio = (current_amount / total_value * 100) if total_value > 0 else 0
            
            # ========== 1. 止损建议（深度亏损） ==========
            if return_rate < -30 and can_redeem:
                recommendations.append({
                    'type': '止损',
                    'fund_name': fund_name,
                    'reason': f'深度亏损{return_rate:.1f}%',
                    'action': '建议减仓50%或全部清仓',
                    'urgency': '高',
                    'cost': f'赎回费{redemption_fee:.2f}%',
                    'amount': int(current_amount * 0.5)  # 建议减仓金额
                })
            
            # ========== 2. 止盈建议（高收益） ==========
            elif return_rate > 50 and can_redeem:
                recommendations.append({
                    'type': '止盈',
                    'fund_name': fund_name,
                    'reason': f'收益率{return_rate:.1f}%已较高',
                    'action': '建议减仓30-50%锁定利润',
                    'urgency': '中',
                    'cost': f'赎回费{redemption_fee:.2f}%',
                    'amount': int(current_amount * 0.4)
                })
            
            # ========== 3. 超跌反弹机会（新增） ==========
            # 条件：亏损10-25%，今日反弹>3%，识别为超跌修复
            elif -25 < return_rate < -10 and today_change > 3:
                suggested_amount = self._calculate_add_position_amount(
                    current_amount, return_rate, position_ratio
                )
                recommendations.append({
                    'type': '加仓',
                    'fund_name': fund_name,
                    'reason': f'昨日超跌后反弹{today_change:+.1f}%，是加仓机会',
                    'action': f'建议加仓{suggested_amount}元摊低成本',
                    'urgency': '中',
                    'cost': '申购费约0.15%',
                    'amount': suggested_amount,
                    'target_position': f'加仓后仓位约{position_ratio + (suggested_amount/total_value*100):.1f}%'
                })
            
            # ========== 4. 仓位配置优化（新增） ==========
            # 黄金类资产：建议15-20%
            elif '黄金' in fund_name and position_ratio < 15 and -20 < return_rate < 0:
                suggested_amount = int(total_value * 0.17 - current_amount)  # 加仓到17%
                if suggested_amount > 500:
                    recommendations.append({
                        'type': '仓位优化',
                        'fund_name': fund_name,
                        'reason': f'黄金仓位偏低（当前{position_ratio:.1f}%），建议15-20%',
                        'action': f'建议加仓{suggested_amount}元优化配置',
                        'urgency': '低',
                        'cost': '申购费约0.15%',
                        'amount': suggested_amount,
                        'target_position': '17%'
                    })
            
            # ========== 5. 成本摊薄机会（新增） ==========
            # 条件：亏损10-30%，今日继续下跌>2%，考虑摊薄成本
            elif -30 < return_rate < -10 and today_change < -2:
                suggested_amount = int(current_amount * 0.2)  # 加仓20%
                if suggested_amount > 300:
                    recommendations.append({
                        'type': '成本摊薄',
                        'fund_name': fund_name,
                        'reason': f'当前亏损{return_rate:.1f}%，可考虑摊低成本',
                        'action': f'如看好长期，建议加仓{suggested_amount}元',
                        'urgency': '低',
                        'cost': '申购费约0.15%',
                        'amount': suggested_amount,
                        'expected_return': self._calculate_breakeven_return(return_rate, 0.2)
                    })
            
            # ========== 6. 长期持有建议（新增） ==========
            # 条件：收益率30-50%，继续持有等待更高收益
            elif 30 < return_rate < 50:
                recommendations.append({
                    'type': '持有',
                    'fund_name': fund_name,
                    'reason': f'收益率{return_rate:.1f}%表现优异',
                    'action': '建议继续持有，涨至+60%考虑减仓',
                    'urgency': '低',
                    'cost': '-',
                    'amount': 0
                })
        
        # 按紧急程度排序
        urgency_order = {'高': 0, '中': 1, '低': 2}
        recommendations.sort(key=lambda x: urgency_order.get(x.get('urgency', '低'), 2))
        
        return recommendations
    
    def _calculate_add_position_amount(self, current_amount: float, return_rate: float, 
                                      position_ratio: float) -> int:
        """
        计算建议加仓金额
        
        规则：
        1. 亏损越多，建议加仓越多
        2. 仓位占比越大，建议加仓越少
        3. 单次加仓不超过当前持仓的30%
        """
        base_amount = current_amount * 0.2  # 基础加仓20%
        
        # 亏损调整系数
        loss_factor = min(abs(return_rate) / 10, 2)  # 亏损10%=1倍，20%=2倍
        
        # 仓位调整系数
        position_factor = max(1 - position_ratio / 30, 0.5)  # 仓位30%=0.5倍
        
        suggested = base_amount * loss_factor * position_factor
        
        # 限制范围
        suggested = min(suggested, current_amount * 0.3)  # 不超过30%
        suggested = max(suggested, 500)  # 至少500元
        suggested = min(suggested, 2000)  # 最多2000元
        
        return int(suggested / 100) * 100  # 整百
    
    def _calculate_breakeven_return(self, current_return: float, add_ratio: float) -> str:
        """
        计算加仓后回本所需收益率
        
        Args:
            current_return: 当前收益率
            add_ratio: 加仓比例（0.2 = 加仓20%）
        
        Returns:
            回本所需收益率描述
        """
        # 简化计算：加仓后平均成本下降
        new_avg_return = current_return / (1 + add_ratio)
        breakeven = abs(new_avg_return)
        return f"回本需反弹约{breakeven:.1f}%"
    
    def generate_daily_report(self, analysis: Dict) -> str:
        """
        生成每日分析报告（文本格式）
        
        Args:
            analysis: 分析结果
            
        Returns:
            报告文本
        """
        report_lines = []
        
        # 标题
        today = datetime.now().strftime('%Y年%m月%d日 %A')
        report_lines.append(f"📊 投资组合分析报告")
        report_lines.append(f"⏰ {today} 午间分析\n")
        
        # 组合概览
        report_lines.append("=" * 40)
        report_lines.append("💼 组合概览")
        report_lines.append("=" * 40)
        report_lines.append(f"持仓总值：¥{analysis['total_value']:,.2f}")
        report_lines.append(f"持仓成本：¥{analysis['total_cost']:,.2f}")
        report_lines.append(f"持有收益：¥{analysis['total_profit']:+,.2f}")
        report_lines.append(f"总收益率：{analysis['total_return']:+.2f}%")
        report_lines.append(f"基金数量：{analysis['fund_count']}只\n")
        
        # 单只基金详情
        report_lines.append("=" * 40)
        report_lines.append("📈 持仓明细")
        report_lines.append("=" * 40)
        
        for fund in analysis['fund_analysis']:
            status_emoji = {
                '深度亏损': '🔴',
                '亏损': '🟠',
                '轻微亏损': '🟡',
                '微盈': '🟢',
                '盈利': '🟢',
                '良好盈利': '💚',
                '优秀盈利': '💎'
            }.get(fund['status'], '⚪')
            
            report_lines.append(f"\n{status_emoji} {fund['fund_name']}")
            report_lines.append(f"   持仓：¥{fund['current_amount']:,.2f}")
            report_lines.append(f"   成本：¥{fund['cost']:,.2f}")
            report_lines.append(f"   收益：¥{fund['profit']:+,.2f}")
            report_lines.append(f"   收益率：{fund['return_rate']:+.2f}%")
            if fund.get('confirmed_date'):
                report_lines.append(f"   昨日净值：{fund['confirmed_nav']:.4f}（{fund['confirmed_date']}）")
            if fund['today_change'] != 0:
                report_lines.append(f"   今日估算：{fund['today_change']:+.2f}%")
        
        # 风险提示
        if analysis['risk_alerts']:
            report_lines.append("\n" + "=" * 40)
            report_lines.append("⚠️ 风险提示")
            report_lines.append("=" * 40)
            for alert in analysis['risk_alerts']:
                report_lines.append(alert)
        
        # 调仓建议
        if analysis['recommendations']:
            report_lines.append("\n" + "=" * 40)
            report_lines.append("💡 调仓建议")
            report_lines.append("=" * 40)
            
            for i, rec in enumerate(analysis['recommendations'], 1):
                urgency_emoji = {
                    '高': '🔴',
                    '中': '🟡',
                    '低': '🟢'
                }.get(rec['urgency'], '⚪')
                
                type_emoji = {
                    '止损': '🔴',
                    '止盈': '💰',
                    '加仓': '📈',
                    '仓位优化': '⚖️',
                    '成本摊薄': '🔻',
                    '持有': '✋'
                }.get(rec['type'], '💡')
                
                report_lines.append(f"\n{i}. {type_emoji} 【{rec['type']}】{rec['fund_name']}")
                report_lines.append(f"   原因：{rec['reason']}")
                report_lines.append(f"   建议：{rec['action']}")
                
                # 显示金额（如果有）
                if rec.get('amount', 0) > 0:
                    report_lines.append(f"   金额：¥{rec['amount']:,}元")
                
                # 显示目标仓位（如果有）
                if rec.get('target_position'):
                    report_lines.append(f"   目标仓位：{rec['target_position']}")
                
                # 显示预期收益（如果有）
                if rec.get('expected_return'):
                    report_lines.append(f"   预期：{rec['expected_return']}")
                
                report_lines.append(f"   成本：{rec['cost']}")
        else:
            report_lines.append("\n" + "=" * 40)
            report_lines.append("✅ 今日无需调仓")
            report_lines.append("=" * 40)
            report_lines.append("当前持仓状态良好，建议继续持有观察")
        
        # 底部提示
        report_lines.append("\n" + "=" * 40)
        report_lines.append("📌 温馨提示")
        report_lines.append("=" * 40)
        report_lines.append("• 本建议仅供参考，不构成投资建议")
        report_lines.append("• 请根据自身风险承受能力决策")
        report_lines.append("• 投资有风险，入市需谨慎")
        
        return "\n".join(report_lines)
