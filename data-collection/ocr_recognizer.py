#!/usr/bin/env python3
"""
OCR识别器 - 自动识别图片中的汉字并建立映射
"""

import os
import json
from pathlib import Path
from PIL import Image
import pytesseract
from tqdm import tqdm

class CharacterRecognizer:
    """汉字OCR识别器"""

    def __init__(self, input_dir="./collected_characters", output_dir="./collected_characters"):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.mapping_file = self.output_dir / "char_url_mapping.json"

        # 加载已有映射
        self.char_mapping = {}
        if self.mapping_file.exists():
            with open(self.mapping_file, 'r', encoding='utf-8') as f:
                try:
                    self.char_mapping = json.load(f)
                except:
                    pass

    def recognize_all(self):
        """识别所有图片"""
        print("=" * 70)
        print("🔍 开始OCR识别")
        print("=" * 70)

        # 获取所有PNG文件
        png_files = list(self.input_dir.glob("*.png"))
        jpeg_files = list(self.input_dir.glob("*.jpg")) + list(self.input_dir.glob("*.jpeg"))
        all_files = png_files + jpeg_files

        print(f"📊 发现 {len(all_files)} 个图片文件")

        recognized_count = 0
        failed_count = 0

        for img_file in tqdm(all_files, desc="识别中"):
            try:
                result = self.recognize_character(img_file)
                if result:
                    recognized_count += 1
                    # 重命名文件
                    char, confidence = result
                    new_name = self.rename_file(img_file, char)
                    if new_name:
                        print(f"✅ {img_file.name} → {new_name} (汉字: {char})")
                else:
                    failed_count += 1
            except Exception as e:
                print(f"❌ 识别失败 {img_file.name}: {e}")
                failed_count += 1

        # 保存映射
        self.save_mapping()

        print("\n" + "=" * 70)
        print("🎉 识别完成！")
        print("=" * 70)
        print(f"✅ 成功: {recognized_count}")
        print(f"❌ 失败: {failed_count}")
        print(f"📁 映射文件: {self.mapping_file}")
        print("=" * 70)

    def recognize_character(self, image_path):
        """识别单个图片中的汉字"""
        try:
            # 打开图片
            img = Image.open(image_path)

            # 使用tesseract识别中文
            # 配置：只识别中文字符
            custom_config = r'--oem 3 --psm 10 -l chi_sim'
            text = pytesseract.image_to_string(img, config=custom_config, lang='chi_sim')

            # 清理结果
            text = text.strip()

            # 提取第一个中文字符
            for char in text:
                if '\u4e00' <= char <= '\u9fff':
                    return (char, 1.0)  # 返回字符和置信度

            return None
        except Exception as e:
            print(f"识别错误: {e}")
            return None

    def rename_file(self, old_path, char):
        """重命名文件为 unicode_汉字.png 格式"""
        try:
            # 获取unicode编码
            unicode_hex = f"{ord(char):04x}"

            # 新文件名
            ext = old_path.suffix
            new_name = f"{unicode_hex}_{char}{ext}"
            new_path = old_path.parent / new_name

            # 如果新文件已存在，添加序号
            counter = 1
            while new_path.exists() and new_path != old_path:
                new_name = f"{unicode_hex}_{char}_{counter}{ext}"
                new_path = old_path.parent / new_name
                counter += 1

            # 重命名
            if new_path != old_path:
                old_path.rename(new_path)

                # 更新映射
                self.char_mapping[char] = {
                    "filename": new_name,
                    "unicode": f"U+{unicode_hex.upper()}",
                    "original_filename": old_path.name,
                    "recognized_at": str(Path(new_path).stat().st_mtime)
                }

                return new_name
            return None
        except Exception as e:
            print(f"重命名错误: {e}")
            return None

    def save_mapping(self):
        """保存映射文件"""
        with open(self.mapping_file, 'w', encoding='utf-8') as f:
            json.dump(self.char_mapping, f, indent=2, ensure_ascii=False)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='OCR识别图片中的汉字')
    parser.add_argument('--input', '-i', default='./collected_characters',
                       help='输入目录')
    parser.add_argument('--output', '-o', default='./collected_characters',
                       help='输出目录')

    args = parser.parse_args()

    recognizer = CharacterRecognizer(args.input, args.output)
    recognizer.recognize_all()


if __name__ == '__main__':
    main()


"""
使用方法:
=========
# 安装依赖
pip install pytesseract pillow tqdm

# Mac上安装tesseract
brew install tesseract tesseract-lang

# 运行识别
python3 ocr_recognizer.py

# 指定目录
python3 ocr_recognizer.py --input ./debug_logs --output ./collected_characters

识别后:
=======
- 文件会被重命名为: 6c34_水.png
- 生成映射文件: char_url_mapping.json
- 可以直接上传到GitHub，同步到Cloudflare
"""
