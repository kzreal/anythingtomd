#!/usr/bin/env python3
"""
测试网页是否能正常启动
"""
from playwright.sync_api import sync_playwright
import sys

def test_webpage():
    """测试网页是否正常启动"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("正在访问 http://localhost:8080 ...")
            page.goto('http://localhost:8080', timeout=30000)

            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=10000)

            # 检查页面标题
            title = page.title()
            print(f"页面标题: {title}")

            # 检查页面内容
            content = page.content()

            # 检查是否有错误
            errors = []
            if '500' in content:
                errors.append("页面显示 500 错误")
            if 'error' in content.lower() and 'internal server error' in content.lower():
                errors.append("服务器内部错误")

            # 检查主要元素
            try:
                # 查找上传按钮
                upload_elements = page.locator('input[type="file"], button').count()
                print(f"找到 {upload_elements} 个可能的上传元素")

                # 查找标题元素
                h1_elements = page.locator('h1, h2').count()
                print(f"找到 {h1_elements} 个标题元素")

                # 截图
                screenshot_path = '/tmp/webpage_test.png'
                page.screenshot(path=screenshot_path, full_page=True)
                print(f"页面截图已保存到: {screenshot_path}")

            except Exception as e:
                print(f"检查页面元素时出错: {e}")
                errors.append(f"元素检查失败: {e}")

            # 检查控制台错误
            console_errors = []
            page.on('console', lambda msg: console_errors.append(msg) if msg.type == 'error' else None)
            page.wait_for_timeout(1000)  # 等待收集控制台消息

            if console_errors:
                print(f"\n发现 {len(console_errors)} 个控制台错误:")
                for error in console_errors:
                    print(f"  - {error.text}")
            else:
                print("✓ 没有控制台错误")

            # 最终判断
            if errors:
                print("\n✗ 网页存在问题:")
                for error in errors:
                    print(f"  - {error}")
                return False
            else:
                print("\n✓ 网页启动正常!")
                return True

        except Exception as e:
            print(f"\n✗ 网页访问失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == '__main__':
    success = test_webpage()
    sys.exit(0 if success else 1)
