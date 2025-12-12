# 汉字手写体图片搜索 API

基于 Cloudflare Workers 的汉字手写体图片搜索服务。

## 📋 功能特性

- **快速搜索**: 通过汉字查询对应的手写体图片
- **全球 CDN**: 利用 Cloudflare 全球网络加速
- **无服务器**: 基于 Workers 平台，无需维护服务器
- **R2 存储**: 图片存储在 Cloudflare R2（兼容 S3）
- **KV 缓存**: 字符映射存储在 Workers KV
- **CORS 支持**: 支持跨域访问
- **速率限制**: 防止滥用

## 🏗️ 架构

```
┌─────────────┐
│   用户请求   │
└──────┬──────┘
       │
       ▼
┌─────────────────┐
│ Cloudflare Worker│  ← 处理 API 请求
└────┬───────┬────┘
     │       │
     │       ▼
     │   ┌──────┐
     │   │  KV  │  ← 存储字符映射
     │   └──────┘
     │
     ▼
  ┌──────┐
  │  R2  │  ← 存储图片文件
  └──────┘
```

## 🚀 快速开始

### 1. 前置要求

- Node.js 16+
- Cloudflare 账号
- Wrangler CLI

```bash
# 安装 Wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login
```

### 2. 安装依赖

```bash
cd handwriting-api-worker
npm install
```

### 3. 创建 Cloudflare 资源

```bash
# 创建 R2 Bucket
wrangler r2 bucket create handwriting-characters

# 创建 KV Namespace
wrangler kv:namespace create "CHAR_MAPPING"

# 创建预览 KV (可选)
wrangler kv:namespace create "CHAR_MAPPING" --preview
```

### 4. 更新配置

将 KV Namespace ID 更新到 `wrangler.toml`:

```toml
[[kv_namespaces]]
binding = "CHAR_MAPPING"
id = "your-kv-namespace-id"  # 替换为实际 ID
preview_id = "your-preview-kv-id"  # 可选
```

### 5. 上传数据

```bash
# 上传图片到 R2 和字符映射到 KV
python3 upload-data.py
```

### 6. 部署 Worker

```bash
# 部署到生产环境
wrangler deploy

# 或部署到开发环境
wrangler deploy --env development
```

## 📖 API 文档

### GET /api/search

搜索汉字手写体图片

**参数:**
- `q` (必需): 要搜索的汉字

**示例:**
```bash
curl "https://handwriting-api.workers.dev/api/search?q=水火山"
```

**响应:**
```json
{
  "success": true,
  "query": "水火山",
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
    },
    {
      "char": "火",
      "url": "https://handwriting-characters.r2.dev/chars/706b_火.png",
      "unicode": "U+706B",
      "filename": "706b_火.png",
      "available": true
    },
    {
      "char": "山",
      "url": null,
      "unicode": "U+5C71",
      "available": false,
      "message": "Character not yet collected"
    }
  ],
  "count": 3,
  "timestamp": "2024-01-01T12:00:00.000Z"
}
```

### GET /api/health

健康检查

**响应:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00.000Z",
  "version": "1.0.0"
}
```

### GET /api/stats

获取统计信息

**响应:**
```json
{
  "total_characters": 3500,
  "api_version": "1.0.0",
  "endpoints": [
    "/api/search?q={query}",
    "/api/health",
    "/api/stats"
  ]
}
```

## 🛠️ 开发

### 本地开发

```bash
# 启动本地开发服务器
npm run dev

# 访问 http://localhost:8787
```

### 查看日志

```bash
# 实时查看 Worker 日志
npm run tail
```

### 测试

```bash
# 测试健康检查
curl http://localhost:8787/api/health

# 测试搜索
curl "http://localhost:8787/api/search?q=水"
```

## 📦 项目结构

```
handwriting-api-worker/
├── src/
│   └── index.js          # Worker 入口文件
├── package.json          # 依赖配置
├── wrangler.toml         # Cloudflare 配置
├── upload-data.py        # 数据上传脚本
└── README.md            # 本文件
```

## 🔧 配置说明

### wrangler.toml

主要配置项：

```toml
name = "handwriting-api"              # Worker 名称
main = "src/index.js"                 # 入口文件
compatibility_date = "2024-01-01"     # 兼容日期

# R2 Bucket 配置
[[r2_buckets]]
binding = "CHAR_IMAGES"
bucket_name = "handwriting-characters"

# KV Namespace 配置
[[kv_namespaces]]
binding = "CHAR_MAPPING"
id = "your-kv-namespace-id"

# 环境变量
[vars]
R2_PUBLIC_DOMAIN = "handwriting-characters.r2.dev"
API_VERSION = "1.0.0"
```

## 📊 使用限制

### Cloudflare Workers 免费版限制

- 每天 100,000 次请求
- CPU 时间: 10ms/请求
- 脚本大小: 1MB

### Cloudflare R2 免费版限制

- 存储: 10GB
- 每月读取: 10M 次
- 每月写入: 1M 次

### Cloudflare KV 免费版限制

- 存储: 1GB
- 每天读取: 100K 次
- 每天写入: 1K 次

## 🔐 安全

- **速率限制**: 每个 IP 每分钟最多 100 次请求
- **CORS**: 允许所有源访问（可根据需要调整）
- **输入验证**: 只处理有效的汉字字符

## 🚧 待办事项

- [ ] 添加更多汉字数据
- [ ] 实现缓存策略优化
- [ ] 添加图片格式转换
- [ ] 支持批量查询
- [ ] 添加用户认证
- [ ] 性能监控和分析

## 📝 许可证

MIT License

## 🙏 致谢

- Cloudflare Workers
- Cloudflare R2
- Cloudflare KV
