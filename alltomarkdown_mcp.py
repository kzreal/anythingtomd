"""
AlltoMarkdown MCP 服务器
提供文档转换为 Markdown 的 MCP 工具
"""
import os
import sys
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from mcp.server import FastMCP
from pydantic import BaseModel, Field

import config
from services.qwen_ocr_service import QwenOCRService
from converters.word_converter import WordConverter
from converters.excel_converter import ExcelConverter
from converters.pdf_converter import PDFConverter
from converters.image_converter import ImageConverter

# 设置日志
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建 MCP 服务器
mcp = FastMCP("alltomarkdown")


class ConversionError(Exception):
    """转换错误"""
    pass


def get_file_type(file_path: Path) -> Optional[str]:
    """
    根据文件扩展名获取文件类型

    Args:
        file_path: 文件路径

    Returns:
        文件类型: word|excel|pdf|image 或 None
    """
    ext = file_path.suffix.lower()

    if ext in ['.docx']:
        return 'word'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    elif ext in ['.pdf']:
        return 'pdf'
    elif ext in ['.png', '.jpg', '.jpeg']:
        return 'image'

    return None


def create_converter(file_path: Path) -> Any:
    """
    根据文件类型创建转换器

    Args:
        file_path: 文件路径

    Returns:
        转换器实例
    """
    file_type = get_file_type(file_path)
    if not file_type:
        raise ValueError(f"不支持的文件类型: {file_path.suffix}")

    # 初始化 OCR 服务（用于 PDF 和图片）
    ocr_service = None
    if config.QWEN_VL_API_KEY:
        try:
            ocr_service = QwenOCRService(
                api_key=config.QWEN_VL_API_KEY,
                base_url=config.QWEN_VL_BASE_URL
            )
        except Exception as e:
            logger.warning(f"OCR 服务初始化失败: {e}")

    if file_type == 'word':
        return WordConverter(str(file_path))
    elif file_type == 'excel':
        return ExcelConverter(str(file_path))
    elif file_type == 'pdf':
        if not ocr_service:
            raise ValueError("PDF 转换需要配置 QWEN_VL_API_KEY")
        return PDFConverter(str(file_path), ocr_service)
    elif file_type == 'image':
        if not ocr_service:
            raise ValueError("图片转换需要配置 QWEN_VL_API_KEY")
        return ImageConverter(str(file_path), ocr_service)

    raise ValueError(f"不支持的文件类型: {file_type}")


# 注册 MCP 工具 - 使用完整名称

@mcp.tool(name="analyze_file", description="📄 分析文件信息：获取文件类型、大小等元数据。支持 Word/Excel/PDF/图片")
def analyze_file(file_path: str) -> str:
    """
    分析文件信息，获取文件类型、大小等元数据。

    支持 Word (.docx)、Excel (.xlsx, .xls)、PDF (.pdf) 和图片 (.png, .jpg, .jpeg) 文件。

    Args:
        file_path: 文件路径（绝对路径或相对路径）

    Returns:
        JSON 格式的文件信息
    """
    try:
        info = _analyze_file_internal(file_path)
        return json.dumps(info, ensure_ascii=False, indent=2)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e), "code": "FILE_NOT_FOUND"}, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e), "code": "INVALID_ARGUMENT"}, ensure_ascii=False)


@mcp.tool(name="convert_file", description="🔄 转换文件为 Markdown。支持 Word/Excel/PDF/图片，可指定输出格式和保存为 ZIP")
def convert_file(file_path: str, output_format: str = "markdown", max_level: str = "0", save_to_zip: bool = False) -> str:
    """
    将文件转换为 Markdown 格式。

    支持 Word（可按章节切片）、Excel（按 sheet 切片）、PDF（按页切片）和图片文件。

    Args:
        file_path: 文件路径
        output_format: 输出格式 (markdown|json|sections|zip)
        max_level: 切片级别（仅 Word）：0=整个文档, 1=一级标题, 2=二级标题, 3=三级标题, all=全部
        save_to_zip: 是否保存为 ZIP 文件（默认 False）

    Returns:
        根据 output_format 返回相应内容；如果 save_to_zip=True 或 output_format=zip，返回 ZIP 文件路径
    """
    try:
        result = _convert_file_internal(file_path, output_format, max_level, save_to_zip)
        if isinstance(result, dict):
            return json.dumps(result, ensure_ascii=False, indent=2)
        return result
    except FileNotFoundError as e:
        return json.dumps({"error": str(e), "code": "FILE_NOT_FOUND"}, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e), "code": "INVALID_ARGUMENT"}, ensure_ascii=False)
    except Exception as e:
        logger.exception(f"转换失败: {e}")
        return json.dumps({"error": f"转换失败: {str(e)}", "code": "CONVERSION_ERROR"}, ensure_ascii=False)


