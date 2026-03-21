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
from typing import Dict, List, Optional
from urllib.parse import quote

from flask import Flask, jsonify, render_template, request, send_file
from werkzeug.exceptions import RequestEntityTooLarge

import config
from utils.file_detector import detect_file_type, is_allowed_file
from converters.word_converter import WordConverter
from converters.excel_converter import ExcelConverter
from services.qwen_ocr_service import QwenOCRService

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

# 初始化千问 OCR 服务
qwen_ocr_service = None
if config.QWEN_VL_API_KEY:
    qwen_ocr_service = QwenOCRService(
        api_key=config.QWEN_VL_API_KEY,
        base_url=config.QWEN_VL_BASE_URL
    )
    logger.info("千问 OCR 服务已启用")
else:
    logger.warning("千问 OCR 服务未启用：缺少 API Key")

# 全局缓存字典
conversion_cache = {}

# 临时文件清理列表
temp_files_to_cleanup = []


def cleanup_temp_files():
    """清理临时文件"""
    for file_path in temp_files_to_cleanup[:]:  # 使用切片避免修改列表时的问题
        try:
            if file_path.exists():
                file_path.unlink()
                logger.info(f"已清理临时文件: {file_path}")
        except Exception as e:
            logger.warning(f"清理文件失败 {file_path}: {e}")
    temp_files_to_cleanup.clear()


@app.after_request
def after_request_cleanup(response):
    """请求完成后清理临时文件"""
    cleanup_temp_files()
    return response


def get_session_id():
    """生成唯一的会话ID"""
    import uuid
    return str(uuid.uuid4())


def cache_conversion(session_id: str, sections: List, options: Dict, file_type: str):
    """缓存转换结果"""
    conversion_cache[session_id] = {
        'sections': sections,
        'options': options,
        'file_type': file_type,
        'timestamp': time.time()
    }


