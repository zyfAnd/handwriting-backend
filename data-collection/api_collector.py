#!/usr/bin/env python3
"""
CloudBrush API 直接采集器
使用 token 直接调用 API 批量获取汉字图片
"""

import json
import os
import time
import base64
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, List
from tqdm import tqdm


class APICollector:
    """使用 API Token 直接采集汉字图片"""
    
    def __init__(self, 
                 token: str,
                 api_base_url: str = "https://sfapi.fanglige.com",
                 token_header: str = "Authorization",
                 token_format: str = "Bearer {token}"):
        """
        初始化采集器
        
        Args:
            token: API token
            api_base_url: API 基础 URL
            token_header: token 在 header 中的字段名（如 "Authorization", "Token", "X-Auth-Token"）
            token_format: token 的格式（如 "Bearer {token}", "{token}", "Token {token}"）
        """
        self.token = token
        self.api_base_url = api_base_url.rstrip('/')
        self.token_header = token_header
        self.token_format = token_format
        
        # 输出目录
        self.output_dir = Path("./collected_characters")
        self.output_dir.mkdir(exist_ok=True)
        
        # 加载常用汉字列表
        self.common_chars = self.load_common_chars()
        self.collected_chars = set()
        
        # URL映射
        self.char_urls = {}
        self.mapping_file = self.output_dir / "char_url_mapping.json"
        
        # 统计信息
        self.stats = {
            'total_requests': 0,
            'images_saved': 0,
            'api_responses': 0,
            'failed': 0,
            'start_time': datetime.now().isoformat()
        }
        
        # 加载已有数据
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.char_urls = json.load(f)
                self.collected_chars = set(self.char_urls.keys())
                print(f"📂 已加载 {len(self.char_urls)} 个已采集字符")
        
        # 创建 session
        self.session = requests.Session()
        self._setup_session()
    
    def _setup_session(self):
        """配置 requests session"""
        # 设置 token header
        token_value = self.token_format.format(token=self.token)
        self.session.headers[self.token_header] = token_value
        
        # 设置其他常用 headers
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)'
        self.session.headers['Accept'] = 'application/json, image/png, */*'
        self.session.headers['Accept-Language'] = 'zh-CN,zh;q=0.9'
    
    def load_common_chars(self) -> List[str]:
        """加载常用汉字列表"""
        chars_file = Path("./common_3500_chars.txt")
        
        if chars_file.exists():
            with open(chars_file, 'r', encoding='utf-8') as f:
                chars = f.read().strip()
        else:
            # 默认常用字
            chars = "的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严"
        
        return list(set(chars))  # 去重
    
    def get_char_image(self, char: str) -> Optional[Dict]:
        """
        获取单个汉字的图片
        
        Args:
            char: 汉字
            
        Returns:
            包含图片 URL 或数据的字典，失败返回 None
        """
        try:
            import random
            import string
            import urllib.parse
            
            # 根据实际 API 格式构建请求
            # API: /class/action.php?api=queryDict&cnChar={base64}&fontId=-1&limit=24&page=1&src=0
            cn_char_base64 = base64.b64encode(char.encode('utf-8')).decode('utf-8')
            
            endpoint = f"{self.api_base_url}/class/action.php"
            params = {
                'api': 'queryDict',
                'cnChar': cn_char_base64,
                'fontId': '-1',
                'limit': '24',
                'page': '1',
                'src': '0'
            }
            
            # 添加其他必要的 headers（从实际请求中提取）
            headers = {
                'X-Client-OS': 'ios',
                'timeStamp': str(int(time.time())),
                'locale': 'zh',
                'requestId': ''.join(random.choices(string.ascii_lowercase + string.digits, k=16)),
                'Accept-Language': 'zh-Hans-CN;q=1, en-CN;q=0.9',
                'X-App-Build': '307',
                'X-App-Version': '2.9.9',
                'X-Channel': 'AppStore',
            }
            
            try:
                response = self.session.get(endpoint, params=params, headers=headers, timeout=10)
                self.stats['total_requests'] += 1
                
                # 如果返回的是图片
                if response.headers.get('content-type', '').startswith('image/'):
                    return {
                        'type': 'image',
                        'data': response.content,
                        'url': response.url,
                        'content_type': response.headers.get('content-type')
                    }
                
                # 如果返回的是 JSON（可能是加密的）
                elif response.headers.get('content-type', '').startswith('application/json'):
                    try:
                        data = response.json()
                        self.stats['api_responses'] += 1
                        
                        # 检查是否是加密的响应（有 iv 和 value 字段）
                        if isinstance(data, dict) and 'iv' in data and 'value' in data:
                            # 加密的响应，尝试从加密字符串中提取 URL
                            encrypted_value = data.get('value', '')
                            # 使用正则表达式查找图片 URL
                            url_pattern = r'https?://sfapi\.fanglige\.com/svg_png/[^\s]+\.png'
                            matches = re.findall(url_pattern, encrypted_value)
                            if matches:
                                # 返回第一个匹配的 URL
                                image_url = matches[0]
                                return self._download_image(image_url)
                            return None
                        
                        # 尝试从 JSON 中提取图片 URL
                        image_url = self._extract_image_url_from_json(data)
                        if image_url:
                            return self._download_image(image_url)
                        
                        # 如果 JSON 中直接包含图片数据（base64）
                        if 'image' in data or 'data' in data:
                            image_data = data.get('image') or data.get('data')
                            if isinstance(image_data, str) and image_data.startswith('data:image'):
                                # data:image/png;base64,xxx
                                base64_data = image_data.split(',')[1]
                                return {
                                    'type': 'image',
                                    'data': base64.b64decode(base64_data),
                                    'url': response.url,
                                    'content_type': 'image/png'
                                }
                    
                    except json.JSONDecodeError:
                        # 响应不是 JSON，可能是文本
                        text = response.text
                        # 尝试从文本中提取图片 URL
                        url_pattern = r'https?://sfapi\.fanglige\.com/svg_png/[^\s]+\.png'
                        matches = re.findall(url_pattern, text)
                        if matches:
                            return self._download_image(matches[0])
                
            except requests.exceptions.RequestException as e:
                print(f"❌ 请求失败: {e}")
                return None
            
            return None
            
        except Exception as e:
            print(f"❌ 获取 '{char}' 失败: {e}")
            return None
    
    def _download_image(self, image_url: str) -> Optional[Dict]:
        """下载图片"""
        try:
            img_response = self.session.get(image_url, timeout=10)
            if img_response.status_code == 200:
                return {
                    'type': 'image',
                    'data': img_response.content,
                    'url': image_url,
                    'content_type': img_response.headers.get('content-type', 'image/png')
                }
        except Exception as e:
            print(f"❌ 下载图片失败 {image_url}: {e}")
        return None
    
    def _extract_image_url_from_json(self, data: Dict) -> Optional[str]:
        """从 JSON 响应中提取图片 URL"""
        def find_url(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ['url', 'image_url', 'imageUrl', 'img', 'src', 'path']:
                        if isinstance(v, str) and ('.png' in v or '.jpg' in v or 'http' in v):
                            return v
                    result = find_url(v, f"{path}.{k}")
                    if result:
                        return result
            elif isinstance(obj, list):
                for item in obj:
                    result = find_url(item, path)
                    if result:
                        return result
            elif isinstance(obj, str):
                if ('.png' in obj or '.jpg' in obj) and ('http' in obj or obj.startswith('/')):
                    return obj
            return None
        
        return find_url(data)
    
    def save_char_image(self, char: str, image_data: bytes, url: str, content_type: str = 'image/png'):
        """保存汉字图片"""
        # 生成文件名
        unicode_hex = f"{ord(char):04x}"
        filename = f"{unicode_hex}_{char}.png"
        filepath = self.output_dir / filename
        
        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        self.stats['images_saved'] += 1
        
        # 记录映射
        self.char_urls[char] = {
            "url": url,
            "filename": filename,
            "unicode": f"U+{ord(char):04X}",
            "size": len(image_data),
            "timestamp": datetime.now().isoformat()
        }
        
        self.collected_chars.add(char)
        
        print(f"✅ [{self.stats['images_saved']}] 保存: '{char}' -> {filename} ({len(image_data)} bytes)")
    
    def collect_char(self, char: str) -> bool:
        """采集单个汉字"""
        if char in self.collected_chars:
            print(f"⏭️  '{char}' 已存在，跳过")
            return True
        
        result = self.get_char_image(char)
        
        if result and result['type'] == 'image':
            self.save_char_image(
                char=char,
                image_data=result['data'],
                url=result['url'],
                content_type=result.get('content_type', 'image/png')
            )
            
            # 定期保存
            if len(self.char_urls) % 10 == 0:
                self._save_mapping()
                self._print_progress()
            
            return True
        else:
            self.stats['failed'] += 1
            print(f"❌ 无法获取 '{char}' 的图片")
            return False
    
    def collect_batch(self, chars: List[str] = None, delay: float = 0.5):
        """
        批量采集汉字
        
        Args:
            chars: 要采集的汉字列表，None 表示使用常用字列表
            delay: 每次请求之间的延迟（秒）
        """
        if chars is None:
            chars = self.common_chars
        
        # 过滤已采集的字符
        chars_to_collect = [c for c in chars if c not in self.collected_chars]
        
        if not chars_to_collect:
            print("✅ 所有字符已采集完成！")
            return
        
        print(f"🚀 开始批量采集 {len(chars_to_collect)} 个汉字...")
        print(f"   已采集: {len(self.collected_chars)}")
        print(f"   待采集: {len(chars_to_collect)}")
        print()
        
        # 使用进度条
        with tqdm(total=len(chars_to_collect), desc="采集进度") as pbar:
            for char in chars_to_collect:
                success = self.collect_char(char)
                pbar.update(1)
                
                # 延迟，避免请求过快
                if delay > 0:
                    time.sleep(delay)
        
        # 最终保存
        self._save_mapping()
        self._print_progress()
    
    def _save_mapping(self):
        """保存字符映射"""
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.char_urls, f, indent=2, ensure_ascii=False)
    
    def _print_progress(self):
        """打印进度"""
        total = len(self.common_chars)
        collected = len(self.collected_chars)
        percentage = (collected / total * 100) if total > 0 else 0
        
        print("\n" + "="*70)
        print(f"📊 采集进度: {collected}/{total} ({percentage:.1f}%)")
        print(f"   图片总数: {self.stats['images_saved']}")
        print(f"   失败: {self.stats['failed']}")
        print("="*70 + "\n")
    
    def done(self):
        """清理和总结"""
        self._save_mapping()
        
        # 生成采集报告
        report = {
            'summary': {
                'total_chars': len(self.common_chars),
                'collected_chars': len(self.collected_chars),
                'images_saved': self.stats['images_saved'],
                'failed': self.stats['failed'],
                'completion_rate': f"{len(self.collected_chars) / len(self.common_chars) * 100:.1f}%"
            },
            'missing_chars': list(set(self.common_chars) - self.collected_chars)[:50],
            'stats': self.stats,
            'char_mapping': self.char_urls
        }
        
        report_file = self.output_dir / "collection_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print("\n" + "="*70)
        print("🎉 采集完成！")
        print("="*70)
        print(f"   常用字总数: {len(self.common_chars)}")
        print(f"   已采集字符: {len(self.collected_chars)}")
        print(f"   完成率: {len(self.collected_chars) / len(self.common_chars) * 100:.1f}%")
        print(f"   图片总数: {self.stats['images_saved']}")
        print(f"   失败: {self.stats['failed']}")
        print(f"   保存位置: {self.output_dir}")
        print(f"   映射文件: {self.mapping_file}")
        print(f"   报告文件: {report_file}")
        print("="*70)


