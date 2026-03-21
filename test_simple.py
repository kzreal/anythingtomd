"""
简单测试脚本 - 直接验证图片识别功能
"""
import requests
import json
import re

# 测试文档
test_doc = "/Users/kyle/Downloads/测试.docx"

print("🧪 开始测试 Word 图片识别功能...\n")

# API 请求 - 零级模式（整个文档为一个切片）
print("📄 发送转换请求（零级模式）...")
with open(test_doc, 'rb') as f:
    files = {'file': (test_doc.split('/')[-1], f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    data = {
        'options': json.dumps({'max_level': '0'}),
        'mode': 'preview'
    }
    response = requests.post('http://localhost:8080/api/convert', files=files, data=data)

print(f"状态码: {response.status_code}")

if response.status_code == 200:
    result = response.json()
    preview = result.get('preview_text', '')
    sections = result.get('sections', [])

    print(f"\n✅ 转换成功")
    print(f"📊 切片数量: {len(sections)}")
    print(f"📝 预览内容长度: {len(preview)} 字符\n")

    # 完整预览内容
    print("=" * 60)
    print("完整预览内容:")
    print("=" * 60)
    print(preview)
    print("=" * 60)

    # 检查行号
    if '<!--' in preview:
        print("\n✅ 检测到行号注释")
    else:
        print("\n⚠ 未检测到行号注释")

    # 检查图片识别结果
    if '[图片:' in preview:
        image_descriptions = re.findall(r'\[图片: (.*?)\]', preview)
        print(f"\n✅ 检测到图片识别结果 ({len(image_descriptions)} 个):")
        for i, desc in enumerate(image_descriptions, 1):
            print(f"   {i}. {desc}")
    else:
        print("\n⚠ 未检测到图片识别结果")

    # 切片信息
    print(f"\n📑 切片信息:")
    for section in sections:
        print(f"   切片 {section['index']}: {section['title']}")

    print("\n✅ 测试完成")
else:
    print(f"\n❌ 转换失败: {response.status_code}")
    print(f"错误信息: {response.text}")