def get_cached_sections(session_id: str, index: int = None) -> Optional[Dict]:
    """获取缓存的切片内容"""
    if session_id not in conversion_cache:
        return None

    cached = conversion_cache[session_id]
    if index is not None:
        # 返回指定切片
        if 0 <= index < len(cached['sections']):
            return cached['sections'][index]
        return None

    return cached


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

    files = request.files.getlist('file')
    if not files:
        return jsonify({'error': '未上传文件'}), 400

    # 获取第一个文件用于分析
    file = files[0]
    if file.filename == '':
        return jsonify({'error': '文件名为空'}), 400

    if not is_allowed_file(file.filename):
        return jsonify({'error': '不支持的文件格式，仅支持 .docx, .xlsx, .xls, .pdf, .png, .jpg, .jpeg'}), 400

    # 保存文件到磁盘（在获取 content_length 之前）
    import time
    timestamp = str(int(time.time()))
    saved_path = config.UPLOAD_FOLDER / f"{timestamp}_{file.filename}"
    file.save(str(saved_path))

    # 获取文件类型
    file_type = detect_file_type(file.filename)

    # 获取保存后的文件大小
    import os
    saved_size = os.path.getsize(saved_path) if os.path.exists(saved_path) else 0

    result = {
        'success': True,
        'file_type': file_type,
        'filename': file.filename,
        'file_size': saved_size,
        'file_count': len(files),  # 文件数量（用于多图）
        'saved_path': str(saved_path)
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
    elif file_type == 'pdf':
        result['pdf_options'] = {
            'description': 'PDF 将按页转换为 Markdown，每页作为一个独立文件'
        }
    elif file_type == 'image':
        result['image_options'] = {
            'description': '图片将通过千问 OCR 识别转换为 Markdown，仅支持单张图片'
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

    # 从表单中获取已保存的文件路径（如果有的话）
    saved_path_str = request.form.get('saved_path')
    if saved_path_str:
        file_path = Path(saved_path_str)
        logger.info(f"使用已保存的文件: {file_path}")
    else:
        # 如果没有已保存的路径，保存文件
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
        elif file_type == 'pdf':
            if qwen_ocr_service is None:
                return jsonify({'error': '千问 OCR 服务未启用，请配置 QWEN_VL_API_KEY'}), 500
            from converters.pdf_converter import PDFConverter
            converter = PDFConverter(str(file_path), qwen_ocr_service)
        elif file_type == 'image':
            if qwen_ocr_service is None:
                return jsonify({'error': '千问 OCR 服务未启用，请配置 QWEN_VL_API_KEY'}), 500
            # 图片文件已经在前面保存到 file_path
            from converters.image_converter import ImageConverter
            converter = ImageConverter(str(file_path), qwen_ocr_service)
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        # 根据文件类型决定处理方式
        if file_type == 'word':
            # Word：支持预览模式和下载模式
            if mode == 'preview':
                # 预览模式：返回 JSON
                preview_text, sections_info = converter.get_preview_text(options)

                # 生成会话ID并缓存
                session_id = get_session_id()
                cache_conversion(session_id, sections_info, options, file_type)

                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'sections': sections_info,
                    'preview_text': preview_text,
                    'file_count': len(sections_info),
                    'zip_ready': True
                })
            else:
                # 下载模式：返回 ZIP
                zip_path = converter.convert(options)
                converter.cleanup()

                # 将文件添加到清理列表
                temp_files_to_cleanup.append(Path(zip_path))
                # 清理上传的原始文件
                temp_files_to_cleanup.append(file_path)

                safe_filename = quote(f"converted_{filename}.zip", safe='')

                return send_file(
                    zip_path,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"converted_{filename}.zip"
                )
        elif file_type == 'excel':
            # Excel：预览模式或下载模式
            if mode == 'preview':
                # 预览模式：返回 JSON
                preview_text = converter.get_preview_text(options)
                sections = converter.get_sections()

                # 生成会话ID并缓存
                session_id = get_session_id()
                cache_conversion(session_id, sections, options, file_type)

                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'sections': sections,
                    'preview_text': preview_text,
                    'file_count': len(sections),
                    'zip_ready': True
                })
            else:
                # 下载模式：返回ZIP文件
                zip_path = converter.convert(options)
                converter.cleanup()

                # 将文件添加到清理列表
                temp_files_to_cleanup.append(Path(zip_path))
                # 清理上传的原始文件
                temp_files_to_cleanup.append(file_path)

                safe_filename = quote(f"converted_{filename}.zip", safe='')

                return send_file(
                    zip_path,
                    mimetype='application/zip',
                    as_attachment=True,
                    download_name=f"converted_{filename}.zip"
                )
        elif file_type in ['pdf', 'image']:
            # PDF/图片：预览模式或下载模式
            if mode == 'preview':
                preview_text, sections_info = converter.get_preview_text(options)

                # 生成会话ID并缓存
                session_id = get_session_id()
                cache_conversion(session_id, sections_info, options, file_type)

                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'sections': sections_info,
                    'preview_text': preview_text,
                    'file_count': len(sections_info),
                    'zip_ready': True
                })
            else:
                # 下载模式：返回ZIP文件
                zip_path = converter.convert(options)
                converter.cleanup()

                # 将文件添加到清理列表
                temp_files_to_cleanup.append(Path(zip_path))
                # 清理上传的原始文件
                temp_files_to_cleanup.append(file_path)

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
        # 注意：不在 finally 中清理 file_path，因为 send_file 需要它
        # ZIP 文件由 converter.convert() 生成，需要保留给 send_file 使用
        # 清理由客户端下载后手动处理，或者使用定时清理机制
        pass


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
        elif file_type == 'pdf':
            if qwen_ocr_service is None:
                return jsonify({'error': '千问 OCR 服务未启用，请配置 QWEN_VL_API_KEY'}), 500
            from converters.pdf_converter import PDFConverter
            converter = PDFConverter(str(file_path), qwen_ocr_service)
        elif file_type == 'image':
            if qwen_ocr_service is None:
                return jsonify({'error': '千问 OCR 服务未启用，请配置 QWEN_VL_API_KEY'}), 500
            # 图片文件已经在前面保存到 file_path
            from converters.image_converter import ImageConverter
            converter = ImageConverter(str(file_path), qwen_ocr_service)
        else:
            return jsonify({'error': '不支持的文件类型'}), 400

        # 生成ZIP
        zip_path = converter.convert(options)
        converter.cleanup()

        # 将文件添加到清理列表
        temp_files_to_cleanup.append(Path(zip_path))
        # 清理上传的原始文件
        temp_files_to_cleanup.append(file_path)

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
        # 注意：不在 finally 中清理 file_path，因为 send_file 需要它
        # ZIP 文件由 converter.convert() 生成，需要保留给 send_file 使用
        # 清理由客户端下载后手动处理，或者使用定时清理机制
        pass


@app.route('/api/section/<session_id>/<int:index>', methods=['GET'])
def get_section_content(session_id: str, index: int):
    """
    获取指定切片的内容（从缓存中读取）

    Args:
        session_id: 会话ID
        index: 切片索引
    """
    section = get_cached_sections(session_id, index)

    if section is None:
        return jsonify({'error': '会话不存在或切片索引无效'}), 404

    return jsonify({
        'success': True,
        'index': section['index'],
        'title': section['title'],
        'content': section['content']
    })


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
