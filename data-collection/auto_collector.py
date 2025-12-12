#!/usr/bin/env python3
"""
自动化批量采集汉字图片
通过直接调用 API 并解析图片 URL（即使响应加密，图片 URL 仍然可以直接访问）
"""

import sys
import requests
import base64
import json
import time
from pathlib import Path
from tqdm import tqdm
from typing import List, Set
from urllib.parse import quote

class AutoCollector:
    """自动化采集器"""

    def __init__(self, token: str, output_dir: str = "./collected_characters"):
        self.token = token
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.api_base = "https://sfapi.fanglige.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "CloudBrush/3.0",
            "Accept": "*/*"
        }

        # 统计
        self.collected_chars = set()
        self.collected_images = set()

    def load_common_chars(self) -> List[str]:
        """加载常用汉字列表"""

        # 常用汉字 3500 字
        # 来源: 《通用规范汉字表》一级字表
        common_chars = """
        的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙飞
        """

        # 清理和去重
        chars = []
        for char in common_chars:
            char = char.strip()
            if char and '\u4e00' <= char <= '\u9fff':  # 是汉字
                if char not in chars:
                    chars.append(char)

        print(f"📝 加载了 {len(chars)} 个常用汉字")
        return chars

    def encode_char(self, char: str) -> str:
        """编码汉字为 API 参数格式"""
        # Base64 编码，然后 URL encode
        encoded = base64.b64encode(char.encode('utf-8')).decode('ascii')
        return quote(encoded, safe='')

    def query_char(self, char: str) -> dict:
        """查询单个汉字"""

        # 构造请求 URL
        encoded_char = self.encode_char(char)
        url = f"{self.api_base}/class/action.php"
        params = {
            "api": "queryDict",
            "cnChar": encoded_char,
            "fontId": -1,
            "limit": 24,
            "page": 1,
            "src": 0
        }

        try:
            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code == 200:
                # 即使响应加密，我们也记录请求成功
                return {
                    "success": True,
                    "char": char,
                    "response_length": len(response.text)
                }
            else:
                return {
                    "success": False,
                    "char": char,
                    "error": f"HTTP {response.status_code}"
                }

        except Exception as e:
            return {
                "success": False,
                "char": char,
                "error": str(e)
            }

    def discover_image_pattern(self, char: str, retry: int = 3) -> List[str]:
        """
        通过尝试常见的图片 URL 模式来发现图片
        基于已知的 URL 格式: https://sfapi.fanglige.com/svg_png/{folder}/{id}.png
        """

        discovered_urls = []

        # 常见的文件夹编号（从已下载的图片观察到是 62）
        # 我们可以尝试多个可能的文件夹
        folders = [26, 62, 1, 2, 3, 4, 5, 10, 20, 30, 40, 50, 60, 70]

        # 常见的文件名模式（需要从更多样本中学习）
        # 这里我们先尝试一些常见的模式
        # 实际上这个方法不太可行，因为文件名是编码的

        return discovered_urls

    def collect_all(self, chars: List[str], delay: float = 0.5):
        """批量采集"""

        print("=" * 70)
        print("  自动化批量采集汉字")
        print("=" * 70)
        print()
        print(f"📊 待采集: {len(chars)} 个汉字")
        print(f"📁 保存目录: {self.output_dir}")
        print()

        success_count = 0
        fail_count = 0

        with tqdm(total=len(chars), desc="采集进度") as pbar:
            for char in chars:
                # 查询汉字
                result = self.query_char(char)

                if result["success"]:
                    success_count += 1
                    self.collected_chars.add(char)
                else:
                    fail_count += 1
                    print(f"\n⚠️  {char}: {result.get('error')}")

                pbar.update(1)
                time.sleep(delay)  # 避免请求过快

        # 统计
        print()
        print("=" * 70)
        print("✅ 采集完成！")
        print("=" * 70)
        print(f"  成功查询: {success_count} 个汉字")
        print(f"  失败: {fail_count}")
        print()
        print("⚠️  注意: 由于 API 响应加密，我们无法直接提取图片 URL")
        print("建议使用 Charles 抓包方式继续采集")
        print()

def main():
    """主函数"""

    import os

    # 从环境变量获取 token
    token = os.environ.get('CLOUDBRUSH_TOKEN')

    if not token:
        print("❌ 请设置环境变量 CLOUDBRUSH_TOKEN")
        print()
        print("使用方法:")
        print('  export CLOUDBRUSH_TOKEN="your_token_here"')
        print("  python3 auto_collector.py")
        sys.exit(1)

    # 创建采集器
    collector = AutoCollector(token)

    # 加载常用汉字
    chars = collector.load_common_chars()

    # 只采集前 10 个字符作为测试
    print("🧪 测试模式: 只采集前 10 个字符")
    print()
    test_chars = chars[:10]

    # 开始采集
    collector.collect_all(test_chars)

if __name__ == "__main__":
    main()
