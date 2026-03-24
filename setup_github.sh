#!/bin/bash
# GitHub Actions版本初始化脚本

echo "🚀 投资顾问系统 - GitHub Actions版部署"
echo "=========================================="

# 检查是否在正确的目录
if [ ! -f "config.yaml" ]; then
    echo "❌ 请在investment-advisor目录下运行此脚本"
    exit 1
fi

# 1. 创建必要的目录
echo "📁 创建目录结构..."
mkdir -p data
mkdir -p docs/history
mkdir -p .github/workflows

# 2. 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未安装Python3，请先安装"
    exit 1
fi

# 3. 安装依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 4. 本地测试
echo ""
echo "🧪 测试基金数据API..."
python3 real_fund_api.py

if [ $? -ne 0 ]; then
    echo "⚠️  基金API测试失败，但可以继续"
fi

# 5. 配置Git
echo ""
echo "📝 配置提示："
echo ""
echo "1️⃣  更新持仓数据："
echo "   编辑 data/holdings.json"
echo ""
echo "2️⃣  配置OpenAI API Key："
echo "   方式A: 编辑 config.yaml（本地测试）"
echo "   方式B: GitHub Secrets（部署用）"
echo ""
echo "3️⃣  推送到GitHub："
echo "   git init"
echo "   git add ."
echo "   git commit -m 'Initial commit'"
echo "   git branch -M main"
echo "   git remote add origin <你的仓库地址>"
echo "   git push -u origin main"
echo ""
echo "4️⃣  启用GitHub Actions："
echo "   进入GitHub仓库 > Settings > Actions"
echo "   允许Actions运行"
echo ""
echo "5️⃣  配置GitHub Secrets："
echo "   Settings > Secrets and variables > Actions"
echo "   添加 OPENAI_API_KEY"
echo ""
echo "6️⃣  启用GitHub Pages："
echo "   Settings > Pages"
echo "   Source: gh-pages分支"
echo ""
echo "✅ 初始化完成！"
echo ""
echo "📖 详细说明请查看: DEPLOY_README.md"
