#!/usr/bin/env python3
"""
投资顾问系统 - 快速配置向导
帮助用户快速配置系统
"""

import yaml
import sys
from pathlib import Path


def print_banner():
    """打印标题"""
    print("="*60)
    print("投资顾问系统 - 快速配置向导")
    print("="*60)
    print()


def get_serverchan_key():
    """获取Server酱配置"""
    print("📱 配置微信推送（Server酱）")
    print("-" * 60)
    print()
    print("Server酱是最简单的微信推送方式（免费，每天5条）")
    print()
    print("获取步骤：")
    print("1. 访问 https://sct.ftqq.com/")
    print("2. 使用微信扫码登录")
    print("3. 扫码关注'Server酱'公众号")
    print("4. 在网站上复制你的SendKey（类似 SCT12345xxxxx）")
    print()
    
    sendkey = input("请输入你的SendKey（直接回车跳过）: ").strip()
    
    if sendkey:
        print(f"✅ SendKey已配置: {sendkey[:10]}...")
        return sendkey
    else:
        print("⚠️ 跳过Server酱配置")
        return None


def get_user_info():
    """获取用户信息"""
    print("\n👤 配置用户信息")
    print("-" * 60)
    print()
    
    name = input("你的姓名（默认：老李）: ").strip() or "老李"
    
    print("\n风险偏好：")
    print("1. 稳健型（低风险低收益）")
    print("2. 平衡型（中等风险中等收益）")
    print("3. 激进型（高风险高收益）")
    
    risk_map = {"1": "稳健型", "2": "平衡型", "3": "激进型"}
    risk_choice = input("请选择（默认：2）: ").strip() or "2"
    risk = risk_map.get(risk_choice, "平衡型")
    
    horizon_map = {"1": "短期", "2": "中期", "3": "长期"}
    print("\n投资期限：")
    print("1. 短期（<1年）")
    print("2. 中期（1-3年）")
    print("3. 长期（>3年）")
    
    horizon_choice = input("请选择（默认：3）: ").strip() or "3"
    horizon = horizon_map.get(horizon_choice, "长期")
    
    print(f"\n✅ 用户信息: {name} | {risk} | {horizon}")
    
    return {
        "name": name,
        "nickname": name,
        "risk_preference": risk,
        "investment_horizon": horizon,
        "max_drawdown": 50,
        "total_capital": 150000
    }


def add_holdings():
    """添加持仓信息"""
    print("\n💼 配置持仓信息")
    print("-" * 60)
    print()
    print("现在添加你的基金持仓（可以稍后在config.yaml中修改）")
    print()
    
    holdings = []
    
    while True:
        print(f"\n第{len(holdings) + 1}只基金：")
        
        name = input("  基金名称（直接回车结束）: ").strip()
        if not name:
            break
        
        code = input("  基金代码（6位数字）: ").strip()
        amount = input("  持有金额（元）: ").strip()
        return_rate = input("  当前收益率（%）: ").strip()
        buy_date = input("  买入日期（YYYY-MM-DD，可选）: ").strip()
        
        try:
            holding = {
                "name": name,
                "code": code,
                "amount": float(amount),
                "return_rate": float(return_rate),
            }
            
            if buy_date:
                holding["buy_date"] = buy_date
            
            holdings.append(holding)
            print(f"  ✅ 已添加: {name}")
        
        except ValueError:
            print("  ❌ 输入格式错误，请重新输入")
    
    if not holdings:
        print("⚠️ 未添加任何持仓，将使用示例数据")
        holdings = [
            {
                "name": "示例基金A",
                "code": "000001",
                "amount": 10000,
                "return_rate": 10.0,
                "buy_date": "2024-01-01"
            }
        ]
    
    print(f"\n✅ 共添加 {len(holdings)} 只基金")
    return holdings


def generate_config(sendkey, user_info, holdings):
    """生成配置文件"""
    config = {
        "holdings": holdings,
        "user": user_info,
        "serverchan": {
            "enabled": bool(sendkey),
            "sendkey": sendkey or "YOUR_SENDKEY_HERE"
        },
        "wechat_work": {
            "enabled": False,
            "webhook_url": "YOUR_WEBHOOK_URL_HERE"
        },
        "openai": {
            "api_key": "YOUR_OPENAI_API_KEY_HERE",
            "model": "gpt-4o-mini",
            "base_url": "https://api.openai.com/v1"
        },
        "trading_rules": {
            "min_trade_amount": 1000,
            "min_return_threshold": 5,
            "short_term_days": 7,
            "emergency_threshold": 10,
            "max_position_ratio": 30
        },
        "schedule": {
            "daily_analysis_time": "12:00",
            "timezone": "Asia/Shanghai"
        },
        "logging": {
            "level": "INFO",
            "file": "logs/advisor.log",
            "max_bytes": 10485760,
            "backup_count": 5
        },
        "data_sources": {
            "fund_api": "https://fund.eastmoney.com",
            "news_sources": [
                "https://finance.sina.com.cn",
                "https://www.21jingji.com",
                "https://stock.eastmoney.com"
            ]
        }
    }
    
    return config


def main():
    """主函数"""
    print_banner()
    
    # 检查config.yaml是否已存在
    if Path("config.yaml").exists():
        print("⚠️ 检测到config.yaml已存在")
        choice = input("是否覆盖？(y/n): ").strip().lower()
        if choice != 'y':
            print("已取消配置")
            return
    
    # 引导配置
    sendkey = get_serverchan_key()
    user_info = get_user_info()
    holdings = add_holdings()
    
    # 生成配置
    print("\n📝 生成配置文件...")
    config = generate_config(sendkey, user_info, holdings)
    
    # 保存配置
    with open("config.yaml", 'w', encoding='utf-8') as f:
        yaml.dump(config, f, allow_unicode=True, default_flow_style=False, sort_keys=False)
    
    print("✅ 配置文件已保存: config.yaml")
    
    # 下一步提示
    print("\n" + "="*60)
    print("🎉 配置完成！")
    print("="*60)
    print()
    print("接下来的步骤：")
    print("1. 运行测试: python3 test.py")
    print("2. 手动运行一次: python3 advisor.py")
    print("3. 安装定时任务: ./install.sh")
    print()
    print("详细文档: README.md")
    print()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n已取消配置")
        sys.exit(1)
