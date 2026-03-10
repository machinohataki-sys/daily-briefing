# 📊 每日AI简报生成器

> 每天早上7:30自动发送经济+AI资讯简报到你的邮箱

## 功能特性

- 🕐 **定时推送**：每天北京时间7:30自动运行
- 📡 **多源聚合**：自动抓取财经、AI产品、AI研究等多个信息源
- 🤖 **AI分析**：使用GLM-5生成专业分析和预测
- 📧 **邮件推送**：精美HTML格式，支持Resend/SMTP
- 💰 **完全免费**：GitHub Actions + GLM免费额度 + Resend免费额度

## 信息源覆盖

| 分类 | 来源 |
|------|------|
| 宏观经济 | 财联社、华尔街见闻 |
| AI产品动态 | 36Kr、机器之心、The Verge |
| AI研究前沿 | arXiv CS.AI、arXiv CS.LG |

## 快速开始

### 1. Fork本仓库

点击右上角 Fork 按钮

### 2. 获取API Keys

**GLM API Key（必需）**
1. 访问 [智谱AI开放平台](https://open.bigmodel.cn/)
2. 注册并创建API Key
3. 免费额度足够日常使用

**邮件发送（二选一）**

方式A - Resend（推荐）：
1. 访问 [Resend](https://resend.com/)
2. 注册并创建API Key
3. 免费额度：100封/天

方式B - Gmail SMTP：
1. 开启Gmail的"两步验证"
2. 生成"应用专用密码"
3. 使用该密码作为SMTP_PASS

### 3. 配置GitHub Secrets

进入你fork的仓库 → Settings → Secrets and variables → Actions

添加以下Secrets：

| Secret名称 | 说明 |
|-----------|------|
| `GLM_API_KEY` | 智谱API Key |
| `RECIPIENT_EMAIL` | 你的收件邮箱 |
| `RESEND_API_KEY` | Resend API Key（方式A）|
| 或 `SMTP_USER` + `SMTP_PASS` | Gmail配置（方式B）|

### 4. 启用GitHub Actions

1. 进入 Actions 标签页
2. 点击 "I understand my workflows, go ahead and enable them"
3. 选择 "Daily AI Briefing" workflow
4. 点击 "Run workflow" 手动测试

### 5. 等待每日推送

配置完成！每天早上7:30你会收到简报邮件。

## 本地开发

```bash
# 克隆仓库
git clone https://github.com/your-username/daily-briefing.git
cd daily-briefing

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 填入你的配置

# 运行测试
python main.py
```

## 自定义配置

### 修改信息源

编辑 `sources.py` 中的 `RSS_SOURCES` 字典，添加或删除RSS源。

### 修改推送时间

编辑 `.github/workflows/daily-briefing.yml` 中的cron表达式：

```yaml
schedule:
  - cron: '30 23 * * *'  # UTC时间，+8小时=北京时间
```

### 修改AI提示词

编辑 `ai_processor.py` 中的 `SYSTEM_PROMPT` 变量。

## 项目结构

```
daily-briefing/
├── main.py              # 主程序入口
├── sources.py           # 信息源抓取
├── ai_processor.py      # AI处理（GLM-5）
├── email_sender.py      # 邮件发送
├── report_generator.py  # HTML报告生成
├── requirements.txt     # Python依赖
├── .env.example         # 环境变量示例
└── .github/
    └── workflows/
        └── daily-briefing.yml  # GitHub Actions配置
```

## 后续扩展（Phase 2-3）

- [ ] 添加PDF附件生成
- [ ] Web配置界面
- [ ] 自定义信息源管理
- [ ] 历史简报存档
- [ ] 多收件人支持

## License

MIT