@mcp.tool(name="list_sections", description="📋 列出文档切片：章节、页面、sheet 等，不含完整内容")
def list_sections(file_path: str, max_level: str = "0") -> str:
    """
    列出文档的切片信息（章节、页面、sheet 等），不包含完整内容。

    Args:
        file_path: 文件路径
        max_level: 切片级别（仅 Word）：0=整个文档, 1=一级标题, 2=二级标题, 3=三级标题, all=全部

    Returns:
        JSON 格式的切片列表
    """
    try:
        sections = _list_sections_internal(file_path, max_level)
        return json.dumps(sections, ensure_ascii=False, indent=2)
    except FileNotFoundError as e:
        return json.dumps({"error": str(e), "code": "FILE_NOT_FOUND"}, ensure_ascii=False)
    except ValueError as e:
        return json.dumps({"error": str(e), "code": "INVALID_ARGUMENT"}, ensure_ascii=False)


@mcp.tool(name="convert_batch", description="📦 批量转换多个文件为 Markdown 格式")
def convert_batch(file_paths: List[str], max_level: str = "0") -> str:
    """
    批量转换多个文件为 Markdown 格式。

    Args:
        file_paths: 文件路径列表
        max_level: 切片级别（仅 Word）：0=整个文档, 1=一级标题, 2=二级标题, 3=三级标题, all=全部

    Returns:
        JSON 格式的转换结果列表
    """
    try:
        results = _convert_batch_internal(file_paths, max_level)
        return json.dumps(results, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception(f"批量转换失败: {e}")
        return json.dumps({"error": f"批量转换失败: {str(e)}", "code": "BATCH_CONVERSION_ERROR"}, ensure_ascii=False)


@mcp.tool(name="list_downloads", description="📁 列出所有已生成的下载文件（ZIP格式）")
def list_downloads(limit: int = 20) -> str:
    """
    列出 downloads 目录中的所有已生成文件。

    Args:
        limit: 返回文件数量限制（默认20）

    Returns:
        JSON 格式的文件列表
    """
    try:
        downloads_dir = Path(__file__).parent / 'downloads'
        if not downloads_dir.exists():
            return json.dumps({"files": [], "message": "downloads 目录不存在"}, ensure_ascii=False)

        files = []
        for file_path in sorted(downloads_dir.glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'created': file_path.stat().st_mtime
            })

        return json.dumps({
            'files': files,
            'total': len(files),
            'download_dir': str(downloads_dir)
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception(f"列出文件失败: {e}")
        return json.dumps({"error": f"列出文件失败: {str(e)}", "code": "LIST_ERROR"}, ensure_ascii=False)


@mcp.tool(name="download_file", description="⬇️ 下载已生成的 ZIP 文件（返回文件内容和base64编码）")
def download_file(filename: str) -> str:
    """
    下载已生成的 ZIP 文件，返回文件内容和 base64 编码。

    Args:
        filename: ZIP 文件名（如：converted_1234567890_文档.zip）

    Returns:
        JSON 格式，包含文件路径、大小和 base64 内容
    """
    try:
        downloads_dir = Path(__file__).parent / 'downloads'
        file_path = downloads_dir / filename

        if not file_path.exists():
            return json.dumps({
                "error": f"文件不存在: {filename}",
                "code": "FILE_NOT_FOUND",
                "hint": "使用 list_downloads 工具查看可用文件"
            }, ensure_ascii=False, indent=2)

        import base64

        # 读取文件内容并编码为 base64
        with open(file_path, 'rb') as f:
            file_content = base64.b64encode(f.read()).decode('utf-8')

        return json.dumps({
            'filename': filename,
            'path': str(file_path),
            'size': file_path.stat().st_size,
            'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
            'content': file_content,
            'message': '文件内容已编码为 base64，解码后可使用'
        }, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.exception(f"下载文件失败: {e}")
        return json.dumps({"error": f"下载文件失败: {str(e)}", "code": "DOWNLOAD_ERROR"}, ensure_ascii=False)


# 内部函数实现

def _analyze_file_internal(file_path: str) -> Dict[str, Any]:
    """
    分析文件信息（内部实现）
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    file_type = get_file_type(path)
    if not file_type:
        raise ValueError(f"不支持的文件类型: {path.suffix}")

    file_size = path.stat().st_size

    info = {
        'file_path': str(path),
        'filename': path.name,
        'file_type': file_type,
        'file_size': file_size,
        'file_size_mb': round(file_size / (1024 * 1024), 2),
    }

    # Word 文档特有信息
    if file_type == 'word':
        info['word_options'] = {
            'max_levels': '0, 1, 2, 3, or "all"',
            'description': '切片级别控制文档拆分方式'
        }

    return info


def _convert_file_internal(file_path: str, output_format: str = 'markdown',
                       max_level: Union[str, int] = 0, save_to_zip: bool = False) -> Union[str, Dict]:
    """
    转换文件为指定格式（内部实现）

    Args:
        file_path: 文件路径
        output_format: 输出格式 (markdown|json|sections|zip)
        max_level: 切片级别（仅 Word）
        save_to_zip: 是否保存为 ZIP 文件

    Returns:
        根据 output_format 返回相应内容
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    file_type = get_file_type(path)
    if not file_type:
        raise ValueError(f"不支持的文件类型: {path.suffix}")

    logger.info(f"开始转换文件: {file_path}, 类型: {file_type}, 输出格式: {output_format}, 保存ZIP: {save_to_zip}")

    converter = create_converter(path)
    options = {'max_level': max_level}

    try:
        # 如果要求保存为 ZIP，调用 convert() 方法
        if save_to_zip or output_format == 'zip':
            zip_path = converter.convert(options)
            return json.dumps({
                'file_path': str(path),
                'filename': path.name,
                'file_type': file_type,
                'zip_path': zip_path,
                'message': 'ZIP 文件已生成，使用 download_file 工具下载'
            }, ensure_ascii=False, indent=2)

        # 获取预览文本和切片信息
        if file_type == 'word':
            preview_text, sections = converter.get_preview_text(options)
        else:
            # 对于其他类型，也需要获取预览
            if file_type in ['pdf', 'image']:
                preview_text, sections = converter.get_preview_text(options)
            else:
                preview_text = converter.get_preview_text(options)
                sections = converter.sections

        if output_format == 'markdown':
            # 返回完整 Markdown 内容（合并所有章节）
            if isinstance(sections, list) and sections:
                full_content = []
                for section in sections:
                    title = section.get('title', '')
                    content = section.get('content', '')
                    if title:
                        full_content.append(f"## {title}\n\n")
                    if content:
                        full_content.append(content)
                return '\n'.join(full_content)
            return preview_text

        elif output_format == 'json':
            # 返回结构化 JSON
            return {
                'file_path': str(path),
                'filename': path.name,
                'file_type': file_type,
                'sections': sections if isinstance(sections, list) else []
            }

        elif output_format == 'sections':
            # 返回切片列表（不含完整内容）
            if isinstance(sections, list):
                return [{
                    'index': s.get('index'),
                    'title': s.get('title'),
                    'filename': s.get('filename')
                } for s in sections]
            return []

        else:
            raise ValueError(f"不支持的输出格式: {output_format}")

    finally:
        converter.cleanup()


def _list_sections_internal(file_path: str, max_level: Union[str, int] = 0) -> List[Dict]:
    """
    列出文档切片（内部实现）
    """
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {file_path}")

    file_type = get_file_type(path)
    if not file_type:
        raise ValueError(f"不支持的文件类型: {path.suffix}")

    converter = create_converter(path)
    options = {'max_level': max_level}

    try:
        # 先执行转换获取切片信息
        if file_type == 'word':
            converter.get_preview_text(options)
        elif file_type in ['pdf', 'image']:
            converter.get_preview_text(options)
        else:
            converter.get_preview_text(options)

        sections = converter.get_sections()
        return [{
            'index': s.get('index'),
            'title': s.get('title'),
            'filename': s.get('filename')
        } for s in sections]

    finally:
        converter.cleanup()


def _convert_batch_internal(file_paths: List[str], max_level: Union[str, int] = 0) -> List[Dict]:
    """
    批量转换多个文件（内部实现）
    """
    results = []

    for file_path in file_paths:
        result = {
            'file_path': file_path,
            'success': False,
            'error': None,
            'output': None
        }

        try:
            output = _convert_file_internal(file_path, output_format='markdown', max_level=max_level)
            result['success'] = True
            result['output'] = output
            logger.info(f"成功转换文件: {file_path}")
        except Exception as e:
            result['error'] = str(e)
            logger.error(f"转换失败 {file_path}: {e}")

        results.append(result)

    return results


def _list_downloads_internal(limit: int = 20) -> Dict[str, Any]:
    """
    列出 downloads 目录中的文件（内部实现）
    """
    try:
        downloads_dir = Path(__file__).parent / 'downloads'
        if not downloads_dir.exists():
            return {'files': [], 'message': 'downloads 目录不存在'}

        files = []
        for file_path in sorted(downloads_dir.glob('*.zip'), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            files.append({
                'filename': file_path.name,
                'path': str(file_path),
                'size': file_path.stat().st_size,
                'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
                'created': file_path.stat().st_mtime
            })

        return {
            'files': files,
            'total': len(files),
            'download_dir': str(downloads_dir)
        }
    except Exception as e:
        logger.exception(f"列出文件失败: {e}")
        raise


def _download_file_internal(filename: str) -> Dict[str, Any]:
    """
    下载已生成的 ZIP 文件（内部实现）
    """
    import base64

    downloads_dir = Path(__file__).parent / 'downloads'
    file_path = downloads_dir / filename

    if not file_path.exists():
        raise FileNotFoundError(f"文件不存在: {filename}")

    # 读取文件内容并编码为 base64
    with open(file_path, 'rb') as f:
        file_content = base64.b64encode(f.read()).decode('utf-8')

    return {
        'filename': filename,
        'path': str(file_path),
        'size': file_path.stat().st_size,
        'size_mb': round(file_path.stat().st_size / (1024 * 1024), 2),
        'content': file_content
    }


# 导出内部函数供测试使用
__all__ = ['analyze_file_internal', 'convert_file_internal', 'convert_batch_internal', 'list_sections_internal', 'list_downloads_internal', 'download_file_internal']

def analyze_file_internal(file_path: str) -> Dict[str, Any]:
    """分析文件信息（供测试使用）"""
    return _analyze_file_internal(file_path)

def convert_file_internal(file_path: str, output_format: str = 'markdown',
                       max_level: Union[str, int] = 0, save_to_zip: bool = False) -> Union[str, Dict]:
    """转换文件（供测试使用）"""
    return _convert_file_internal(file_path, output_format, max_level, save_to_zip)

def convert_batch_internal(file_paths: List[str], max_level: Union[str, int] = 0) -> List[Dict]:
    """批量转换（供测试使用）"""
    return _convert_batch_internal(file_paths, max_level)

def list_sections_internal(file_path: str, max_level: Union[str, int] = 0) -> List[Dict]:
    """列出切片（供测试使用）"""
    return _list_sections_internal(file_path, max_level)


def list_downloads_internal(limit: int = 20) -> Dict[str, Any]:
    """列出下载文件（供测试使用）"""
    return _list_downloads_internal(limit)


def download_file_internal(filename: str) -> Dict[str, Any]:
    """下载文件（供测试使用）"""
    return _download_file_internal(filename)


async def main():
    """启动 MCP 服务器"""
    logger.info("启动 AlltoMarkdown MCP 服务器")
    logger.info(f"支持的文件类型: {', '.join(['docx', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'])}")

    if config.LLM_AVAILABLE:
        logger.info("LLM 图片识别服务已启用")
    else:
        logger.warning("LLM 图片识别服务未配置，图片识别功能不可用")

    if config.QWEN_VL_API_KEY:
        logger.info("千问 OCR 服务已启用")
    else:
        logger.warning("千问 OCR 服务未配置，PDF/图片转换功能不可用")

    # 运行 stdio 服务器
    await mcp.run_stdio_async()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
