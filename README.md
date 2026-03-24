# 投资顾问系统 - 使用文档

## 📚 系统简介

这是一个**全自动的投资组合分析系统**，每天中午12点自动分析你的基金持仓，结合最新市场信息生成调仓建议，并推送到你的微信。

### 核心功能

✅ 每日定时分析持仓（避免短期操作的手续费陷阱）  
✅ 自动止损/止盈提醒（基于收益率和持有天数）  
✅ 组合风险评估（仓位过高、过度集中等）  
✅ 微信推送报告（Server酱或企业微信）  
✅ 紧急情况预警（单日波动超过阈值）

---

## 🚀 快速开始

### 第一步：安装依赖

```bash
cd ~/Documents/金融大鳄/investment-advisor
pip3 install -r requirements.txt
```

或者使用国内镜像加速：

```bash
pip3 install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

---

### 第二步：配置Server酱（推送到微信）

#### 2.1 注册Server酱

1. 访问 https://sct.ftqq.com/
2. 使用微信扫码登录
3. 扫码关注"Server酱"公众号
4. 在网站上获取你的 **SendKey**（类似 `SCT12345xxxxx`）

#### 2.2 配置SendKey

编辑 `config.yaml` 文件：

```yaml
serverchan:
  enabled: true
  sendkey: "SCT12345xxxxx"  # 替换成你的真实SendKey
```

---

### 第三步：配置持仓信息

编辑 `config.yaml` 文件中的 `holdings` 部分：

```yaml
holdings:
  - name: "广发医疗保健股票A"
    code: "004851"
    amount: 9681  # 当前持有金额
    return_rate: -30.8  # 当前收益率
    buy_date: "2023-06-15"  # 买入日期（可选）
```

**注意事项：**
- `amount` 是当前的持有金额（元），不是成本
- `return_rate` 是当前的收益率（%），负数表示亏损
- `buy_date` 用于计算持有天数，影响赎回费率

---

### 第四步：测试运行

手动运行一次，检查是否正常：

```bash
cd ~/Documents/金融大鳄/investment-advisor
python3 advisor.py
```

如果一切正常，你的微信应该会收到一条推送消息！

---

### 第五步：配置定时任务

#### macOS 使用 launchd（推荐）

1. 创建 plist 文件：

```bash
cat > ~/Library/LaunchAgents/com.investment.advisor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.investment.advisor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/litianyu6/Documents/金融大鳄/investment-advisor/advisor.py</string>
    </array>
    
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>12</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    
    <key>StandardOutPath</key>
    <string>/Users/litianyu6/Documents/金融大鳄/investment-advisor/logs/launchd.out.log</string>
    
    <key>StandardErrorPath</key>
    <string>/Users/litianyu6/Documents/金融大鳄/investment-advisor/logs/launchd.err.log</string>
    
    <key>WorkingDirectory</key>
    <string>/Users/litianyu6/Documents/金融大鳄/investment-advisor</string>
</dict>
</plist>
EOF
```

2. 加载定时任务：

```bash
launchctl load ~/Library/LaunchAgents/com.investment.advisor.plist
```

3. 验证任务状态：

```bash
launchctl list | grep investment
```

如果看到 `com.investment.advisor`，说明配置成功！

---

## 📊 报告示例

```
📊 投资组合分析报告
⏰ 2026年03月20日 星期五 午间分析

========================================
💼 组合概览
========================================
持仓总值：¥32,251.00
持仓成本：¥28,500.00
总收益率：+13.17%
基金数量：5只

========================================
📈 持仓明细
========================================

💎 信澳新能源产业股票A
   持仓：¥7,097.00
   收益：+47.00%
   持有：210天
   今日：-2.96%

🟠 广发医疗保健股票A
   持仓：¥9,681.00
   收益：-30.80%
   持有：310天
   今日：-1.37%

========================================
⚠️ 风险提示
========================================
⚠️ 广发医疗保健股票A深度亏损（-30.8%），建议关注止损

========================================
💡 调仓建议
========================================

