# iOS 完全自动化采集方案

## 🎯 目标

完全自动化浏览 CloudBrush App 中的 3500 个汉字，无需手动操作。

---

## 方案对比

| 方案 | 难度 | 效果 | 时间 |
|------|------|------|------|
| **A. iOS 快捷指令** | ⭐ 简单 | ✅ 可行 | 2小时 |
| **B. Appium 自动化** | ⭐⭐⭐ 复杂 | ✅✅ 最佳 | 30分钟 |
| **C. 手动+批量下载** | ⭐ 最简单 | ✅ 可行 | 2小时 |

---

## 🚀 推荐方案 A：iOS 快捷指令（最简单）

### 原理

使用 iOS 快捷指令自动点击和滑动 CloudBrush App，配合 mitmproxy 自动记录图片 URL。

### 步骤

#### 1. 创建快捷指令

在 iPhone 上打开「快捷指令」App，创建新快捷指令：

```
重复 100 次
  - 打开 App: CloudBrush
  - 等待 1 秒
  - 点击屏幕 (坐标: 中间位置)
  - 等待 2 秒
  - 向左滑动 (切换到下一个字)
  - 等待 1 秒
结束重复
```

#### 2. 配置辅助功能

- **设置 → 辅助功能 → 触控 → 辅助触控**
- 启用「辅助触控」
- 录制自定义手势

#### 3. 运行自动化

1. 确保 mitmproxy 正在运行
2. 打开 CloudBrush App
3. 运行快捷指令
4. iPhone 会自动浏览汉字

**缺点**：iOS 快捷指令不支持精确的 UI 操作

---

## 🏆 最佳方案 B：Appium 自动化（推荐）

### 原理

使用 Appium + WebDriverAgent 完全控制 iOS 设备，自动化浏览所有汉字。

### 安装步骤

#### 1. 安装依赖

```bash
# 安装 Appium
npm install -g appium

# 安装 iOS 驱动
appium driver install xcuitest

# 安装 Python 客户端
pip install Appium-Python-Client
```

#### 2. 配置 WebDriverAgent

```bash
# 克隆 WebDriverAgent
git clone https://github.com/appium/WebDriverAgent.git
cd WebDriverAgent

# 用 Xcode 打开
open WebDriverAgent.xcodeproj

# 配置签名
# - 选择 WebDriverAgentLib target
# - Signing & Capabilities → Team → 选择你的 Apple ID
# - 对 WebDriverAgentRunner 做同样操作

# 构建并安装到设备
xcodebuild -project WebDriverAgent.xcodeproj \
  -scheme WebDriverAgentRunner \
  -destination 'platform=iOS,id=<你的设备UDID>' \
  test
```

#### 3. 获取设备 UDID

```bash
# 连接 iPhone 到 Mac
# 运行
instruments -s devices

# 或者
system_profiler SPUSBDataType | grep "Serial Number"
```

#### 4. 创建自动化脚本

我来创建这个脚本...

---

## ⚡ 最快方案 C：优化手动浏览

### 技巧

1. **快速浏览模式**
   - 按部首浏览（每个部首有多个字）
   - 快速点击，每个字 0.5 秒
   - mitmproxy 自动记录

2. **分批进行**
   - 每次浏览 200 个字（约 2 分钟）
   - 运行下载命令
   - 休息一下，继续下一批

3. **预计时间**
   - 3500 字 ÷ 200 = 18 批
   - 每批 2 分钟 = 36 分钟总浏览时间
   - 加上下载时间，约 1 小时完成

### 执行命令

```bash
# 查看进度
watch -n 5 'wc -l auto_extracted_urls.txt'

# 每浏览 100 个字后运行
python3 download_from_urls.py auto_extracted_urls.txt
```

---

## 💡 我的建议

### 如果你想要最快完成：

**使用方案 C（优化手动浏览）**

理由：
- ✅ 无需额外配置
- ✅ mitmproxy 已经在运行
- ✅ 快速点击即可（每个字 0.5-1 秒）
- ✅ 实际只需 30-60 分钟

**操作流程**：

1. **在 CloudBrush 中快速点击浏览**
   - 不需要仔细看每个字
   - 只要点进去让图片加载即可
   - 快速返回，点下一个

2. **每 100 个字检查一次**
   ```bash
   wc -l auto_extracted_urls.txt
   ```

3. **每 200 个字下载一次**
   ```bash
   python3 download_from_urls.py auto_extracted_urls.txt
   ```

---

### 如果你想要完全自动化：

**使用方案 B（Appium）**

需要时间配置（约 30 分钟），但配置好后可以完全无人值守。

---

## 🤔 你的选择？

请告诉我你想用哪个方案，我可以帮你：

- **方案 A**: 创建 iOS 快捷指令配置
- **方案 B**: 创建 Appium 自动化脚本
- **方案 C**: 优化当前的半自动化流程
