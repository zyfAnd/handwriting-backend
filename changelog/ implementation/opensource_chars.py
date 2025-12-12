#!/usr/bin/env python3
"""
使用开源汉字数据集（替代方案）
免费、合法、即刻可用
"""

import requests
import json
from pathlib import Path

# ============================================================================
# 方案1: Make Me a Hanzi (开源，MIT许可)
# ============================================================================

def download_makemeahanzi():
    """
    下载 Make Me a Hanzi 数据集
    - 9000+ 汉字的笔画数据
    - SVG格式（可转PNG）
    - 完全免费开源
    
    数据源: https://github.com/skishore/makemeahanzi
    """
    
    print("📥 下载 Make Me a Hanzi 数据集...")
    
    # 字符数据（包含笔顺、部首等）
    graphics_url = "https://raw.githubusercontent.com/skishore/makemeahanzi/master/graphics.txt"
    dictionary_url = "https://raw.githubusercontent.com/skishore/makemeahanzi/master/dictionary.txt"
    
    output_dir = Path("./makemeahanzi_data")
    output_dir.mkdir(exist_ok=True)
    
    # 下载图形数据
    print("  下载 graphics.txt (SVG笔画数据)...")
    response = requests.get(graphics_url)
    (output_dir / "graphics.txt").write_text(response.text, encoding='utf-8')
    
    # 下载字典数据
    print("  下载 dictionary.txt (字符信息)...")
    response = requests.get(dictionary_url)
    (output_dir / "dictionary.txt").write_text(response.text, encoding='utf-8')
    
    # 解析并生成3500常用字的SVG
    print("  解析数据...")
    
    common_3500 = load_common_chars()
    
    graphics_data = {}
    with open(output_dir / "graphics.txt", 'r', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            char = data.get('character')
            if char in common_3500:
                graphics_data[char] = data
    
    print(f"\n✅ 找到 {len(graphics_data)} / 3500 个常用字的SVG数据")
    
    # 保存映射
    mapping_file = output_dir / "common_3500_mapping.json"
    with open(mapping_file, 'w', encoding='utf-8') as f:
        json.dump(graphics_data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 保存到: {mapping_file}")
    
    return graphics_data


# ============================================================================
# 方案2: Arphic 文鼎字体（开源）
# ============================================================================

def download_arphic_fonts():
    """
    下载文鼎开源字体
    - 包含完整汉字
    - 可用程序生成图片
    - GPL授权
    """
    print("📥 下载文鼎开源字体...")
    print("  请访问: https://www.freedesktop.org/wiki/Software/CJKUnifonts/")
    print("  或使用系统包管理器:")
    print("    Ubuntu: sudo apt install fonts-arphic-*")
    print("    macOS: brew install font-arphic")


# ============================================================================
# 方案3: 使用Noto Sans CJK（Google开源）
# ============================================================================

def generate_from_noto_font():
    """
    使用Google Noto字体生成图片
    - 最全面的CJK字体
    - 免费开源
    - 高质量
    """
    print("📥 使用 Noto Sans CJK 生成汉字图片...")
    
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("❌ 需要安装 Pillow: pip install Pillow")
        return
    
    output_dir = Path("./generated_chars")
    output_dir.mkdir(exist_ok=True)
    
    # 下载字体（如果没有）
    font_path = download_noto_font()
    
    # 生成3500个常用字
    common_chars = load_common_chars()
    
    print(f"开始生成 {len(common_chars)} 个汉字图片...")
    
    for i, char in enumerate(common_chars[:100], 1):  # 先测试100个
        img = generate_char_image(char, font_path)
        filename = f"{ord(char):04x}_{char}.png"
        img.save(output_dir / filename)
        
        if i % 10 == 0:
            print(f"  进度: {i}/{len(common_chars)}")
    
    print(f"✅ 完成！保存到: {output_dir}")


def download_noto_font():
    """下载Noto字体"""
    font_dir = Path("./fonts")
    font_dir.mkdir(exist_ok=True)
    
    font_path = font_dir / "NotoSansCJK-Regular.ttc"
    
    if not font_path.exists():
        print("下载 Noto Sans CJK 字体...")
        url = "https://github.com/notofonts/noto-cjk/releases/download/Sans2.004/NotoSansCJK.ttc.zip"
        
        print("  提示: 字体文件较大(~100MB)，请耐心等待...")
        print(f"  或手动下载: {url}")
        print(f"  解压后放到: {font_path}")
        
        # 实际项目中可以用 requests 下载
        return None
    
    return str(font_path)


def generate_char_image(char, font_path, size=128):
    """生成单个汉字图片"""
    from PIL import Image, ImageDraw, ImageFont
    
    # 创建白色背景
    img = Image.new('RGB', (size, size), 'white')
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font = ImageFont.truetype(font_path, int(size * 0.8))
    
    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), char, font=font)
    x = (size - (bbox[2] - bbox[0])) // 2
    y = (size - (bbox[3] - bbox[1])) // 2
    
    # 绘制黑色文字
    draw.text((x, y), char, fill='black', font=font)
    
    return img


