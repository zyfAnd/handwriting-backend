#!/bin/bash

# CloudBrush 字符采集执行脚本
# 使用方法: ./run.sh "your_token_here"

set -e

echo "================================="
echo "  CloudBrush 字符批量采集工具"
echo "================================="
echo ""

# 切换到脚本所在目录
cd "$(dirname "$0")"

# 检查参数
if [ $# -eq 0 ]; then
    echo "⚠️  未提供 Token"
    echo ""
    echo "使用方法:"
    echo "  ./run.sh 'your_token_here'"
    echo ""
    echo "或者设置环境变量:"
    echo "  export CLOUDBRUSH_TOKEN='your_token_here'"
    echo "  ./run.sh"
    echo ""
    exit 1
fi

# 设置 Token
export CLOUDBRUSH_TOKEN="$1"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 未找到 python3，请先安装 Python 3"
    exit 1
fi

# 检查依赖
echo "📦 检查依赖..."
if ! python3 -c "import requests, tqdm" &> /dev/null; then
    echo "⚠️  缺少依赖，正在安装..."
    pip3 install requests tqdm
fi

echo "✅ 依赖检查完成"
echo ""

# 运行采集脚本
echo "🚀 开始采集..."
echo ""

python3 api_collector.py

echo ""
echo "================================="
echo "  采集完成！"
echo "================================="