def main():
    """主程序"""
    import sys
    
    print("="*70)
    print("CloudBrush API 直接采集器")
    print("="*70)
    print()
    
    # 获取 token
    token = os.getenv('CLOUDBRUSH_TOKEN')
    if not token:
        token = input("请输入 API Token: ").strip()
        if not token:
            print("❌ Token 不能为空")
            sys.exit(1)
    
    # 获取配置
    api_base_url = os.getenv('CLOUDBRUSH_API_URL', 'https://sfapi.fanglige.com')
    token_header = os.getenv('CLOUDBRUSH_TOKEN_HEADER', 'Authorization')
    token_format = os.getenv('CLOUDBRUSH_TOKEN_FORMAT', 'Bearer {token}')
    
    print(f"📡 API 地址: {api_base_url}")
    print(f"🔑 Token Header: {token_header}")
    print(f"📝 Token 格式: {token_format}")
    print()
    
    # 创建采集器
    collector = APICollector(
        token=token,
        api_base_url=api_base_url,
        token_header=token_header,
        token_format=token_format
    )
    
    # 测试单个字符
    print("🧪 测试连接...")
    test_char = "水"
    result = collector.get_char_image(test_char)
    
    if result and result['type'] == 'image':
        print(f"✅ 测试成功！可以获取 '{test_char}' 的图片")
        print(f"   图片大小: {len(result['data'])} bytes")
        print()
    else:
        print(f"⚠️  测试失败，可能的原因：")
        print("   1. Token 无效或已过期")
        print("   2. Token 格式不正确")
        print("   3. API 地址不正确")
        print("   4. 需要调整 token_header 或 token_format")
        print()
        
        # 询问是否继续
        continue_anyway = input("是否继续尝试采集？(y/n): ").strip().lower()
        if continue_anyway != 'y':
            sys.exit(1)
    
    # 批量采集
    print("🚀 开始批量采集...")
    print()
    
    try:
        collector.collect_batch(delay=0.5)  # 每次请求间隔 0.5 秒
    except KeyboardInterrupt:
        print("\n\n⚠️  用户中断采集")
    finally:
        collector.done()


if __name__ == "__main__":
    # 检查依赖
    try:
        import requests
        from tqdm import tqdm
    except ImportError:
        print("❌ 缺少依赖，请先安装:")
        print("   pip install requests tqdm")
        sys.exit(1)
    
    main()
