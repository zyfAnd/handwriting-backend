# iPhone 配置指南 - mitmproxy

## 📱 完整配置步骤

### 第一步：获取你的 Mac IP 地址

在 Mac 上运行：

```bash
ifconfig | grep "inet " | grep -v 127.0.0.1
```

找到类似 `192.168.x.x` 的地址，这就是你的 Mac IP。

---

### 第二步：在 Mac 上启动 mitmproxy

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
source venv/bin/activate
cd data-collection
mitmweb -s smart_collector.py -p 8080 --web-host 0.0.0.0
```

看到以下输出表示成功：
```
Web server listening at http://0.0.0.0:8081/
Proxy server listening at http://*:8080
```

**保持这个终端窗口运行！**

---

### 第三步：配置 iPhone Wi-Fi 代理

1. **打开 iPhone 设置**
   - 设置 → Wi-Fi

2. **点击已连接的 Wi-Fi 网络右边的 (i) 图标**

3. **向下滚动到「配置代理」**
   - 点击「配置代理」

4. **选择「手动」**

5. **填写代理信息**：
   - 服务器：`<你的 Mac IP>`（例如：192.168.1.100）
   - 端口：`8080`
   - 鉴定：关闭

6. **点击「存储」**

---

### 第四步：安装 mitmproxy 证书

**⚠️ 重要：必须完成这一步，否则无法拦截 HTTPS 流量！**

1. **在 iPhone Safari 中访问**：
   ```
   http://mitm.it
   ```

2. **点击「Apple」图标** 下载证书

3. **允许下载配置描述文件**
   - 会看到提示「描述文件已下载」

4. **安装证书**：
   - 设置 → 通用 → VPN 与设备管理
   - 点击「mitmproxy」
   - 点击「安装」
   - 输入密码
   - 点击「安装」（确认）
   - 点击「完成」

5. **启用证书信任** （关键步骤！）：
   - 设置 → 通用 → 关于本机
   - 向下滚动到最底部，点击「证书信任设置」
   - 找到「mitmproxy」，**打开开关**
   - 点击「继续」确认

---

### 第五步：测试连接

1. **在 iPhone Safari 中访问**：
   ```
   https://www.baidu.com
   ```

2. **在 Mac 的 mitmweb 界面中检查**：
   - 打开浏览器访问：`http://localhost:8081`
   - 应该能看到刚才的 baidu.com 请求

3. **如果看到请求，说明配置成功！** ✅

---

### 第六步：开始采集汉字图片

1. **打开 CloudBrush App**

2. **浏览汉字**：
   - 按部首/笔画浏览
   - 或者搜索汉字
   - 每个字停留 1-2 秒

3. **在 Mac 终端中看到输出**：
   ```
   🎯 发现图片: https://sfapi.fanglige.com/svg_png/62/2omf.png
      保存为: 62_2omf.png
   ```

4. **持续浏览**，mitmproxy 会自动记录所有图片 URL

---

### 第七步：批量下载图片

当你浏览了足够多的汉字后：

1. **停止 mitmproxy**：
   - 在 Mac 终端按 `Ctrl+C`

2. **查看收集到的 URL**：
   ```bash
   cat auto_extracted_urls.txt
   ```

3. **批量下载**：
   ```bash
   python3 download_from_urls.py auto_extracted_urls.txt
   ```

---

### 第八步：采集完成后，恢复 iPhone 网络

1. **设置 → Wi-Fi → (i) 图标**

2. **配置代理 → 关闭**

3. **（可选）删除 mitmproxy 证书**：
   - 设置 → 通用 → VPN 与设备管理
   - 点击「mitmproxy」→ 删除描述文件

---

## 🔧 常见问题

### Q1: Safari 访问 mitm.it 显示无法连接

**原因**：代理配置不正确

**解决**：
- 检查 Mac IP 是否正确
- 检查 iPhone 和 Mac 是否在同一 Wi-Fi 网络
- 检查 mitmproxy 是否正在运行

### Q2: 访问 https 网站显示证书错误

**原因**：未安装或未信任 mitmproxy 证书

**解决**：
- 重新执行「第四步」的步骤 5（证书信任设置）
- 确保开关已打开

### Q3: CloudBrush App 无法联网

**原因**：证书未正确配置

**解决**：
- 检查「设置 → 通用 → 关于本机 → 证书信任设置」
- 确保 mitmproxy 证书的开关是**绿色**的

### Q4: mitmproxy 没有捕获到图片请求

**原因**：图片可能已缓存

**解决**：
- 在 CloudBrush 中浏览**新的汉字**
- 或者清除 App 缓存后重试

---

## 📊 预计采集时间

- **3500 个汉字**
- **每个停留 2 秒**
- **总计约 2 小时**
- **可以分 10 次完成**，每次 20 分钟

---

## 💡 提示

1. **浏览速度不要太快**
   - 每个字停留 1-2 秒
   - 确保 App 加载完图片

2. **定期检查采集进度**
   ```bash
   wc -l auto_extracted_urls.txt
   ```

3. **可以边采集边下载**
   - 不需要等到全部采集完
   - 每采集 100 个 URL 就可以运行一次下载

4. **支持断点续传**
   - `auto_extracted_urls.txt` 会追加新 URL
   - `download_from_urls.py` 会跳过已下载的图片

---

## ✅ 准备就绪

现在可以开始了！按照以下顺序执行：

1. ✅ mitmproxy 已安装
2. ⏭️ 获取 Mac IP 地址
3. ⏭️ 启动 mitmproxy
4. ⏭️ 配置 iPhone 代理
5. ⏭️ 安装并信任证书
6. ⏭️ 测试连接
7. ⏭️ 开始采集
