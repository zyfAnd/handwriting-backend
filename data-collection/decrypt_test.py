#!/usr/bin/env python3
"""测试解析加密响应"""

import json
import base64

# 从响应中获取的字符串
response_text = '"eyJpdiI6Ikc4eVhJMHJ2TXR5VnZpc1F5dWZ5bWc9PSIsInZhbHVlIjoiZ0VRcWYxUHdwMFczRjd3YnF4QkxPMFlLdWw3ZE9xUEdvSFBWVGd3aTl6bVE4OGhlTnpVemRkbjRzbFFzekVsd0N6Z1NEa05qS1lMZGxMN3B6SkVkUFpWVWZab2R4SDdWQmF5SHZoRFpxQndpNWZZTndYbGNOQWlBQWRJTTNhRjkiLCJtYWMiOiIzOGQxZmJmZTI3MDA5ZDMxOGZiMDE1Mjk2MThlOWExOWJjMmM0MzBhZWMzMDRiNjE4NGIxOWM2MGE5MzQxM2JkIn0="'

print("原始响应:")
print(response_text)
print()

# 去掉外层引号并解析
json_str = json.loads(response_text)
print("去掉引号后:")
print(json_str)
print()

# 解析加密数据结构
encrypted_data = json.loads(json_str)
print("加密数据结构:")
print(json.dumps(encrypted_data, indent=2))
print()

print("字段说明:")
print(f"  iv (初始化向量): {encrypted_data['iv']}")
print(f"  value (加密内容): {encrypted_data['value'][:50]}...")
print(f"  mac (消息认证码): {encrypted_data['mac']}")
print()

print("⚠️  这是 Laravel 的加密格式（AES-256-CBC）")
print("   需要 APP_KEY 才能解密")
print()
print("💡 建议的解决方案:")
print("   1. 使用抓包方式 - enhanced_collector.py （通过 mitmproxy）")
print("   2. 从 Charles 中直接获取解密后的图片 URL")
print("   3. 反编译 App 获取 APP_KEY")
