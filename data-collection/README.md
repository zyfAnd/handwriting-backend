# 数据采集模块

## 📋 功能说明

这个模块用于从 CloudBrush App 采集汉字图片数据。

**三种采集方式：**
1. **可视化 Web 界面**（🌟 推荐） - 实时监控、自动同步到 GitHub/Cloudflare
2. **API Token 直接采集**（快速） - 使用已获取的 token 直接调用 API
3. **抓包采集**（备选） - 通过 mitmproxy 抓包自动保存

---

## 🌟 方式一：可视化 Web 界面（强烈推荐）

**最新功能！** 提供完整的可视化采集系统，支持实时监控、自动同步。

### 特性

- ✅ **实时可视化界面** - 查看采集进度、字符列表
- ✅ **自动监控** - WebSocket 实时更新
- ✅ **一键同步** - 自动提交到 GitHub
- ✅ **自动部署** - GitHub Actions 自动上传到 Cloudflare
- ✅ **完整流程** - 采集 → 存储 → GitHub → Cloudflare R2/KV

### 快速开始

```bash
cd data-collection
./start_collector.sh
```

启动后：
1. 访问 http://localhost:5000 查看 Web 界面
2. 配置 iPhone 代理（界面会显示 IP 和端口）
3. 点击 "开始采集" 按钮
4. 在 iPhone 上打开 CloudBrush App 浏览汉字
5. 实时查看采集进度
6. 点击 "提交到 GitHub" 一键同步

**详细说明：** 查看本目录下的完整使用文档

---

## 🚀 方式二：API Token 直接采集（快速）

如果你已经通过 Charles 抓包获取到了 token，可以使用这种方式，**无需手动操作，全自动批量采集**。

### 快速开始

```bash
# 1. 安装依赖
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
pip install requests tqdm

# 2. 设置 token（从 Charles 中获取）
export CLOUDBRUSH_TOKEN='your_token_here'

# 3. 运行采集脚本
cd data-collection
python3 api_collector.py
```

**详细说明：** 查看 [`API_TOKEN_GUIDE.md`](API_TOKEN_GUIDE.md)

---

## 🔧 方式三：抓包采集（备选方案）

如果无法获取 token，可以使用抓包方式。

### 1. 安装依赖

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
pip install -r requirements.txt
```

### 2. 启动抓包工具

```bash
cd data-collection
mitmweb -s enhanced_collector.py -p 8080
```

### 3. 配置 iPhone

1. **设置代理**
   - iPhone 连接与电脑同一 WiFi
   - 设置 → Wi-Fi → (i) → 配置代理 → 手动
   - 服务器：你的电脑IP（如：192.168.1.100）
   - 端口：8080

2. **安装证书**
   - iPhone Safari 访问：`mitm.it`
   - 点击 iOS 图标下载证书
   - 设置 → 已下载的描述文件 → 安装
   - 设置 → 通用 → 关于本机 → 证书信任设置
   - 启用 mitmproxy 证书

### 4. 开始采集

1. 打开 CloudBrush App
2. 进入字典/字库功能
3. 按部首/笔画浏览
4. 慢慢滑动，每个字停留1秒
5. mitmproxy 会自动保存图片

### 5. 检查结果

```bash
cd collected_characters
ls *.png | wc -l  # 统计采集数量
cat char_url_mapping.json | head  # 查看映射
```

## 📁 文件说明

### 可视化 Web 界面
- `start_collector.sh` - **一键启动脚本**
- `web_collector.py` - Web 界面后端（Flask + SocketIO）
- `templates/collector.html` - Web 界面前端
- `requirements.txt` - Python 依赖

### 采集脚本
- `api_collector.py` - API Token 直接采集脚本
- `enhanced_collector.py` - 增强版抓包脚本
- `common_3500_chars.txt` - 常用汉字列表（用于进度统计）

### 数据存储
- `collected_characters/` - 采集的图片保存目录（自动创建）
  - `6c34_水.png` - 图片文件（格式：unicode_汉字.png）
  - `char_url_mapping.json` - 字符映射文件

### 文档
- `API_TOKEN_GUIDE.md` - API Token 采集详细指南

## 📊 采集进度

- **Web 界面方式**：实时可视化进度条、字符列表、实时日志
- **API Token 方式**：自动显示进度条
- **抓包方式**：每10个字符自动保存一次，并在终端显示进度

## ⚠️ 注意事项

### API Token 方式
1. Token 可能会过期，如果采集失败，检查 token 是否还有效
2. 脚本默认每次请求间隔 0.5 秒，避免请求过快
3. 如果 API 端点不对，需要根据实际 API 修改代码

### 抓包方式
1. 确保 iPhone 和电脑在同一网络
2. 证书必须正确安装并信任
3. 采集过程需要手动操作，3000字预计需要1-2小时
4. 采集的图片会自动保存到 `collected_characters/` 目录

## 🚀 自动同步到 Cloudflare

使用 **Web 界面** 或手动提交到 GitHub 后，系统会自动：

1. **触发 GitHub Actions** - 检测到 `collected_characters/` 变化
2. **上传图片到 R2** - 所有 PNG 文件上传到 `handwriting-characters` bucket
3. **上传映射到 KV** - 字符映射上传到 KV Namespace
4. **实时生效** - Cloudflare Worker API 立即可用

查看同步状态: https://github.com/zyfAnd/handwriting-backend/actions

## 📖 详细文档

- **可视化 Web 界面：** 查看本 README 上方的 "方式一" 说明
- **API Token 采集：** [`API_TOKEN_GUIDE.md`](API_TOKEN_GUIDE.md)
- **完整实施指南：** `../changelog/implementation/COMPLETE_IMPLEMENTATION_GUIDE.md`
- **GitHub Actions：** [`../.github/workflows/sync-data.yml`](../.github/workflows/sync-data.yml)