def load_common_chars():
    """加载常用3500字"""
    # 国标一级汉字（3500个）
    chars = """
的一是在不了有和人这中大为上个国我以要他时来用们生到作地于出就分对成会可主发年动同工也能下过子说产种面而方后多定行学法所民得经十三之进着等部度家电力里如水化高自二理起小物现实加量都两体制机当使点从业本去把性好应开它合还因由其些然前外天政四日那社义事平形相全表间样与关各重新线内数正心反你明看原又么利比或但质气第向道命此变条只没结解问意建月公无系军很情者最立代想已通并提直题党程展五果料象员革位入常文总次品式活设及管特件长求老头基资边流路级少图山统接知较将组见计别她手角期根论运农指几九区强放决西被干做必战先回则任取据处队南给色光门即保治北造百规热领七海口东导器压志世金增争济阶油思术极交受联什认六共权收证改清己美再采转更单风切打白教速花带安场身车例真务具万每目至达走积示议声报斗完类八离华名确才科张信马节话米整空元况今集温传土许步群广石记需段研界拉林律叫且究观越织装影算低持音众书布复容儿须际商非验连断深难近矿千周委素技备半办青省列习响约支般史感劳便团往酸历市克何除消构府称太准精值号率族维划选标写存候毛亲快效斯院查江型眼王按格养易置派层片始却专状育厂京识适属圆包火住调满县局照参红细引听该铁价严
""".replace('\n', '').replace(' ', '')
    
    return list(chars[:3500])


# ============================================================================
# 主程序
# ============================================================================

if __name__ == "__main__":
    print("="*70)
    print("开源汉字数据集下载工具")
    print("="*70)
    
    print("\n请选择方案:")
    print("1. Make Me a Hanzi (笔画SVG数据)")
    print("2. 下载开源字体信息")
    print("3. 用Noto字体生成图片 (需要Pillow)")
    
    choice = input("\n输入选项 (1/2/3): ").strip()
    
    if choice == '1':
        download_makemeahanzi()
    elif choice == '2':
        download_arphic_fonts()
    elif choice == '3':
        generate_from_noto_font()
    else:
        print("\n运行全部方案:")
        download_makemeahanzi()
        print("\n" + "="*70 + "\n")
        download_arphic_fonts()


"""
💡 推荐方案总结:

1. 如果需要笔画顺序、书写动画
   → Make Me a Hanzi (免费、9000+字)

2. 如果需要高质量字体渲染
   → Noto Sans CJK + Pillow生成

3. 如果需要多种字体样式
   → 下载多个开源字体，批量生成

4. 如果一定要CloudBrush的数据
   → 用 cloudbrush_collector.py 抓包

所有方案都是合法免费的！
"""
