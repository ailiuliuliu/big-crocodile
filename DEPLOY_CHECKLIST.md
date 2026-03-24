# 📋 GitHub Actions版部署检查清单

## ✅ 部署前检查

### 第一步：本地准备
- [ ] Python 3.9+ 已安装
- [ ] 运行 `pip install -r requirements.txt` 安装依赖
- [ ] 编辑 `data/holdings.json` 填入你的持仓数据
- [ ] （可选）本地测试：`python github_analyzer.py`

### 第二步：创建GitHub仓库
- [ ] 在GitHub创建新仓库 `investment-advisor`
- [ ] 仓库设为Public（Private也可，但Pages需要Pro账户）
- [ ] 不要勾选"Initialize with README"（我们已有文件）

### 第三步：推送代码到GitHub
```bash
cd investment-advisor
git init
git add .
git commit -m "Initial commit: AI投资顾问系统"
git branch -M main
git remote add origin https://github.com/<你的用户名>/investment-advisor.git
git push -u origin main
```

### 第四步：配置GitHub Secrets
进入仓库 **Settings** > **Secrets and variables** > **Actions**

添加Secrets：
- [ ] `OPENAI_API_KEY` = `sk-proj-xxxxx` (必需)
- [ ] `SERVERCHAN_KEY` = `SCTxxxxx` (可选，用于微信推送)

**获取OpenAI API Key：**
1. 访问 https://platform.openai.com/api-keys
2. 注册/登录
3. 创建API Key
4. 复制并保存（只显示一次）
5. 充值$5-10（首次使用）

### 第五步：启用GitHub Actions
- [ ] 进入 **Actions** 标签
- [ ] 如果提示"Workflows aren't being run"，点击"I understand my workflows, go ahead and enable them"

### 第六步：启用GitHub Pages
进入 **Settings** > **Pages**：
- [ ] **Source**: 选择 `gh-pages` 分支
- [ ] **Folder**: 选择 `/ (root)`
- [ ] 点击 **Save**

💡 **注意**：第一次需要先运行Actions生成 `gh-pages` 分支，如果没有此分支选项，先执行下一步

### 第七步：手动触发首次运行
- [ ] 进入 **Actions** 标签
- [ ] 选择 "每日投资分析" workflow
- [ ] 点击 **Run workflow** > **Run workflow**
- [ ] 等待执行完成（约2-3分钟）
- [ ] 检查是否成功（绿色✓）

### 第八步：验证GitHub Pages
- [ ] 返回 **Settings** > **Pages**
- [ ] 查看"Your site is published at"后面的网址
- [ ] 访问该网址，确认报告显示正常
- [ ] 网址格式：`https://<你的用户名>.github.io/investment-advisor/`

## ✅ 部署后验证

### 验证清单
- [ ] GitHub Actions每天自动运行
- [ ] 报告页面正常访问
- [ ] 报告数据更新（对比时间戳）
- [ ] 微信推送正常（如配置）
- [ ] 历史数据正常保存

### 查看日志
如果出现问题：
1. 进入 **Actions** 标签
2. 点击失败的workflow run
3. 展开各个步骤查看详细日志
4. 根据错误信息调试

## 🎯 日常使用

### 更新持仓数据
**方式1：GitHub网页编辑**
1. 进入 `data/holdings.json`
2. 点击编辑按钮✏️
3. 修改数据
4. 点击 "Commit changes"
5. 系统自动触发分析

**方式2：本地修改推送**
```bash
# 编辑 data/holdings.json
git add data/holdings.json
git commit -m "更新持仓数据"
git push
```

### 手动触发分析
- 进入 **Actions** > **每日投资分析**
- 点击 **Run workflow**
- 选择 `main` 分支
- 点击 **Run workflow**

### 修改定时时间
编辑 `.github/workflows/daily-analysis.yml`:
```yaml
schedule:
  - cron: '0 4 * * *'  # UTC 04:00 = 北京时间 12:00
```

改为其他时间：
```yaml
schedule:
  - cron: '0 0 * * *'  # UTC 00:00 = 北京时间 08:00
  - cron: '0 9 * * *'  # UTC 09:00 = 北京时间 17:00
```

## 🐛 常见问题

### Q1: Actions执行失败 "Invalid API Key"
- 检查Secrets中的 `OPENAI_API_KEY` 是否正确
- 确认OpenAI账户有余额
- 尝试重新生成API Key

### Q2: Pages显示404
- 等待3-5分钟让Pages部署
- 确认 `gh-pages` 分支已创建
- 确认Settings > Pages已正确配置

### Q3: 报告数据不更新
- 检查Actions是否正常运行
- 查看workflow日志排查错误
- 确认 `docs/latest.json` 已更新

### Q4: 微信推送未收到
- 检查 `SERVERCHAN_KEY` 是否正确配置
- 访问 https://sct.ftqq.com/ 确认账号正常
- 查看Actions日志中的推送状态

## 💰 费用预估

### GitHub Actions
- **免费额度**：2000分钟/月
- **单次消耗**：约2-3分钟
- **每日运行**：每天1次 = 月消耗90分钟
- **结论**：完全免费 ✅

### OpenAI API
- **GPT-4o定价**：
  - Input: $2.50 / 1M tokens
  - Output: $10.00 / 1M tokens
- **单次消耗**：约2000-3000 tokens
- **单次成本**：¥0.10-0.15元
- **每月成本**：约¥3-5元（每天1次）

### 总计
**每月约¥3-5元** 🎉

## 🎉 完成！

如果所有步骤都打✓，恭喜你成功部署了AI投资顾问系统！

**访问你的报告：**
```
https://<你的GitHub用户名>.github.io/investment-advisor/
```

**例如：**
```
https://litianyu03.github.io/investment-advisor/
```

---

📞 **需要帮助？** 查看 `DEPLOY_README.md` 或提Issue
