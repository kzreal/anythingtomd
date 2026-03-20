#!/usr/bin/env python3
"""
详细检查网页内容和截图
"""
from playwright.sync_api import sync_playwright
import sys

def test_webpage_detailed():
    """详细测试网页内容"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            print("正在访问 http://localhost:8080 ...")
            response = page.goto('http://localhost:8080', timeout=30000)
            print(f"HTTP 状态码: {response.status}")

            # 等待页面加载完成
            page.wait_for_load_state('networkidle', timeout=10000)

            # 获取页面标题
            title = page.title()
            print(f"\n页面标题: {title}")

            # 获取页面内容
            content = page.content()
            print(f"\n页面 HTML 内容（前 1000 字符）:\n{content[:1000]}")

            # 查找所有文本
            body_text = page.locator('body').inner_text()
            print(f"\n页面文本内容:\n{body_text[:500]}")

            # 检查是否有 500 错误
            if '500' in content:
                print("\n⚠️  页面中包含 '500' 字符串")
                # 检查是否在错误消息中
                if '<h1>' in content and '500' in content[content.find('<h1>'):content.find('<h1>')+100]:
                    print("   警告：可能是真正的 500 错误!")
                else:
                    print("   说明：'500' 可能出现在文档或说明中，不是错误")

            # 截图
            screenshot_path = '/tmp/webpage_detailed.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"\n✓ 页面截图已保存到: {screenshot_path}")
            print(f"  可以使用以下命令查看: open {screenshot_path}")

            # 检查控制台错误
            console_errors = []
            page.on('console', lambda msg: console_errors.append(msg) if msg.type == 'error' else None)
            page.wait_for_timeout(2000)  # 等待收集控制台消息

            if console_errors:
                print(f"\n发现 {len(console_errors)} 个控制台错误:")
                for error in console_errors:
                    print(f"  - {error.text}")
            else:
                print("\n✓ 没有控制台错误")

            # 检查关键元素
            print("\n检查关键元素:")
            h1_count = page.locator('h1').count()
            print(f"  - h1 元素: {h1_count} 个")

            if h1_count > 0:
                h1_text = page.locator('h1').first.inner_text()
                print(f"    内容: {h1_text}")

            file_input_count = page.locator('input[type="file"]').count()
            print(f"  - 文件上传输入框: {file_input_count} 个")

            button_count = page.locator('button').count()
            print(f"  - 按钮: {button_count} 个")

            # 检查是否有 JavaScript 错误
            page_errors = []
            page.on('pageerror', lambda error: page_errors.append(error))
            page.wait_for_timeout(1000)

            if page_errors:
                print(f"\n发现 {len(page_errors)} 个 JavaScript 错误:")
                for error in page_errors:
                    print(f"  - {error}")
            else:
                print("\n✓ 没有 JavaScript 错误")

            print("\n" + "="*50)
            print("网页状态总结:")
            print("="*50)
            print(f"✓ HTTP 状态码: {response.status}")
            print(f"✓ 页面标题: {title}")
            print(f"✓ 页面可访问: 是")
            print(f"✓ 控制台错误: {len(console_errors)} 个")
            print(f"✓ JavaScript 错误: {len(page_errors)} 个")

            if response.status == 200 and len(console_errors) == 0 and len(page_errors) == 0:
                print("\n✅ 网页启动正常，可以正常使用!")
                return True
            else:
                print("\n⚠️  网页可能存在问题，请检查上述错误")
                return False

        except Exception as e:
            print(f"\n❌ 网页访问失败: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == '__main__':
    success = test_webpage_detailed()
    sys.exit(0 if success else 1)
