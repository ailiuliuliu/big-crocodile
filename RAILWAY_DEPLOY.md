# 🚂 Railway部署指南 - 多用户投资分析平台

> 5分钟部署，免费使用，全球访问

## 📋 部署清单

### ✅ 已完成
- [x] Flask API服务（`api_server.py`）
- [x] 前端Web界面（`web/index.html`）
- [x] OCR识别服务（硅基流动GPT-4 Vision）
- [x] 实时基金数据API（天天基金）
- [x] AI投资分析（硅基流动DeepSeek-V3）
- [x] Railway部署配置（`Procfile` + `railway.json`）

### 🎯 待完成
- [ ] 连接GitHub到Railway
- [ ] 配置环境变量
- [ ] 验证线上服务

---

## 🚀 快速部署（3步完成）

### 第1步：推送代码到GitHub ✅

代码已推送到：`https://github.com/ailiuliuliu/big-crocodile`

### 第2步：连接Railway部署 ⏱️ 2分钟

#### 2.1 访问Railway
https://railway.app/

#### 2.2 登录/注册
- 使用GitHub账号登录（推荐）
- 或使用邮箱注册

#### 2.3 创建新项目
1. 点击 **"New Project"**
2. 选择 **"Deploy from GitHub repo"**
3. 搜索并选择 **`ailiuliuliu/big-crocodile`**
4. Railway会自动检测到：
   - ✅ Python项目
   - ✅ `Procfile`（启动命令）
   - ✅ `requirements.txt`（依赖列表）
   - ✅ `railway.json`（部署配置）

#### 2.4 自动部署
- Railway会自动开始构建和部署
- 构建时间：约2-3分钟
- 不需要任何额外配置！

### 第3步：配置环境变量 ⏱️ 1分钟

#### 3.1 进入项目设置
1. 点击你的项目
2. 进入 **"Variables"** 标签页

#### 3.2 添加环境变量
点击 **"New Variable"** 添加以下变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `OPENAI_API_KEY` | `sk-vtzvieqpnikmxalabgotxhvddoitjennxeqxzonrugljmugl` | 硅基流动API Key |
| `FLASK_ENV` | `production` | 生产环境模式 |

**重要**：添加变量后，Railway会自动重新部署服务。

#### 3.3 获取公网地址
1. 在项目设置中找到 **"Settings"** 标签页
2. 点击 **"Generate Domain"**
3. Railway会分配一个公网地址，例如：
   ```
   https://big-crocodile-production.up.railway.app
   ```
4. 复制这个地址，任何人都能访问！

---

## 🎉 部署完成！

### 访问你的平台
```
https://你的域名.up.railway.app
```

### 功能清单
✅ **上传截图** - 支持支付宝/微信基金持仓截图  
✅ **AI识别** - GPT-4 Vision自动识别持仓信息  
✅ **实时数据** - 获取最新基金净值和涨跌  
✅ **智能分析** - DeepSeek-V3深度分析市场趋势  
✅ **投资建议** - 专业的止盈止损和加仓建议  

---

## 🔧 Railway管理

### 查看日志
1. 进入项目
2. 点击 **"Deployments"**
3. 选择最新的部署
4. 查看实时日志

### 重新部署
- **方式1**：推送新代码到GitHub（自动触发）
- **方式2**：在Railway中点击 **"Redeploy"**

### 监控资源
- 点击 **"Metrics"** 查看：
  - CPU使用率
  - 内存使用
  - 网络流量
  - 请求次数

---

## 💰 费用说明

### Railway免费套餐
- ✅ **免费额度**：每月 $5 美元额度
- ✅ **足够使用**：约500小时运行时间
- ✅ **自动休眠**：无流量时自动休眠节省资源
- ✅ **自动唤醒**：有访问时自动唤醒（约10秒）

### 硅基流动费用
- ✅ **免费额度**：40万tokens
- ✅ **超出后**：¥0.14/百万tokens
- ✅ **预估使用**：每次分析约3000 tokens
- ✅ **免费可用**：约130次分析

**总成本**：完全免费（免费额度内）

---

## 🛠️ 故障排查

### 问题1：部署失败

**症状**：Railway显示 "Build Failed"

**排查步骤**：
1. 查看构建日志（Deployments > View Logs）
2. 检查是否是依赖安装失败
3. 确认 `requirements.txt` 格式正确

**解决方案**：
```bash
# 本地测试依赖安装
cd investment-advisor
pip install -r requirements.txt
```

### 问题2：服务无法访问

**症状**：访问域名返回502/503错误

**排查步骤**：
1. 查看服务状态（Deployments > 最新部署）
2. 查看运行日志是否有错误
3. 检查环境变量是否配置正确

**解决方案**：
- 确认 `OPENAI_API_KEY` 已设置
- 检查Railway是否在重新部署中
- 等待服务完全启动（约30秒）

### 问题3：AI分析失败

**症状**：上传截图后分析失败

**排查步骤**：
1. 检查浏览器控制台（F12）
2. 查看Railway日志
3. 确认API Key是否有效

**解决方案**：
```bash
# 测试硅基流动API Key
curl -X POST https://api.siliconflow.cn/v1/chat/completions \
  -H "Authorization: Bearer sk-vtzvieqpnikmxalabgotxhvddoitjennxeqxzonrugljmugl" \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-ai/DeepSeek-V3","messages":[{"role":"user","content":"测试"}],"max_tokens":10}'
```

### 问题4：OCR识别不准确

**症状**：识别的基金信息错误

**原因**：
- 截图不清晰
- 截图格式不支持
- 截图内容不完整

**解决方案**：
- 使用高清截图
- 确保包含基金代码、名称、金额
- 避免截图被压缩

---

## 🔒 安全建议

### API Key保护
- ✅ **使用环境变量**：不要在代码中硬编码
- ✅ **定期轮换**：每月更换一次API Key
- ✅ **监控使用**：在硅基流动控制台查看调用量

### 用户数据
- ✅ **不存储敏感信息**：持仓数据不落盘
- ✅ **HTTPS加密**：所有请求强制HTTPS
- ✅ **无用户认证**：匿名使用，无需登录

---

## 📊 监控和优化

### 性能监控
- 使用Railway Metrics查看：
  - 响应时间
  - 错误率
  - 并发用户数

### 优化建议
1. **开启缓存**：缓存基金数据（5分钟）
2. **限流保护**：防止API滥用
3. **图片压缩**：前端压缩后再上传

---

## 🎯 下一步

### 功能增强
- [ ] 添加历史记录功能
- [ ] 支持多个持仓对比
- [ ] 生成PDF分析报告
- [ ] 邮件通知功能

### 部署优化
- [ ] 配置自定义域名
- [ ] 添加CDN加速
- [ ] 集成错误监控（Sentry）

---

## 📞 获取帮助

- **Railway文档**：https://docs.railway.app/
- **硅基流动文档**：https://docs.siliconflow.cn/
- **Flask文档**：https://flask.palletsprojects.com/

---

**🎉 恭喜！你的多用户投资分析平台已上线！**

立即分享给朋友使用吧！ 🚀
