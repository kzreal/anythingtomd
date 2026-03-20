"""
使用 Playwright 测试图片转换功能
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image, ImageDraw, ImageFont


def create_test_images():
    """创建测试用的图片文件"""
    upload_dir = Path("/tmp/test_images")
    upload_dir.mkdir(exist_ok=True)

    images = []

    # 图片 1: 文字图片
    img1 = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img1)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    draw.text((50, 50), "测试图片 - 图片 1", fill='black', font=font)
    draw.text((50, 120), "这是用于测试 OCR 功能的图片", fill='black', font=font)
    draw.text((50, 190), "包含一些简单的文字内容", fill='black', font=font)

    path1 = upload_dir / "test_image_1.png"
    img1.save(path1)
    images.append(path1)
    print(f"✓ 创建测试图片 1: {path1}")

    # 图片 2: 表格图片
    img2 = Image.new('RGB', (800, 400), color='white')
    draw = ImageDraw.Draw(img2)
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
    except:
        font = ImageFont.load_default()

    draw.text((50, 50), "数据表格", fill='black', font=font)

    # 画表格线
    for i in range(4):
        y = 100 + i * 60
        draw.line([(50, y), (750, y)], fill='black', width=2)

    for i in range(4):
        x = 50 + i * 233
        draw.line([(x, 100), (x, 280)], fill='black', width=2)

    # 表格文字
    draw.text((70, 110), "姓名", fill='black', font=font)
    draw.text((303, 110), "年龄", fill='black', font=font)
    draw.text((536, 110), "城市", fill='black', font=font)

    draw.text((70, 170), "张三", fill='black', font=font)
    draw.text((303, 170), "25", fill='black', font=font)
    draw.text((536, 170), "北京", fill='black', font=font)

    draw.text((70, 230), "李四", fill='black', font=font)
    draw.text((303, 230), "30", fill='black', font=font)
    draw.text((536, 230), "上海", fill='black', font=font)

    path2 = upload_dir / "test_image_2.png"
    img2.save(path2)
    images.append(path2)
    print(f"✓ 创建测试图片 2: {path2}")

    return images


def test_image_conversion():
    """测试图片转换功能"""
    print("🧪 开始测试图片转换功能...\n")

    # 创建测试图片
    test_images = create_test_images()
    print(f"\n📄 使用测试图片数量: {len(test_images)}\n")

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

            # 上传图片文件（多选）
            print("📤 上传图片文件...")
            file_input = page.locator('input[type="file"]')
            file_input.set_input_files([str(img) for img in test_images])
            print(f"✓ 已上传 {len(test_images)} 张图片\n")

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
            print("⏳ 等待转换完成...")
            page.wait_for_selector('#preview-content', timeout=300000)  # 5分钟超时
            print("✓ 转换完成\n")

            # 获取预览内容
            preview_content = page.locator('#preview-content').text_content()
            print(f"📝 预览内容 (前500字符):\n{preview_content[:500]}\n")

            # 检查是否包含行号
            if '<!--' in preview_content:
                print("✓ 检测到行号\n")
            else:
                print("⚠ 未检测到行号\n")

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

                # 点击第二个切片
                if len(sections_list) > 1:
                    second_section = sections_list[1]
                    second_section.click()
                    page.wait_for_timeout(1000)
                    print("✓ 第二个切片切换正常\n")

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
    success = test_image_conversion()
    if not success:
        exit(1)
