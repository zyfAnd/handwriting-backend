# Token 和凭证获取指南

本文档说明连接 GitHub 和 Cloudflare 需要的所有 token 和凭证。

## 📋 需要的 Token 清单

### ✅ 必需的 Token

1. **GitHub Personal Access Token** (推送代码到 GitHub)
2. **Cloudflare Account ID** (部署 Worker)
3. **Cloudflare API Token** (自动化部署，可选)

### 🔹 可选的 Token

1. **CloudBrush API Token** (数据采集，如果使用 API 采集方式)

---

## 🔐 1. GitHub Personal Access Token

### 用途
- 推送代码到 GitHub 仓库
- GitHub Actions 自动部署（可选）

### 获取步骤

#### 方式 A: 通过 GitHub CLI (推荐)

```bash
# 安装 GitHub CLI
brew install gh

# 登录 GitHub
gh auth login

# 选择:
# - GitHub.com
# - HTTPS
# - Yes (authenticate Git)
# - Login with a web browser
```

#### 方式 B: 手动创建 Token

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 设置:
   - **Note**: `handwriting-backend-deploy`
   - **Expiration**: 90 days (或自定义)
   - **Scopes**: 勾选以下权限:
     - ✅ `repo` (完整仓库访问)
     - ✅ `workflow` (GitHub Actions，可选)
4. 点击 "Generate token"
5. **重要**: 复制并保存 token（只显示一次）

### 使用 Token

```bash
# 方式 1: 使用 GitHub CLI (推荐)
gh auth login

# 方式 2: 配置 Git
git config --global credential.helper store

# 首次推送时会要求输入用户名和 token
git push -u origin main
# Username: your-github-username
# Password: ghp_xxxxxxxxxxxxxxxxxxxx (粘贴你的 token)
```

---

## ☁️ 2. Cloudflare 凭证

### 用途
- 部署 Worker 到 Cloudflare
- 创建和管理 R2 Bucket
- 创建和管理 KV Namespace

### 获取步骤

#### 方式 A: OAuth 登录 (最简单，推荐)

```bash
# 安装 wrangler
npm install -g wrangler

# OAuth 登录
wrangler login

# 这会:
# 1. 打开浏览器
# 2. 要求你登录 Cloudflare
# 3. 授权 wrangler 访问你的账号
# 4. 自动保存凭证
```

**优点**:
- ✅ 最简单，不需要手动获取 token
- ✅ 自动管理凭证
- ✅ 推荐方式

#### 方式 B: API Token (用于 CI/CD 自动化)

如果需要在 CI/CD 中使用（如 GitHub Actions），需要创建 API Token:

1. **获取 Account ID**:
   - 登录 https://dash.cloudflare.com/
   - 右侧查看 "Account ID"
   - 复制保存

2. **创建 API Token**:
   - 访问 https://dash.cloudflare.com/profile/api-tokens
   - 点击 "Create Token"
   - 选择 "Edit Cloudflare Workers" 模板
   - 或者自定义权限:
     - ✅ Account - Workers Scripts - Edit
     - ✅ Account - Workers KV Storage - Edit
     - ✅ Account - R2 - Edit
   - 点击 "Continue to summary"
   - 点击 "Create Token"
   - **重要**: 复制并保存 token

3. **配置到 Wrangler**:

创建 `.env` 文件（已在 .gitignore 中，不会被提交）:

```bash
# handwriting-api-worker/.env
CLOUDFLARE_ACCOUNT_ID=your-account-id
CLOUDFLARE_API_TOKEN=your-api-token
```

或者使用环境变量:

```bash
export CLOUDFLARE_ACCOUNT_ID=your-account-id
export CLOUDFLARE_API_TOKEN=your-api-token
```

---

## 📱 3. CloudBrush API Token (可选)

### 用途
- 使用 API 方式采集汉字图片（推荐方式）
- 比 MIT 抓包更快更稳定

### 获取步骤

1. **安装 Charles Proxy** (macOS):
   ```bash
   brew install charles
   ```

2. **配置 iPhone 代理**:
   - iPhone 连接与 Mac 同一 WiFi
   - 设置 → Wi-Fi → (i) → 配置代理 → 手动
   - 服务器: 你的 Mac IP (如: 192.168.1.100)
   - 端口: 8888

