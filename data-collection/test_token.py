#!/usr/bin/env python3
"""
Token 测试脚本
用于快速验证 CloudBrush API Token 是否有效
"""

import sys
import os
import base64
import time
import random
import string
import requests


def test_token(token, api_base_url='https://sfapi.fanglige.com'):
    """测试 token 是否有效"""

    print("="*70)
    print("  CloudBrush API Token 测试工具")
    print("="*70)
    print()
    print(f"📡 API 地址: {api_base_url}")
    print(f"🔑 Token: {token[:20]}..." if len(token) > 20 else f"🔑 Token: {token}")
    print()

    # 创建 session
    session = requests.Session()

    # 设置 headers
    session.headers['Authorization'] = f'Bearer {token}'
    session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
    session.headers['Accept'] = 'application/json, image/png, */*'
    session.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    session.headers['X-Client-OS'] = 'ios'
    session.headers['timeStamp'] = str(int(time.time()))
    session.headers['locale'] = 'zh'
    session.headers['requestId'] = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))
    session.headers['X-App-Build'] = '307'
    session.headers['X-App-Version'] = '2.9.9'
    session.headers['X-Channel'] = 'AppStore'

    # 测试字符
    test_chars = ['水', '火', '木', '金', '土']

    print("🧪 开始测试...\n")

    success_count = 0

    for char in test_chars:
        try:
            # 构建请求
            cn_char_base64 = base64.b64encode(char.encode('utf-8')).decode('utf-8')

            endpoint = f"{api_base_url}/class/action.php"
            params = {
                'api': 'queryDict',
                'cnChar': cn_char_base64,
                'fontId': '-1',
                'limit': '24',
                'page': '1',
                'src': '0'
            }

            print(f"测试字符: '{char}'", end=' ... ')

            response = session.get(endpoint, params=params, timeout=10)

            # 检查响应
            if response.status_code == 200:
                content_type = response.headers.get('content-type', '')

                if content_type.startswith('image/'):
                    # 返回图片
                    size = len(response.content)
                    print(f"✅ 成功（图片，{size} bytes）")
                    success_count += 1

                elif content_type.startswith('application/json'):
                    # 返回 JSON
                    try:
                        data = response.json()
                        print(f"✅ 成功（JSON，{len(str(data))} chars）")
                        success_count += 1

                        # 打印部分响应（调试用）
                        if isinstance(data, dict):
                            keys = list(data.keys())[:5]
                            print(f"   响应字段: {keys}")
                    except:
                        print(f"⚠️  返回 JSON 但解析失败")
                        print(f"   响应: {response.text[:200]}")
                else:
                    print(f"⚠️  未知响应类型: {content_type}")
                    print(f"   响应: {response.text[:200]}")

            elif response.status_code == 401:
                print(f"❌ 认证失败（401）- Token 可能无效或过期")
                break

            elif response.status_code == 403:
                print(f"❌ 访问被拒绝（403）- Token 可能没有权限")
                break

            else:
                print(f"❌ 请求失败（状态码: {response.status_code}）")
                print(f"   响应: {response.text[:200]}")

        except requests.exceptions.Timeout:
            print(f"❌ 请求超时")

        except requests.exceptions.ConnectionError:
            print(f"❌ 连接失败 - 检查网络或 API 地址")

        except Exception as e:
            print(f"❌ 错误: {e}")

        # 延迟，避免请求过快
        time.sleep(0.5)

    # 总结
    print()
    print("="*70)
    print("📊 测试结果")
    print("="*70)
    print(f"   测试字符数: {len(test_chars)}")
    print(f"   成功: {success_count}")
    print(f"   失败: {len(test_chars) - success_count}")

    if success_count == len(test_chars):
        print()
        print("✅ Token 有效！可以开始批量采集")
        print()
        print("执行采集:")
        print(f"  export CLOUDBRUSH_TOKEN='{token}'")
        print(f"  python3 api_collector.py")
        return True

    elif success_count > 0:
        print()
        print("⚠️  部分成功，可能存在网络问题或 API 不稳定")
        print("   建议再次测试或调整请求参数")
        return False

    else:
        print()
        print("❌ Token 无效或 API 配置错误")
        print()
        print("可能的原因:")
        print("  1. Token 已过期 - 需要重新从 Charles 获取")
        print("  2. Token 格式不正确 - 检查是否完整复制")
        print("  3. API 地址错误 - 检查 API_BASE_URL")
        print("  4. Token Header 格式不对 - 可能需要调整")
        return False


def main():
    """主函数"""
    # 从环境变量或命令行参数获取 token
    token = None

    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = os.getenv('CLOUDBRUSH_TOKEN')

    if not token:
        print("❌ 未提供 Token")
        print()
        print("使用方法:")
        print("  python3 test_token.py 'your_token_here'")
        print()
        print("或者设置环境变量:")
        print("  export CLOUDBRUSH_TOKEN='your_token_here'")
        print("  python3 test_token.py")
        print()
        sys.exit(1)

    # 获取 API 地址
    api_base_url = os.getenv('CLOUDBRUSH_API_URL', 'https://sfapi.fanglige.com')

    # 执行测试
    success = test_token(token, api_base_url)

    # 返回退出码
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
