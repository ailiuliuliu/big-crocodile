#!/usr/bin/env python3
"""
投资顾问系统 - 测试脚本
用于验证各个模块是否正常工作
"""

import sys
import yaml
from pathlib import Path

def test_config():
    """测试配置文件"""
    print("📋 测试配置文件...")
    try:
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # 检查必要字段
        assert config.get('holdings'), "持仓信息未配置"
        assert config.get('user'), "用户信息未配置"
        assert config.get('serverchan') or config.get('wechat_work'), "推送渠道未配置"
        
        print("✅ 配置文件格式正确")
        print(f"   - 持仓数量: {len(config['holdings'])}只")
        print(f"   - 用户: {config['user'].get('nickname', '未知')}")
        return True
    except Exception as e:
        print(f"❌ 配置文件错误: {e}")
        return False


def test_dependencies():
    """测试依赖包"""
    print("\n📦 测试依赖包...")
    dependencies = ['requests', 'yaml', 'bs4']
    
    all_ok = True
    for dep in dependencies:
        try:
            __import__(dep)
            print(f"✅ {dep} 已安装")
        except ImportError:
            print(f"❌ {dep} 未安装")
            all_ok = False
    
    return all_ok


def test_data_fetcher():
    """测试数据获取模块"""
    print("\n🌐 测试数据获取模块...")
    try:
        from data_fetcher import DataFetcher
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        fetcher = DataFetcher(config)
        
        # 测试获取基金净值
        test_fund = config['holdings'][0]['code']
        nav_data = fetcher.get_fund_nav(test_fund)
        
        if nav_data:
            print(f"✅ 基金净值获取成功")
            print(f"   - 基金: {nav_data.get('name')}")
            print(f"   - 净值: {nav_data.get('nav')}")
            print(f"   - 涨跌: {nav_data.get('change'):+.2f}%")
            return True
        else:
            print("⚠️ 基金净值获取失败（可能是网络问题）")
            return False
    except Exception as e:
        print(f"❌ 数据获取模块错误: {e}")
        return False


def test_analyzer():
    """测试分析模块"""
    print("\n📊 测试分析模块...")
    try:
        from data_fetcher import DataFetcher
        from analyzer import Analyzer
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        fetcher = DataFetcher(config)
        analyzer = Analyzer(config, fetcher)
        
        # 分析持仓
        holdings = config['holdings']
        result = analyzer.analyze_portfolio(holdings)
        
        print(f"✅ 分析模块正常")
        print(f"   - 总收益率: {result['total_return']:+.2f}%")
        print(f"   - 风险提示: {len(result['risk_alerts'])}条")
        print(f"   - 调仓建议: {len(result['recommendations'])}条")
        return True
    except Exception as e:
        print(f"❌ 分析模块错误: {e}")
        return False


def test_notifier():
    """测试推送模块"""
    print("\n📱 测试推送模块...")
    try:
        from notifier import Notifier
        
        with open('config.yaml', 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        notifier = Notifier(config)
        
        # 测试连接
        print("发送测试消息...")
        results = notifier.test_connection()
        
        if any(results.values()):
            print("✅ 推送模块正常")
            for channel, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                print(f"   - {channel}: {status}")
            return True
        else:
            print("❌ 所有推送渠道均失败")
            print("   请检查config.yaml中的推送配置")
            return False
    except Exception as e:
        print(f"❌ 推送模块错误: {e}")
        return False


def main():
    """主函数"""
    print("="*50)
    print("投资顾问系统 - 自动测试")
    print("="*50)
    
    tests = [
        ("配置文件", test_config),
        ("依赖包", test_dependencies),
        ("数据获取", test_data_fetcher),
        ("分析模块", test_analyzer),
        ("推送模块", test_notifier),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name}测试失败: {e}")
            results.append((name, False))
    
    # 总结
    print("\n" + "="*50)
    print("测试总结")
    print("="*50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    print(f"\n通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用")
        return 0
    else:
        print("\n⚠️ 部分测试失败，请检查配置或网络连接")
        return 1


if __name__ == '__main__':
    sys.exit(main())
