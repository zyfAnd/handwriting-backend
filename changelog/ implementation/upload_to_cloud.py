#!/usr/bin/env python3
"""
汉字图片批量上传工具
支持 Cloudflare R2 和 AWS S3
"""

import boto3
import os
from pathlib import Path
from typing import List, Dict
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

class CharacterImageUploader:
    """汉字图片上传器"""
    
    def __init__(self, provider='r2'):
        """
        初始化上传器
        
        Args:
            provider: 'r2' 或 's3'
        """
        self.provider = provider
        self.s3_client = self._init_client()
        
    def _init_client(self):
        """初始化S3客户端"""
        
        if self.provider == 'r2':
            # Cloudflare R2 配置
            return boto3.client(
                's3',
                endpoint_url=os.getenv('R2_ENDPOINT'),  # 例如: https://xxx.r2.cloudflarestorage.com
                aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
                region_name='auto'
            )
        
        elif self.provider == 's3':
            # AWS S3 配置
            return boto3.client(
                's3',
                region_name=os.getenv('AWS_REGION', 'ap-southeast-1'),
                aws_access_key_id=os.getenv('AWS_ACCESS_KEY_ID'),
                aws_secret_access_key=os.getenv('AWS_SECRET_ACCESS_KEY')
            )
        
        else:
            raise ValueError(f"Unknown provider: {self.provider}")
    
    def upload_file(self, 
                    local_path: str, 
                    bucket: str,
                    key: str = None) -> bool:
        """
        上传单个文件
        
        Args:
            local_path: 本地文件路径
            bucket: bucket名称
            key: 对象key（默认使用文件名）
            
        Returns:
            上传成功返回True
        """
        if key is None:
            key = Path(local_path).name
        
        try:
            self.s3_client.upload_file(
                local_path,
                bucket,
                key,
                ExtraArgs={
                    'ContentType': 'image/png',
                    'CacheControl': 'public, max-age=31536000',  # 1年缓存
                    'ACL': 'public-read'  # 公开访问
                }
            )
            return True
            
        except Exception as e:
            print(f"❌ 上传失败 {local_path}: {e}")
            return False
    
    def upload_directory(self,
                        local_dir: str,
                        bucket: str,
                        prefix: str = 'chars/',
                        max_workers: int = 10) -> Dict:
        """
        批量上传目录
        
        Args:
            local_dir: 本地目录
            bucket: bucket名称
            prefix: 对象key前缀
            max_workers: 并发上传数
            
        Returns:
            上传统计信息
        """
        local_path = Path(local_dir)
        files = list(local_path.glob('*.png'))
        
        print(f"📂 找到 {len(files)} 个图片文件")
        print(f"☁️  上传到: {self.provider.upper()} - {bucket}/{prefix}")
        
        stats = {
            'total': len(files),
            'success': 0,
            'failed': 0,
            'urls': []
        }
        
        # 并发上传
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(
                    self.upload_file,
                    str(f),
                    bucket,
                    f"{prefix}{f.name}"
                ): f for f in files
            }
            
            # 进度条
            with tqdm(total=len(files), desc="上传进度") as pbar:
                for future in as_completed(futures):
                    file = futures[future]
                    
                    if future.result():
                        stats['success'] += 1
                        
                        # 生成访问URL
                        url = self._get_public_url(bucket, f"{prefix}{file.name}")
                        stats['urls'].append({
                            'char': file.stem.split('_')[-1] if '_' in file.stem else '',
                            'url': url
                        })
                    else:
                        stats['failed'] += 1
                    
                    pbar.update(1)
        
        return stats
    
    def _get_public_url(self, bucket: str, key: str) -> str:
        """生成公开访问URL"""
        
        if self.provider == 'r2':
            # R2 需要配置自定义域名
            # 格式: https://your-domain.com/key
            domain = os.getenv('R2_PUBLIC_DOMAIN', f'{bucket}.r2.dev')
            return f"https://{domain}/{key}"
        
        elif self.provider == 's3':
            region = os.getenv('AWS_REGION', 'ap-southeast-1')
            return f"https://{bucket}.s3.{region}.amazonaws.com/{key}"
    
    def create_cdn_mapping(self, stats: Dict, output_file: str):
        """创建CDN URL映射文件"""
        
        mapping = {
            char_info['char']: char_info['url'] 
            for char_info in stats['urls'] 
            if char_info['char']
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(mapping, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 CDN映射已保存: {output_file}")
        print(f"   示例: 水 -> {mapping.get('水', 'N/A')}")


# ============================================================================
# 使用示例
# ============================================================================

def main():
    """主程序"""
    
    import sys
    
    print("="*70)
    print("汉字图片批量上传工具")
    print("="*70)
    
    # 检查环境变量
    print("\n🔧 配置检查:")
    
    provider = input("选择服务商 (r2/s3) [默认: r2]: ").strip() or 'r2'
    
    if provider == 'r2':
        required_vars = ['R2_ENDPOINT', 'R2_ACCESS_KEY_ID', 'R2_SECRET_ACCESS_KEY']
        print("\n需要设置的环境变量:")
        print("export R2_ENDPOINT='https://xxx.r2.cloudflarestorage.com'")
        print("export R2_ACCESS_KEY_ID='your_access_key'")
        print("export R2_SECRET_ACCESS_KEY='your_secret_key'")
        print("export R2_PUBLIC_DOMAIN='cdn.yourdomain.com'  # 可选")
    else:
        required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY']
        print("\n需要设置的环境变量:")
        print("export AWS_ACCESS_KEY_ID='your_access_key'")
        print("export AWS_SECRET_ACCESS_KEY='your_secret_key'")
        print("export AWS_REGION='ap-southeast-1'  # 可选")
    
    # 检查环境变量
    missing = [v for v in required_vars if not os.getenv(v)]
    if missing:
        print(f"\n❌ 缺少环境变量: {', '.join(missing)}")
        print("请先配置后再运行")
        sys.exit(1)
    
    print("✅ 环境变量配置完整")
    
    # 获取参数
    local_dir = input("\n本地图片目录 [默认: ./collected_characters]: ").strip() or './collected_characters'
    bucket = input("Bucket名称: ").strip()
    
    if not bucket:
        print("❌ Bucket名称不能为空")
        sys.exit(1)
    
    # 创建上传器
    uploader = CharacterImageUploader(provider=provider)
    
    # 开始上传
    print(f"\n🚀 开始上传...")
    stats = uploader.upload_directory(
        local_dir=local_dir,
        bucket=bucket,
        prefix='chars/',
        max_workers=10
    )
    
    # 显示结果
    print("\n" + "="*70)
    print("📊 上传完成")
    print("="*70)
    print(f"总计: {stats['total']}")
    print(f"成功: {stats['success']} ✅")
    print(f"失败: {stats['failed']} ❌")
    
    # 保存映射
    if stats['success'] > 0:
        uploader.create_cdn_mapping(stats, 'cdn_url_mapping.json')
        
        print(f"\n🌐 访问示例:")
        if stats['urls']:
            print(f"   {stats['urls'][0]['url']}")


if __name__ == "__main__":
    # 安装依赖提示
    try:
        import boto3
        from tqdm import tqdm
    except ImportError:
        print("❌ 缺少依赖，请先安装:")
        print("   pip install boto3 tqdm")
        exit(1)
    
    main()


"""
💡 快速开始指南

1️⃣ 安装依赖
-----------
pip install boto3 tqdm

2️⃣ 配置环境变量 (Cloudflare R2)
--------------------------------
# 在 Cloudflare Dashboard → R2 → 创建 API Token
export R2_ENDPOINT='https://your-account-id.r2.cloudflarestorage.com'
export R2_ACCESS_KEY_ID='your_access_key_id'
export R2_SECRET_ACCESS_KEY='your_secret_access_key'
export R2_PUBLIC_DOMAIN='cdn.yourdomain.com'  # 可选，配置自定义域名

3️⃣ 配置环境变量 (AWS S3)
-------------------------
export AWS_ACCESS_KEY_ID='your_access_key_id'
export AWS_SECRET_ACCESS_KEY='your_secret_access_key'
export AWS_REGION='ap-southeast-1'

4️⃣ 运行上传
-----------
python3 upload_to_cloud.py

# 或直接使用代码:
from upload_to_cloud import CharacterImageUploader

uploader = CharacterImageUploader(provider='r2')
stats = uploader.upload_directory(
    local_dir='./collected_characters',
    bucket='my-chinese-chars',
    prefix='chars/'
)

5️⃣ 使用CDN URL
--------------
import json

with open('cdn_url_mapping.json', 'r') as f:
    urls = json.load(f)

# 获取"水"的图片URL
water_url = urls['水']
print(water_url)
# https://cdn.yourdomain.com/chars/6c34_水.png

📖 完整文档: storage_comparison.md
"""