3. **安装 Charles 证书**:
   - iPhone Safari 访问: `chls.pro/ssl`
   - 下载并安装证书
   - 设置 → 通用 → 关于本机 → 证书信任设置 → 启用证书

4. **抓包获取 Token**:
   - 打开 Charles
   - 打开 CloudBrush App
   - 搜索一个汉字
   - 在 Charles 中找到请求 `sfapi.fanglige.com`
   - 查看请求头中的 `Authorization` 或 `Token` 字段
   - 复制 token 值

5. **保存 Token**:
   ```bash
   # 保存到环境变量
   export CLOUDBRUSH_TOKEN='your-token-here'

   # 或保存到文件 (不要提交到 git)
   echo 'your-token-here' > data-collection/CLOUDBRUSH_TOKEN.txt
   ```

详细步骤: [data-collection/API_TOKEN_GUIDE.md](data-collection/API_TOKEN_GUIDE.md)

---

## 📝 Token 安全建议

### ✅ 好的做法

1. **永不提交到 Git**:
   - 使用 `.gitignore` 排除敏感文件
   - 使用环境变量存储 token

2. **定期轮换**:
   - GitHub Token: 建议 90 天轮换
   - Cloudflare Token: 建议 6 个月轮换
   - CloudBrush Token: 可能过期，需要重新获取

3. **最小权限原则**:
   - 只授予必要的权限
   - 不同用途使用不同的 token

4. **环境隔离**:
   - 开发环境和生产环境使用不同的 token
   - 使用 `.env.local` 存储本地 token

### ❌ 避免的做法

1. ❌ 在代码中硬编码 token
2. ❌ 提交 token 到 Git
3. ❌ 在公开渠道分享 token
4. ❌ 使用过期或泄露的 token

---

## 🔒 Token 存储位置

### 本地开发

```bash
# 方式 1: 环境变量 (推荐)
export CLOUDFLARE_API_TOKEN=xxx
export CLOUDBRUSH_TOKEN=xxx

# 方式 2: .env 文件 (已在 .gitignore)
# handwriting-api-worker/.env
CLOUDFLARE_ACCOUNT_ID=xxx
CLOUDFLARE_API_TOKEN=xxx
```

### GitHub Actions (CI/CD)

1. 进入 GitHub 仓库设置
2. Settings → Secrets and variables → Actions
3. 添加 Repository secrets:
   - `CLOUDFLARE_ACCOUNT_ID`
   - `CLOUDFLARE_API_TOKEN`

---

## 🚀 完整部署流程

有了这些 token 后，按以下步骤部署：

### 1. 推送到 GitHub

```bash
# 如果使用 GitHub CLI (推荐)
gh auth login
gh repo create handwriting-backend --public --source=. --remote=origin
git push -u origin main

# 如果手动创建
# 1. 在 GitHub 上创建新仓库 'handwriting-backend'
# 2. 添加远程仓库
git remote add origin https://github.com/your-username/handwriting-backend.git
git push -u origin main
```

### 2. 部署到 Cloudflare

```bash
cd handwriting-api-worker

# OAuth 登录 (推荐)
wrangler login

# 或使用 API Token
export CLOUDFLARE_API_TOKEN=xxx

# 一键部署
./deploy.sh
```

---

## 📞 获取帮助

### 遇到问题？

1. **GitHub 相关**:
   - [GitHub Token 文档](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token)
   - [GitHub CLI 文档](https://cli.github.com/manual/)

2. **Cloudflare 相关**:
   - [Wrangler 文档](https://developers.cloudflare.com/workers/wrangler/)
   - [API Token 文档](https://developers.cloudflare.com/fundamentals/api/get-started/create-token/)

3. **常见问题**:
   - 查看 [DEPLOYMENT_GUIDE.md#故障排查](DEPLOYMENT_GUIDE.md#故障排查)

---

## ✅ Token 检查清单

部署前确认：

- [ ] GitHub Token 已获取并配置
- [ ] Cloudflare 已登录 (`wrangler whoami`)
- [ ] CloudBrush Token 已获取（如果使用 API 采集）
- [ ] 所有 token 都未提交到 Git
- [ ] `.env` 文件已添加到 `.gitignore`

---

**🔐 记住**: Token 就像密码，永远不要分享或提交到代码仓库！
