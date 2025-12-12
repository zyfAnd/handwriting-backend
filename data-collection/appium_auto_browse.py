#!/usr/bin/env python3
"""
Appium 自动化浏览 CloudBrush App
完全无人值守采集所有汉字图片
"""

import time
from appium import webdriver
from appium.options.ios import XCUITestOptions
from appium.webdriver.common.appiumby import AppiumBy

class CloudBrushAutomation:
    """CloudBrush 自动化"""

    def __init__(self, device_udid: str, bundle_id: str = "com.fanglige.CloudBrush"):
        """
        初始化 Appium

        Args:
            device_udid: iPhone 设备 UDID
            bundle_id: CloudBrush App Bundle ID
        """

        self.device_udid = device_udid
        self.bundle_id = bundle_id

        # 配置选项
        options = XCUITestOptions()
        options.platform_name = 'iOS'
        options.automation_name = 'XCUITest'
        options.device_name = 'iPhone'
        options.udid = device_udid
        options.bundle_id = bundle_id
        options.no_reset = True  # 不重置 App

        # 启动 Appium
        print("🚀 连接到 Appium 服务器...")
        self.driver = webdriver.Remote(
            'http://localhost:4723',
            options=options
        )

        print("✅ 已连接到设备")

    def browse_chars(self, target_count: int = 3500):
        """
        自动浏览汉字

        Args:
            target_count: 目标采集数量
        """

        print(f"📊 开始自动浏览 {target_count} 个汉字...")
        print()

        browsed_count = 0

        try:
            while browsed_count < target_count:
                # 点击屏幕中间（打开汉字详情）
                screen_size = self.driver.get_window_size()
                x = screen_size['width'] // 2
                y = screen_size['height'] // 2

                # 点击汉字
                self.driver.tap([(x, y)])

                # 等待图片加载
                time.sleep(1.5)

                # 返回
                self.driver.back()
                time.sleep(0.5)

                # 向左滑动（下一个汉字）
                start_x = screen_size['width'] * 0.8
                end_x = screen_size['width'] * 0.2
                y = screen_size['height'] // 2

                self.driver.swipe(start_x, y, end_x, y, duration=200)
                time.sleep(0.5)

                browsed_count += 1

                # 进度报告
                if browsed_count % 10 == 0:
                    print(f"✅ 已浏览: {browsed_count}/{target_count}")

                # 每 100 个字休息一下
                if browsed_count % 100 == 0:
                    print(f"⏸️  休息 5 秒...")
                    time.sleep(5)

        except KeyboardInterrupt:
            print()
            print(f"⚠️  用户中断，已浏览 {browsed_count} 个汉字")

        except Exception as e:
            print(f"❌ 错误: {e}")

        finally:
            print()
            print("=" * 70)
            print(f"✅ 浏览完成！共浏览 {browsed_count} 个汉字")
            print("=" * 70)

    def close(self):
        """关闭连接"""
        if self.driver:
            self.driver.quit()
            print("👋 已断开连接")

def main():
    """主函数"""

    print("=" * 70)
    print("  CloudBrush 自动化采集器 (Appium)")
    print("=" * 70)
    print()

    # 获取设备 UDID
    device_udid = input("请输入设备 UDID (或按回车使用默认): ").strip()

    if not device_udid:
        print("⚠️  请先获取设备 UDID:")
        print("   运行: instruments -s devices")
        print("   或者: system_profiler SPUSBDataType | grep 'Serial Number'")
        return

    print()
    print("📱 设备 UDID:", device_udid)
    print()
    print("⚠️  请确保:")
    print("  1. iPhone 已连接到 Mac")
    print("  2. mitmproxy 正在运行")
    print("  3. iPhone 已配置代理")
    print("  4. Appium 服务器正在运行 (appium)")
    print()

    input("准备好后按回车开始...")

    try:
        # 创建自动化实例
        automation = CloudBrushAutomation(device_udid)

        # 开始浏览
        automation.browse_chars(target_count=3500)

        # 关闭
        automation.close()

    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print()
        print("请检查:")
        print("  1. Appium 服务器是否运行: appium")
        print("  2. WebDriverAgent 是否已安装到设备")
        print("  3. 设备 UDID 是否正确")

if __name__ == "__main__":
    main()
