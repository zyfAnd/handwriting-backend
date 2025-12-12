#!/usr/bin/env python3
"""
智能自动采集器
通过分析 API 响应模式，自动发现并下载所有图片
"""

import requests
import base64
import time
import json
from pathlib import Path
from tqdm import tqdm
from typing import List, Set, Dict
from urllib.parse import quote
import concurrent.futures

class SmartAutoCollector:
    """智能自动采集器"""

    def __init__(self, token: str, output_dir: str = "./collected_characters"):
        self.token = token
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.api_base = "https://sfapi.fanglige.com"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "User-Agent": "CloudBrush/3.0",
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh-Hans;q=0.9",
        }

        # 已发现的图片
        self.discovered_images = set()
        self.success_count = 0
        self.fail_count = 0

    def get_common_chars(self) -> List[str]:
        """获取常用汉字（3500字）"""

        # 读取常用汉字表
        chars_str = """
        的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严
        龙飞鱼鸟鹿麦麻黄黑齿龙龟上下左右东西南北中内外前后高低大小长短多少好坏新旧快慢早晚冷热干湿轻重粗细宽窄深浅远近亮暗软硬香臭酸甜苦辣咸淡清浊静闹忙闲穷富贵贱胖瘦美丑善恶真假对错是非黑白阴阳雌雄公母父母兄弟姐妹夫妻儿女祖孙师生君臣主仆朋友敌人天地日月星辰风雨雷电云雾霜雪冰雹春夏秋冬梅兰竹菊松柏杨柳花草树木鸟兽虫鱼龙虎豹熊猫狗牛马羊猪鸡鸭鹅鱼虾蟹龟蛇蛙蝴蝶蜜蜂蚂蚁蜘蛛蚊蝇头脸眼耳鼻口舌牙手足心肝脾肺肾肠胃骨肉皮血气筋脉金木水火土石玉珠宝剑刀枪棒锤斧锯凿钉绳索线针布衣裤鞋帽巾袜衫裙袍褂笔墨纸砚书画琴棋诗词歌曲舞戏酒茶饭菜米面油盐酱醋糖肉蛋奶果蔬豆谷麦稻粟黍稷菽麻桑棉麻丝绸绢缎锦罗纱绸缎绵绢丝麻布料衣服饮食住行医药教育工农商学兵政法律经济文化艺术科技体育军事外交宗教哲学历史地理数学物理化学生物语文英语音乐美术体育
        """

        chars = []
        seen = set()
        for char in chars_str:
            char = char.strip()
            if char and '\u4e00' <= char <= '\u9fff':
                if char not in seen:
                    chars.append(char)
                    seen.add(char)

        return chars

    def encode_char(self, char: str) -> str:
        """编码汉字"""
        encoded = base64.b64encode(char.encode('utf-8')).decode('ascii')
        return quote(encoded, safe='')

    def query_and_download(self, char: str) -> int:
        """
        查询汉字并尝试下载图片
        返回下载成功的图片数量

        策略：
        1. 调用 API 触发后端处理
        2. 尝试常见的图片 URL 模式
        3. 下载可访问的图片
        """

        # 1. 调用 API
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
            # 调用 API（即使响应加密，也能触发服务器端处理）
            response = requests.get(url, params=params, headers=self.headers, timeout=10)

            if response.status_code != 200:
                return 0

            # 2. 尝试推测图片 URL
            # 基于观察：文件夹 ID 可能与汉字编码有关
            # 文件名是 4 位字母数字组合

            # 尝试访问可能的图片
            count = self.try_download_images(char)

            return count

        except Exception as e:
            return 0

    def try_download_images(self, char: str) -> int:
        """
        尝试下载图片

        问题：我们不知道图片的确切 URL
        解决：等待 mitmproxy 捕获
        """

        # 这个方法依赖 mitmproxy 捕获
        # 所以我们只调用 API，让 App 的正常流程去加载图片
        return 0

    def batch_query(self, chars: List[str], delay: float = 0.5):
        """批量查询汉字"""

        print("=" * 70)
        print("  智能批量查询")
        print("=" * 70)
        print()
        print(f"📊 待查询: {len(chars)} 个汉字")
        print(f"⚠️  注意：此方法仅触发 API 查询")
        print(f"   需要配合 mitmproxy 捕获实际图片 URL")
        print()

        with tqdm(total=len(chars), desc="查询进度") as pbar:
            for char in chars:
                count = self.query_and_download(char)

                if count > 0:
                    self.success_count += 1

                pbar.update(1)
                pbar.set_postfix({"成功": self.success_count})

                time.sleep(delay)

        print()
        print("=" * 70)
        print(f"✅ 查询完成！共查询 {len(chars)} 个汉字")
        print(f"   后续需要通过 mitmproxy 捕获的 URL 进行下载")
        print("=" * 70)

def main():
    """主函数"""

    print("=" * 70)
    print("  智能自动采集器")
    print("=" * 70)
    print()
    print("⚠️  重要提示:")
    print()
    print("此脚本会自动调用 API 查询所有常用汉字，")
    print("但由于 API 响应加密，无法直接获取图片 URL。")
    print()
    print("最有效的方案组合：")
    print("  1. 保持 mitmproxy 运行")
    print("  2. 运行此脚本自动查询 API")
    print("  3. 同时在 iPhone 上快速浏览（触发图片加载）")
    print("  4. mitmproxy 自动捕获图片 URL")
    print("  5. 批量下载")
    print()
    print("=" * 70)
    print()

    # Token（从 Charles 会话中提取）
    token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJodHRwczovL3NodWh1YXNob3cuZmFuZ2xpZ2UuY29tL2FwaS92My9hdXRoL2xvZ2luIiwiaWF0IjoxNzMxNjcyNjc5LCJleHAiOjE3MzQyNjQ2NzksIm5iZiI6MTczMTY3MjY3OSwianRpIjoiSkNzcEU3Z2txQ3pYWWxvayIsInN1YiI6IjQ2ODEiLCJwcnYiOiI4N2UwYWYxZWY5ZmQxNTgxMmZkZWM5NzE1M2ExNGUwYjA0NzU0NmFhIn0.QgUOhz6jR1XxSu75w9CYuUfx5Mm0v7wrrhgGLK_Opfk"

    collector = SmartAutoCollector(token)

    # 加载汉字
    chars = collector.get_common_chars()
    print(f"📝 已加载 {len(chars)} 个常用汉字")
    print()

    choice = input("是否开始批量查询？(y/n): ").strip().lower()

    if choice == 'y':
        collector.batch_query(chars, delay=0.5)
    else:
        print("已取消")

if __name__ == "__main__":
    main()
