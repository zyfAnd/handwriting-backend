# Mac 远程控制 iPhone 方案

## 问题分析

由于磁盘空间不足，无法安装 Appium。我们需要使用 macOS 自带工具来实现完全自动化。

## 💡 可行的完全自动化方案

### 方案 1：使用 iPhone Mirroring（macOS Sequoia 15+）

如果你的 Mac 是 macOS Sequoia，可以使用 iPhone 镜像功能：

1. **启用 iPhone Mirroring**
   - 系统设置 → iPhone Mirroring
   - 连接你的 iPhone

2. **使用 AppleScript 控制**
   ```applescript
   tell application "System Events"
       tell process "iPhone Mirroring"
           click at {x, y}  -- 点击汉字
           delay 1
           key code 53  -- ESC 返回
           delay 0.5
       end tell
   end tell
   ```

3. **循环执行 3500 次**

**缺点**: 需要 macOS 15+ 和配对的 iPhone

---

### 方案 2：使用 Xcode 的 Simulator（推荐）

虽然 CloudBrush 可能没有 simulator 版本，但我们可以：

1. **检查是否有模拟器版本的 App**
2. **或者直接在模拟器中安装 IPA**

让我帮你检查...

---

### 方案 3：最简单 - 使用 Python 脚本批量调用 API

既然我们已经知道 API 的调用方式，我可以创建一个脚本：

1. **批量调用 API 查询 3500 个汉字**
2. **虽然响应加密，但会触发服务器端图片准备**
3. **然后我们可以尝试推测图片 URL 规律**

基于已下载的图片分析：
- `59/2jsl.png`, `59/2jsm.png` ...
- `62/2omf.png`, `62/2omg.png` ...
- `26/144u.png`, `26/144v.png` ...

文件名可能是某种编码规律。

---

### 方案 4：使用录屏宏工具

Mac 上有轻量级的宏工具可以录制和重放操作：

**使用 macOS 自带的 Automator**:

1. 打开 Automator
2. 新建"工作流程"
3. 添加动作：
   - 运行 AppleScript
   - 控制 QuickTime 录屏窗口
   - 模拟鼠标点击

**缺点**: 无法直接控制 iPhone

---

## 🚀 我推荐的实际方案

### 组合方案：API 批量查询 + 图片 URL 推测

让我分析已下载图片的规律，尝试找出文件名编码方式：

1. **分析已有图片**
2. **找出编码规律**
3. **批量生成所有可能的 URL**
4. **并发下载（自动跳过 404）**

这样可以完全自动化，不需要 iPhone 交互！

让我现在就开始分析...

---

## 📊 已有数据分析

从你已下载的图片来看：

```
26/144u.png, 26/144v.png, 26/144w.png
59/2jsl.png, 59/2jsm.png, 59/2jsn.png, ...
62/2omf.png, 62/2omg.png, 62/2omh.png, ...
```

**观察**:
- 文件夹 ID: 26, 59, 62
- 文件名: 4 位字符 (数字+字母组合)

**问题**: 无法直接推测文件名与汉字的对应关系

**解决**: 需要继续用 mitmproxy 捕获实际 URL

---

## ✅ 最终建议

由于完全自动化需要：
1. iOS 自动化工具（需要磁盘空间安装 Appium）
2. 或者 iPhone 内置的辅助功能自动化

**最快的解决方案仍然是使用 iPhone 的切换控制**：

### 设置步骤（5 分钟）

1. **iPhone: 设置 → 辅助功能 → 切换控制 → 开启**

2. **添加开关 → 屏幕 → 轻点**

3. **配方 → 创建新配方**
   - 名称: "自动浏览"
   - 添加手势: 点击中间 → 等待 1 秒 → 返回 → 滑动
   - 重复: 9999 次

4. **在 CloudBrush 中启动配方**

5. **放置 iPhone，让它自动运行 2 小时**

---

这是目前**唯一**不需要安装额外软件，且能完全自动化的方案。

你要我帮你创建这个配置的详细图文教程吗？
