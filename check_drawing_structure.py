"""检查 drawing 元素的结构"""
from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

doc = Document('/Users/kyle/Downloads/测试.docx')

# 检查段落 19 的 drawing 元素
para = doc.paragraphs[18]  # 索引从 0 开始，段落 19 就是索引 18
print("="*60)
print("段落 19 的 drawing 元素分析")
print("="*60)
print(f"\n文本内容: {para.text}")

# 获取 drawing 元素
drawings = para._element.xpath('.//w:drawing')
if drawings:
    drawing = drawings[0]
    print(f"\nDrawing 元素 XML:")
    print(str(drawing)[:1000])

    print(f"\nDrawing 的子元素:")
    for child in drawing:
        print(f"  标签: {child.tag}")
        print(f"  XML: {str(child)[:500]}")

    # 检查是否有 wp:inline
    inlines = drawing.xpath('.//w:drawing/wp:inline')
    print(f"\nwp:inline 元素数量: {len(inlines)}")

    # 检查是否有 wp:anchor
    anchors = drawing.xpath('.//w:drawing/wp:anchor')
    print(f"wp:anchor 元素数量: {len(anchors)}")

    # 检查是否有 pic:pic
    pics = drawing.xpath('.//w:drawing/pic:pic')
    print(f"pic:pic 元素数量: {len(pics)}")

    if pics:
        for i, pic in enumerate(pics):
            print(f"\npic:pic 元素 {i}:")
            print(str(pic)[:800])

            # 查找所有可能的 r:embed
            all_embeds = pic.xpath('.//@r:embed')
            print(f"  所有 r:embed 属性: {all_embeds}")

    # 检查所有包含 r:embed 的元素
    print(f"\nDrawing 中所有包含 r:embed 的路径:")
    all_embed_paths = drawing.xpath('.//*[@r:embed]')
    for elem in all_embed_paths:
        embed = elem.xpath('.//@r:embed')
        if embed:
            print(f"  元素: {elem.tag}")
            print(f"  r:embed: {embed[0]}")
