# 部署指南

完整的 Cloudflare Workers 部署步骤。

## 📋 部署检查清单

- [ ] Cloudflare 账号
- [ ] 已安装 Node.js 16+
- [ ] 已安装 Wrangler CLI
- [ ] 已采集汉字图片数据
- [ ] 已创建 R2 Bucket
- [ ] 已创建 KV Namespace

## 🚀 详细部署步骤

### 步骤 1: 安装 Wrangler CLI

```bash
# 使用 npm 全局安装
npm install -g wrangler

# 验证安装
wrangler --version
```

### 步骤 2: 登录 Cloudflare

```bash
# 启动 OAuth 登录流程
wrangler login

# 浏览器会打开授权页面
# 授权后返回终端
```

### 步骤 3: 创建 R2 Bucket

```bash
# 创建生产环境 Bucket
wrangler r2 bucket create handwriting-characters

# 查看已创建的 Bucket
wrangler r2 bucket list
```

**配置 R2 公开访问（可选）:**

1. 登录 Cloudflare Dashboard
2. 进入 R2 → handwriting-characters
3. 设置 → Public Access → Allow Access
4. 记录公开域名（如: handwriting-characters.r2.dev）

### 步骤 4: 创建 KV Namespace

```bash
# 创建生产环境 KV
wrangler kv:namespace create "CHAR_MAPPING"

# 输出示例:
# 🌀 Creating namespace with title "handwriting-api-CHAR_MAPPING"
# ✨ Success!
# Add the following to your configuration file in your kv_namespaces array:
# { binding = "CHAR_MAPPING", id = "abc123..." }

# 创建预览环境 KV（可选）
wrangler kv:namespace create "CHAR_MAPPING" --preview

# 输出示例:
# { binding = "CHAR_MAPPING", preview_id = "def456..." }
```

**重要**: 复制输出的 `id` 和 `preview_id`，将它们更新到 `wrangler.toml` 文件。

### 步骤 5: 更新 wrangler.toml

编辑 `wrangler.toml`，更新以下配置：

```toml
[[kv_namespaces]]
binding = "CHAR_MAPPING"
id = "abc123..."           # 替换为步骤4中的 id
preview_id = "def456..."   # 替换为步骤4中的 preview_id

[vars]
R2_PUBLIC_DOMAIN = "handwriting-characters.r2.dev"  # 替换为你的 R2 公开域名
```

### 步骤 6: 上传数据

#### 6.1 检查数据

```bash
# 确保数据目录存在
ls -l ../data-collection/collected_characters/

# 应该看到类似这样的输出:
# 6c34_水.png
# 706b_火.png
# char_url_mapping.json
```

#### 6.2 运行上传脚本

```bash
cd handwriting-api-worker

# 完整上传（R2 + KV）
python3 upload-data.py

# 或者分步上传
python3 upload-data.py --skip-kv  # 仅上传 R2
python3 upload-data.py --skip-r2  # 仅上传 KV
```

**上传过程示例:**

```
🚀 开始上传汉字手写体数据到 Cloudflare
======================================================================
✅ 已加载 24 个字符映射
✅ 构建了 24 个字符映射

📤 开始上传图片到 R2...
======================================================================
✅ 上传: 水 -> chars/6c34_水.png
✅ 上传: 火 -> chars/706b_火.png
...
======================================================================
✅ 上传完成: 24 成功, 0 失败

📤 上传字符映射到 KV...
✅ 字符映射已上传到 KV (共 24 个字符)

📊 上传报告
======================================================================
字符总数: 24
图片上传成功: 24
图片上传失败: 0
KV映射更新: 成功
报告文件: ../data-collection/collected_characters/upload_report.json
======================================================================

✨ 上传流程完成！
```

### 步骤 7: 部署 Worker

```bash
# 首次部署
wrangler deploy

# 输出示例:
# ⛅️ wrangler 3.x.x
# ------------------
# Uploading...
# ✨ Success! Uploaded 1 file (5.23 sec)
# Published handwriting-api (0.43 sec)
#   https://handwriting-api.<your-subdomain>.workers.dev
```

**记录 Worker URL**: `https://handwriting-api.<your-subdomain>.workers.dev`

### 步骤 8: 验证部署

#### 8.1 健康检查

```bash
curl https://handwriting-api.<your-subdomain>.workers.dev/api/health
```

