"""完整输出测试"""
import requests
import json

test_doc = "/Users/kyle/Downloads/测试.docx"

with open(test_doc, 'rb') as f:
    files = {'file': (test_doc.split('/')[-1], f, 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')}
    data = {
        'options': json.dumps({'max_level': '0'}),
        'mode': 'preview'
    }
    response = requests.post('http://localhost:8080/api/convert', files=files, data=data)

if response.status_code == 200:
    result = response.json()
    preview = result.get('preview_text', '')

    # 按行分割
    lines = preview.split('\n')

    # 输出第 7-12 行
    print("预览内容第 7-12 行:")
    print("="*60)
    for i, line in enumerate(lines[6:12], 7):
        print(f"<!-- {i} --> {line}")
else:
    print(f"转换失败: {response.status_code}")
