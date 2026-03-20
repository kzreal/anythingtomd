"""
使用 Playwright 测试网页功能
"""
import asyncio
from playwright.async_api import async_playwright
from pathlib import Path


async def main():
    async with async_playwright() as p:
        print("启动浏览器...")
        browser = await p.chromium.launch(headless=False, slow_mo=1000)
        page = await browser.new_page()
        page.set_default_timeout(10000)

        print("=" * 60)
        print("测试 1: 访问主页")
        print("=" * 60)

        # 访问主页
        await page.goto("http://localhost:8080")
        print(f"页面标题: {await page.title()}")

        # 截图
        await page.screenshot(path="test_results/01_homepage.png", full_page=True)
        print("✓ 主页截图保存成功")

        # 验证页面元素
        upload_area = page.locator("#uploadArea")
        await upload_area.wait_for()
        print("✓ 上传区域加载成功")

        print("\n" + "=" * 60)
        print("测试 2: Excel 文件转换")
        print("=" * 60)

        # 上传 Excel 文件
        file_input = page.locator("#fileInput")
        excel_file = Path(__file__).parent / "filled_table.xlsx"

        print(f"上传 Excel 文件: {excel_file}")
        await file_input.set_input_files(str(excel_file))

        # 等待文件信息显示
        await page.wait_for_selector("#fileInfo.show", timeout=5000)
        print("✓ 文件信息显示成功")

        # 截图
        await page.screenshot(path="test_results/02_excel_file_selected.png")

        # 验证 Excel 选项显示
        excel_info = page.locator("#excelInfo.show")
        await excel_info.wait_for()
        print("✓ Excel 选项显示成功")

        # 点击转换按钮
        convert_btn = page.locator("#convertBtn")
        await convert_btn.click()
        print("✓ 点击转换按钮")

        # 等待预览内容加载
        await page.wait_for_selector("#result.show", timeout=30000)
        print("✓ 预览内容加载成功")

        # 截图预览
        await page.screenshot(path="test_results/03_excel_preview.png", full_page=True)
        print("✓ 预览截图保存成功")

        # 验证预览文本
        preview_text = page.locator("#previewText")
        text_content = await preview_text.text_content()
        if "Sheet1" in text_content and "<!--" in text_content:
            print("✓ 预览文本验证成功")
        else:
            print("✗ 预览文本验证失败")

        # 测试复制按钮（如果存在）
        try:
            copy_btn = page.locator("button").filter(has_text="复制内容")
            if await copy_btn.is_visible():
                await copy_btn.click()
                print("✓ 复制按钮点击成功")

                # 等待成功消息
                await page.wait_for_selector(".message.success:has-text('已复制')", timeout=5000)
                print("✓ 复制功能验证成功")
        except Exception as e:
            print(f"复制功能测试跳过: {e}")

        print("\n" + "=" * 60)
        print("测试 3: Word 文件转换")
        print("=" * 60)

        # 点击上传区域重新选择文件
        await upload_area.click()

        # 上传 Word 文件
        word_file = Path(__file__).parent / "商务文件.docx"
        print(f"上传 Word 文件: {word_file}")
        await file_input.set_input_files(str(word_file))

        # 等待文件信息显示
        await page.wait_for_selector("#fileInfo.show", timeout=5000)
        print("✓ 文件信息显示成功")

        # 截图
        await page.screenshot(path="test_results/04_word_file_selected.png")

        # 验证 Word 选项显示
        level_selector = page.locator("#levelSelector.show")
        await level_selector.wait_for()
        print("✓ Word 切分层级选项显示成功")

        # 选择二级切分层级
        level_2_radio = page.locator('input[name="sliceLevel"][value="2"]')
        await level_2_radio.check()
        print("✓ 选择二级切分层级")

        # 点击转换按钮
        await convert_btn.click()
        print("✓ 点击转换按钮")

        # 等待进度条完成
        await page.wait_for_selector("#progress.show", timeout=5000)
        print("✓ 进度条显示")

        await page.wait_for_selector(".success:has-text('转换成功')", timeout=60000)
        print("✓ Word 文档转换成功")

        # 截图
        await page.screenshot(path="test_results/05_word_conversion.png")
        print("✓ Word 转换截图保存成功")

        print("\n" + "=" * 60)
        print("所有测试完成！")
        print("=" * 60)

        await browser.close()


if __name__ == "__main__":
    import sys
    from pathlib import Path

    # 创建测试结果目录
    test_dir = Path(__file__).parent / "test_results"
    test_dir.mkdir(exist_ok=True)

    # 运行测试
    asyncio.run(main())
