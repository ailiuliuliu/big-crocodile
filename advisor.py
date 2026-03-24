"""
投资顾问系统 - 主程序
每日自动分析持仓并推送建议
"""

import yaml
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict

from data_fetcher import DataFetcher
from analyzer import Analyzer
from notifier import Notifier


def setup_logging(config: dict):
    """配置日志"""
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', 'logs/advisor.log')
    
    # 确保日志目录存在
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )


def load_config(config_path: str = 'config.yaml') -> dict:
    """加载配置文件"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        print(f"加载配置文件失败: {e}")
        sys.exit(1)


def check_config(config: dict) -> bool:
    """检查配置是否完整"""
    errors = []
    
    # 检查持仓信息
    if not config.get('holdings'):
        errors.append("未配置持仓信息")
    
    # 检查推送配置
    serverchan = config.get('serverchan', {})
    wechat_work = config.get('wechat_work', {})
    
    if serverchan.get('enabled') and serverchan.get('sendkey') == 'YOUR_SENDKEY_HERE':
        errors.append("Server酱SendKey未配置")
    
    if wechat_work.get('enabled') and wechat_work.get('webhook_url') == 'YOUR_WEBHOOK_URL_HERE':
        errors.append("企业微信Webhook URL未配置")
    
    if not serverchan.get('enabled') and not wechat_work.get('enabled'):
        errors.append("未启用任何推送渠道")
    
    if errors:
        for error in errors:
            logging.error(f"配置错误: {error}")
        return False
    
    return True


def main():
    """主函数"""
    # 切换到脚本所在目录
    script_dir = Path(__file__).parent
    Path.cwd()
    
    # 加载配置
    config = load_config(script_dir / 'config.yaml')
    
    # 配置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 50)
    logger.info("投资顾问系统启动")
    logger.info("=" * 50)
    
    # 检查配置
    if not check_config(config):
        logger.error("配置检查失败，请修改config.yaml后重试")
        sys.exit(1)
    
    try:
        # 初始化模块
        data_fetcher = DataFetcher(config)
        analyzer = Analyzer(config, data_fetcher)
        notifier = Notifier(config)
        
        # 获取持仓信息
        holdings = config.get('holdings', [])
        logger.info(f"当前持仓: {len(holdings)}只基金")
        
        # 分析持仓
        logger.info("开始分析持仓...")
        analysis_result = analyzer.analyze_portfolio(holdings)
        
        # 生成报告
        logger.info("生成分析报告...")
        report = analyzer.generate_daily_report(analysis_result)
        
        # 打印报告到日志
        logger.info("\n" + report)
        
        # 推送到微信
        user_name = config.get('user', {}).get('nickname', '用户')
        title = f"📊 {user_name}的投资组合分析"
        
        logger.info("推送报告到微信...")
        success = notifier.send_report(title, report)
        
        if success:
            logger.info("✅ 报告推送成功")
        else:
            logger.error("❌ 报告推送失败")
        
        # 检查紧急情况
        emergency_threshold = config.get('trading_rules', {}).get('emergency_threshold', 10)
        for fund_analysis in analysis_result['fund_analysis']:
            if abs(fund_analysis['today_change']) > emergency_threshold:
                alert_msg = (
                    f"⚠️ 紧急提醒\n\n"
                    f"{fund_analysis['fund_name']}\n"
                    f"今日波动: {fund_analysis['today_change']:+.2f}%\n"
                    f"已超过预警阈值({emergency_threshold}%)\n"
                    f"建议关注市场动态"
                )
                notifier.send_alert(alert_msg)
        
        logger.info("=" * 50)
        logger.info("投资顾问系统完成")
        logger.info("=" * 50)
    
    except Exception as e:
        logger.error(f"执行失败: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
