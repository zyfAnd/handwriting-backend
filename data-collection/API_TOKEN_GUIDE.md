# API Token 直接采集指南

## 📋 说明

如果你已经通过 Charles 抓包获取到了 CloudBrush API 的 token，可以使用这个脚本直接调用 API 批量获取汉字图片，无需手动在 App 中浏览。

## 🚀 快速开始

### 1. 安装依赖

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
pip install requests tqdm
```

### 2. 获取 Token

通过 Charles 抓包，找到 CloudBrush App 的 API 请求，获取：
- **Token 值**：实际的 token 字符串
- **Token 位置**：在 Header 中还是在参数中？
- **Token 格式**：是 `Bearer token` 还是直接是 `token`？
- **Header 名称**：如果是 Header，字段名是什么？（如 `Authorization`, `Token`, `X-Auth-Token`）

### 3. 运行采集脚本

#### 方式1：直接运行（交互式）

```bash
cd data-collection
python3 api_collector.py
```

按提示输入 token。

#### 方式2：使用环境变量

```bash
# 设置 token
export CLOUDBRUSH_TOKEN='your_token_here'

# 可选：自定义配置
export CLOUDBRUSH_API_URL='https://sfapi.fanglige.com'  # API 地址
export CLOUDBRUSH_TOKEN_HEADER='Authorization'          # Token Header 名称
export CLOUDBRUSH_TOKEN_FORMAT='Bearer {token}'         # Token 格式

# 运行
cd data-collection
python3 api_collector.py
```

## 🔧 配置说明

### Token 格式示例

根据你从 Charles 中看到的实际请求，可能需要调整：

1. **Bearer Token**（最常见）
   ```bash
   export CLOUDBRUSH_TOKEN_HEADER='Authorization'
   export CLOUDBRUSH_TOKEN_FORMAT='Bearer {token}'
   ```

2. **直接 Token**
   ```bash
   export CLOUDBRUSH_TOKEN_HEADER='Authorization'
   export CLOUDBRUSH_TOKEN_FORMAT='{token}'
   ```

3. **自定义 Header**
   ```bash
   export CLOUDBRUSH_TOKEN_HEADER='X-Auth-Token'
   export CLOUDBRUSH_TOKEN_FORMAT='{token}'
   ```

## 🔍 如何从 Charles 获取 Token

1. **打开 Charles**
2. **在 App 中触发一个 API 请求**（如查询某个汉字）
3. **在 Charles 中找到该请求**
4. **查看 Request Headers**，找到 token 相关的 header
   - 常见字段：`Authorization`, `Token`, `X-Auth-Token`, `X-Token`
5. **复制 token 值**

### 示例：Charles 中看到的请求

```
GET https://sfapi.fanglige.com/class/action.php?cnChar=5rWL
Headers:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
  User-Agent: CloudBrush/1.0
```

那么：
- Token: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- Header: `Authorization`
- Format: `Bearer {token}`

## ⚠️ 注意事项

1. **Token 有效期**：Token 可能会过期，如果采集失败，检查 token 是否还有效
2. **请求频率**：脚本默认每次请求间隔 0.5 秒，避免请求过快
3. **API 端点**：脚本会尝试多个常见的 API 端点，如果都不对，需要根据实际 API 修改代码

## 🐛 故障排除

### 问题1：测试失败，无法获取图片

**解决方法：**
1. 在 Charles 中重新查看最新的请求
2. 确认 token 和 header 配置正确
3. 尝试手动用 curl 测试

### 问题2：返回 401 或 403

**解决方法：**
- 重新获取 token
- 检查 token_format 配置

## 📁 输出文件

采集完成后会生成：
- `collected_characters/*.png` - 汉字图片文件
- `collected_characters/char_url_mapping.json` - 字符映射文件
- `collected_characters/collection_report.json` - 采集报告
