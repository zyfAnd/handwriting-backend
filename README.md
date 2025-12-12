# Handwriting Backend

汉字手写体图片搜索服务 - 基于 Cloudflare Workers 的无服务器 API

## 🌟 项目简介

Handwriting Backend 是一个完整的汉字手写体图片采集和搜索解决方案，包含：

1. **数据采集模块**: 从 CloudBrush App 采集汉字手写体图片
2. **API 服务**: 基于 Cloudflare Workers 的高性能搜索 API
3. **全球 CDN**: 利用 Cloudflare R2 + Workers 提供全球加速访问

## ✨ 功能特性

- ✅ **快速搜索**: 通过汉字查询对应的手写体图片
- ✅ **全球加速**: Cloudflare 全球 CDN 网络
- ✅ **无服务器**: 零维护成本，按需付费
- ✅ **RESTful API**: 简单易用的 HTTP 接口
- ✅ **自动化部署**: 一键部署脚本
- ✅ **完整文档**: 详细的使用和部署指南

## 🚀 快速开始

### 5分钟快速部署

```bash
# 1. 克隆项目
git clone https://github.com/your-username/handwriting-backend.git
cd handwriting-backend

# 2. 安装依赖
cd handwriting-api-worker
npm install -g wrangler

# 3. 登录 Cloudflare
wrangler login

# 4. 一键部署
./deploy.sh
```

详细步骤请查看 [QUICK_START.md](QUICK_START.md)

## 📋 项目结构

```
handwriting-backend/
├── data-collection/           # 数据采集模块
│   ├── api_collector.py       # API Token 采集 (推荐)
│   ├── enhanced_collector.py  # MIT 抓包采集
│   └── collected_characters/  # 采集的图片
│
├── handwriting-api-worker/    # Cloudflare Worker API
│   ├── src/index.js          # Worker 代码
│   ├── upload-data.py        # 数据上传脚本
│   ├── deploy.sh             # 一键部署
│   └── wrangler.toml         # Cloudflare 配置
│
├── QUICK_START.md            # 快速开始指南
├── DEPLOYMENT_GUIDE.md       # 完整部署指南
└── README.md                 # 本文件
```

## 📖 API 使用

### 搜索 API

```bash
GET /api/search?q={汉字}
```

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
      "url": "https://cdn.example.com/chars/6c34_水.png",
      "unicode": "U+6C34",
      "available": true
    }
  ],
  "count": 3
}
```

### 其他端点

- `GET /api/health` - 健康检查
- `GET /api/stats` - 统计信息

完整 API 文档: [handwriting-api-worker/README.md](handwriting-api-worker/README.md)

## 🏗️ 架构设计

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

## 📚 文档

- [快速开始](QUICK_START.md) - 5分钟部署指南
- [部署指南](DEPLOYMENT_GUIDE.md) - 完整部署流程
- [API 文档](handwriting-api-worker/README.md) - API 使用说明
- [数据采集](data-collection/README.md) - 数据采集指南

## 🔧 技术栈

### 数据采集
- Python 3.x
- mitmproxy (MIT 抓包)
- requests (HTTP 请求)

### API 服务
- Cloudflare Workers (无服务器计算)
- Cloudflare R2 (对象存储)
- Cloudflare KV (键值存储)
- JavaScript

### 部署工具
- Wrangler CLI (Cloudflare 部署工具)
- Bash (自动化脚本)

## 💰 成本估算

### Cloudflare Workers 免费版
- ✅ 每天 100,000 次请求
- ✅ CPU 时间: 10ms/请求
- ✅ 完全免费

### Cloudflare R2 免费版
- ✅ 存储: 10GB
- ✅ 每月读取: 10M 次
- ✅ 每月写入: 1M 次
- ✅ 完全免费

### Cloudflare KV 免费版
- ✅ 存储: 1GB
- ✅ 每天读取: 100K 次
- ✅ 每天写入: 1K 次
- ✅ 完全免费

**总成本**: $0/月（适合中小规模使用）

## 🛠️ 开发

### 本地开发

```bash
cd handwriting-api-worker
npm run dev
```

访问: `http://localhost:8787`

### 查看日志

```bash
wrangler tail
```

### 更新部署

```bash
wrangler deploy
```

## 🔐 环境变量

需要在 `wrangler.toml` 中配置：

```toml
[vars]
R2_PUBLIC_DOMAIN = "your-r2-domain.r2.dev"
API_VERSION = "1.0.0"
```

## 📊 使用限制

- 速率限制: 每个 IP 每分钟 100 次请求
- 图片格式: PNG (300x300)
- 字符集: CJK 统一汉字

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📝 许可证

MIT License

## 🙏 致谢

- [Cloudflare Workers](https://workers.cloudflare.com/)
- [CloudBrush App](https://apps.apple.com/) - 数据来源
- [Novel Backend](../novel-backend) - 架构参考

## 📧 联系方式

如有问题或建议，请提交 Issue。

---

**⚡ Powered by Cloudflare Workers**