# 🚀 快速开始 - 3 步完成批量采集

## 📌 你需要的

1. ✅ Python 3.6+
2. ✅ CloudBrush App 的 API Token（从 Charles 获取）

## 🎯 三步搞定

### 1️⃣ 获取 Token

在 Charles 中找到 CloudBrush 的请求：
- 地址：`sfapi.fanglige.com/class/action.php?api=queryDict`
- Header：`Authorization: Bearer xxxxx...`
- 复制 `Bearer` 后面的 token

### 2️⃣ 测试 Token

```bash
cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection
python3 test_token.py 'your_token_here'
```

看到 `✅ Token 有效！` 就可以继续了。

### 3️⃣ 开始采集

```bash
./run.sh 'your_token_here'
```

就这么简单！🎉

---

## 📖 详细文档

- **执行指南**：[EXECUTE.md](./EXECUTE.md) - 完整的执行步骤
- **使用指南**：[使用指南.md](./使用指南.md) - 详细的配置和说明
- **API 说明**：[API_TOKEN_GUIDE.md](./API_TOKEN_GUIDE.md) - Token 获取指南

---

## 🎁 采集结果

采集完成后，你会得到：

```
collected_characters/
├── 6c34_水.png              # 约 3500 个汉字图片
├── 4e00_一.png
├── ...
├── char_url_mapping.json   # 字符映射文件
└── collection_report.json  # 采集报告
```

---

## ⚡ 命令速查

```bash
# 测试 token
python3 test_token.py 'token'

# 采集（方式1 - 推荐）
./run.sh 'token'

# 采集（方式2）
export CLOUDBRUSH_TOKEN='token'
python3 api_collector.py

# 查看结果
ls collected_characters/*.png | wc -l
cat collected_characters/collection_report.json
```

---

**现在就开始吧！** 🚀
