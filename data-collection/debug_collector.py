#!/usr/bin/env python3
"""
Debug 调试采集器 - 记录所有请求详情
用于分析 CloudBrush API 的数据格式
"""

import json
from pathlib import Path
from mitmproxy import http
from datetime import datetime
import base64

class DebugCollector:
    """调试采集器 - 记录所有请求和响应详情"""

    def __init__(self):
        self.output_dir = Path("./debug_logs")
        self.output_dir.mkdir(exist_ok=True)
        self.request_count = 0

        print("=" * 70)
        print("🔍 Debug 调试模式启动")
        print("=" * 70)
        print(f"📁 日志目录: {self.output_dir}")
        print("🎯 将记录所有 sfapi.fanglige.com 的请求")
        print("=" * 70)

    def request(self, flow: http.HTTPFlow) -> None:
        """记录所有请求"""
        if "sfapi.fanglige.com" not in flow.request.host:
            return

        self.request_count += 1
        timestamp = datetime.now().strftime("%H%M%S")

        # 记录请求详情
        request_info = {
            "timestamp": datetime.now().isoformat(),
            "method": flow.request.method,
            "url": flow.request.pretty_url,
            "host": flow.request.host,
            "path": flow.request.path,
            "query_params": dict(flow.request.query),
            "headers": dict(flow.request.headers),
            "content_type": flow.request.headers.get("content-type", ""),
            "body_preview": None
        }

        # 尝试解析请求体
        if flow.request.content:
            try:
                if "json" in request_info["content_type"]:
                    request_info["body"] = json.loads(flow.request.content)
                else:
                    request_info["body_preview"] = flow.request.content[:200].decode('utf-8', errors='ignore')
            except:
                request_info["body_preview"] = f"[Binary data, {len(flow.request.content)} bytes]"

        # 尝试解码 query 参数中的 base64
        decoded_params = {}
        for key, value in request_info["query_params"].items():
            try:
                decoded = base64.b64decode(value).decode('utf-8', errors='ignore')
                if decoded and len(decoded) < 100:  # 可能是汉字
                    decoded_params[f"{key}_decoded"] = decoded
            except:
                pass

        if decoded_params:
            request_info["decoded_params"] = decoded_params

        # 保存请求日志
        log_file = self.output_dir / f"request_{timestamp}_{self.request_count:03d}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(request_info, f, indent=2, ensure_ascii=False)

        print(f"\n📥 请求 #{self.request_count}: {flow.request.method} {flow.request.path}")
        print(f"   URL: {flow.request.pretty_url}")
        if decoded_params:
            print(f"   🔓 解码参数: {decoded_params}")
        print(f"   💾 日志: {log_file.name}")

    def response(self, flow: http.HTTPFlow) -> None:
        """记录所有响应"""
        if "sfapi.fanglige.com" not in flow.request.host:
            return

        timestamp = datetime.now().strftime("%H%M%S")
        content_type = flow.response.headers.get("content-type", "")

        response_info = {
            "timestamp": datetime.now().isoformat(),
            "status_code": flow.response.status_code,
            "url": flow.request.pretty_url,
            "content_type": content_type,
            "content_length": len(flow.response.content),
            "headers": dict(flow.response.headers)
        }

        # 处理不同类型的响应
        if "image" in content_type:
            # 保存图片
            ext = content_type.split('/')[-1].split(';')[0]
            img_file = self.output_dir / f"image_{timestamp}_{self.request_count:03d}.{ext}"
            with open(img_file, 'wb') as f:
                f.write(flow.response.content)

            response_info["image_saved"] = str(img_file)
            print(f"📷 图片响应: {len(flow.response.content)} bytes -> {img_file.name}")

        elif "json" in content_type:
            # 解析 JSON
            try:
                response_data = json.loads(flow.response.content)
                response_info["body"] = response_data

                # 尝试找到汉字相关字段
                def find_chinese_chars(obj, path=""):
                    results = []
                    if isinstance(obj, dict):
                        for k, v in obj.items():
                            new_path = f"{path}.{k}" if path else k
                            # 检查值是否包含汉字
                            if isinstance(v, str) and any('\u4e00' <= c <= '\u9fff' for c in v):
                                results.append(f"{new_path} = {v}")
                            results.extend(find_chinese_chars(v, new_path))
                    elif isinstance(obj, list):
                        for i, item in enumerate(obj):
                            results.extend(find_chinese_chars(item, f"{path}[{i}]"))
                    return results

                chinese_fields = find_chinese_chars(response_data)
                if chinese_fields:
                    response_info["chinese_fields"] = chinese_fields
                    print(f"🔍 JSON响应 - 发现汉字字段:")
                    for field in chinese_fields[:5]:  # 显示前5个
                        print(f"   {field}")

            except Exception as e:
                response_info["parse_error"] = str(e)
                print(f"⚠️  JSON解析失败: {e}")

        else:
            response_info["body_preview"] = flow.response.content[:200].decode('utf-8', errors='ignore')

        # 保存响应日志
        log_file = self.output_dir / f"response_{timestamp}_{self.request_count:03d}.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(response_info, f, indent=2, ensure_ascii=False)

        print(f"   💾 响应日志: {log_file.name}")


# mitmproxy addon 注册
addons = [DebugCollector()]


"""
使用方法:
=========
mitmweb -s debug_collector.py -p 8080

这会记录所有 CloudBrush API 的详细信息到 debug_logs/ 目录
查看日志就能知道 API 的实际数据格式
"""
