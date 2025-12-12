#!/usr/bin/env python3
"""
从 URL 列表批量下载图片
"""

import sys
import requests
from pathlib import Path
from tqdm import tqdm
import time

def download_image(url: str, output_dir: Path, retry: int = 3) -> bool:
    """下载单个图片"""

    # 从 URL 中提取文件名
    # https://sfapi.fanglige.com/svg_png/26/144y.png -> 26_144y.png
    parts = url.split('/')
    filename = f"{parts[-2]}_{parts[-1]}"  # 26_144y.png

    output_path = output_dir / filename

    # 如果已存在，跳过
    if output_path.exists():
        return True

    # 重试下载
    for attempt in range(retry):
        try:
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"\n⚠️  {url} - 状态码: {response.status_code}")

        except Exception as e:
            if attempt < retry - 1:
                time.sleep(1)
            else:
                print(f"\n❌ {url} - 错误: {e}")
                return False

    return False

def load_urls(file_path: str) -> list:
    """加载 URL 列表"""

    with open(file_path, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip()]

    return urls

def main():
    """主函数"""

    if len(sys.argv) < 2:
        print("用法:")
        print("  python3 download_from_urls.py <urls.txt> [output_dir]")
        print()
        print("示例:")
        print("  python3 download_from_urls.py extracted_urls.txt")
        print("  python3 download_from_urls.py extracted_urls.txt ./images")
        sys.exit(1)

    urls_file = sys.argv[1]
    output_dir = Path(sys.argv[2] if len(sys.argv) > 2 else "./collected_characters")

    # 创建输出目录
    output_dir.mkdir(exist_ok=True)

    print("="*70)
    print("  批量下载图片")
    print("="*70)
    print()
    print(f"📂 URL 列表: {urls_file}")
    print(f"📁 保存目录: {output_dir}")
    print()

    # 加载 URL
    urls = load_urls(urls_file)

    if not urls:
        print("❌ URL 列表为空")
        sys.exit(1)

    print(f"📊 共 {len(urls)} 个图片")
    print()

    # 下载
    success = 0
    failed = 0

    with tqdm(total=len(urls), desc="下载进度") as pbar:
        for url in urls:
            if download_image(url, output_dir):
                success += 1
            else:
                failed += 1

            pbar.update(1)
            time.sleep(0.1)  # 避免请求过快

    # 统计
    print()
    print("="*70)
    print("✅ 下载完成！")
    print("="*70)
    print(f"  成功: {success}")
    print(f"  失败: {failed}")
    print(f"  保存位置: {output_dir}")
    print()

if __name__ == "__main__":
    main()
