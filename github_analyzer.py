"""
GitHub Actions版投资分析器
读取holdings.json，生成静态HTML报告
"""

import os
import json
import yaml
import logging
from datetime import datetime
from pathlib import Path

from real_fund_api import RealFundDataAPI
from ai_analyzer import AIInvestmentAnalyzer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_holdings():
    """加载持仓数据"""
    holdings_file = Path('data/holdings.json')
    
    if not holdings_file.exists():
        logger.error("❌ holdings.json不存在！")
        raise FileNotFoundError("请先创建 data/holdings.json 文件")
    
    with open(holdings_file, 'r', encoding='utf-8') as f:
        holdings = json.load(f)
    
    logger.info(f"✅ 加载了{len(holdings)}只基金")
    return holdings


def load_config():
    """加载配置（优先使用环境变量）"""
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # 从环境变量覆盖API Key（GitHub Secrets）
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        config['openai']['api_key'] = openai_key
        logger.info("✅ 使用GitHub Secrets中的OpenAI API Key")
    
    serverchan_key = os.getenv('SERVERCHAN_KEY')
    if serverchan_key:
        config['serverchan']['sendkey'] = serverchan_key
        config['serverchan']['enabled'] = True
        logger.info("✅ 使用GitHub Secrets中的Server酱Key")
    
    return config


