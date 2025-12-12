# 快速开始 - 5分钟部署到 Cloudflare

最快速的部署方式，适合已经有采集数据的情况。

## ⚡ 超快速部署（3 步）

### 1. 准备工作（1分钟）

```bash
# 安装 wrangler
npm install -g wrangler

# 登录 Cloudflare
wrangler login
```

### 2. 一键部署（3分钟）

```bash
cd handwriting-api-worker
./deploy.sh
```

脚本会自动：
- ✅ 创建 R2 Bucket
- ✅ 创建 KV Namespace
- ✅ 上传图片数据
- ✅ 部署 Worker API

### 3. 验证（1分钟）

```bash
# 测试 API
curl "https://handwriting-api.<你的子域>.workers.dev/api/search?q=水"
```

## 📝 注意事项

1. **更新 KV ID**: 首次运行时，脚本会提示更新 `wrangler.toml` 中的 KV Namespace ID
2. **数据准备**: 确保 `data-collection/collected_characters/` 目录下有 PNG 图片
3. **网络连接**: 部署过程需要稳定的网络连接

## 🔧 常用命令

```bash
# 查看实时日志
wrangler tail

# 重新部署
wrangler deploy

# 更新数据
python3 upload-data.py

# 仅更新 KV
python3 upload-data.py --skip-r2

# 仅上传图片
python3 upload-data.py --skip-kv
```

## 📖 详细文档

- 完整部署指南: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- API 使用文档: [handwriting-api-worker/README.md](handwriting-api-worker/README.md)
- 详细部署步骤: [handwriting-api-worker/DEPLOYMENT.md](handwriting-api-worker/DEPLOYMENT.md)

## 🆘 遇到问题？

1. 检查 wrangler 是否登录: `wrangler whoami`
2. 检查数据目录: `ls ../data-collection/collected_characters/`
3. 查看错误日志: `wrangler tail`
4. 参考常见问题: [DEPLOYMENT_GUIDE.md#常见问题](DEPLOYMENT_GUIDE.md#常见问题)
