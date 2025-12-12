# 快速开始 - 使用 Charles 获取的 Token

## 📋 步骤

### 1. 从 Charles 获取 Token

在 Charles 中找到 CloudBrush App 的 API 请求，查看 Request Headers：

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

复制完整的 token 值（`Bearer` 后面的部分）。

### 2. 运行采集脚本

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection

# 方式1：使用环境变量
export CLOUDBRUSH_TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'
python3 api_collector.py

# 方式2：直接运行（会提示输入 token）
python3 api_collector.py
# 输入 token: eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### 3. 脚本会自动：

1. ✅ 使用正确的 API 端点：`/class/action.php?api=queryDict&cnChar=...`
2. ✅ 添加必要的 headers（X-Client-OS, timeStamp, locale 等）
3. ✅ 处理加密的响应（从加密字符串中提取图片 URL）
4. ✅ 下载图片并保存到 `collected_characters/` 目录

## 📝 注意事项

1. **Token 有效期**：Token 可能会过期，如果采集失败，检查 token 是否还有效
2. **请求频率**：脚本默认每次请求间隔 0.5 秒，避免请求过快
3. **响应格式**：API 返回的是加密的 JSON，脚本会自动从加密字符串中提取图片 URL

## 🔍 测试

脚本会先测试连接，尝试获取"水"字的图片。如果测试成功，说明配置正确。

## �� 输出

采集的图片会保存到：
- `collected_characters/6c34_水.png` - 图片文件
- `collected_characters/char_url_mapping.json` - 字符映射
- `collected_characters/collection_report.json` - 采集报告

## ⚠️ 如果遇到问题

1. **测试失败**：检查 token 是否有效，是否从最新的请求中获取
2. **无法提取 URL**：响应格式可能已变化，需要查看实际的响应内容
3. **下载失败**：检查网络连接，或图片 URL 是否可访问