def generate_html_report(analysis_result, output_dir='docs'):
    """生成静态HTML报告"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # 保存JSON数据（供JavaScript使用）
    with open(output_path / 'latest.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    # 生成HTML
    html_content = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>投资分析报告 - {analysis_result['analyzed_at']}</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
        }}
        .header h1 {{ font-size: 36px; margin-bottom: 10px; }}
        .header p {{ font-size: 16px; opacity: 0.9; }}
        .card {{
            background: white;
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
        }}
        .overview {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 20px;
        }}
        .overview-item {{
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }}
        .overview-item.positive {{
            background: linear-gradient(135deg, #d4fc79 0%, #96e6a1 100%);
        }}
        .overview-item.negative {{
            background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        }}
        .overview-item .label {{
            font-size: 14px;
            color: #666;
            margin-bottom: 8px;
        }}
        .overview-item .value {{
            font-size: 28px;
            font-weight: 700;
            color: #333;
        }}
        .rec-card {{
            border: 2px solid #e0e0e0;
            border-radius: 12px;
            padding: 20px;
            margin-bottom: 16px;
            border-left: 6px solid #667eea;
        }}
        .rec-card.stop-loss {{ border-left-color: #f44336; }}
        .rec-card.take-profit {{ border-left-color: #4caf50; }}
        .rec-card.buy {{ border-left-color: #2196f3; }}
        .rec-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 12px;
        }}
        .rec-type {{
            font-size: 18px;
            font-weight: 700;
        }}
        .rec-urgency {{
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
        }}
        .rec-urgency.high {{ background: #fee; color: #c00; }}
        .rec-urgency.medium {{ background: #ffefd5; color: #ff8c00; }}
        .rec-urgency.low {{ background: #e8f5e9; color: #2e7d32; }}
        .market-analysis {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 12px;
            line-height: 1.8;
            color: #333;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 16px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }}
        th {{
            background: #f5f7fa;
            font-weight: 600;
            color: #666;
        }}
        .footer {{
            text-align: center;
            color: white;
            margin-top: 30px;
            opacity: 0.8;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 投资分析报告</h1>
            <p>生成时间: {analysis_result['analyzed_at']}</p>
            <p>AI驱动 · 每日自动更新</p>
        </div>

        <div class="card">
            <h2 style="margin-bottom: 20px;">💼 组合概览</h2>
            <div class="overview">
                <div class="overview-item">
                    <div class="label">持仓总值</div>
                    <div class="value">¥{analysis_result['portfolio_metrics']['total_value']:,.2f}</div>
                </div>
                <div class="overview-item">
                    <div class="label">持仓成本</div>
                    <div class="value">¥{analysis_result['portfolio_metrics']['total_cost']:,.2f}</div>
                </div>
                <div class="overview-item {'positive' if analysis_result['portfolio_metrics']['total_profit'] >= 0 else 'negative'}">
                    <div class="label">持有收益</div>
                    <div class="value">{'+'if analysis_result['portfolio_metrics']['total_profit'] >= 0 else ''}¥{analysis_result['portfolio_metrics']['total_profit']:,.2f}</div>
                </div>
                <div class="overview-item {'positive' if analysis_result['portfolio_metrics']['total_return'] >= 0 else 'negative'}">
                    <div class="label">总收益率</div>
                    <div class="value">{'+'if analysis_result['portfolio_metrics']['total_return'] >= 0 else ''}{analysis_result['portfolio_metrics']['total_return']:.2f}%</div>
                </div>
            </div>
        </div>

        <div class="card">
            <h2 style="margin-bottom: 20px;">💡 智能建议（共{len(analysis_result['recommendations'])}条）</h2>
            {''.join([f'''
            <div class="rec-card">
                <div class="rec-header">
                    <div class="rec-type">{rec.get('type', '建议')} · {rec['fund_name']}</div>
                    <div class="rec-urgency {rec['urgency'].lower()}">紧急度: {rec['urgency']}</div>
                </div>
                <div style="margin-bottom: 12px;"><strong>原因：</strong>{rec['reason']}</div>
                <div style="margin-bottom: 12px;"><strong>建议：</strong>{rec['action']}</div>
                {''.join([f"<div style='font-size: 14px; color: #666; margin-top: 8px;'>{k}: {v}</div>" for k, v in rec.get('details', {}).items()])}
            </div>
            ''' for rec in analysis_result['recommendations']])}
        </div>

        <div class="card">
            <h2 style="margin-bottom: 20px;">📈 市场分析</h2>
            <div class="market-analysis">
                {analysis_result.get('market_analysis', '暂无市场分析')}
            </div>
        </div>

        <div class="card">
            <h2 style="margin-bottom: 20px;">📋 持仓明细</h2>
            <table>
                <thead>
                    <tr>
                        <th>基金名称</th>
                        <th>持仓金额</th>
                        <th>收益率</th>
                        <th>实时涨跌</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{h['name']}</td>
                        <td>¥{h['amount']:,.2f}</td>
                        <td style="color: {'#2e7d32' if h['return_rate'] >= 0 else '#c62828'}; font-weight: 600;">
                            {'+'if h['return_rate'] >= 0 else ''}{h['return_rate']:.2f}%
                        </td>
                        <td style="color: {'#2e7d32' if h.get('real_time', {}).get('estimated_change', 0) >= 0 else '#c62828'};">
                            {'+'if h.get('real_time', {}).get('estimated_change', 0) >= 0 else ''}{h.get('real_time', {}).get('estimated_change', 0):.2f}%
                        </td>
                    </tr>
                    ''' for h in analysis_result['holdings']])}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>📊 数据来源: 天天基金 · 东方财富</p>
            <p>🤖 AI分析: GPT-4</p>
            <p>🔄 每日自动更新 · GitHub Actions驱动</p>
        </div>
    </div>
</body>
</html>"""
    
    with open(output_path / 'index.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    logger.info(f"✅ HTML报告已生成: {output_path / 'index.html'}")
    
    # 保存历史记录
    history_dir = output_path / 'history'
    history_dir.mkdir(exist_ok=True)
    
    date_str = datetime.now().strftime('%Y-%m-%d')
    with open(history_dir / f'{date_str}.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✅ 历史数据已保存: {date_str}.json")


def main():
    """主函数"""
    try:
        logger.info("="*60)
        logger.info("🚀 GitHub Actions投资分析器启动")
        logger.info("="*60)
        
        # 1. 加载配置和持仓
        config = load_config()
        holdings = load_holdings()
        
        # 2. 创建分析器
        analyzer = AIInvestmentAnalyzer(config)
        
        # 3. 执行分析
        logger.info("📊 开始分析...")
        analysis_result = analyzer.analyze_portfolio(holdings)
        
        # 4. 生成HTML报告
        logger.info("📄 生成HTML报告...")
        generate_html_report(analysis_result)
        
        logger.info("="*60)
        logger.info("✅ 分析完成！")
        logger.info("="*60)
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
