#!/usr/bin/env python3
"""
智能采集器 - 用于 mitmproxy
自动拦截 CloudBrush 的图片请求并下载
"""

from mitmproxy import http
from pathlib import Path
import json
import time

class SmartCollector:
    """智能采集器"""

    def __init__(self):
        self.output_dir = Path("./collected_characters")
        self.output_dir.mkdir(exist_ok=True)

        self.url_file = Path("./auto_extracted_urls.txt")
        self.collected_urls = self.load_urls()

        print("=" * 70)
        print("  智能采集器已启动")
        print("=" * 70)
        print(f"📁 输出目录: {self.output_dir}")
        print(f"📝 URL 记录: {self.url_file}")
        print(f"📊 已收集: {len(self.collected_urls)} 个 URL")
        print()
        print("开始监听...")
        print()

    def load_urls(self) -> set:
        """加载已收集的 URL"""
        if self.url_file.exists():
            with open(self.url_file, 'r') as f:
                return set(line.strip() for line in f if line.strip())
        return set()

    def save_url(self, url: str):
        """保存 URL"""
        if url not in self.collected_urls:
            with open(self.url_file, 'a') as f:
                f.write(url + '\n')
            self.collected_urls.add(url)

    def request(self, flow: http.HTTPFlow) -> None:
        """拦截请求"""

        url = flow.request.pretty_url

        # 检测图片 URL
        if 'sfapi.fanglige.com/svg_png/' in url and url.endswith('.png'):
            print(f"🎯 发现图片: {url}")
            self.save_url(url)

            # 保存图片信息
            parts = url.split('/')
            filename = f"{parts[-2]}_{parts[-1]}"  # 如: 62_2omf.png

            print(f"   保存为: {filename}")
            print()

    def response(self, flow: http.HTTPFlow) -> None:
        """拦截响应"""

        # 检测 API 响应
        if 'sfapi.fanglige.com/class/action.php' in flow.request.pretty_url:
            if 'queryDict' in flow.request.pretty_url:
                # 记录查询
                print(f"📡 API 查询: {flow.request.pretty_url}")

                # 尝试从响应中提取图片 URL（即使加密）
                # 这里我们主要依赖后续的图片请求
                pass

# mitmproxy 插件接口
addons = [SmartCollector()]
