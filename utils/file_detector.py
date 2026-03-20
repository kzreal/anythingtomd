"""
文件类型检测工具
"""
from pathlib import Path
from typing import Optional


def detect_file_type(filename: str) -> Optional[str]:
    """
    检测文件类型

    Args:
        filename: 文件名

    Returns:
        'word', 'excel', 或 None（未知类型）
    """
    if not filename:
        return None

    ext = Path(filename).suffix.lower()
    if ext == '.docx':
        return 'word'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    else:
        return None


def is_allowed_file(filename: str) -> bool:
    """
    检查文件是否允许上传

    Args:
        filename: 文件名

    Returns:
        是否允许
    """
    return detect_file_type(filename) is not None


def get_file_display_name(filename: str) -> str:
    """
    获取文件显示名称

    Args:
        filename: 文件名

    Returns:
        显示名称（如 "Word文档", "Excel表格"）
    """
    file_type = detect_file_type(filename)
    if file_type == 'word':
        return 'Word文档'
    elif file_type == 'excel':
        return 'Excel表格'
    else:
        return '未知类型'
