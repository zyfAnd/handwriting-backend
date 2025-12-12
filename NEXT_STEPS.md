# 🚀 下一步：配置自动部署

代码已成功推送到 GitHub！现在需要配置 Cloudflare 凭证以启用自动部署。

**GitHub 仓库**: https://github.com/zyfAnd/handwriting-backend

---

## 📋 快速配置指南

### 方式 A: 使用配置脚本（推荐）

```bash
# 运行配置脚本
./SETUP_SECRETS.sh
```

脚本会引导你完成所有配置。

### 方式 B: 手动配置（3步）

#### 步骤 1: 获取 Cloudflare Account ID

访问 https://dash.cloudflare.com/，在右侧找到 **Account ID** 并复制。

#### 步骤 2: 创建 Cloudflare API Token

1. 访问 https://dash.cloudflare.com/profile/api-tokens
2. 点击 **"Create Token"**
3. 选择 **"Edit Cloudflare Workers"** 模板
4. 点击 **"Create Token"**
5. 复制并保存 Token

#### 步骤 3: 配置 GitHub Secrets

**方法 1: 使用 GitHub CLI（快）**

```bash
# 设置 Account ID
echo "你的Account_ID" | gh secret set CLOUDFLARE_ACCOUNT_ID

# 设置 API Token
echo "你的API_Token" | gh secret set CLOUDFLARE_API_TOKEN

# 验证
gh secret list
```

**方法 2: 通过网页（慢）**

1. 访问 https://github.com/zyfAnd/handwriting-backend/settings/secrets/actions
2. 点击 **"New repository secret"**
3. 添加两个 secrets:
   - Name: `CLOUDFLARE_ACCOUNT_ID`, Value: 你的 Account ID
   - Name: `CLOUDFLARE_API_TOKEN`, Value: 你的 API Token

---

## 🔧 步骤 4: 创建 Cloudflare 资源

需要手动创建一次（GitHub Actions 无法自动创建）：

```bash
# 如果 wrangler 有问题，先修复
npm install -g wrangler@latest

# 登录 Cloudflare
wrangler login

# 创建 R2 Bucket
wrangler r2 bucket create handwriting-characters

# 创建 KV Namespace
wrangler kv:namespace create "CHAR_MAPPING"
```

**重要**: 复制 KV Namespace ID 的输出，例如：
```
{ binding = "CHAR_MAPPING", id = "abc123..." }
```

---

## 📝 步骤 5: 更新配置文件

编辑 [handwriting-api-worker/wrangler.toml](handwriting-api-worker/wrangler.toml)，更新 KV ID:

```toml
[[kv_namespaces]]
binding = "CHAR_MAPPING"
id = "abc123..."  # 替换为你的 KV ID
```

提交并推送：

```bash
git add handwriting-api-worker/wrangler.toml
git commit -m "Update KV namespace ID"
git push
```

**这会自动触发部署！** 🚀

---

## 📤 步骤 6: 上传数据

数据上传有两种方式：

### 方式 A: GitHub Actions 手动触发

1. 访问 https://github.com/zyfAnd/handwriting-backend/actions
2. 选择 **"Upload Data to Cloudflare"**
3. 点击 **"Run workflow"**
4. 点击 **"Run workflow"** 确认

### 方式 B: 本地上传

```bash
cd handwriting-api-worker
python3 upload-data.py
```

---

## ✅ 验证部署

部署完成后，测试 API：

```bash
# 获取 Worker URL
# 查看 GitHub Actions 日志或 Cloudflare Dashboard

# 测试健康检查
curl https://handwriting-api.你的子域.workers.dev/api/health

# 测试搜索
curl "https://handwriting-api.你的子域.workers.dev/api/search?q=水"
```

---

## 📊 监控部署

### 查看 GitHub Actions

访问 https://github.com/zyfAnd/handwriting-backend/actions

每次推送到 `main` 分支都会自动触发部署。

### 查看 Cloudflare 日志

```bash
# 实时查看 Worker 日志
wrangler tail
```

---

## 🎯 完整流程总结

```bash
# 1. 配置 GitHub Secrets（一次性）
./SETUP_SECRETS.sh

# 2. 创建 Cloudflare 资源（一次性）
wrangler login
wrangler r2 bucket create handwriting-characters
wrangler kv:namespace create "CHAR_MAPPING"

# 3. 更新 wrangler.toml 并推送
vim handwriting-api-worker/wrangler.toml  # 更新 KV ID
git add .
git commit -m "Update KV namespace ID"
git push  # 自动部署！

# 4. 上传数据
# 方式 A: GitHub Actions (手动触发)
# 方式 B: python3 upload-data.py

# 5. 测试
curl https://handwriting-api.你的子域.workers.dev/api/health
```

---

## 🆘 遇到问题？

### Wrangler 安装问题

```bash
# 重新安装 wrangler
npm uninstall -g wrangler
npm install -g wrangler@latest
```

### GitHub Actions 失败

1. 检查 Secrets 是否正确配置
2. 查看 Actions 日志找到错误信息
3. 参考 [.github/CLOUDFLARE_SETUP.md](.github/CLOUDFLARE_SETUP.md)

### API 测试失败

1. 确保已创建 R2 Bucket 和 KV Namespace
2. 确保已上传数据
3. 检查 wrangler.toml 配置是否正确

---

## 📚 详细文档

- [Tokens 获取指南](TOKENS_GUIDE.md)
- [GitHub + Cloudflare 配置](.github/CLOUDFLARE_SETUP.md)
- [完整部署指南](DEPLOYMENT_GUIDE.md)

---

**准备好了？开始配置吧！** 🚀

如有任何问题，请查看文档或提交 Issue。
