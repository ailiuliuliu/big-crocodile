#!/bin/bash
# 快速启动脚本

echo "🚀 投资顾问系统 - 快速启动"
echo "================================"

# 1. 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未安装Python3，请先安装"
    exit 1
fi

# 2. 检查依赖
echo "📦 检查依赖包..."
pip3 list | grep -q flask
if [ $? -ne 0 ]; then
    echo "📥 安装依赖包..."
    pip3 install -r requirements.txt
fi

# 3. 检查配置
echo "🔍 检查配置..."
if grep -q "YOUR_OPENAI_API_KEY_HERE" config.yaml || grep -q '""' config.yaml | grep -q "api_key"; then
    echo ""
    echo "⚠️  未配置OpenAI API Key"
    echo "   当前模式: 模拟识别 + 规则引擎"
    echo ""
    echo "💡 如需启用AI功能："
    echo "   1. 编辑 config.yaml"
    echo "   2. 填入 openai.api_key"
    echo "   3. 重新运行此脚本"
    echo ""
    read -p "按Enter继续使用模拟模式，或Ctrl+C退出去配置..."
else
    echo "✅ OpenAI API已配置"
fi

# 4. 启动服务
echo ""
echo "🚀 启动API服务器..."
echo "================================"
python3 api_server.py &
SERVER_PID=$!

# 等待服务启动
sleep 3

# 5. 打开浏览器
echo ""
echo "🌐 打开浏览器..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    open web/index.html
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open web/index.html
fi

echo ""
echo "================================"
echo "✅ 系统已启动！"
echo "📍 前端页面: web/index.html"
echo "📡 API地址: http://localhost:5001"
echo ""
echo "⏹  按 Ctrl+C 停止服务"
echo "================================"

# 等待用户中断
wait $SERVER_PID
