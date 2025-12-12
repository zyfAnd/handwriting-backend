# 数据采集模块 - 完成总结

## ✅ 已完成的工作

### 1. 创建了 API Token 直接采集脚本

**文件**: `data-collection/api_collector.py`

**功能**:
- ✅ 使用 Charles 获取的 token 直接调用 API
- ✅ 自动构建正确的 API 请求（`/class/action.php?api=queryDict&cnChar=...`）
- ✅ 添加必要的 headers（X-Client-OS, timeStamp, locale 等）
- ✅ 处理加密的 JSON 响应，自动提取图片 URL
- ✅ 批量下载汉字图片
- ✅ 自动保存映射文件和进度报告

### 2. 创建了使用文档

- **`data-collection/QUICK_START.md`** - 快速开始指南
- **`data-collection/API_TOKEN_GUIDE.md`** - API Token 详细使用指南
- **`data-collection/README.md`** - 数据采集模块总览（已更新）

### 3. 脚本特性

根据你提供的实际 API 信息，脚本已配置为：

1. **API 端点**: `/class/action.php?api=queryDict&cnChar={base64}&fontId=-1&limit=24&page=1&src=0`
2. **Token 格式**: `Bearer {token}` 在 `Authorization` header 中
3. **响应处理**: 自动从加密的 JSON 响应中提取图片 URL
4. **图片 URL 格式**: `https://sfapi.fanglige.com/svg_png/{数字}/{字符串}.png`

## 🚀 使用方法

### 快速开始

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection

# 1. 从 Charles 获取 token（Bearer 后面的部分）
export CLOUDBRUSH_TOKEN='eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...'

# 2. 运行采集脚本
python3 api_collector.py
```

### 详细步骤

1. **获取 Token**
   - 在 Charles 中找到 CloudBrush App 的 API 请求
   - 查看 `Authorization` header
   - 复制 `Bearer` 后面的 token 值

2. **运行脚本**
   ```bash
   export CLOUDBRUSH_TOKEN='your_token_here'
   python3 api_collector.py
   ```

3. **脚本会自动**:
   - 测试连接（尝试获取"水"字的图片）
   - 批量采集常用汉字图片
   - 保存到 `collected_characters/` 目录

## 📁 文件结构

```
data-collection/
├── api_collector.py          # API Token 直接采集脚本 ⭐
├── enhanced_collector.py     # 抓包采集脚本（备选）
├── common_3500_chars.txt    # 常用汉字列表
├── QUICK_START.md           # 快速开始指南
├── API_TOKEN_GUIDE.md       # API Token 详细指南
├── README.md                # 模块总览
└── collected_characters/    # 采集的图片（运行后自动创建）
    ├── 6c34_水.png
    ├── char_url_mapping.json
    └── collection_report.json
```

## 📝 注意事项

1. **Token 有效期**: Token 可能会过期，如果采集失败，需要重新获取
2. **请求频率**: 脚本默认每次请求间隔 0.5 秒，避免请求过快
3. **响应格式**: API 返回加密的 JSON，脚本会自动提取图片 URL
4. **图片格式**: 图片保存为 PNG 格式，文件名格式：`{unicode}_{汉字}.png`

## 🔄 下一步

完成数据采集后，可以使用 `data-upload/upload_to_cloud.py` 将图片上传到 Cloudflare R2。

## 📖 相关文档

- **快速开始**: `data-collection/QUICK_START.md`
- **详细指南**: `data-collection/API_TOKEN_GUIDE.md`
- **模块总览**: `data-collection/README.md`
- **完整实施**: `changelog/ implementation/COMPLETE_IMPLEMENTATION_GUIDE.md`
