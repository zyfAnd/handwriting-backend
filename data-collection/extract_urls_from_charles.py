#!/usr/bin/env python3
"""
从 Charles 导出的会话文件中提取图片 URL
支持 JSON 和 HAR 格式
"""

import json
import sys
import re
from pathlib import Path
from typing import List, Set

def extract_urls_from_json(data, urls: Set[str], char_map: dict):
    """递归提取 JSON 中的图片 URL"""

    if isinstance(data, dict):
        # 检查是否包含图片 URL
        for key, value in data.items():
            if isinstance(value, str):
                # 查找图片 URL
                if 'svg_png' in value and '.png' in value:
                    # 补全 URL（如果是相对路径）
                    if value.startswith('http'):
                        urls.add(value)
                    elif value.startswith('/'):
                        urls.add(f'https://sfapi.fanglige.com{value}')
                    else:
                        urls.add(f'https://sfapi.fanglige.com/{value}')

                # 尝试提取汉字名称
                if key in ['name', 'char', 'character', 'word']:
                    # 关联汉字和 URL（后续可能用到）
                    pass

            # 递归处理
            extract_urls_from_json(value, urls, char_map)

    elif isinstance(data, list):
        for item in data:
            extract_urls_from_json(item, urls, char_map)

def extract_from_charles_session(file_path: str) -> tuple[Set[str], dict]:
    """从 Charles 会话文件中提取图片 URL"""

    urls = set()
    char_map = {}

    print(f"📂 读取文件: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print("🔍 提取图片 URL...")

    # 递归提取
    extract_urls_from_json(data, urls, char_map)

    return urls, char_map

def extract_from_response_text(response_text: str) -> Set[str]:
    """从响应文本中提取图片 URL（使用正则）"""

    urls = set()

    # 正则模式
    patterns = [
        r'https?://sfapi\.fanglige\.com/svg_png/[^"\s]+\.png',
        r'/svg_png/\d+/[^"\s]+\.png',
        r'svg_png/\d+/[^"\s]+\.png',
    ]

    for pattern in patterns:
        matches = re.findall(pattern, response_text)
        for match in matches:
            if match.startswith('http'):
                urls.add(match)
            elif match.startswith('/'):
                urls.add(f'https://sfapi.fanglige.com{match}')
            else:
                urls.add(f'https://sfapi.fanglige.com/{match}')

    return urls

def save_urls(urls: Set[str], output_file: str):
    """保存 URL 列表到文件"""

    sorted_urls = sorted(urls)

    with open(output_file, 'w', encoding='utf-8') as f:
        for url in sorted_urls:
            f.write(url + '\n')

    print(f"💾 保存 {len(sorted_urls)} 个 URL 到: {output_file}")

def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 extract_urls_from_charles.py <charles_session.json>")
        print()
        print("示例:")
        print("  python3 extract_urls_from_charles.py charles_session.json")
        print("  python3 extract_urls_from_charles.py session.har")
        sys.exit(1)

    input_file = sys.argv[1]

    if not Path(input_file).exists():
        print(f"❌ 文件不存在: {input_file}")
        sys.exit(1)

    print("="*70)
    print("  从 Charles 会话中提取图片 URL")
    print("="*70)
    print()

    try:
        # 提取 URL
        urls, char_map = extract_from_charles_session(input_file)

        if not urls:
            print("⚠️  未找到任何图片 URL")
            print()
            print("可能的原因:")
            print("  1. Charles 会话中没有查询汉字的请求")
            print("  2. 导出格式不正确")
            print("  3. API 响应被加密（需要在 App 中查看才能解密）")
            sys.exit(1)

        # 保存结果
        output_file = "extracted_urls.txt"
        save_urls(urls, output_file)

        # 统计
        print()
        print("="*70)
        print("✅ 提取完成！")
        print("="*70)
        print(f"  图片 URL 数量: {len(urls)}")
        print(f"  保存位置: {output_file}")
        print()
        print("下一步:")
        print(f"  python3 download_from_urls.py {output_file}")
        print()

    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        print()
        print("请确保文件是有效的 JSON 格式")
        sys.exit(1)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
