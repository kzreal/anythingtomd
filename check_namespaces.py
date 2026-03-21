"""检查命名空间"""
from docx import Document

doc = Document('/Users/kyle/Downloads/测试.docx')

# 获取段落 19 的 drawing 元素
para = doc.paragraphs[18]  # 索引从 0 开始，段落 19 就是索引 18

# 获取 drawing 元素
drawings = para._element.xpath('.//w:drawing')
if drawings:
    drawing = drawings[0]

    print("Drawing 元素及其所有子元素:")
    print(f"Drawing tag: {drawing.tag}")
    print(f"\n子元素列表:")

    for child in drawing:
        print(f"  {child.tag}")
        print(f"    {type(child).__name__}")

    # 检查 anchor 元素
    print("\n尝试查找 anchor:")
    anchors1 = drawing.xpath('./wp:anchor')
    print(f"  ./wp:anchor 数量: {len(anchors1)}")

    # 检查 anchor 元素（使用完整命名空间）
    print("\n尝试查找 anchor (完整命名空间):")
    anchors2 = drawing.xpath('.//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}anchor')
    print(f"  数量: {len(anchors2)}")

    # 检查是否有任何 anchor 相关的元素
    print("\n检查所有子元素中是否包含 'anchor':")
    for child in drawing:
        tag_str = str(child.tag)
        if 'anchor' in tag_str.lower():
            print(f"  找到 anchor 元素: {child.tag}")

    # 检查是否有 pic:pic
    print("\n检查是否有 pic:pic:")
    pics = drawing.xpath('.//pic:pic')
    print(f"  数量: {len(pics)}")

    if pics:
        print(f"\n第一个 pic:pic 元素:")
        pic = pics[0]
        print(f"  Tag: {pic.tag}")

        # 检查 blip
        blips = pic.xpath('.//a:blip/@r:embed')
        print(f"  blip r:embed: {blips}")
