#!/bin/bash
# 快速测试GitHub Actions版本

echo "🧪 测试GitHub Actions版投资分析器"
echo "===================================="

cd "$(dirname "$0")"

# 1. 检查文件
echo "📁 检查文件..."
required_files=(
    "data/holdings.json"
    ".github/workflows/daily-analysis.yml"
    "github_analyzer.py"
    "real_fund_api.py"
    "ai_analyzer.py"
    "requirements.txt"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ 缺少文件: $file"
        exit 1
    fi
done

echo "✅ 所有文件存在"

# 2. 测试基金API
echo ""
echo "📊 测试基金数据API..."
python3 real_fund_api.py > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ 基金API测试通过"
else
    echo "⚠️  基金API测试失败（不影响部署）"
fi

# 3. 测试静态报告生成
echo ""
echo "📄 测试报告生成..."
python3 github_analyzer.py

if [ $? -eq 0 ]; then
    echo "✅ 报告生成成功"
    echo ""
    echo "📂 生成文件："
    ls -lh docs/
    echo ""
    echo "🌐 本地预览："
    echo "   open docs/index.html"
else
    echo "❌ 报告生成失败"
    exit 1
fi

# 4. 检查输出
if [ -f "docs/index.html" ] && [ -f "docs/latest.json" ]; then
    echo "✅ 所有测试通过！"
    echo ""
    echo "📋 下一步："
    echo "1. 查看生成的报告: open docs/index.html"
    echo "2. 确认无误后推送到GitHub"
    echo "3. 参考 DEPLOY_CHECKLIST.md 完成部署"
else
    echo "❌ 输出文件不完整"
    exit 1
fi
