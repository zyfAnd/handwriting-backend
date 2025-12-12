# 数据采集和上传指南

## 🎯 概述

本指南将帮助你完成：
1. ✅ **数据采集** - 从 CloudBrush App 采集汉字图片
2. ✅ **数据上传** - 上传图片到 Cloudflare R2

## 📋 前置要求

- Python 3.8+
- Cloudflare 账号（用于 R2 存储）
- iPhone + CloudBrush App（用于数据采集）

## 🚀 快速开始

### 阶段一：数据采集

```bash
# 1. 安装依赖
cd /Volumes/thinkplus-1T/my-github/handwriting-backend
pip install -r requirements.txt

# 2. 启动抓包工具
cd data-collection
mitmweb -s enhanced_collector.py -p 8080

# 3. 配置 iPhone（详见 data-collection/README.md）
# - 设置代理：你的电脑IP:8080
# - 安装证书：访问 mitm.it

# 4. 打开 CloudBrush App，开始浏览汉字
# 脚本会自动保存图片到 collected_characters/ 目录
```

**预计时间**：1-2小时（3000字）

### 阶段二：数据上传

```bash
# 1. 配置 Cloudflare R2（详见 data-upload/README.md）
# - 创建 R2 Bucket
# - 生成 API Token
# - 设置环境变量

# 2. 执行上传
cd data-upload
python3 upload_to_cloud.py

# 3. 配置公开访问
# - 在 Cloudflare Dashboard 启用 R2.dev 域名
```

**预计时间**：30分钟

## 📁 目录结构

```
handwriting-backend/
├── data-collection/          # 数据采集模块
│   ├── enhanced_collector.py # 抓包脚本
│   ├── common_3500_chars.txt # 常用字列表
│   ├── collected_characters/ # 采集的图片（自动创建）
│   └── README.md
│
├── data-upload/              # 数据上传模块
│   ├── upload_to_cloud.py    # 上传脚本
│   ├── cdn_url_mapping.json  # CDN映射（上传后生成）
│   └── README.md
│
└── requirements.txt          # Python 依赖
```

## 📖 详细文档

- **数据采集**：查看 `data-collection/README.md`
- **数据上传**：查看 `data-upload/README.md`
- **完整指南**：查看 `changelog/ implementation/COMPLETE_IMPLEMENTATION_GUIDE.md`

## ✅ 检查清单

### 数据采集完成检查

- [ ] 已安装 mitmproxy
- [ ] iPhone 代理配置正确
- [ ] 证书已安装并信任
- [ ] 采集了至少 1000+ 个汉字图片
- [ ] `collected_characters/` 目录中有图片文件
- [ ] `char_url_mapping.json` 文件已生成

### 数据上传完成检查

- [ ] Cloudflare R2 Bucket 已创建
- [ ] API Token 已生成并配置
- [ ] 环境变量已设置
- [ ] 图片已成功上传到 R2
- [ ] `cdn_url_mapping.json` 文件已生成
- [ ] R2 公开访问已启用
- [ ] 可以通过 URL 访问图片

## 📞 下一步

完成数据采集和上传后，你可以：

1. **部署 API** - 使用 Cloudflare Worker 创建搜索 API
2. **部署前端** - 创建搜索界面
3. **查看完整实现** - 参考 `changelog/ implementation/` 目录
