"""调试签名图片检测"""
from docx import Document
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

doc = Document('/Users/kyle/Downloads/测试.docx')

# 查找包含"签字"或"盖章"的段落
print("🔍 查找包含签名的段落...\n")

for i, para in enumerate(doc.paragraphs, 1):
    text = para.text.strip()
    if '签字' in text or '盖章' in text or '签' in text:
        print(f"\n📄 段落 {i}: {text[:100]}")
        print(f"   段落 XML 结构:")
        print(f"   {para._element}")

        # 检查图片
        print(f"\n   检查图片...")
        image_count = 0

        # 方法1: 检查 wp:inline
        for run in para.runs:
            for inline in run._element.xpath('.//w:drawing/wp:inline'):
                image_count += 1
                print(f"   ✅ 找到 wp:inline 图片 {image_count}")
                embed = inline.xpath('.//a:blip/@r:embed')
                if embed:
                    print(f"      图片 ID: {embed[0]}")

        # 方法2: 检查 pic:pic
        for run in para.runs:
            for drawing in run._element.xpath('.//w:drawing/pic:pic'):
                image_count += 1
                print(f"   ✅ 找到 pic:pic 图片 {image_count}")
                print(f"      Drawing XML: {drawing}")

                # 获取所有可能的 r:embed
                all_embeds = drawing.xpath('.//@r:embed')
                print(f"      所有 r:embed: {all_embeds}")

        print(f"   🔢 段落中 run 数量: {len(para.runs)}")
        for j, run in enumerate(para.runs):
            print(f"      Run {j}: text='{run.text}'")
            print(f"         XML: {run._element}")

        if image_count == 0:
            print(f"   ⚠️ 段落中未检测到任何图片元素")
        else:
            print(f"   ✅ 段落中共检测到 {image_count} 个图片元素")

print("\n" + "="*60)
print("检查文档关系中的所有图片...")
print("="*60 + "\n")

if hasattr(doc, 'part') and hasattr(doc.part, 'related_parts'):
    print(f"文档共有 {len(doc.part.related_parts)} 个关系\n")

    for rId, part in doc.part.related_parts.items():
        content_type = part.content_type
        if 'image' in content_type:
            print(f"✅ 图片 rId: {rId}")
            print(f"   Content-Type: {content_type}")
            print(f"   Part Type: {type(part).__name__}")
            print(f"   Blob Size: {len(part.blob)} bytes")
            print()
