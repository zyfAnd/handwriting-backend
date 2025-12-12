#!/bin/bash
# CloudBrush API 采集脚本启动器

cd "$(dirname "$0")"

# 激活虚拟环境
if [ -d "../venv" ]; then
    source ../venv/bin/activate
else
    echo "❌ 虚拟环境不存在，请先运行: python3 -m venv ../venv && source ../venv/bin/activate && pip install requests tqdm"
    exit 1
fi

# 检查 token
if [ -z "$CLOUDBRUSH_TOKEN" ]; then
    echo "📋 未设置 CLOUDBRUSH_TOKEN 环境变量"
    echo ""
    echo "请从 Charles 获取 token，然后执行："
    echo "  export CLOUDBRUSH_TOKEN='你的token值'"
    echo "  $0"
    echo ""
    echo "或者直接运行（会提示输入 token）："
    echo "  $0"
    echo ""
    read -p "是否现在输入 token？(y/n): " answer
    if [ "$answer" = "y" ] || [ "$answer" = "Y" ]; then
        read -p "请输入 token: " token
        export CLOUDBRUSH_TOKEN="$token"
    else
        echo "❌ 需要 token 才能继续"
        exit 1
    fi
fi

# 执行采集脚本
echo "🚀 开始执行采集脚本..."
echo ""
python3 api_collector.py
