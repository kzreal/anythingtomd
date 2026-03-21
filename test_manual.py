"""
手动测试脚本 - 使用浏览器打开页面进行测试
"""
import time
import subprocess
from playwright.sync_api import sync_playwright
from pathlib import Path

# 打开浏览器窗口
print("🌐 启动浏览器...")

# 创建测试文档
test_doc = Path("/tmp/test_word/test_with_images.docx")
print(f"📄 测试文档: {test_doc}")
print(f"📝 文件存在: {test_doc.exists()}")

# 获取 API 返回的预览内容
import requests
import json

print("\n=== 测试 API ===")
with open(test_doc, 'rb') as f:
    files = {'file': (test_doc.name, f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    data = {
        'options': json.dumps({'max_level': '0'}),
        'mode': 'preview'
    }
    response = requests.post('http://localhost:8080/api/convert', files=files, data=data)
    print(f"状态码: {response.status_code}")

    if response.status_code == 200:
        result = response.json()
        preview = result.get('preview_text', '')
        print(f"\n预览内容长度: {len(preview)} 字符")

        # 检查图片识别
        if '[图片:' in preview:
            import re
            matches = re.findall(r'\[图片: (.*?)\]', preview)
            print(f"\n✅ 检测到 {len(matches)} 个图片识别结果:")
            for i, m in enumerate(matches, 1):
                print(f"   {i}. {m}")
        else:
            print("\n⚠ 未检测到图片识别结果")

        print(f"\n前 1000 字符预览:")
        print(preview[:1000])
    else:
        print(f"错误: {response.text}")

print("\n=== 测试完成 ===")
