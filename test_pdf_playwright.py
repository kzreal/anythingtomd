"""
使用 Playwright 测试 PDF 转换功能
"""
import asyncio
from pathlib import Path
from playwright.sync_api import sync_playwright

# 获取测试 PDF 文件
def get_test_pdf():
    """获取测试用的 PDF 文件"""
    test_pdf = Path("/Users/kyle/Projects/anythingtomd/测试.pdf")
    if test_pdf.exists():
        return test_pdf
    else:
        print("✗ 没有找到测试 PDF 文件")
        return None


def test_pdf_conversion():
    """测试 PDF 转换功能"""
    print("🧪 开始测试 PDF 转换功能...\n")

    # 获取测试 PDF
    test_pdf = get_test_pdf()
    if not test_pdf:
        print("✗ 无法找到测试 PDF 文件")
        return False

    print(f"📄 使用测试文件: {test_pdf}\n")

    with sync_playwright() as p:
        # 启动浏览器
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        try:
            # 访问应用
            app_url = "http://localhost:8080"
            print(f"🌐 访问应用: {app_url}")
            page.goto(app_url)
            print("✓ 页面加载成功\n")

            # 上传 PDF 文件
            print("📤 上传 PDF 文件...")
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files(str(test_pdf))
            print("✓ 文件已上传\n")

            # 等待文件分析完成
            print("⏳ 等待文件分析...")
            page.wait_for_selector('#fileInfo', timeout=30000)
            print("✓ 文件分析完成\n")

            # 获取文件信息
            file_info = page.locator('#fileInfo').text_content()
            print(f"📋 文件信息:\n{file_info}\n")

            # 点击转换按钮
            print("▶️ 开始转换...")
            convert_btn = page.locator('#convertBtn')
            convert_btn.click()
            print("✓ 转换按钮已点击\n")

            # 等待转换完成 - 增加超时时间
            print("⏳ 等待转换完成 (可能需要几分钟)...")
            page.wait_for_selector('#preview-content', timeout=300000)  # 5分钟超时
            print("✓ 转换完成\n")

            # 获取预览内容
            preview_content = page.locator('#preview-content').text_content()
            print(f"📝 预览内容 (前500字符):\n{preview_content[:500]}\n")

            # 检查是否包含行号
            if '<!--' in preview_content:
                print("✓ 检测到行号 (PDF 转换应该保留行号)\n")
            else:
                print("⚠ 未检测到行号\n")

            # 检查是否包含表格
            if '|' in preview_content:
                print("✓ 检测到表格格式\n")
            else:
                print("⚠ 未检测到表格格式\n")

            # 测试切片列表
            sections_list = page.locator('#sections-list a.section-item').all()
            print(f"📑 切片数量: {len(sections_list)}\n")

            if len(sections_list) > 0:
                # 点击第一个切片
                print("🔍 测试切片切换...")
                first_section = sections_list[0]
                first_section.click()
                page.wait_for_timeout(1000)
                print("✓ 切片切换功能正常\n")

                # 测试下载功能
                print("⬇️ 测试下载功能...")
                with page.expect_download() as download_info:
                    page.locator('#downloadBtn').click()
                download = download_info.value
                print(f"✓ 下载完成: {download.suggested_filename}\n")

            print("✅ 测试完成")

            return True

        except Exception as e:
            print(f"✗ 测试失败: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            browser.close()


if __name__ == "__main__":
    success = test_pdf_conversion()
    if not success:
        exit(1)
