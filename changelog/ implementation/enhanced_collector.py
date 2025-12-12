#!/usr/bin/env python3
"""
CloudBrush 汉字图片自动化采集器 (增强版)
支持自动化查询和批量采集
"""

import json
import os
import time
import base64
from pathlib import Path
from mitmproxy import http
from datetime import datetime
import hashlib

class EnhancedCharacterCollector:
    """增强版汉字采集器 - 支持自动化和手动模式"""
    
    def __init__(self):
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
            'start_time': datetime.now().isoformat()
        }
        
        # 加载已有数据
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                self.char_urls = json.load(f)
                self.collected_chars = set(self.char_urls.keys())
                print(f"📂 已加载 {len(self.char_urls)} 个已采集字符")
    
    def load_common_chars(self):
        """加载常用汉字列表"""
        chars_file = Path("./common_3500_chars.txt")
        
        if chars_file.exists():
            with open(chars_file, 'r', encoding='utf-8') as f:
                chars = f.read().strip()
        else:
            # 默认常用字（简化版）
            chars = """
的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严龙程论眼志制李杜早吕老考者志伺青杨妙权姐茶夫虚移
""".replace('\n', '').replace(' ', '')
        
        return list(set(chars))  # 去重
    
    def request(self, flow: http.HTTPFlow) -> None:
        """拦截请求"""
        if "sfapi.fanglige.com" not in flow.request.host:
            return
        
        self.stats['total_requests'] += 1
        
        # 记录查询的汉字
        if '/class/action.php' in flow.request.path:
            cn_char = flow.request.query.get('cnChar', '')
            if cn_char:
                try:
                    char = base64.b64decode(cn_char).decode('utf-8', errors='ignore')
                    if char and '\u4e00' <= char[0] <= '\u9fff':
                        print(f"🔍 正在查询: '{char}'")
                except:
                    pass
    
    def response(self, flow: http.HTTPFlow) -> None:
        """拦截响应"""
        if "sfapi.fanglige.com" not in flow.request.host:
            return
        
        content_type = flow.response.headers.get("content-type", "")
        
        # 1. 保存PNG图片
        if "image/png" in content_type and flow.response.status_code == 200:
            self._save_image(flow)
        
        # 2. 保存API响应
        elif "application/json" in content_type:
            self._process_api_response(flow)
    
    def _save_image(self, flow: http.HTTPFlow):
        """保存图片文件"""
        url = flow.request.pretty_url
        
        # 尝试从多个来源提取汉字
        char = self._extract_character(flow.request)
        
        if not char:
            # 如果无法提取，使用URL hash作为文件名
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename = f"unknown_{url_hash}.png"
        else:
            # Unicode编码_汉字.png
            unicode_hex = f"{ord(char):04x}"
            filename = f"{unicode_hex}_{char}.png"
        
        filepath = self.output_dir / filename
        
        # 保存图片
        with open(filepath, 'wb') as f:
            f.write(flow.response.content)
        
        self.stats['images_saved'] += 1
        
        if char:
            # 记录映射
            self.char_urls[char] = {
                "url": url,
                "filename": filename,
                "unicode": f"U+{ord(char):04X}",
                "size": len(flow.response.content),
                "timestamp": datetime.now().isoformat()
            }
            
            self.collected_chars.add(char)
            
            print(f"✅ [{self.stats['images_saved']}] 保存: '{char}' -> {filename} ({len(flow.response.content)} bytes)")
            
            # 定期保存
            if len(self.char_urls) % 10 == 0:
                self._save_mapping()
                self._print_progress()
        else:
            print(f"💾 保存未知图片: {filename}")
    
    def _process_api_response(self, flow: http.HTTPFlow):
        """处理API响应"""
        try:
            data = json.loads(flow.response.text)
            
            # 如果是解密后的响应（不包含iv字段）
            if isinstance(data, dict) and 'iv' not in data:
                self.stats['api_responses'] += 1
                
                # 保存API响应用于分析
                timestamp = int(time.time())
                api_file = self.output_dir / f"api_response_{timestamp}.json"
                
                with open(api_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'url': flow.request.pretty_url,
                        'query': dict(flow.request.query),
                        'response': data
                    }, f, indent=2, ensure_ascii=False)
                
                print(f"💾 API响应: {api_file.name}")
                
                # 尝试从响应中提取图片URL
                self._extract_urls_from_response(data)
        except:
            pass
    
    def _extract_urls_from_response(self, data):
        """从API响应中提取图片URL"""
        # 递归查找所有图片URL
        def find_urls(obj, path=""):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    find_urls(v, f"{path}.{k}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    find_urls(item, f"{path}[{i}]")
            elif isinstance(obj, str):
                if '.png' in obj or '.jpg' in obj:
                    print(f"   🔗 发现URL: {obj}")
        
        find_urls(data)
    
    def _extract_character(self, request) -> str:
        """从请求中提取汉字"""
        # 方法1: 从cnChar参数
        cn_char = request.query.get('cnChar', '')
        if cn_char:
            try:
                decoded = base64.b64decode(cn_char).decode('utf-8', errors='ignore')
                if decoded and len(decoded) >= 1:
                    char = decoded[0]
                    if '\u4e00' <= char <= '\u9fff':
                        return char
            except:
                pass
        
        # 方法2: 从URL路径
        path = request.path
        if '/chars/' in path:
            parts = path.split('/')
            for part in parts:
                if len(part) > 0 and '\u4e00' <= part[0] <= '\u9fff':
                    return part[0]
        
        # 方法3: 从其他参数
        for param in request.query.values():
            try:
                if len(param) == 1 and '\u4e00' <= param <= '\u9fff':
                    return param
            except:
                pass
        
        return None
    
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
        print(f"   API响应: {self.stats['api_responses']}")
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
                'api_responses': self.stats['api_responses'],
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
        print(f"   保存位置: {self.output_dir}")
        print(f"   映射文件: {self.mapping_file}")
        print(f"   报告文件: {report_file}")
        print("="*70)
        
        # 显示未采集的字符
        missing = set(self.common_chars) - self.collected_chars
        if missing:
            print(f"\n⚠️  未采集字符 ({len(missing)}个):")
            print("   " + "".join(list(missing)[:100]))
            if len(missing) > 100:
                print(f"   ... 还有 {len(missing) - 100} 个")


# mitmproxy addon 注册
addons = [EnhancedCharacterCollector()]


"""
📱 使用说明

基本用法:
=========
mitmweb -s enhanced_collector.py -p 8080

高级选项:
=========
# 静默模式（无Web界面）
mitmproxy -s enhanced_collector.py -p 8080

# 保存所有流量（用于调试）
mitmproxy -s enhanced_collector.py -p 8080 -w traffic.flow


准备工作:
=========
1. 创建常用字列表文件（可选）
   echo "水火山石..." > common_3500_chars.txt

2. iPhone配置代理（详见主文档）

3. 启动抓包

4. 打开CloudBrush App，开始浏览汉字


采集技巧:
=========
1. 手动模式：
   - 打开App字典功能
   - 按部首/笔画浏览
   - 慢慢滑动，每个字停留1秒

2. 批量模式：
   - 如果App有搜索功能
   - 逐个搜索常用字

3. 检查进度：
   - 每10个字会自动保存
   - 查看终端输出的进度


故障排除:
=========
Q: 看不到任何输出？
A: 确保App流量经过代理，检查证书是否信任

Q: 只保存了unknown_xxx.png？
A: URL中没有汉字信息，需要从API响应中提取

Q: 图片无法打开？
A: 可能是加密的，检查是否为PNG格式

Q: 采集很慢？
A: 这是正常的，3000字需要1-2小时手动操作


采集完成后:
=========
cd collected_characters
ls *.png | wc -l                    # 统计数量
cat char_url_mapping.json | head   # 查看映射
python3 -m http.server 8000        # 本地预览
"""
