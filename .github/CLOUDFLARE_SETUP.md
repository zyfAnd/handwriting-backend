# GitHub Actions + Cloudflare 自动部署设置

本文档说明如何设置 GitHub Actions 自动部署到 Cloudflare。

## 📋 概述

当你推送代码到 GitHub 的 `main` 分支时，会自动触发部署到 Cloudflare Workers。

## 🔑 步骤 1: 获取 Cloudflare 凭证

### 1.1 获取 Account ID

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 在右侧边栏找到 **Account ID**
3. 点击复制
4. 保存这个 ID（类似: `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6`）

### 1.2 创建 API Token

1. 访问 [API Tokens 页面](https://dash.cloudflare.com/profile/api-tokens)
2. 点击 **"Create Token"**
3. 选择 **"Edit Cloudflare Workers"** 模板
4. 或者自定义权限:
   ```
   Account - Workers Scripts - Edit
   Account - Workers KV Storage - Edit
   Account - Account Settings - Read
   Account - R2 - Edit
   ```
5. 点击 **"Continue to summary"**
6. 点击 **"Create Token"**
7. **复制并保存** 这个 Token（只显示一次！）

## 🔐 步骤 2: 配置 GitHub Secrets

### 2.1 在 GitHub 仓库中添加 Secrets

1. 进入你的 GitHub 仓库
2. 点击 **Settings** → **Secrets and variables** → **Actions**
3. 点击 **"New repository secret"**
4. 添加以下两个 secrets:

#### Secret 1: CLOUDFLARE_ACCOUNT_ID
- **Name**: `CLOUDFLARE_ACCOUNT_ID`
- **Value**: 你的 Cloudflare Account ID
- 点击 **"Add secret"**

#### Secret 2: CLOUDFLARE_API_TOKEN
- **Name**: `CLOUDFLARE_API_TOKEN`
- **Value**: 你的 Cloudflare API Token
- 点击 **"Add secret"**

### 2.2 验证 Secrets

确保你添加了这两个 secrets:
- ✅ `CLOUDFLARE_ACCOUNT_ID`
- ✅ `CLOUDFLARE_API_TOKEN`

## 🚀 步骤 3: 首次部署

### 3.1 创建 Cloudflare 资源

在自动部署之前，需要手动创建一次资源：

```bash
# 登录 Cloudflare
wrangler login

# 创建 R2 Bucket
wrangler r2 bucket create handwriting-characters

# 创建 KV Namespace
wrangler kv:namespace create "CHAR_MAPPING"

# 记录输出的 KV Namespace ID，更新到 wrangler.toml
```

### 3.2 更新 wrangler.toml

编辑 `handwriting-api-worker/wrangler.toml`，填入 KV Namespace ID:

```toml
[[kv_namespaces]]
binding = "CHAR_MAPPING"
id = "你的KV_ID"  # 替换为实际 ID
```

提交这个修改:

```bash
git add handwriting-api-worker/wrangler.toml
git commit -m "Update KV namespace ID"
git push
```

### 3.3 上传初始数据

首次部署需要手动上传数据（或使用 GitHub Actions 手动触发）：

#### 方式 A: 本地上传

```bash
cd handwriting-api-worker
python3 upload-data.py
```

#### 方式 B: GitHub Actions 上传

1. 进入 GitHub 仓库
2. 点击 **Actions**
3. 选择 **"Upload Data to Cloudflare"**
4. 点击 **"Run workflow"**
5. 点击 **"Run workflow"** 确认

## 🔄 步骤 4: 自动部署流程

现在每次你推送代码到 `main` 分支，都会自动部署！

### 触发自动部署

```bash
# 修改代码
vim handwriting-api-worker/src/index.js

# 提交并推送
git add .
git commit -m "Update API code"
git push origin main
```

### 查看部署状态

1. 进入 GitHub 仓库
2. 点击 **Actions** 标签
3. 查看最新的 workflow 运行
4. 点击进去查看详细日志

## 📊 可用的 Workflows

### 1. Deploy to Cloudflare (自动)

**触发条件**:
- 推送到 `main` 分支
- 修改了 `handwriting-api-worker/` 下的文件

**功能**:
- 自动部署 Worker 到 Cloudflare
- 更新 API 代码

### 2. Upload Data to Cloudflare (手动)

**触发方式**:
- GitHub → Actions → "Upload Data to Cloudflare" → Run workflow

**功能**:
- 上传图片到 R2
- 更新字符映射到 KV
- 可选择只上传 R2 或只更新 KV

## 🛠️ 高级配置

### 添加环境

可以在 `wrangler.toml` 中配置多个环境：

```toml
# 生产环境
[env.production]
name = "handwriting-api-prod"
vars = { R2_PUBLIC_DOMAIN = "cdn.yourdomain.com" }

# 开发环境
[env.development]
name = "handwriting-api-dev"
vars = { R2_PUBLIC_DOMAIN = "handwriting-characters-dev.r2.dev" }
```

然后修改 workflow 文件，根据分支部署到不同环境。

### 添加测试步骤

在 `.github/workflows/deploy.yml` 中添加测试：

```yaml
- name: Run tests
  working-directory: handwriting-api-worker
  run: npm test

- name: Deploy only if tests pass
  if: success()
  uses: cloudflare/wrangler-action@v3
  ...
```

## 🐛 故障排查

### 问题 1: Deployment failed - Authentication error

**原因**: Cloudflare API Token 无效或权限不足

**解决**:
1. 检查 GitHub Secrets 中的 `CLOUDFLARE_API_TOKEN`
2. 重新创建 API Token
3. 确保 Token 有正确的权限

### 问题 2: KV Namespace not found

**原因**: wrangler.toml 中的 KV ID 不正确

**解决**:
1. 运行 `wrangler kv:namespace list`
2. 更新 wrangler.toml 中的 ID
3. 推送更新

### 问题 3: R2 Bucket not found

**原因**: R2 Bucket 未创建

**解决**:
```bash
wrangler r2 bucket create handwriting-characters
```

### 问题 4: Upload data failed

**原因**: 数据目录为空或文件不存在

**解决**:
1. 确保 `data-collection/collected_characters/` 有 PNG 文件
2. 本地先运行 `python3 upload-data.py` 测试

## 📚 参考资源

- [GitHub Actions 文档](https://docs.github.com/en/actions)
- [Cloudflare Workers Actions](https://github.com/cloudflare/wrangler-action)
- [Wrangler 配置](https://developers.cloudflare.com/workers/wrangler/configuration/)

## ✅ 检查清单

部署前确认：

- [ ] 获取了 Cloudflare Account ID
- [ ] 创建了 Cloudflare API Token
- [ ] 在 GitHub 添加了两个 Secrets
- [ ] 创建了 R2 Bucket
- [ ] 创建了 KV Namespace
- [ ] 更新了 wrangler.toml 中的 KV ID
- [ ] 上传了初始数据

全部完成后，就可以享受自动部署了！🚀
