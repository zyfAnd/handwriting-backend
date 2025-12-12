# 数据上传模块

## 📋 功能说明

这个模块用于将采集的汉字图片批量上传到 Cloudflare R2 或 AWS S3。

## 🚀 快速开始

### 1. 配置 Cloudflare R2

#### 步骤1：创建 R2 Bucket

1. 登录 [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. 左侧菜单 → R2
3. Create bucket
   - 名称：`chinese-characters`（全球唯一）
   - 位置：自动选择
   - 点击 Create

#### 步骤2：生成 API Token

1. R2 → Manage R2 API Tokens
2. Create API Token
   - Token name: `character-uploader`
   - Permissions: ✅ Object Read & Write
   - TTL: Forever
3. 复制保存：
   - Access Key ID
   - Secret Access Key
   - Endpoint URL

#### 步骤3：配置环境变量

```bash
# 在 ~/.bashrc 或 ~/.zshrc 添加
export R2_ENDPOINT='https://xxxxxxxxxxxx.r2.cloudflarestorage.com'
export R2_ACCESS_KEY_ID='your_access_key_id_here'
export R2_SECRET_ACCESS_KEY='your_secret_key_here'
export R2_PUBLIC_DOMAIN='chinese-characters.r2.dev'  # 或自定义域名

# 重新加载
source ~/.bashrc
```

### 2. 执行上传

```bash
cd data-upload
python3 upload_to_cloud.py
```

按提示输入：
- 服务商：`r2`（默认）
- 本地图片目录：`../data-collection/collected_characters`（默认）
- Bucket名称：`chinese-characters`

### 3. 配置公开访问

#### 方案A：使用 R2.dev 域名（最简单）

1. Cloudflare Dashboard → R2
2. 选择 `chinese-characters` bucket
3. Settings → Public Access
4. 启用 `r2.dev subdomain`
5. 复制域名：`https://chinese-characters.xxxx.r2.dev`

### 4. 验证上传

```bash
# 测试访问
curl -I https://chinese-characters.xxxx.r2.dev/chars/6c34_水.png

# 应该返回 200 OK
HTTP/2 200
content-type: image/png
```

## 📁 输出文件

上传完成后会生成：
- `cdn_url_mapping.json` - CDN URL 映射文件

## 📖 详细文档

更多信息请参考：
- `../changelog/ implementation/COMPLETE_IMPLEMENTATION_GUIDE.md` - 完整实施指南
