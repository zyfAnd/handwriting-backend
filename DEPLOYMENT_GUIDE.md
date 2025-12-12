# Handwriting Backend - Cloudflare 部署完整指南

本指南帮助你完成从数据采集到 Cloudflare 部署的完整流程。

## 📋 项目概述

**Handwriting Backend** 是一个汉字手写体图片搜索服务，包含两个主要部分：

1. **数据采集模块** (`data-collection/`): 从 CloudBrush App 采集汉字手写体图片
2. **API 服务** (`handwriting-api-worker/`): 基于 Cloudflare Workers 的搜索 API

## 🏗️ 架构设计

参考了 **novel-backend** 项目的架构：

```
┌──────────────────┐
│   数据采集模块    │
│  (Python + MIT)  │
└────────┬─────────┘
         │ 采集图片
         ▼
┌──────────────────┐
│  collected_chars │  ← PNG 图片 + 映射文件
└────────┬─────────┘
         │ 上传
         ▼
┌──────────────────────────────────┐
│      Cloudflare 基础设施          │
│                                   │
│  ┌──────────┐    ┌─────────┐    │
│  │ Worker   │ ←→ │   KV    │    │
│  │   API    │    │ (映射)   │    │
│  └────┬─────┘    └─────────┘    │
│       │                          │
│       ▼                          │
│  ┌──────────┐                   │
│  │    R2    │ (图片存储)         │
│  └──────────┘                   │
└──────────────────────────────────┘
         │
         ▼
   ┌──────────┐
   │  用户请求 │
   └──────────┘
```

## 🚀 快速开始

### 方案 A: 一键部署（推荐）

```bash
# 进入 API Worker 目录
cd handwriting-api-worker

# 运行一键部署脚本
./deploy.sh
```

脚本会自动完成：
1. ✅ 创建 R2 Bucket
2. ✅ 创建 KV Namespace
3. ✅ 上传图片数据
4. ✅ 部署 Worker
5. ✅ 验证部署

### 方案 B: 手动部署

详细步骤请参考 [handwriting-api-worker/DEPLOYMENT.md](handwriting-api-worker/DEPLOYMENT.md)

## 📁 项目结构

```
handwriting-backend/
├── data-collection/                # 数据采集模块
│   ├── enhanced_collector.py       # MIT 抓包采集脚本
│   ├── api_collector.py            # API Token 采集脚本 (推荐)
│   ├── common_3500_chars.txt       # 常用汉字列表
│   └── collected_characters/       # 采集的图片
│       ├── 6c34_水.png
│       ├── char_url_mapping.json   # 字符映射
│       └── collection_report.json  # 采集报告
│
├── handwriting-api-worker/         # Cloudflare Worker API
│   ├── src/
│   │   └── index.js                # Worker 入口文件
│   ├── package.json                # npm 依赖
│   ├── wrangler.toml               # Cloudflare 配置
│   ├── upload-data.py              # 数据上传脚本
│   ├── deploy.sh                   # 一键部署脚本
│   ├── README.md                   # API 文档
│   └── DEPLOYMENT.md               # 详细部署指南
│
└── DEPLOYMENT_GUIDE.md             # 本文件
```

## 📖 完整部署流程

### 第一步：数据采集

有两种采集方式可选：

#### 方式 1: API Token 采集（推荐，更快）

```bash
cd data-collection

# 1. 设置 token（从 Charles 抓包获取）
export CLOUDBRUSH_TOKEN='your_token_here'

# 2. 运行采集脚本
python3 api_collector.py
```

#### 方式 2: MIT 抓包采集（备选）

```bash
cd data-collection

# 1. 启动抓包工具
mitmweb -s enhanced_collector.py -p 8080

# 2. 配置 iPhone 代理和证书
# 3. 打开 CloudBrush App 浏览汉字
```

详细说明: [data-collection/README.md](data-collection/README.md)

### 第二步：部署到 Cloudflare

```bash
cd handwriting-api-worker

# 选择以下任一方式：

# 方式 A: 一键部署
./deploy.sh

# 方式 B: 手动部署
# 1. 安装依赖
npm install

# 2. 创建资源
wrangler r2 bucket create handwriting-characters
wrangler kv:namespace create "CHAR_MAPPING"

# 3. 更新 wrangler.toml (填入 KV ID)

# 4. 上传数据
python3 upload-data.py

# 5. 部署 Worker
wrangler deploy
```

