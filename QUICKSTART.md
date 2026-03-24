# 🚀 快速开始指南

## 5分钟快速部署

### 步骤1：运行配置向导（推荐）

```bash
cd ~/Documents/金融大鳄/investment-advisor
python3 setup_wizard.py
```

**配置向导会引导你完成：**
✅ Server酱推送配置  
✅ 用户信息设置  
✅ 持仓信息录入  

### 步骤2：安装系统

```bash
./install.sh
```

**安装脚本会自动：**
✅ 安装Python依赖  
✅ 测试系统运行  
✅ 配置定时任务  
✅ 发送测试消息到微信  

### 步骤3：完成！

系统已经开始工作，每天中午12点会自动：
1. 分析你的持仓
2. 生成调仓建议
3. 推送到你的微信

---

## 手动配置（如果不想用向导）

### 1. 安装依赖

```bash
cd ~/Documents/金融大鳄/investment-advisor
pip3 install -r requirements.txt
```

### 2. 获取Server酱SendKey

1. 访问 https://sct.ftqq.com/
2. 微信扫码登录
3. 关注"Server酱"公众号
4. 复制SendKey

### 3. 编辑配置文件

```bash
nano config.yaml
```

修改以下部分：

```yaml
# 推送配置
serverchan:
  enabled: true
  sendkey: "粘贴你的SendKey"  # ← 这里

# 持仓信息
holdings:
  - name: "你的基金名称"
    code: "基金代码"  # 6位数字
    amount: 10000  # 持有金额
    return_rate: 10.0  # 收益率%
    buy_date: "2024-01-01"  # 买入日期
```

保存：`Ctrl+X` → `Y` → `Enter`

### 4. 测试运行

```bash
python3 advisor.py
```

如果一切正常，你的微信会收到推送！

### 5. 安装定时任务

```bash
./install.sh
```

---

## 常用命令

```bash
# 手动运行一次
python3 advisor.py

# 查看日志
tail -f logs/advisor.log

# 运行测试
python3 test.py

# 重启定时任务
launchctl unload ~/Library/LaunchAgents/com.investment.advisor.plist
launchctl load ~/Library/LaunchAgents/com.investment.advisor.plist

# 停止定时任务
launchctl unload ~/Library/LaunchAgents/com.investment.advisor.plist
```

---

## 故障排查

### 没收到微信推送？

1. 检查SendKey是否正确配置
2. 确认已关注"Server酱"公众号
3. 查看日志：`cat logs/advisor.log`
4. 手动测试：`python3 test.py`

### 定时任务没执行？

```bash
# 检查任务状态
launchctl list | grep investment

# 查看错误日志
cat logs/launchd.err.log

# 重新加载任务
launchctl unload ~/Library/LaunchAgents/com.investment.advisor.plist
launchctl load ~/Library/LaunchAgents/com.investment.advisor.plist
```

---

## 下一步

📖 阅读完整文档：[README.md](README.md)

💡 了解配置选项：[config.yaml](config.yaml)

🐛 运行测试：`python3 test.py`

---

**祝投资顺利！💰**