**预期响应:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "1.0.0"
}
```

#### 8.2 统计信息

```bash
curl https://handwriting-api.<your-subdomain>.workers.dev/api/stats
```

**预期响应:**
```json
{
  "total_characters": 24,
  "api_version": "1.0.0",
  "endpoints": [
    "/api/search?q={query}",
    "/api/health",
    "/api/stats"
  ]
}
```

#### 8.3 搜索测试

```bash
curl "https://handwriting-api.<your-subdomain>.workers.dev/api/search?q=水"
```

**预期响应:**
```json
{
  "success": true,
  "query": "水",
  "results": [
    {
      "char": "水",
      "url": "https://handwriting-characters.r2.dev/chars/6c34_水.png",
      "unicode": "U+6C34",
      "filename": "6c34_水.png",
      "available": true,
      "metadata": {
        "size": 4567,
        "timestamp": "2024-01-01T00:00:00.000Z"
      }
    }
  ],
  "count": 1,
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

## 🔄 更新部署

### 更新代码

```bash
# 修改代码后重新部署
wrangler deploy
```

### 更新数据

```bash
# 重新上传图片
python3 upload-data.py

# 仅更新 KV 映射
python3 upload-data.py --skip-r2
```

### 更新 KV 数据

```bash
# 手动更新单个键值
wrangler kv:key put --binding=CHAR_MAPPING "char_mapping" \
  --path=../data-collection/collected_characters/char_url_mapping.json

# 列出 KV 中的键
wrangler kv:key list --binding=CHAR_MAPPING

# 获取 KV 值
wrangler kv:key get --binding=CHAR_MAPPING "char_mapping"
```

### 更新 R2 对象

```bash
# 上传单个文件到 R2
wrangler r2 object put handwriting-characters/chars/6c34_水.png \
  --file ../data-collection/collected_characters/6c34_水.png

# 列出 R2 对象
wrangler r2 object list handwriting-characters

# 删除 R2 对象
wrangler r2 object delete handwriting-characters/chars/6c34_水.png
```

## 🌍 配置自定义域名（可选）

### 步骤 1: 添加域名到 Cloudflare

1. 登录 Cloudflare Dashboard
2. 添加你的域名
3. 更新 DNS 记录到 Cloudflare

### 步骤 2: 为 Worker 配置路由

1. 进入 Workers & Pages
2. 选择 `handwriting-api`
3. Settings → Triggers → Add Custom Domain
4. 输入域名: `api.yourdomain.com`

### 步骤 3: 为 R2 配置自定义域名

1. 进入 R2 → handwriting-characters
2. Settings → Custom Domains
3. 添加域名: `cdn.yourdomain.com`

### 步骤 4: 更新配置

编辑 `wrangler.toml`:

```toml
[env.production]
name = "handwriting-api-prod"
vars = { R2_PUBLIC_DOMAIN = "cdn.yourdomain.com" }

routes = [
  { pattern = "api.yourdomain.com/*", zone_name = "yourdomain.com" }
]
```

重新部署:

```bash
wrangler deploy --env production
```

## 📊 监控和日志

### 实时日志

```bash
# 查看实时日志
wrangler tail

# 查看生产环境日志
wrangler tail --env production

# 过滤日志
wrangler tail --format pretty
```

### 查看部署列表

```bash
wrangler deployments list
```

### 查看使用统计

1. 登录 Cloudflare Dashboard
2. Workers & Pages → handwriting-api
3. Analytics → 查看请求统计

## 🐛 故障排查

### 常见问题

#### 1. KV 数据未找到

**问题**: 搜索返回空结果

**解决**:
```bash
# 检查 KV 数据
wrangler kv:key get --binding=CHAR_MAPPING "char_mapping"

# 重新上传
python3 upload-data.py --skip-r2
```

#### 2. R2 图片无法访问

**问题**: 图片 URL 返回 403

**解决**:
1. 检查 R2 Bucket 公开访问设置
2. 确认 R2_PUBLIC_DOMAIN 配置正确

#### 3. Worker 部署失败

**问题**: `wrangler deploy` 报错

**解决**:
```bash
# 检查 wrangler 版本
wrangler --version

# 更新 wrangler
npm install -g wrangler@latest

# 重新登录
wrangler logout
wrangler login
```

#### 4. 数据上传失败

**问题**: `upload-data.py` 报错

**解决**:
```bash
# 检查数据目录
ls ../data-collection/collected_characters/

# 确认 wrangler 已登录
wrangler whoami

# 分步上传
python3 upload-data.py --skip-kv  # 先上传 R2
python3 upload-data.py --skip-r2  # 再上传 KV
```

## 🔒 安全建议

1. **API Key 管理**: 不要将敏感信息提交到 Git
2. **速率限制**: 根据需求调整速率限制
3. **CORS 设置**: 在生产环境限制允许的源
4. **日志监控**: 定期查看日志检测异常

## 📚 参考资源

- [Cloudflare Workers 文档](https://developers.cloudflare.com/workers/)
- [Cloudflare R2 文档](https://developers.cloudflare.com/r2/)
- [Cloudflare KV 文档](https://developers.cloudflare.com/workers/runtime-apis/kv/)
- [Wrangler CLI 文档](https://developers.cloudflare.com/workers/wrangler/)
