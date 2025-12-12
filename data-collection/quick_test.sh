#!/bin/bash
# 快速测试脚本 - 启动调试模式

cd "$(dirname "$0")"

echo "=========================================="
echo "🔍 启动 Debug 调试模式"
echo "=========================================="
echo ""
echo "📱 iPhone 配置:"
echo "   代理: $(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -n 1):8080"
echo ""
echo "🌐 mitmproxy Web 界面:"
echo "   http://localhost:8081"
echo ""
echo "📁 日志目录: ./debug_logs"
echo ""
echo "=========================================="
echo ""
echo "现在在 iPhone 上打开 CloudBrush，浏览 2-3 个汉字"
echo "然后按 Ctrl+C 停止，我们查看日志"
echo ""

# 清理旧日志
rm -rf debug_logs
mkdir -p debug_logs

# 启动 mitmweb
mitmweb -s debug_collector.py -p 8080 --web-port 8081 --no-web-open-browser
