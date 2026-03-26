# 🇨🇳 国内大模型配置指南

> 无需科学上网，免费额度充足，完全替代OpenAI

## 🎯 推荐方案对比

| 平台 | 模型 | 免费额度 | 价格 | 国内访问 | 推荐指数 |
|------|------|---------|------|---------|---------|
| **硅基流动** | DeepSeek-V3 | 40万tokens | ¥0.14/百万 | ✅ 极快 | ⭐⭐⭐⭐⭐ |
| 阿里云 | 通义千问Max | 100万tokens | ¥0.4/千tokens | ✅ 快 | ⭐⭐⭐⭐ |
| 腾讯云 | 混元 | 免费试用 | ¥0.45/千tokens | ✅ 快 | ⭐⭐⭐ |
| 百度 | 文心4.0 | 限时免费 | ¥1.2/千tokens | ✅ 快 | ⭐⭐⭐ |

**综合推荐：硅基流动（SiliconFlow）- 便宜、快速、免费额度多**

---

## 🚀 方案1：硅基流动（SiliconFlow）【推荐】

### 为什么推荐？
- ✅ **完全兼容OpenAI格式** - 无需改代码
- ✅ **国内极速访问** - 无需代理
- ✅ **超低价格** - DeepSeek-V3仅¥0.14/百万tokens（比GPT-4便宜50倍）
- ✅ **免费额度** - 注册送40万tokens
- ✅ **多模型选择** - DeepSeek、Qwen、GLM等

### 快速开始（3分钟）

#### 1️⃣ 注册账号

访问：**https://siliconflow.cn/**
- 点击右上角"登录/注册"
- 使用手机号注册（支持微信登录）
- 完成实名认证（可选，但建议做）

#### 2️⃣ 获取API Key

1. 登录后访问：https://cloud.siliconflow.cn/account/ak
2. 点击"创建新令牌"
3. 输入令牌名称（如：`big-crocodile`）
4. 点击"确定"
5. **立即复制API Key**（格式：`sk-xxxxxxxx`）

#### 3️⃣ 配置系统

编辑 `config.yaml`：

```yaml
openai:
  api_key: "sk-xxxxxxxx"  # 粘贴你的硅基流动API Key
  model: "deepseek-ai/DeepSeek-V3"  # 推荐DeepSeek-V3
  base_url: "https://api.siliconflow.cn/v1"
```

#### 4️⃣ 测试

```bash
cd investment-advisor
python3 ai_analyzer.py
```

看到"✅ 使用GPT-4进行投资分析"就成功了！

### 可用模型列表

| 模型 | 说明 | 价格（每百万tokens） | 推荐场景 |
|------|------|---------------------|---------|
| `deepseek-ai/DeepSeek-V3` | 性价比之王 | ¥0.14 | 日常分析（推荐） |
| `Qwen/Qwen2.5-72B-Instruct` | 阿里通义 | ¥0.36 | 复杂分析 |
| `01-ai/Yi-Lightning` | 零一万物 | ¥0.14 | 快速响应 |
| `Pro/deepseek-ai/DeepSeek-V3` | DeepSeek专业版 | ¥1.0 | 高质量分析 |

**推荐用 `deepseek-ai/DeepSeek-V3`** - 免费额度能用几百次！

---

## 🔧 方案2：阿里云通义千问

### 优势
- 阿里云官方
- 稳定可靠
- 100万tokens免费额度

### 配置步骤

#### 1️⃣ 开通服务

1. 访问：https://dashscope.aliyun.com/
2. 登录阿里云账号
3. 点击"开通DashScope"
4. 完成实名认证

#### 2️⃣ 获取API Key

1. 访问：https://dashscope.console.aliyun.com/apiKey
2. 点击"创建新的API-KEY"
3. 复制API Key（格式：`sk-xxxxxxxx`）

#### 3️⃣ 配置系统

