#!/bin/bash

# 投资顾问系统 - 一键安装脚本

echo "========================================="
echo "投资顾问系统 - 自动安装脚本"
echo "========================================="
echo ""

# 检查Python3
echo "检查Python环境..."
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到Python3，请先安装Python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version)
echo "✅ 找到 $PYTHON_VERSION"
echo ""

# 安装依赖
echo "安装Python依赖..."
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
if [ $? -ne 0 ]; then
    echo "❌ 依赖安装失败"
    exit 1
fi
echo "✅ 依赖安装完成"
echo ""

# 获取Python3的完整路径
PYTHON_PATH=$(which python3)
echo "Python路径: $PYTHON_PATH"

# 获取当前目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo "项目目录: $SCRIPT_DIR"
echo ""

# 创建日志目录
mkdir -p "$SCRIPT_DIR/logs"
mkdir -p "$SCRIPT_DIR/data"

# 配置文件检查
echo "检查配置文件..."
if [ ! -f "$SCRIPT_DIR/config.yaml" ]; then
    echo "❌ 未找到config.yaml，请先创建配置文件"
    exit 1
fi

# 检查Server酱配置
SENDKEY=$(grep "sendkey:" "$SCRIPT_DIR/config.yaml" | awk '{print $2}' | tr -d '"')
if [ "$SENDKEY" == "YOUR_SENDKEY_HERE" ]; then
    echo "⚠️ 警告: Server酱SendKey未配置"
    echo "请访问 https://sct.ftqq.com/ 获取SendKey并配置到config.yaml"
    echo ""
    read -p "是否继续安装？(y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi
echo "✅ 配置文件检查完成"
echo ""

# 生成launchd配置文件
echo "生成定时任务配置..."
PLIST_PATH="$HOME/Library/LaunchAgents/com.investment.advisor.plist"

cat > "$PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.investment.advisor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$PYTHON_PATH</string>
        <string>$SCRIPT_DIR/advisor.py</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>12</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>$SCRIPT_DIR/logs/launchd.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>$SCRIPT_DIR/logs/launchd.err.log</string>
    
    <key>WorkingDirectory</key>
    <string>$SCRIPT_DIR</string>
    
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

echo "✅ 配置文件已生成: $PLIST_PATH"
echo ""

# 测试运行
echo "========================================="
echo "测试运行系统..."
echo "========================================="
python3 "$SCRIPT_DIR/advisor.py"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 测试运行成功！"
    echo ""
    
    # 加载定时任务
    echo "加载定时任务..."
    launchctl unload "$PLIST_PATH" 2>/dev/null
    launchctl load "$PLIST_PATH"
    
    if [ $? -eq 0 ]; then
        echo "✅ 定时任务已加载"
        echo ""
        echo "========================================="
        echo "🎉 安装完成！"
        echo "========================================="
        echo ""
        echo "系统将在每天中午12:00自动运行"
        echo "分析报告将推送到你的微信"
        echo ""
        echo "常用命令："
        echo "  查看日志: tail -f $SCRIPT_DIR/logs/advisor.log"
        echo "  手动运行: python3 $SCRIPT_DIR/advisor.py"
        echo "  停止任务: launchctl unload $PLIST_PATH"
        echo "  重启任务: launchctl unload $PLIST_PATH && launchctl load $PLIST_PATH"
        echo ""
        echo "配置文件: $SCRIPT_DIR/config.yaml"
        echo "详细文档: $SCRIPT_DIR/README.md"
        echo ""
    else
        echo "❌ 定时任务加载失败"
        echo "你可以手动加载: launchctl load $PLIST_PATH"
    fi
else
    echo ""
    echo "❌ 测试运行失败，请检查配置"
    echo "查看日志: cat $SCRIPT_DIR/logs/advisor.log"
fi
