"""详细测试脚本"""
import requests
import json

# 测试文档
test_doc = "/Users/kyle/Downloads/测试.docx"

print("🧪 开始详细测试...\n")

# 清空日志文件
with open('/tmp/flask_full.log', 'w') as f:
    f.write('')

# 启动 Flask
import subprocess
import time
import os

# 检查端口是否被占用
if os.system('lsof -i:8080 > /dev/null 2>&1') == 0:
    print("端口 8080 被占用，先关闭...")
    os.system('pkill -9 -f "python.*app.py"')
    time.sleep(2)

# 启动 Flask
print("启动 Flask 服务...")
subprocess.Popen(['python3', 'app.py'], stdout=open('/tmp/flask_full.log', 'w'), stderr=subprocess.STDOUT)
time.sleep(3)

# API 请求
print("📄 发送转换请求...")
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

    print(f"✅ 转换成功")
    print(f"📊 切片数量: {len(sections)}")
    print(f"📝 预览内容长度: {len(preview)} 字符\n")
else:
    print(f"❌ 转换失败: {response.status_code}")

# 显示 Flask 日志
print("\n" + "="*60)
print("Flask 日志:")
print("="*60 + "\n")
with open('/tmp/flask_full.log', 'r') as f:
    log_content = f.read()
    print(log_content)

# 查找图片相关日志
print("\n" + "="*60)
print("图片相关日志:")
print("="*60 + "\n")
for line in log_content.split('\n'):
    if '图片' in line.lower() or 'image' in line.lower() or 'drawing' in line.lower() or 'anchor' in line.lower() or 'extract' in line.lower() or 'llm' in line.lower():
        print(line)