```yaml
openai:
  api_key: "sk-xxxxxxxx"
  model: "qwen-max"  # 或 qwen-plus、qwen-turbo
  base_url: "https://dashscope.aliyuncs.com/compatible-mode/v1"
```

---

## 💰 成本对比（每月运行30次）

### 使用DeepSeek-V3（硅基流动）

- 单次消耗：约3000 tokens
- 月消耗：30次 × 3000 = 9万tokens = 0.09百万tokens
- **月成本**：¥0.09 × 0.14 = **¥0.01元**
- 免费额度：40万tokens能用400+次

### 使用GPT-4o（OpenAI）

- 单次消耗：约3000 tokens
- 月消耗：9万tokens
- **月成本**：约 **¥3-5元**

**国内模型便宜300倍！** 🎉

---

## 🔐 配置GitHub Secrets

无论用哪个方案，都需要配置Secrets：

1. 访问：https://github.com/ailiuliuliu/big-crocodile/settings/secrets/actions

2. 点击 **"New repository secret"**

3. 添加Secret：
   - **Name**: `OPENAI_API_KEY`
   - **Value**: 你的API Key（硅基流动或通义千问）

4. 点击 **"Add secret"**

**注意：** 虽然用的是国内模型，但Secret名称还是叫 `OPENAI_API_KEY`（因为代码兼容）

---

## 🧪 测试验证

### 本地测试

```bash
cd investment-advisor

# 测试AI分析
python3 ai_analyzer.py

# 测试完整流程
python3 github_analyzer.py
```

### GitHub Actions测试

1. 访问：https://github.com/ailiuliuliu/big-crocodile/actions
2. 点击"每日投资分析" workflow
3. 点击"Run workflow"
4. 等待执行完成

---

## ❓ 常见问题

### Q1: API Key在哪里填？

**本地测试**：编辑 `config.yaml`

**GitHub Actions**：在GitHub仓库的 Settings > Secrets 中添加

### Q2: 报错"Invalid API Key"

- 检查API Key是否复制完整
- 检查base_url是否正确
- 硅基流动：`https://api.siliconflow.cn/v1`
- 通义千问：`https://dashscope.aliyuncs.com/compatible-mode/v1`

### Q3: 硅基流动免费额度用完了怎么办？

- 充值最低10元即可用几千次
- 或者换用通义千问（100万tokens免费）

### Q4: 能同时配置多个模型吗？

不能，一次只能用一个。但可以随时切换：
- 修改 `config.yaml` 中的 `model` 和 `base_url`
- 重新运行即可

---

## 📊 效果对比

### 使用规则引擎（if-else）

```
建议：止损
理由：亏损-35%
操作：减仓50%
```

### 使用DeepSeek-V3（AI）

```
建议：分批止损 + 仓位重配
理由：广发医疗当前-35.22%，处于历史底部区间。医疗板块近期受
集采政策影响严重，但长期成长逻辑未变。建议先止损50%控制风险，
剩余仓位等待反弹。同时增配黄金（+2000元至17%仓位），对冲系统
性风险。新能源板块+36%建议部分止盈（35%减仓），锁定利润后可
择机低位回补。

预期：降低组合波动率15%，优化夏普比率至0.8以上
```

**AI分析深度提升10倍！** 🚀

---

## 🎯 推荐配置（复制即用）

```yaml
# config.yaml - 硅基流动DeepSeek-V3（推荐）
openai:
  api_key: "你的硅基流动API_Key"
  model: "deepseek-ai/DeepSeek-V3"
  base_url: "https://api.siliconflow.cn/v1"
  max_tokens: 4000
  temperature: 0.7
```

---

## 📞 获取帮助

- 硅基流动文档：https://docs.siliconflow.cn/
- 通义千问文档：https://help.aliyun.com/zh/dashscope/

---

**立即开始 → 访问 https://siliconflow.cn/ 注册账号！** 🚀
