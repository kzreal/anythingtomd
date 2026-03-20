#!/bin/bash

# 启动任意文档转Markdown服务

echo "=================================="
echo "  任意文档转Markdown服务"
echo "=================================="
echo ""

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装 Python 3.7+"
    exit 1
fi

echo "检查依赖..."
python3 -c "import flask, pandas, docx" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

echo ""
echo "启动服务..."
echo "访问地址: http://localhost:8080"
echo "按 Ctrl+C 停止服务"
echo "=================================="
echo ""

python3 app.py