### 第三步：验证部署

```bash
# 健康检查
curl https://handwriting-api.<你的子域>.workers.dev/api/health

# 搜索测试
curl "https://handwriting-api.<你的子域>.workers.dev/api/search?q=水火山"

# 查看统计
curl https://handwriting-api.<你的子域>.workers.dev/api/stats
```

## 🔑 关键配置

### Cloudflare 资源

1. **R2 Bucket**: `handwriting-characters`
   - 存储汉字图片 PNG 文件
   - 路径格式: `chars/6c34_水.png`

2. **KV Namespace**: `CHAR_MAPPING`
   - 存储字符映射 JSON
   - Key: `char_mapping`

3. **Worker**: `handwriting-api`
   - 提供搜索 API
   - 速率限制: 100 req/min/IP

### 环境变量

在 `wrangler.toml` 中配置：

```toml
[vars]
R2_PUBLIC_DOMAIN = "handwriting-characters.r2.dev"
API_VERSION = "1.0.0"
```

## 📊 API 端点

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
      "url": "https://handwriting-characters.r2.dev/chars/6c34_水.png",
      "unicode": "U+6C34",
      "available": true
    },
    ...
  ],
  "count": 3
}
```

### 其他端点

- `GET /api/health` - 健康检查
- `GET /api/stats` - 统计信息
- `GET /` - API 文档页面

完整 API 文档: [handwriting-api-worker/README.md](handwriting-api-worker/README.md)

## 🔄 数据更新流程

### 更新采集数据

```bash
# 1. 采集新数据
cd data-collection
python3 api_collector.py

# 2. 上传到 Cloudflare
cd ../handwriting-api-worker
python3 upload-data.py
```

### 仅更新 KV 映射

```bash
cd handwriting-api-worker
python3 upload-data.py --skip-r2
```

### 仅上传新图片

```bash
cd handwriting-api-worker
python3 upload-data.py --skip-kv
```

## 🛠️ 运维管理

### 查看实时日志

```bash
cd handwriting-api-worker
wrangler tail
```

### 更新 Worker 代码

```bash
# 修改代码后
wrangler deploy
```

### 查看使用统计

登录 [Cloudflare Dashboard](https://dash.cloudflare.com) → Workers & Pages → handwriting-api → Analytics

## 🐛 常见问题

### Q1: 数据采集失败

**原因**: Token 过期或 API 端点变更

**解决**:
1. 重新用 Charles 抓包获取新 token
2. 检查 API 端点是否正确

### Q2: 图片无法访问

**原因**: R2 Bucket 未开启公开访问

**解决**:
1. 登录 Cloudflare Dashboard
2. R2 → handwriting-characters → Settings
3. 开启 Public Access

### Q3: KV 数据未找到

**原因**: 数据未正确上传

**解决**:
```bash
# 检查 KV
wrangler kv:key get --binding=CHAR_MAPPING "char_mapping"

# 重新上传
python3 upload-data.py --skip-r2
```

### Q4: Worker 部署失败

**原因**: wrangler 版本过旧或未登录

**解决**:
```bash
# 更新 wrangler
npm install -g wrangler@latest

# 重新登录
wrangler logout
wrangler login
```

## 📚 参考文档

### 本项目文档

- [数据采集指南](data-collection/README.md)
- [API 使用文档](handwriting-api-worker/README.md)
- [详细部署步骤](handwriting-api-worker/DEPLOYMENT.md)

### 参考项目

- [novel-backend](../novel-backend) - 本项目参考的架构示例

### Cloudflare 文档

- [Workers 文档](https://developers.cloudflare.com/workers/)
- [R2 文档](https://developers.cloudflare.com/r2/)
- [KV 文档](https://developers.cloudflare.com/workers/runtime-apis/kv/)
- [Wrangler CLI](https://developers.cloudflare.com/workers/wrangler/)

## 🎯 后续计划

- [ ] 采集更多汉字（目标 3500+）
- [ ] 添加拼音搜索功能
- [ ] 实现图片格式转换
- [ ] 支持批量查询
- [ ] 添加缓存优化
- [ ] 部署到自定义域名
- [ ] 添加使用统计分析

## 📝 许可证

MIT License

## 🙏 致谢

- Novel Backend 项目架构参考
- Cloudflare Workers/R2/KV 服务
- CloudBrush App 数据源
