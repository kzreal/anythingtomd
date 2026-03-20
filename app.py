"""
主Flask应用
任意文档转Markdown服务
"""
import io
import logging
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.parse import quote

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

import config
from utils.file_detector import detect_file_type, is_allowed_file
from converters.word_converter import WordConverter
from converters.excel_converter import ExcelConverter

# 日志配置
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config.update({
    'UPLOAD_FOLDER': str(config.UPLOAD_FOLDER),
    'MAX_CONTENT_LENGTH': config.MAX_CONTENT_LENGTH,
})

logger.info(f"Flask应用初始化完成")
logger.info(f"LLM服务可用: {config.LLM_AVAILABLE}")
if config.LLM_AVAILABLE:
    logger.info(f"LLM端点: {config.LLM_API_ENDPOINT[:50]}...")
logger.info(f"下载路径: {config.DOWNLOAD_FOLDER}")


# 错误处理
@app.errorhandler(RequestEntityTooLarge)
def handle_request_entity_too_large(e):
    return jsonify({'error': '文件大小超过限制，最大支持 1 GB'}), 413


@app.errorhandler(413)
def handle_413(e):
    return jsonify({'error': '文件大小超过限制，最大支持 1 GB'}), 413


# 路由定义
@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_file():
    """分析文件信息"""
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，仅支持 .docx, .xlsx, .xls'}), 400

    file_type = detect_file_type(file.filename)

    result = {
        'success': True,
        'file_type': file_type,
        'filename': file.filename,
        'file_size': file.content_length,
    }

    # 添加文件类型特定信息
    if file_type == 'word':
        result['word_options'] = {
            'max_level': [0, 1, 2, 3, 'all'],
            'default': 2,
            'description': '0=全部转成一个文件，1-3=按标题层级切片，all=按所有层级切片'
        }
    elif file_type == 'excel':
        result['excel_options'] = {
            'description': '每个sheet将转换为独立的Markdown文件'
        }

    return jsonify(result)


@app.route('/api/convert', methods=['POST'])
def convert_file():
    """
    转换文件接口

    参数:
    - file: 文件
    - options: JSON字符串
    - mode: "preview" | "download" (默认为 "preview"）
    """
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 获取参数
    mode = request.form.get('mode', 'preview')
    options_json = request.form.get('options', '{}')

    try:
        import json
        options = json.loads(options_json)
    except json.JSONDecodeError:
        options = {}

    # 保存文件（使用原始文件名）
    filename = file.filename
    # 添加时间戳避免文件名冲突
    timestamp = str(int(time.time()))
    safe_filename = f"{timestamp}_{filename}"
    file_path = config.UPLOAD_FOLDER / safe_filename
    file.save(str(file_path))

    logger.info(f"开始转换文件: {filename}, 模式: {mode}, 选项: {options}")

    try:
        # 根据文件类型选择转换器
        file_type = detect_file_type(filename)

        if file_type == 'word':
            converter = WordConverter(str(file_path))
        elif file_type == 'excel':
            converter = ExcelConverter(str(file_path))
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        # 根据文件类型决定处理方式
        if file_type == 'word':
            # Word：直接下载，不做预览
            zip_path = converter.convert(options)
            converter.cleanup()

            safe_filename = quote(f"converted_{filename}.zip", safe='')

            return send_file(
                zip_path,
                mimetype='application/zip',
                as_attachment=True,
                download_name=f"converted_{filename}.zip"
            )
        else:
            # Excel：预览模式或下载模式
            if mode == 'preview':
                # 预览模式：返回文本
                preview_text = converter.get_preview_text(options)
                sections = converter.get_sections()

                return jsonify({
                    'success': True,
                    'preview_text': preview_text,
                    'file_count': len(sections),
                    'preview_info': {
                        'file_name': sections[0]['filename'] if sections else 'preview.md',
                        'total_files': len(sections)
                    },
                    'zip_ready': True
                })
            else:
                # 下载模式：返回ZIP文件
                zip_path = converter.convert(options)
                converter.cleanup()

                safe_filename = quote(f"converted_{filename}.zip", safe='')

                return send_file(
                    zip_path,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"converted_{filename}.zip"
                )

    except Exception as e:
        logger.error(f"转换失败: {str(e)}", exc_info=True)
        return jsonify({'error': f'转换失败: {str(e)}'}), 500
    finally:
        # 清理上传文件
        if file_path.exists():
            file_path.unlink()


@app.route('/api/download', methods=['POST'])
def download_file():
    """
    下载ZIP文件接口（单独的下载端点）

    参数:
    - file: 文件
    - options: JSON字符串
    """
    if 'file' not in request.files:
        return jsonify({'error': '未上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式'}), 400

    # 获取参数
    options_json = request.form.get('options', '{}')

    try:
        import json
        options = json.loads(options_json)
    except json.JSONDecodeError:
        options = {}

    # 保存文件（使用原始文件名）
    filename = file.filename
    # 添加时间戳避免文件名冲突
    timestamp = str(int(time.time()))
    safe_filename = f"{timestamp}_{filename}"
    file_path = config.UPLOAD_FOLDER / safe_filename
    file.save(str(file_path))

    logger.info(f"开始生成ZIP文件: {filename}, 选项: {options}")

    try:
        # 根据文件类型选择转换器
        file_type = detect_file_type(filename)

        if file_type == 'word':
            converter = WordConverter(str(file_path))
        elif file_type == 'excel':
            converter = ExcelConverter(str(file_path))
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        # 生成ZIP
        zip_path = converter.convert(options)
        converter.cleanup()

        safe_filename = quote(f"converted_{filename}.zip", safe='')

        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name=f"converted_{filename}.zip"
        )

    except Exception as e:
        logger.error(f"下载失败: {str(e)}", exc_info=True)
        return jsonify({'error': f'下载失败: {str(e)}'}), 500
    finally:
        # 清理上传文件
        if file_path.exists():
            file_path.unlink()


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("任意文档转Markdown服务")
    logger.info("=" * 50)
    logger.info(f"访问地址: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
    logger.info(f"调试模式: {config.FLASK_DEBUG}")
    logger.info(f"最大上传大小: {config.MAX_CONTENT_LENGTH / 1024 / 1024:.0f} MB")
    logger.info(f"下载路径: {config.DOWNLOAD_FOLDER}")
    logger.info(f"LLM服务: {'启用' if config.LLM_AVAILABLE else '禁用'}")
    logger.info("=" * 50)

    app.run(
        host=config.FLASK_HOST,
        port=config.FLASK_PORT,
        debug=config.FLASK_DEBUG,
        threaded=True
    )
