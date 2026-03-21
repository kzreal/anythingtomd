"""检查 wp:anchor 元素的结构"""
from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

doc = Document('/Users/kyle/Downloads/测试.docx')

# 检查段落 19 的 drawing 元素
para = doc.paragraphs[18]  # 索引从 0 开始，段落 19 就是索引 18

# 获取 drawing 元素
drawings = para._element.xpath('.//w:drawing')
if drawings:
    drawing = drawings[0]

    # 获取 anchor 元素（drawing 的直接子元素）
    anchors = drawing.xpath('./wp:anchor')
    print(f"Anchor 元素数量: {len(anchors)}")

    if anchors:
        anchor = anchors[0]
        print(f"\nAnchor 元素 XML:")
        print(str(anchor)[:1000])

        print(f"\nAnchor 的子元素:")
        for child in anchor:
            print(f"  标签: {child.tag}")
            print(f"  类型: {type(child).__name__}")

        # 检查 anchor 下的所有 pic:pic
        pics = anchor.xpath('.//pic:pic')
        print(f"\nAnchor 下 pic:pic 元素数量: {len(pics)}")

        if pics:
            pic = pics[0]
            print(f"\npic:pic 元素 XML:")
            print(str(pic)[:1000])

            # 获取 blip 引用
            blips = pic.xpath('.//a:blip')
            if blips:
                print(f"\nblip 元素数量: {len(blips)}")
                for i, blip in enumerate(blips):
                    embed = blip.xpath('.//@r:embed')
                    print(f"  blip {i} r:embed: {embed}")
