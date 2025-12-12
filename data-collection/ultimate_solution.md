# 终极自动化解决方案

## 🎯 分析结论

经过分析，完全自动化采集面临的核心问题：

1. ✅ API 可以调用（token 有效）
2. ❌ API 响应加密（无法直接获取图片 URL）
3. ✅ 图片 URL 可以直接访问
4. ❌ 图片文件名是编码的（如 `2jsl`, `2omf`），无法推测规律
5. ✅ mitmproxy 可以捕获实际的图片请求

## 💡 最佳自动化方案

### 方案：使用 iOS 录制宏 + mitmproxy

**核心思路**：
- iOS 的辅助功能可以录制触摸操作
- 录制一次"点击→等待→返回→滑动"的操作
- 设置重复播放 3500 次
- mitmproxy 自动捕获所有图片 URL

### 详细步骤

#### 1. 设置 iOS 辅助触控

在 iPhone 上：

1. **设置 → 辅助功能 → 触控 → 辅助触控** → 打开

2. **自定义顶层菜单**
   - 点击"自定"
   - 添加"录制手势"

3. **录制手势**：
   - 点击"录制手势"
   - 执行以下动作：
     1. 点击屏幕中间（打开汉字）
     2. 等待 1 秒
     3. 点击返回键位置
     4. 向左滑动（下一个字）
   - 保存

4. **播放手势**：
   - 打开 CloudBrush，进入汉字列表
   - 点击辅助触控按钮
   - 选择刚录制的手势
   - 手势会重复播放

#### 2. 启动自动化循环

**在 Mac 上**：

```bash
# 终端 1: 运行 mitmproxy（已在运行）
cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection
mitmweb -s smart_collector.py -p 8080 --web-host 0.0.0.0

# 终端 2: 实时监控 URL 采集
watch -n 3 'wc -l auto_extracted_urls.txt'

# 终端 3: 自动下载（每 5 分钟运行一次）
while true; do
  python3 download_from_urls.py auto_extracted_urls.txt
  sleep 300
done
```

**在 iPhone 上**：

1. 打开 CloudBrush
2. 进入汉字浏览页面
3. 启动辅助触控手势播放
4. 放置 iPhone，让它自动运行

**预计时间**：
- 每个字 2 秒 = 3500 字 × 2 秒 = 约 2 小时
- 完全无需人工干预

---

## 🚀 更快的方案：使用 Python + iOS 自动化库

由于磁盘空间不足无法安装 Appium，我们可以用轻量级的方案：

### 使用 `pyidevice` （比 Appium 小）

```bash
# 在外接硬盘上安装（避免占用系统盘空间）
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
source venv/bin/activate

# 安装轻量级 iOS 控制库
pip install --target=/Volumes/thinkplus-1T/python-packages pyidevice
```

然后用 Python 脚本控制 iPhone：

```python
import sys
sys.path.insert(0, '/Volumes/thinkplus-1T/python-packages')

from pyidevice import usbmux
from pyidevice.instruments import InstrumentsService

# 控制 iPhone 模拟点击
# 自动浏览 3500 个汉字
```

---

## ⚡ 最快实现方案（推荐）

### 组合使用：半自动 + 批处理

**Step 1**: 使用 iOS 辅助触控自动化（上面的方案）

**Step 2**: 同时运行自动下载脚本

我来创建一个自动下载监控脚本：

```bash
#!/bin/bash
# auto_download_loop.sh

cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection
source ../venv/bin/activate

echo "🚀 启动自动下载监控..."
echo ""

last_count=0

while true; do
  current_count=$(wc -l < auto_extracted_urls.txt 2>/dev/null || echo "0")

  if [ "$current_count" -gt "$last_count" ]; then
    echo "[$(date '+%H:%M:%S')] 发现新 URL: $current_count (新增 $((current_count - last_count)))"

    # 每增加 50 个 URL 就下载一次
    if [ $((current_count % 50)) -eq 0 ]; then
      echo "📥 开始下载..."
      python3 download_from_urls.py auto_extracted_urls.txt
      echo "✅ 下载完成"
    fi

    last_count=$current_count
  fi

  sleep 10
done
```

---

## 📋 执行清单

### 现在立即执行：

- [ ] **1. 保持 mitmproxy 运行**（已在运行 ✅）

- [ ] **2. iPhone 设置辅助触控手势**
  - 设置 → 辅助功能 → 触控 → 辅助触控
  - 录制"点击中间→等待→返回→滑动"手势

- [ ] **3. 在 Mac 上启动自动下载脚本**
  ```bash
  chmod +x auto_download_loop.sh
  ./auto_download_loop.sh
  ```

- [ ] **4. 在 iPhone 上启动自动播放**
  - 打开 CloudBrush
  - 播放录制的手势
  - 让它自动运行 2 小时

- [ ] **5. 等待完成** ☕

---

## 🎁 备选方案：如果辅助触控不支持重复

可以使用 **Switch Control**（切换控制）：

1. **设置 → 辅助功能 → 切换控制**
2. **开关 → 添加新开关 → 屏幕**
3. **录制新手势 → 自定**
4. **配方 → 创建新配方**
   - 动作：自定手势
   - 重复：无限次

这样可以无限重复执行手势！

---

## 💡 我的建议

**立即使用辅助触控或切换控制方案**

理由：
- ✅ 不需要安装任何软件（系统自带）
- ✅ 完全自动化（录制一次，自动重复）
- ✅ mitmproxy 已经在运行
- ✅ 2 小时内完成全部采集

你现在就可以开始设置 iPhone 的辅助触控了！
