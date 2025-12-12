#!/bin/bash
# 自动下载监控脚本
# 监控 URL 文件变化，自动触发下载

cd /Volumes/thinkplus-1T/my-github/handwriting-backend/data-collection
source ../venv/bin/activate

echo "=========================================="
echo "  自动下载监控已启动"
echo "=========================================="
echo ""
echo "📊 监控文件: auto_extracted_urls.txt"
echo "📁 下载目录: collected_characters/"
echo ""
echo "策略: 每新增 50 个 URL 自动下载一次"
echo ""
echo "按 Ctrl+C 停止"
echo ""

last_count=0
download_threshold=50

while true; do
  # 读取当前 URL 数量
  current_count=$(wc -l < auto_extracted_urls.txt 2>/dev/null || echo "0")
  new_count=$((current_count - last_count))

  if [ "$current_count" -gt "$last_count" ]; then
    echo "[$(date '+%H:%M:%S')] 📈 URL 数量: $current_count (+$new_count)"

    # 检查是否达到下载阈值
    if [ $((current_count / download_threshold)) -gt $((last_count / download_threshold)) ]; then
      echo ""
      echo "=========================================="
      echo "  触发自动下载 (达到 $current_count 个 URL)"
      echo "=========================================="
      echo ""

      python3 download_from_urls.py auto_extracted_urls.txt

      # 统计已下载图片
      downloaded=$(ls collected_characters/*.png 2>/dev/null | wc -l)
      echo ""
      echo "✅ 已下载图片: $downloaded"
      echo "📊 进度: $current_count / 3500 ($(echo "scale=2; $current_count * 100 / 3500" | bc)%)"
      echo ""
    fi

    last_count=$current_count
  fi

  # 每 10 秒检查一次
  sleep 10
done
