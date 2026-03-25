#!/bin/bash
# GitHub代码推送脚本

echo "🚀 准备推送代码到GitHub..."
echo "========================================"

# 检查是否在正确的目录
if [ ! -d ".git" ]; then
    echo "❌ 错误：当前不在Git仓库目录"
    echo "请先运行: cd ~/Documents/金融大鳄/investment-advisor"
    exit 1
fi

# 检查是否有提交
if ! git rev-parse HEAD > /dev/null 2>&1; then
    echo "❌ 错误：没有找到Git提交"
    exit 1
fi

# 设置远程仓库地址
echo ""
echo "📍 设置远程仓库地址..."
git remote set-url origin https://github.com/litianyu03/big-crocodile.git 2>/dev/null || \
git remote add origin https://github.com/litianyu03/big-crocodile.git

echo "✅ 远程仓库: https://github.com/litianyu03/big-crocodile.git"

# 推送代码
echo ""
echo "📤 开始推送代码..."
echo "========================================"
echo ""
echo "⚠️  注意："
echo "   如果提示输入用户名和密码："
echo "   • Username: litianyu03"
echo "   • Password: 使用Personal Access Token (不是GitHub密码)"
echo ""
echo "💡 如何获取Token："
echo "   1. 访问 https://github.com/settings/tokens"
echo "   2. 点击 Generate new token (classic)"
echo "   3. 勾选 repo 权限"
echo "   4. 生成后复制token（ghp_xxxx...）"
echo ""
echo "========================================"
echo ""

# 执行推送
git push -u origin main

# 检查结果
if [ $? -eq 0 ]; then
    echo ""
    echo "========================================"
    echo "✅ 推送成功！"
    echo ""
    echo "📍 仓库地址: https://github.com/litianyu03/big-crocodile"
    echo ""
    echo "🎯 下一步："
    echo "   1. 访问仓库 Settings > Secrets"
    echo "   2. 添加 OPENAI_API_KEY"
    echo "   3. 手动触发 Actions 运行"
    echo "   4. 启用 GitHub Pages"
    echo ""
    echo "📖 详细步骤请查看: DEPLOY_CHECKLIST.md"
    echo "========================================"
else
    echo ""
    echo "========================================"
    echo "❌ 推送失败"
    echo ""
    echo "常见问题："
    echo ""
    echo "1️⃣  如果提示 'Authentication failed':"
    echo "   → 密码必须使用Personal Access Token"
    echo "   → 不是GitHub账号密码"
    echo ""
    echo "2️⃣  如果提示 'Repository not found':"
    echo "   → 确认仓库名是 big-crocodile"
    echo "   → 确认仓库是Public（公开）"
    echo ""
    echo "3️⃣  如果提示 'Permission denied':"
    echo "   → 检查Token权限是否包含 repo"
    echo ""
    echo "💡 手动操作："
    echo "   git push -u origin main"
    echo ""
    echo "========================================"
    exit 1
fi
