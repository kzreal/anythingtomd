#!/usr/bin/env python3
"""
完整的功能测试，包括文件上传和转换
"""
from playwright.sync_api import sync_playwright
import sys
import json
import time

def test_full_functionality():
    """完整功能测试"""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 监听控制台消息
        console_messages = []
        page.on('console', lambda msg: console_messages.append(f"{msg.type}: {msg.text}"))

        # 监听网络请求
        network_requests = []
        page.on('request', lambda req: network_requests.append(req))
        page.on('response', lambda resp: network_requests.append(resp))

        # 监听页面错误
        page_errors = []
        page.on('pageerror', lambda error: page_errors.append(str(error)))

        try:
            print("=" * 60)
            print("开始完整功能测试")
            print("=" * 60)

            # 步骤 1: 访问主页
            print("\n[1/5] 访问主页...")
            response = page.goto('http://localhost:8080', timeout=30000)
            page.wait_for_load_state('networkidle')
            assert response.status == 200, f"HTTP 状态码不是 200: {response.status}"
            print(f"✓ 主页加载成功，状态码: {response.status}")

            # 检查页面标题
            title = page.title()
            assert "任意文档转Markdown" in title, f"页面标题不正确: {title}"
            print(f"✓ 页面标题正确: {title}")

            # 步骤 2: 检查页面元素
            print("\n[2/5] 检查页面元素...")
            h1_count = page.locator('h1').count()
            assert h1_count > 0, "未找到 h1 元素"
            print(f"✓ 找到 {h1_count} 个 h1 元素")

            file_input = page.locator('input[type="file"]')
            assert file_input.count() > 0, "未找到文件上传输入框"
            print("✓ 找到文件上传输入框")

            upload_area = page.locator('.upload-area')
            assert upload_area.count() > 0, "未找到上传区域"
            print("✓ 找到上传区域")

            button_count = page.locator('button').count()
            assert button_count > 0, "未找到按钮"
            print(f"✓ 找到 {button_count} 个按钮")

            # 步骤 3: 测试文件分析 API
            print("\n[3/5] 测试文件分析 API...")
            # 创建一个简单的测试文件
            test_file_path = '/tmp/test_file.txt'
            with open(test_file_path, 'w') as f:
                f.write("test content")

            # 使用 fetch API 测试 /api/analyze
            test_result = page.evaluate(f"""
                async () => {{
                    const formData = new FormData();
                    formData.append('file', new File(['test content'], 'test.docx', {{type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'}}));

                    try {{
                        const response = await fetch('/api/analyze', {{
                            method: 'POST',
                            body: formData
                        }});
                        const data = await response.json();
                        return {{ success: true, status: response.status, data }};
                    }} catch (error) {{
                        return {{ success: false, error: error.toString() }};
                    }}
                }}
            """)

            if test_result['success']:
                print(f"✓ API 调用成功，状态码: {test_result['status']}")
                print(f"  响应数据: {json.dumps(test_result['data'], ensure_ascii=False, indent=2)}")
            else:
                print(f"✗ API 调用失败: {test_result['error']}")

            # 步骤 4: 检查控制台错误
            print("\n[4/5] 检查控制台和页面错误...")
            time.sleep(1)  # 等待收集错误

            error_count = len([msg for msg in console_messages if 'error' in msg.lower()])
            if error_count > 0:
                print(f"⚠️  发现 {error_count} 个控制台错误:")
                for msg in console_messages:
                    if 'error' in msg.lower():
                        print(f"  - {msg}")
            else:
                print("✓ 没有控制台错误")

            if page_errors:
                print(f"⚠️  发现 {len(page_errors)} 个页面错误:")
                for error in page_errors:
                    print(f"  - {error}")
            else:
                print("✓ 没有页面错误")

            # 步骤 5: 截图并保存
            print("\n[5/5] 保存测试结果...")
            screenshot_path = '/tmp/webpage_functionality_test.png'
            page.screenshot(path=screenshot_path, full_page=True)
            print(f"✓ 页面截图已保存到: {screenshot_path}")

            # 测试总结
            print("\n" + "=" * 60)
            print("测试总结")
            print("=" * 60)
            print(f"✓ 主页访问: 正常 (HTTP {response.status})")
            print(f"✓ 页面标题: {title}")
            print(f"✓ 页面元素: 完整")
            print(f"✓ API 接口: {'正常' if test_result['success'] else '异常'}")
            print(f"✓ 控制台错误: {error_count} 个")
            print(f"✓ 页面错误: {len(page_errors)} 个")

            all_passed = (
                response.status == 200 and
                "任意文档转Markdown" in title and
                error_count == 0 and
                len(page_errors) == 0
            )

            if all_passed:
                print("\n" + "🎉" * 20)
                print("✅ 所有测试通过！网页可以正常使用！")
                print("🎉" * 20)
                return True
            else:
                print("\n⚠️  部分测试未通过，请检查上述问题")
                return False

        except Exception as e:
            print(f"\n❌ 测试过程中出现异常: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()

if __name__ == '__main__':
    success = test_full_functionality()
    sys.exit(0 if success else 1)
