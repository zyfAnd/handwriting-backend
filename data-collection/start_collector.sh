#!/bin/bash
# 启动汉字采集可视化界面

set -e

echo "=========================================="
echo "🚀 启动汉字采集可视化系统"
echo "=========================================="

# 检查 Python 版本
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误: 未找到 python3"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✅ Python: $PYTHON_VERSION"

# 检查 Python 版本是否兼容
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 13 ]; then
    echo "⚠️  警告: Python 3.13+ 可能与某些依赖包不兼容"
    echo "   建议使用 Python 3.11 或 3.12"
    echo ""

    # 检查是否有 Python 3.12
    if command -v python3.12 &> /dev/null; then
        echo "✅ 发现 Python 3.12，建议使用: python3.12 web_collector.py"
        read -p "是否使用 Python 3.12? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            PYTHON_CMD="python3.12"
        else
            PYTHON_CMD="python3"
        fi
    else
        echo "   继续使用 Python $PYTHON_VERSION..."
        PYTHON_CMD="python3"
    fi
else
    PYTHON_CMD="python3"
fi

# 检查并安装依赖
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    $PYTHON_CMD -m venv venv
fi

echo "🔧 激活虚拟环境..."
source venv/bin/activate

echo "📦 安装依赖..."
echo "   这可能需要几分钟..."
pip install --upgrade pip setuptools wheel

# 尝试安装依赖，如果失败提供替代方案
if ! pip install -r requirements.txt; then
    echo ""
    echo "❌ 依赖安装失败"
    echo ""
    echo "可能的解决方案:"
    echo "1. 使用 Python 3.11 或 3.12:"
    echo "   brew install python@3.12"
    echo "   python3.12 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -r requirements.txt"
    echo ""
    echo "2. 或者跳过 mitmproxy，手动安装："
    echo "   pip install Flask Flask-SocketIO gevent gevent-websocket requests"
    echo "   brew install mitmproxy  # 使用系统包管理器安装"
    echo ""
    exit 1
fi

# 检查是否存在常用字列表
if [ ! -f "common_3500_chars.txt" ]; then
    echo "⚠️  未找到 common_3500_chars.txt"
    echo "   使用默认常用字列表..."
fi

# 获取本机 IP
LOCAL_IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1)

echo ""
echo "=========================================="
echo "✅ 准备就绪！"
echo "=========================================="
echo ""
echo "📊 Web 界面: http://localhost:5000"
echo "   访问此地址查看采集进度"
echo ""
echo "📱 iPhone 代理配置:"
echo "   服务器: ${LOCAL_IP}"
echo "   端口: 8080"
echo ""
echo "🔒 证书安装:"
echo "   在 iPhone 上访问: http://mitm.it"
echo "   安装并信任证书"
echo ""
echo "=========================================="
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

# 启动 Web 界面
$PYTHON_CMD web_collector.py
