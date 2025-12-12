#!/usr/bin/env python3
"""
上传汉字手写体数据到 Cloudflare
- 上传图片到 R2 Bucket
- 上传字符映射到 KV Store

使用前需要安装: pip install boto3 requests
"""

import os
import json
import subprocess
from pathlib import Path
from datetime import datetime


class CloudflareUploader:
    """Cloudflare 数据上传器"""

    def __init__(self, data_dir):
        self.data_dir = Path(data_dir)
        self.char_mapping = {}
        self.upload_stats = {
            'images_uploaded': 0,
            'images_failed': 0,
            'kv_updated': False,
            'start_time': datetime.now().isoformat()
        }

    def load_existing_mapping(self):
        """加载已有的字符映射"""
        mapping_file = self.data_dir / "char_url_mapping.json"

        if mapping_file.exists():
            with open(mapping_file, 'r', encoding='utf-8') as f:
                try:
                    self.char_mapping = json.load(f)
                    print(f"✅ 已加载 {len(self.char_mapping)} 个字符映射")
                except:
                    print("⚠️  映射文件为空或格式错误")
                    self.char_mapping = {}
        else:
            print("⚠️  未找到字符映射文件，将从图片文件名推断")

    def scan_images(self):
        """扫描图片文件并构建映射"""
        png_files = list(self.data_dir.glob("*.png"))
        print(f"\n📂 找到 {len(png_files)} 个PNG文件")

        for png_file in png_files:
            filename = png_file.name

            # 跳过未知文件
            if filename.startswith('unknown_'):
                continue

            # 尝试从文件名提取信息
            # 格式1: unicode_汉字.png (例如: 6c34_水.png)
            # 格式2: 其他格式需要特殊处理
            parts = filename.replace('.png', '').split('_')

            if len(parts) >= 2:
                unicode_hex = parts[0]
                char = parts[1] if len(parts[1]) > 0 else None

                if char and self.is_chinese_char(char):
                    # 如果映射中没有这个字符，添加它
                    if char not in self.char_mapping:
                        self.char_mapping[char] = {
                            'filename': filename,
                            'unicode': f"U+{unicode_hex.upper()}",
                            'size': png_file.stat().st_size,
                            'timestamp': datetime.now().isoformat()
                        }

        print(f"✅ 构建了 {len(self.char_mapping)} 个字符映射")

    def is_chinese_char(self, char):
        """检查是否为汉字"""
        if len(char) != 1:
            return False
        code = ord(char)
        return (
            (0x4e00 <= code <= 0x9fff) or
            (0x3400 <= code <= 0x4dbf) or
            (0x20000 <= code <= 0x2a6df)
        )

    def upload_images_to_r2(self):
        """上传图片到 R2"""
        print("\n📤 开始上传图片到 R2...")
        print("=" * 70)

        for char, info in self.char_mapping.items():
            filename = info['filename']
            filepath = self.data_dir / filename

            if not filepath.exists():
                print(f"⚠️  文件不存在: {filename}")
                self.upload_stats['images_failed'] += 1
                continue

            # R2 路径: chars/unicode_汉字.png
            r2_key = f"chars/{filename}"

            # 使用 wrangler r2 object put 命令上传
            try:
                cmd = [
                    'wrangler', 'r2', 'object', 'put',
                    f'handwriting-characters/{r2_key}',
                    '--file', str(filepath)
                ]

                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )

                if result.returncode == 0:
                    print(f"✅ 上传: {char} -> {r2_key}")
                    self.upload_stats['images_uploaded'] += 1

                    # 更新映射中的URL
                    info['r2_key'] = r2_key
                else:
                    print(f"❌ 上传失败: {char} - {result.stderr}")
                    self.upload_stats['images_failed'] += 1

            except subprocess.TimeoutExpired:
                print(f"⏱️  上传超时: {char}")
                self.upload_stats['images_failed'] += 1
            except Exception as e:
                print(f"❌ 上传错误: {char} - {str(e)}")
                self.upload_stats['images_failed'] += 1

        print("=" * 70)
        print(f"✅ 上传完成: {self.upload_stats['images_uploaded']} 成功, "
              f"{self.upload_stats['images_failed']} 失败")

    def upload_mapping_to_kv(self):
        """上传字符映射到 KV"""
        print("\n📤 上传字符映射到 KV...")

        # 保存映射到临时文件
        temp_file = self.data_dir / "char_mapping_upload.json"
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(self.char_mapping, f, ensure_ascii=False, indent=2)

        try:
            # 使用 wrangler kv:key put 命令
            cmd = [
                'wrangler', 'kv:key', 'put',
                '--binding=CHAR_MAPPING',
                'char_mapping',
                '--path', str(temp_file)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            if result.returncode == 0:
                print(f"✅ 字符映射已上传到 KV (共 {len(self.char_mapping)} 个字符)")
                self.upload_stats['kv_updated'] = True
            else:
                print(f"❌ KV上传失败: {result.stderr}")
                self.upload_stats['kv_updated'] = False

        except Exception as e:
            print(f"❌ KV上传错误: {str(e)}")
            self.upload_stats['kv_updated'] = False

    def generate_report(self):
        """生成上传报告"""
        report = {
            'upload_summary': {
                'total_characters': len(self.char_mapping),
                'images_uploaded': self.upload_stats['images_uploaded'],
                'images_failed': self.upload_stats['images_failed'],
                'kv_updated': self.upload_stats['kv_updated'],
                'start_time': self.upload_stats['start_time'],
                'end_time': datetime.now().isoformat()
            },
            'character_mapping': self.char_mapping
        }

        report_file = self.data_dir / "upload_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)

        print("\n" + "=" * 70)
        print("📊 上传报告")
        print("=" * 70)
        print(f"字符总数: {len(self.char_mapping)}")
        print(f"图片上传成功: {self.upload_stats['images_uploaded']}")
        print(f"图片上传失败: {self.upload_stats['images_failed']}")
        print(f"KV映射更新: {'成功' if self.upload_stats['kv_updated'] else '失败'}")
        print(f"报告文件: {report_file}")
        print("=" * 70)

    def run(self):
        """运行完整的上传流程"""
        print("🚀 开始上传汉字手写体数据到 Cloudflare")
        print("=" * 70)

        # 1. 加载/扫描数据
        self.load_existing_mapping()
        self.scan_images()

        # 2. 上传图片到 R2
        self.upload_images_to_r2()

        # 3. 上传映射到 KV
        self.upload_mapping_to_kv()

        # 4. 生成报告
        self.generate_report()

        print("\n✨ 上传流程完成！")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='上传汉字手写体数据到 Cloudflare')
    parser.add_argument(
        '--data-dir',
        type=str,
        default='../data-collection/collected_characters',
        help='数据目录路径 (默认: ../data-collection/collected_characters)'
    )
    parser.add_argument(
        '--skip-r2',
        action='store_true',
        help='跳过 R2 上传，仅更新 KV'
    )
    parser.add_argument(
        '--skip-kv',
        action='store_true',
        help='跳过 KV 上传，仅上传 R2'
    )

    args = parser.parse_args()

    # 检查 wrangler 是否安装
    try:
        subprocess.run(['wrangler', '--version'], capture_output=True, check=True)
    except:
        print("❌ 错误: wrangler 未安装")
        print("请运行: npm install -g wrangler")
        return

    # 创建上传器并运行
    uploader = CloudflareUploader(args.data_dir)

    if args.skip_r2:
        print("⏭️  跳过 R2 上传")
        uploader.load_existing_mapping()
        uploader.scan_images()
        uploader.upload_mapping_to_kv()
        uploader.generate_report()
    elif args.skip_kv:
        print("⏭️  跳过 KV 上传")
        uploader.load_existing_mapping()
        uploader.scan_images()
        uploader.upload_images_to_r2()
        uploader.generate_report()
    else:
        uploader.run()


if __name__ == '__main__':
    main()


"""
📖 使用说明
===========

1. 安装依赖
   pip install boto3 requests

2. 登录 Cloudflare (如果还没登录)
   wrangler login

3. 创建 R2 Bucket
   wrangler r2 bucket create handwriting-characters

4. 创建 KV Namespace
   wrangler kv:namespace create "CHAR_MAPPING"
   # 将输出的 id 更新到 wrangler.toml

5. 运行上传脚本
   cd handwriting-api-worker
   python3 upload-data.py

6. 可选参数
   # 指定数据目录
   python3 upload-data.py --data-dir /path/to/collected_characters

   # 仅上传 KV (跳过 R2)
   python3 upload-data.py --skip-r2

   # 仅上传 R2 (跳过 KV)
   python3 upload-data.py --skip-kv

📝 注意事项
===========
1. 确保已经运行过数据采集脚本
2. 确保 wrangler 已经登录到你的 Cloudflare 账号
3. 确保 wrangler.toml 中的配置正确
4. 大量图片上传可能需要较长时间
5. 上传过程中不要中断，否则可能导致数据不完整
"""
