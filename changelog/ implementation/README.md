# 🔍 CloudBrush 汉字图片搜索系统

> 基于 Cloudflare 全栈架构的汉字图片搜索引擎
> 
> 采集 → 存储 → API → 前端 一站式解决方案

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Cloudflare](https://img.shields.io/badge/Cloudflare-Workers-orange.svg)](https://workers.cloudflare.com/)

## ✨ 特性

- 🎯 **3000+ 汉字图片** - 涵盖常用汉字
- ⚡ **极速搜索** - Cloudflare Workers 边缘计算
- 🌍 **全球 CDN** - R2 存储 + 自动分发
- 💰 **超低成本** - 每月仅需 ￥2.6
- 📱 **响应式设计** - 完美支持移动端
- 🔐 **安全可靠** - 内置速率限制和 CORS

## 📸 预览

```
┌─────────────────────────────────────┐
│     🔍 汉字图片搜索                  │
│  Chinese Character Image Search     │
├─────────────────────────────────────┤
│                                     │
│  [输入汉字搜索...]      [搜索]      │
│                                     │
│  试试这些: 水火山 春夏秋冬 日月星辰  │
│                                     │
├─────────────────────────────────────┤
│  水         火         山           │
│  [图片]     [图片]     [图片]       │
│  U+6C34    U+706B    U+5C71        │
│  [下载]     [下载]     [下载]       │
└─────────────────────────────────────┘
```

## 🚀 快速开始

### 前置要求

- Python 3.8+
- Node.js 16+
- Cloudflare 账号
- iPhone + CloudBrush App（用于数据采集）

### 一键部署

```bash
# 1. 克隆项目
git clone https://github.com/your-repo/chinese-char-search.git
cd chinese-char-search

# 2. 安装依赖
pip install -r requirements.txt
npm install -g wrangler

# 3. 运行一键部署脚本
chmod +x deploy.sh
./deploy.sh
```

就这么简单！部署脚本会自动完成：
- ✅ 创建 R2 Bucket
- ✅ 上传图片
- ✅ 配置 KV
- ✅ 部署 Worker
- ✅ 部署前端

## 📦 项目结构

```
chinese-char-search/
├── README.md                          # 项目说明
├── COMPLETE_IMPLEMENTATION_GUIDE.md   # 完整实施指南
├── requirements.txt                   # Python 依赖
├── package.json                       # Node.js 依赖
│
├── 数据采集/
│   ├── enhanced_collector.py          # 增强版抓包脚本
│   ├── common_3500_chars.txt          # 常用字列表
│   └── collected_characters/          # 采集的图片
│       ├── 6c34_水.png
│       ├── 706b_火.png
│       └── char_url_mapping.json      # 字符映射
│
├── 后端 API/
│   ├── wrangler.toml                  # Worker 配置
│   ├── src/
│   │   └── index.js                   # Worker 代码
│   └── worker-api.js                  # 原始 API 代码
│
├── 前端/
│   ├── frontend-search.html           # 搜索页面
│   └── pages-deploy/                  # Pages 部署目录
│
├── 工具脚本/
│   ├── upload_to_cloud.py             # 上传到 R2/S3
│   ├── deploy.sh                      # 一键部署
│   └── test_api.sh                    # API 测试
│
└── 文档/
    ├── storage_comparison.md          # 存储方案对比
    └── deployment-info.json           # 部署信息
```

## 📖 详细文档

### 阶段一：数据采集（1-2小时）

1. **启动抓包工具**
   ```bash
   mitmweb -s enhanced_collector.py -p 8080
   ```

2. **配置 iPhone**
   - 设置代理：你的电脑IP:8080
   - 安装证书：访问 mitm.it
   - 信任证书：设置 → 证书信任设置

3. **采集汉字**
   - 打开 CloudBrush App
   - 浏览字典/字库
   - 脚本自动保存图片

4. **检查结果**
   ```bash
   cd collected_characters
   ls *.png | wc -l  # 查看采集数量
   ```

详见：[COMPLETE_IMPLEMENTATION_GUIDE.md](COMPLETE_IMPLEMENTATION_GUIDE.md)

### 阶段二：上传到云端（30分钟）

```bash
# 配置环境变量
export R2_ENDPOINT='https://xxx.r2.cloudflarestorage.com'
export R2_ACCESS_KEY_ID='your_key'
export R2_SECRET_ACCESS_KEY='your_secret'

# 上传
python3 upload_to_cloud.py
```

### 阶段三：部署 API（1小时）

```bash
# 登录 Cloudflare
wrangler login

# 创建 KV
wrangler kv:namespace create "CHAR_MAPPING"

# 上传映射数据
wrangler kv:key put --binding=CHAR_MAPPING "char_mapping" \
  --path=cdn_url_mapping.json

# 部署 Worker
wrangler deploy
```

### 阶段四：部署前端（30分钟）

```bash
# 更新 API URL
sed -i 's|your-worker.workers.dev|YOUR_ACTUAL_URL|g' frontend-search.html

# 部署到 Pages
wrangler pages deploy pages-deploy --project-name=chinese-char-search
```

## 🔧 配置说明

### Worker 环境变量

在 `wrangler.toml` 中配置：

```toml
[vars]
R2_PUBLIC_DOMAIN = "chinese-characters.r2.dev"
API_VERSION = "1.0.0"
```

### 自定义域名

1. Cloudflare Dashboard → Workers → 你的 Worker
2. Triggers → Custom Domains
3. Add Custom Domain → 输入域名

## 🌐 API 文档

### 搜索端点

```http
GET /api/search?q={query}
```

**参数：**
- `q` - 要搜索的汉字（必需）

**响应示例：**
```json
{
  "success": true,
  "query": "水火",
  "results": [
    {
      "char": "水",
      "url": "https://cdn.example.com/chars/6c34_水.png",
      "unicode": "U+6C34",
      "filename": "6c34_水.png",
      "metadata": {
        "size": 12345,
        "timestamp": "2025-01-15T10:30:00Z"
      }
    },
    {
      "char": "火",
      "url": "https://cdn.example.com/chars/706b_火.png",
      "unicode": "U+706B",
      "filename": "706b_火.png"
    }
  ],
  "count": 2,
  "timestamp": "2025-01-15T12:00:00Z"
}
```

### 其他端点

- `GET /api/health` - 健康检查
- `GET /api/stats` - 统计信息
- `GET /` - API 文档

完整 API 文档：访问你的 Worker URL

## 💰 成本分析

| 服务 | 用量 | 费用 |
|------|------|------|
| R2 存储 (30MB) | 免费额度内 | $0 |
| R2 读取 (100万/月) | Class B操作 | $0.36 |
| R2 流量 | 无限制 | **$0** ⭐ |
| Worker (100万请求/月) | 免费额度内 | $0 |
| Pages 托管 | 免费 | $0 |
| **总计** | - | **$0.36/月** ≈ **￥2.6/月** |

## 🔒 安全特性

- ✅ 速率限制：100请求/分钟/IP
- ✅ CORS 配置
- ✅ 输入验证
- ✅ 错误处理
- ✅ API Token 保护（可选）

## 📊 性能优化

1. **边缘缓存**
   - Worker 在全球 300+ 城市运行
   - 平均响应时间 < 50ms

2. **CDN 加速**
   - R2 自动 CDN 分发
   - 图片请求零延迟

3. **并发处理**
   - Worker 支持高并发
   - 自动扩展

## 🐛 故障排除

### 抓包看不到流量？

```bash
# 检查代理设置
netstat -an | grep 8080

# 查看 mitmproxy 日志
mitmproxy -s enhanced_collector.py -p 8080 -v
```

### Worker 部署失败？

```bash
# 检查配置
wrangler whoami
wrangler deployments list

# 查看日志
wrangler tail
```

### 图片无法访问？

1. 检查 R2 公开访问已启用
2. 验证 URL 格式正确
3. 查看 CORS 配置

更多问题：[Issues](https://github.com/your-repo/issues)

## 🤝 贡献

欢迎贡献！请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 许可证

[MIT License](LICENSE)

## 🙏 致谢

- [CloudBrush](https://www.fanglige.com/) - 数据来源
- [mitmproxy](https://mitmproxy.org/) - 抓包工具
- [Cloudflare](https://cloudflare.com/) - 基础设施

## 📞 联系方式

- 作者：Your Name
- Email: your.email@example.com
- GitHub: [@yourusername](https://github.com/yourusername)

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