1. 🔴 【止损】广发医疗保健股票A
   原因：深度亏损-30.8%
   建议：建议减仓50%或全部清仓
   成本：赎回费0.00%

========================================
📌 温馨提示
========================================
• 本建议仅供参考，不构成投资建议
• 请根据自身风险承受能力决策
• 投资有风险，入市需谨慎
```

---

## ⚙️ 配置说明

### 交易规则配置

```yaml
trading_rules:
  min_trade_amount: 1000  # 最小交易金额（元），低于此值不建议操作
  min_return_threshold: 5  # 最小调仓收益阈值（%）
  short_term_days: 7  # 短期持有天数，少于此天数不建议卖出（避免高额赎回费）
  emergency_threshold: 10  # 紧急提醒阈值（单日跌幅%）
  max_position_ratio: 30  # 单一标的最大仓位（%）
```

### 赎回费率说明

| 持有天数 | 赎回费率 |
|---------|---------|
| < 7天 | 1.5% |
| 7-30天 | 0.5% |
| 30-365天 | 0.5% |
| 365-730天 | 0% |
| > 730天 | 0% |

**系统会自动计算赎回费，避免不划算的操作！**

---

## 🔧 维护指南

### 更新持仓信息

每次买入/卖出后，手动更新 `config.yaml` 中的持仓信息：

```bash
nano config.yaml
# 修改 holdings 部分
# 保存退出（Ctrl+X, Y, Enter）
```

### 查看日志

```bash
tail -f ~/Documents/金融大鳄/investment-advisor/logs/advisor.log
```

### 停止定时任务

```bash
launchctl unload ~/Library/LaunchAgents/com.investment.advisor.plist
```

### 重新启动定时任务

```bash
launchctl unload ~/Library/LaunchAgents/com.investment.advisor.plist
launchctl load ~/Library/LaunchAgents/com.investment.advisor.plist
```

---

## 🐛 故障排查

### 问题1：没有收到微信推送

**检查步骤：**
1. 确认 `config.yaml` 中的 `sendkey` 已正确配置
2. 手动运行 `python3 advisor.py` 查看错误信息
3. 检查是否关注了"Server酱"公众号
4. 查看日志文件 `logs/advisor.log`

### 问题2：定时任务没有执行

**检查步骤：**
1. 验证 launchd 状态：`launchctl list | grep investment`
2. 查看 launchd 日志：`cat logs/launchd.err.log`
3. 确认 Python 路径：`which python3`
4. 手动运行测试：`python3 advisor.py`

### 问题3：数据获取失败

**可能原因：**
- 网络问题（防火墙、代理）
- 数据源API变更
- 基金代码错误

**解决方法：**
- 检查网络连接
- 查看日志中的详细错误信息
- 确认基金代码是否正确（6位数字）

---

## 📝 常见问题

**Q: 可以修改分析时间吗？**  
A: 可以！编辑 `~/Library/LaunchAgents/com.investment.advisor.plist`，修改 `Hour` 和 `Minute` 的值。

**Q: 可以添加更多基金吗？**  
A: 可以！在 `config.yaml` 的 `holdings` 部分添加新的基金信息即可。

**Q: 系统会自动交易吗？**  
A: **不会**！系统只提供分析和建议，所有交易操作需要你手动执行。

**Q: 可以接入其他推送渠道吗？**  
A: 可以！除了Server酱，还支持企业微信Webhook。你也可以修改 `notifier.py` 添加其他渠道（如Telegram、钉钉等）。

**Q: 数据准确吗？**  
A: 基金净值数据来自天天基金网（实时估值），可能有15-20分钟延迟。收益率需要你在 `config.yaml` 中手动更新。

---

## 🎯 进阶功能（待开发）

- [ ] 接入OpenAI API进行智能分析
- [ ] 自动从支付宝拉取持仓数据
- [ ] 回测历史建议的准确率
- [ ] Web界面查看历史报告
- [ ] 多账户支持

---

## 📞 技术支持

如有问题，可以：
1. 查看日志文件 `logs/advisor.log`
2. 检查配置文件 `config.yaml`
3. 联系开发者（老李的AI助手）

---

**祝投资顺利！💰**
