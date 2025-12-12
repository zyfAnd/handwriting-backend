#!/usr/bin/env python3
"""
图片匹配工具 - 使用简单的方式建立图片和汉字的映射
基于文件修改时间和采集顺序
"""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

class ImageMatcher:
    """图片匹配器"""

    def __init__(self):
        self.chars_dir = Path("./collected_characters")
        self.debug_logs_dir = Path("./debug_logs")

    def match_by_timestamp(self):
        """通过时间戳匹配图片和请求"""
        print("=" * 70)
        print("🔗 根据时间戳匹配图片和请求")
        print("=" * 70)

        # 读取所有图片文件
        images = {}
        for img_file in self.chars_dir.glob("*.png"):
            mtime = img_file.stat().st_mtime
            images[img_file.name] = {
                'path': img_file,
                'timestamp': mtime,
                'datetime': datetime.fromtimestamp(mtime)
            }

        print(f"📊 collected_characters/: {len(images)} 张图片")

        # 读取debug_logs中的图片
        debug_images = {}
        if self.debug_logs_dir.exists():
            for img_file in self.debug_logs_dir.glob("image_*.png"):
                mtime = img_file.stat().st_mtime
                debug_images[img_file.name] = {
                    'path': img_file,
                    'timestamp': mtime,
                    'datetime': datetime.fromtimestamp(mtime)
                }

            print(f"📊 debug_logs/: {len(debug_images)} 张图片")

            # 读取对应的请求日志
            request_logs = {}
            for req_file in self.debug_logs_dir.glob("request_*.json"):
                try:
                    with open(req_file, 'r', encoding='utf-8') as f:
                        req_data = json.load(f)
                        request_logs[req_file.stem] = req_data
                except:
                    pass

            print(f"📊 request logs: {len(request_logs)}")

            # 匹配逻辑：根据时间戳和序号
            matches = []
            for img_name, img_info in sorted(debug_images.items(), key=lambda x: x[1]['timestamp']):
                # 从文件名提取序号 (image_171130_006.png -> 006)
                parts = img_name.replace('image_', '').replace('.png', '').split('_')
                if len(parts) >= 2:
                    seq = parts[1]

                    # 查找对应的请求
                    req_key = f"request_{parts[0]}_{seq}"
                    if req_key in request_logs:
                        req = request_logs[req_key]
                        matches.append({
                            'image': img_name,
                            'request_url': req.get('url', ''),
                            'cn_char_param': req.get('query_params', {}).get('cnChar', ''),
                            'timestamp': img_info['datetime'].isoformat()
                        })

            print(f"\n✅ 成功匹配: {len(matches)} 个")

            # 保存匹配结果
            if matches:
                match_file = self.chars_dir / "image_request_mapping.json"
                with open(match_file, 'w', encoding='utf-8') as f:
                    json.dump(matches, f, indent=2, ensure_ascii=False)

                print(f"💾 保存到: {match_file}")

                # 显示前几个匹配
                print("\n📋 匹配示例:")
                for match in matches[:5]:
                    print(f"   {match['image']} <- {match['request_url']}")

        print("=" * 70)

    def suggest_manual_labeling(self):
        """生成手动标注模板"""
        print("\n" + "=" * 70)
        print("📝 生成手动标注模板")
        print("=" * 70)

        # 获取所有未标注的图片
        unlabeled = []
        for img_file in sorted(self.chars_dir.glob("*.png")):
            # 如果文件名不是 unicode_汉字.png 格式
            if not any(c.isdigit() and c.lower() in 'abcdef' for c in img_file.stem.split('_')[0]):
                unlabeled.append(img_file.name)

        if unlabeled:
            template_file = self.chars_dir / "manual_labeling_template.txt"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write("# 手动标注模板\n")
                f.write("# 格式: 文件名,汉字\n")
                f.write("# 例如: 16_pnr.png,水\n\n")

                for img in unlabeled[:20]:  # 只显示前20个
                    f.write(f"{img},\n")

            print(f"📄 已生成模板: {template_file}")
            print(f"   共 {len(unlabeled)} 个未标注图片")
            print("\n请打开图片查看，然后在模板中填写对应的汉字")
        else:
            print("✅ 所有图片都已标注")

        print("=" * 70)


def main():
    matcher = ImageMatcher()
    matcher.match_by_timestamp()
    matcher.suggest_manual_labeling()

    print("\n💡 下一步:")
    print("1. 使用 OCR 自动识别: python3 ocr_recognizer.py")
    print("2. 或手动标注: 编辑 manual_labeling_template.txt")
    print("3. 上传到 GitHub: git add . && git commit -m 'Add characters' && git push")


if __name__ == '__main__':
    main()
