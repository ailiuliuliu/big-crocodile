# 🚀 AI驱动投资顾问系统 - 配置指南

## 📋 系统架构

```
用户截图 → GPT-4 Vision OCR识别 → 真实基金数据API → GPT-4深度分析 → 智能投资建议
```

## 🔧 配置步骤

### 第一步：获取OpenAI API Key

1. 访问 [OpenAI Platform](https://platform.openai.com/api-keys)
2. 注册/登录账号
3. 创建新的API Key（格式：`sk-proj-...` 或 `sk-...`）
4. 复制API Key（只会显示一次！）

**费用说明：**
- GPT-4o：$2.50 / 1M input tokens，$10.00 / 1M output tokens
- 每次分析约消耗 2000 tokens，成本约 ¥0.10元/次
- 建议充值 $5-10 即可使用很久

### 第二步：配置 API Key

编辑 `investment-advisor/config.yaml`：

```yaml
openai:
  api_key: "sk-proj-xxxxx"  # 填入你的API Key
  model: "gpt-4o"            # 推荐gpt-4o，性价比高
  base_url: "https://api.openai.com/v1"
  max_tokens: 4000
  temperature: 0.7
```

**注意：**
- 如果你的网络访问不了OpenAI，可以配置代理或使用国内中转服务
- 修改 `base_url` 为中转API地址即可

### 第三步：安装依赖

```bash
cd investment-advisor
pip3 install -r requirements.txt
```

主要依赖：
- `openai` - OpenAI官方SDK
- `flask` - Web API服务
- `flask-cors` - 跨域支持
- `requests` - HTTP请求
- `pyyaml` - 配置文件解析

### 第四步：启动服务

```bash
# 方式1：使用新的API服务器（推荐）
python3 api_server.py

# 方式2：使用旧的OCR服务（仅OCR）
python3 ocr_service.py server
```

**启动成功标志：**
```
🚀 投资顾问API服务启动
📍 访问地址: http://localhost:5001
✅ OpenAI API已配置
   模型: gpt-4o
   OCR: GPT-4 Vision
   分析: GPT-4 AI
```

### 第五步：打开网页测试

```bash
cd web
open index.html
```

## 🧪 测试流程

### 测试1：检查配置

访问：http://localhost:5001/api/config/check

预期返回：
```json
{
  "openai_configured": true,
  "openai_model": "gpt-4o",
  "ocr_mode": "GPT-4 Vision",
  "analysis_mode": "GPT-4 AI",
  "message": "OpenAI API已配置，使用真实AI分析"
}
```

### 测试2：OCR识别

1. 打开网页
2. 点击"📷 截图上传"标签
3. 上传支付宝持仓截图
4. 点击"🤖 AI识别持仓"
5. 等待识别完成

**预期结果：**
- 识别出所有基金名称、代码、金额
- 自动填充到JSON输入框
- 显示"✅ 识别成功！共识别到 X 只基金"

### 测试3：AI分析

1. 点击"🚀 开始分析"按钮
2. 等待AI分析（5-10秒）
3. 查看智能建议

**预期结果：**
- 显示组合概览（总值、成本、收益、收益率）
- 显示智能建议（止损、止盈、加仓、持有等）
- 建议包含具体理由、操作金额、风险提示
- 显示市场分析（行业趋势、宏观环境）

### 测试4：真实基金数据

在Python中测试：

```bash
python3 real_fund_api.py
```

预期输出：
```json
{
  "fund_code": "004851",
  "fund_name": "广发医疗保健股票A",
  "confirmed_nav": 1.2345,
  "estimated_change": -2.5,
  ...
}
```

## 🔍 功能对比

| 功能 | 未配置API（模拟模式） | 配置API（AI模式） |
|------|---------------------|-----------------|
| OCR识别 | ❌ 返回固定示例数据 | ✅ 真实识别截图内容 |
| 基金数据 | ❌ 静态数据 | ✅ 实时净值、历史表现 |
| 投资分析 | ⚠️ if-else规则引擎 | ✅ GPT-4深度分析 |
| 建议质量 | ⚠️ 简单规则匹配 | ✅ 结合市场趋势、行业逻辑 |
| 加仓机会 | ⚠️ 固定阈值判断 | ✅ 主动识别超跌反弹、仓位优化 |
| 市场分析 | ❌ 无 | ✅ 宏观环境、行业景气度分析 |

## ⚠️ 常见问题

### Q1: API Key无效
```
Error: Invalid API Key
```

**解决方法：**
1. 检查API Key是否正确复制（没有多余空格）
2. 确认API Key已激活（需要绑定信用卡）
3. 检查账户余额是否充足

### Q2: 网络连接失败
```
Error: Connection timeout
```

**解决方法：**
1. 检查网络是否能访问OpenAI
2. 配置代理：
   ```bash
   export HTTP_PROXY=http://127.0.0.1:7890
   export HTTPS_PROXY=http://127.0.0.1:7890
   ```
3. 或使用国内中转服务（修改base_url）

### Q3: 识别结果不准确

**优化方法：**
1. 确保截图清晰（不要有遮挡）
2. 截图只包含持仓列表部分
3. 避免截图中有重复内容
4. 可以在prompt中增加约束条件

### Q4: 分析速度慢

**原因：**
- GPT-4需要5-10秒处理时间
- 网络延迟

**优化：**
- 使用 `gpt-4o-mini`（更快但质量略低）
- 减少 `max_tokens` 参数
- 使用国内中转加速

## 🎯 下一步优化

### 已完成 ✅
- [x] GPT-4 Vision OCR识别
- [x] 真实基金数据API集成
- [x] GPT-4深度投资分析
- [x] 智能建议生成
- [x] 市场环境分析

### 可以继续优化 🚀
- [ ] 增加基金经理信息
- [ ] 历史收益曲线图表（ECharts）
- [ ] 每日自动推送（定时任务）
- [ ] 多用户系统（用户登录）
- [ ] 持仓历史记录
- [ ] 回测功能（验证建议准确性）
- [ ] 移动端适配优化

## 📞 技术支持

如果遇到问题：
1. 查看终端日志输出
2. 检查 `logs/advisor.log` 文件
3. 访问 http://localhost:5001/api/health 检查服务状态

---

**祝你投资顺利！📈**
