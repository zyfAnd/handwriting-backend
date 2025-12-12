#!/usr/bin/env python3
"""快速测试脚本 - 直接尝试采集"""

import os
import sys
import base64
import time
import random
import string
import requests
import json
import re

# Token
token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NodWh1YXNob3cuZmFuZ2xpZ2UuY29tL2FwaS92My9hdXRoL3JlZnJlc2hUb2tlbiIsImlhdCI6MTc2MzIwNjIzMCwiZXhwIjoxNzY4NDY1OTUyLCJuYmYiOjE3NjMyODE5NTIsImp0aSI6IkQ3bzNVZ1Y5bDVIQnlHZVoiLCJzdWIiOjY4NTMwMDAsInBydiI6IjQ4ZTQ1MzgzMWNlYmE1ZTU3YTQ3NWU2ODY0OWNmZGVlNmU5N2Q4ZDIifQ.k5Zgr8DnCDSjV66BCUK8xTI98KImyFXbP5_0vj0E950'

# 测试字符
test_char = '水'

print(f"测试字符: '{test_char}'")
print()

# 构建请求
cn_char_base64 = base64.b64encode(test_char.encode('utf-8')).decode('utf-8')

url = f"https://sfapi.fanglige.com/class/action.php"
params = {
    'api': 'queryDict',
    'cnChar': cn_char_base64,
    'fontId': '-1',
    'limit': '24',
    'page': '1',
    'src': '0'
}

headers = {
    'Authorization': f'Bearer {token}',
    'Accept': 'application/json',
    'X-Client-OS': 'ios',
    'timeStamp': str(int(time.time())),
    'locale': 'zh',
    'requestId': ''.join(random.choices(string.ascii_lowercase + string.digits, k=16)),
    'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
    'User-Agent': 'CloudBrush/2.9.9 (iPhone; iOS 17.6.1; Scale/2.00)',
    'X-App-Build': '307',
    'X-App-Version': '2.9.9',
    'X-Channel': 'AppStore',
}

print("发送请求...")
response = requests.get(url, params=params, headers=headers)

print(f"状态码: {response.status_code}")
print(f"Content-Type: {response.headers.get('content-type')}")
print()

# 打印响应
print("响应内容（前 500 字符）:")
print(response.text[:500])
print()

# 尝试解析 JSON
try:
    data = response.json()
    print("✅ 成功解析为 JSON")
    print(f"JSON 结构: {json.dumps(data, indent=2, ensure_ascii=False)[:500]}")

    # 检查是否是加密响应
    if isinstance(data, dict) and 'iv' in data and 'value' in data:
        print()
        print("⚠️  这是一个加密的响应（Laravel encryption）")
        print("   需要解密密钥才能读取数据")
        print()
        print("   可能的解决方案:")
        print("   1. 从 App 中提取解密密钥")
        print("   2. 使用抓包方式，直接获取 App 显示的图片 URL")
        print("   3. 反编译 App 查看加密逻辑")

except json.JSONDecodeError:
    print("❌ 无法解析为 JSON")

    # 尝试从文本中提取 URL
    url_pattern = r'https?://[^\s"\'<>]+'
    urls = re.findall(url_pattern, response.text)

    if urls:
        print(f"找到 {len(urls)} 个 URL:")
        for u in urls[:5]:
            print(f"  - {u}")
    else:
        print("未找到任何 URL")
