# 📊 AI投资顾问系统 - GitHub Actions免费版

> 🤖 GPT-4驱动 · 每日自动分析 · 完全免费

## 🎯 核心特性

- ✅ **完全免费** - 基于GitHub Actions，无需服务器
- ✅ **每日自动更新** - 每天中午12点自动分析
- ✅ **AI深度分析** - GPT-4智能建议
- ✅ **实时基金数据** - 天天基金API
- ✅ **微信推送** - Server酱通知（可选）
- ✅ **历史归档** - 自动保存每日报告

## 🚀 快速部署（5分钟）

### 第一步：Fork本仓库

1. 点击右上角 **Fork** 按钮
2. 等待fork完成

### 第二步：配置GitHub Secrets

进入你fork的仓库 **Settings** > **Secrets and variables** > **Actions**

添加以下Secrets：

| Secret名称 | 说明 | 获取方式 |
|-----------|------|---------|
| `OPENAI_API_KEY` | OpenAI API密钥 | [获取地址](https://platform.openai.com/api-keys) |
| `SERVERCHAN_KEY` | Server酱推送密钥（可选） | [获取地址](https://sct.ftqq.com/) |

**OpenAI API Key获取：**
1. 注册 https://platform.openai.com
2. 创建API Key
3. 复制 `sk-proj-xxxxx` 或 `sk-xxxxx`
4. 粘贴到GitHub Secrets

### 第三步：更新持仓数据

编辑 `data/holdings.json`：

```json
[
  {
    "name": "广发医疗保健股票A",
    "code": "004851",
    "amount": 9069.40,
    "cost": 14000.00,
    "return_rate": -35.22
  }
]
```

**如何更新：**
- 在GitHub网页直接编辑
- 或本地修改后commit推送

### 第四步：启用GitHub Pages

1. 进入 **Settings** > **Pages**
2. **Source** 选择 `gh-pages` 分支
3. **Folder** 选择 `/ (root)`
4. 点击 **Save**

### 第五步：手动触发首次分析

1. 进入 **Actions** 标签
2. 选择 **每日投资分析** workflow
3. 点击 **Run workflow** > **Run workflow**
4. 等待执行完成（约2-3分钟）

### 第六步：访问报告

访问地址：
```
https://<你的GitHub用户名>.github.io/investment-advisor/
```

例如：
```
https://litianyu03.github.io/investment-advisor/
```

## 📅 自动化运行

### 定时任务

系统将在以下时间自动运行：
- 🕛 **每天中午12:00**（北京时间）

### 手动触发

任何时候都可以手动触发：
1. 进入 **Actions** 页面
2. 选择 **每日投资分析**
3. 点击 **Run workflow**

### 自动触发

当你更新 `data/holdings.json` 时，会自动触发分析

## 🔧 配置说明

### 修改定时时间

编辑 `.github/workflows/daily-analysis.yml`:

```yaml
schedule:
  - cron: '0 4 * * *'  # UTC 04:00 = 北京时间 12:00
```

改为：
```yaml
schedule:
  - cron: '0 0 * * *'  # 每天早上8点（北京时间）
  - cron: '0 9 * * *'  # 每天下午5点（北京时间）
```

### 微信推送配置（可选）

1. 注册Server酱：https://sct.ftqq.com/
2. 获取SendKey
3. 添加到GitHub Secrets（名称：`SERVERCHAN_KEY`）
4. 每次分析完成会自动推送

## 📊 功能说明

### 1. 持仓分析
- 实时净值更新
- 收益率计算
- 资产配置分析

### 2. 智能建议
- 🔴 止损建议（深度亏损）
- 💰 止盈建议（优秀收益）
- 📈 加仓机会（超跌反弹、仓位优化）
- ✋ 持有建议（正常波动）

### 3. 市场分析
- 宏观经济环境
- 行业景气度判断
- 未来趋势预判

### 4. 历史归档
- 每日报告自动保存在 `docs/history/`
- 可查看历史分析记录

## 💰 费用说明

### GitHub Actions

- 🎁 **免费额度**：2000分钟/月
- 📊 **实际消耗**：每次约2-3分钟
- 🔢 **可用次数**：约600次/月（每天20次）
- ✅ **个人使用完全免费**

### OpenAI API

- 💵 **GPT-4o费用**：
  - $2.50 / 1M input tokens
  - $10.00 / 1M output tokens
- 📊 **单次分析消耗**：约2000-3000 tokens
- 💰 **成本估算**：¥0.10-0.15元/次
- 📅 **每月成本**：约¥3-5元（每天1次）

**充值建议**：
- 首次充值 $5即可使用2-3个月
- 或按需充值$1-2测试

## 🛠️ 本地测试

### 安装依赖

```bash
cd investment-advisor
pip install -r requirements.txt
```

### 配置API Key

编辑 `config.yaml`:

```yaml
openai:
  api_key: "sk-proj-xxxxx"
```

### 运行测试

```bash
# 测试基金数据API
python real_fund_api.py

# 测试AI分析
python ai_analyzer.py

# 生成静态报告
python github_analyzer.py
```

## 📁 项目结构

```
investment-advisor/
├── .github/
│   └── workflows/
│       └── daily-analysis.yml    # GitHub Actions配置
├── data/
│   └── holdings.json              # 持仓数据（需手动更新）
├── docs/                          # 生成的静态报告（自动）
│   ├── index.html
│   ├── latest.json
│   └── history/                   # 历史归档
├── real_fund_api.py               # 真实基金数据API
├── ai_analyzer.py                 # AI分析引擎
├── github_analyzer.py             # GitHub版主程序
├── send_notification.py           # 微信推送
├── requirements.txt               # Python依赖
└── config.yaml                    # 配置文件
```

## 🔍 常见问题

### Q1: GitHub Actions执行失败

**原因**：可能是API Key未配置或无效

**解决**：
1. 检查Secrets是否正确添加
2. 查看Actions日志定位错误
3. 确认OpenAI账户有余额

### Q2: 报告访问404

**原因**：GitHub Pages未启用或分支错误

**解决**：
1. 确认Settings > Pages已启用
2. 确认选择了 `gh-pages` 分支
3. 等待3-5分钟让Pages部署

### Q3: 基金数据获取失败

**原因**：天天基金API限流或网络问题

**解决**：
- GitHub Actions会自动重试
- 手动重新运行workflow

### Q4: 如何更新持仓？

**两种方式：**

1. **网页编辑**（推荐）
   - 进入 `data/holdings.json`
   - 点击编辑按钮✏️
   - 修改后commit

2. **本地更新**
   ```bash
   git clone <你的仓库>
   # 编辑 data/holdings.json
   git add data/holdings.json
   git commit -m "更新持仓"
   git push
   ```

## 🎨 自定义

### 修改报告样式

编辑 `github_analyzer.py` 的HTML模板部分

### 添加更多分析维度

编辑 `ai_analyzer.py` 的prompt

### 修改推送格式

编辑 `send_notification.py`

## 📞 技术支持

如遇问题：
1. 查看GitHub Actions日志
2. 检查 `docs/latest.json` 是否生成
3. 提Issue到原仓库

## 📄 License

MIT License

---

**⭐ 如果觉得有用，请点个Star！**

**📊 示例报告：** https://litianyu03.github.io/investment-advisor/
