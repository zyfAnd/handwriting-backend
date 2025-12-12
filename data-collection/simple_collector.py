#!/usr/bin/env python3
"""
Simple Image Collector - 简单图片采集器
只保存图片，不解析汉字信息
"""

from pathlib import Path
from mitmproxy import http
from datetime import datetime
import hashlib
import json

class SimpleImageCollector:
    """简单图片采集器 - 只保存PNG图片"""

    def __init__(self):
        self.output_dir = Path("./collected_characters")
        self.output_dir.mkdir(exist_ok=True)
        self.image_count = 0

        # 记录图片元数据
        self.metadata = {}
        self.metadata_file = self.output_dir / "image_metadata.json"

        # 加载已有元数据
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
            except:
                pass

        print("=" * 70)
        print("🖼️  Simple Image Collector - 图片采集器")
        print("=" * 70)
        print(f"📁 保存目录: {self.output_dir}")
        print("📸 将保存所有 PNG/JPEG 图片")
        print("📝 同时记录元数据（用于后续匹配汉字）")
        print("=" * 70)

    def response(self, flow: http.HTTPFlow) -> None:
        """拦截并保存图片响应"""
        if "sfapi.fanglige.com" not in flow.request.host:
            return

        content_type = flow.response.headers.get("content-type", "")

        # 只保存图片
        if "image" in content_type and flow.response.status_code == 200:
            self._save_image(flow)

    def _save_image(self, flow: http.HTTPFlow):
        """保存图片文件"""
        content_type = flow.response.headers.get("content-type", "")
        url = flow.request.pretty_url

        # 确定文件扩展名
        if "png" in content_type:
            ext = "png"
        elif "jpeg" in content_type or "jpg" in content_type:
            ext = "jpg"
        else:
            ext = "img"

        # 从URL提取路径信息作为文件名
        # 例如: /svg_png/16/pnr.png -> 16_pnr
        path = flow.request.path
        path_parts = [p for p in path.split('/') if p and p != 'svg_png']

        if path_parts:
            # 使用路径信息构建文件名
            filename_base = '_'.join(path_parts).replace('.png', '').replace('.jpg', '')
        else:
            # 如果无法从路径提取，使用URL hash
            url_hash = hashlib.md5(url.encode()).hexdigest()[:8]
            filename_base = url_hash

        # 生成唯一文件名
        filename = f"{filename_base}.{ext}"
        filepath = self.output_dir / filename

        # 如果文件已存在，添加序号
        counter = 1
        while filepath.exists():
            filename = f"{filename_base}_{counter}.{ext}"
            filepath = self.output_dir / filename
            counter += 1

        # 保存图片
        try:
            with open(filepath, 'wb') as f:
                f.write(flow.response.content)

            self.image_count += 1
            size_kb = len(flow.response.content) / 1024

            # 记录元数据
            self.metadata[filename] = {
                'url': url,
                'path': path,
                'size': len(flow.response.content),
                'timestamp': datetime.now().isoformat(),
                'content_type': content_type,
                'index': self.image_count
            }

            # 定期保存元数据
            if self.image_count % 10 == 0:
                self._save_metadata()

            print(f"✅ [{self.image_count:04d}] {filename} ({size_kb:.1f} KB)")

            # 每10张显示一次进度
            if self.image_count % 10 == 0:
                print(f"\n📊 已采集 {self.image_count} 张图片\n")

        except Exception as e:
            print(f"❌ 保存失败 {filename}: {e}")

    def _save_metadata(self):
        """保存元数据"""
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.metadata, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"⚠️  元数据保存失败: {e}")

    def done(self):
        """清理和总结"""
        # 最后保存一次元数据
        self._save_metadata()

        print("\n" + "=" * 70)
        print("🎉 采集完成！")
        print("=" * 70)
        print(f"📊 总计采集: {self.image_count} 张图片")
        print(f"📁 保存位置: {self.output_dir}")
        print(f"📝 元数据文件: {self.metadata_file}")
        print("\n💡 下一步:")
        print("   1. OCR识别: python3 ocr_recognizer.py")
        print("   2. 匹配分析: python3 match_images.py")
        print("=" * 70)


# mitmproxy addon 注册
addons = [SimpleImageCollector()]


"""
使用方法:
=========
mitmweb -s simple_collector.py -p 8080

或通过 Web 界面启动：
点击 "开始采集" 按钮即可

特点:
=====
- 只保存图片，不解析汉字
- 文件名使用 URL 路径
- 自动去重
- 实时显示进度
"""
