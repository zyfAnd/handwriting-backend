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

echo "✅ Python: $(python3 --version)"

# 检查并安装依赖
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "🔧 激活虚拟环境..."
source venv/bin/activate

echo "📦 安装依赖..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

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
python3 web_collector.py
