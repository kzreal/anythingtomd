"""
ZIP文件处理工具
"""
import io
import zipfile
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime


class ZipHelper:
    """ZIP文件处理辅助类"""

    def __init__(self, output_dir: Path):
        """
        初始化ZIP助手

        Args:
            output_dir: 输出目录
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(exist_ok=True)

    def create_zip(self, files: Dict[str, str], zip_name: str) -> Path:
        """
        创建ZIP文件

        Args:
            files: 文件字典 {filename: content}
            zip_name: ZIP文件名

        Returns:
            ZIP文件路径
        """
        zip_path = self.output_dir / zip_name

        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in files.items():
                zipf.writestr(filename, content.encode('utf-8'))

        return zip_path

    def create_zip_in_memory(self, files: Dict[str, str]) -> io.BytesIO:
        """
        在内存中创建ZIP文件

        Args:
            files: 文件字典 {filename: content}

        Returns:
            ZIP文件的BytesIO对象
        """
        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for filename, content in files.items():
                zipf.writestr(filename, content.encode('utf-8'))

        zip_buffer.seek(0)
        return zip_buffer

    def create_index(self, original_filename: str, file_type: str,
                     sections: List[Dict], options: Optional[Dict] = None) -> str:
        if options is None:
            options = {}
        """
        创建索引文件内容

        Args:
            original_filename: 原始文件名
            file_type: 文件类型（word/excel）
            sections: 章节列表
            options: 转换选项

        Returns:
            索引文件内容
        """
        content = []
        content.append("# 文档转换索引\n\n")
        content.append(f"原文件: {original_filename}\n")
        content.append(f"转换时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append(f"文件类型: {file_type}\n")
        content.append(f"总章节数: {len(sections)}\n")

        if options:
            content.append(f"转换选项: {options}\n")

        content.append("\n---\n\n")
        content.append("## 文件列表\n\n")

        for section in sections:
            index = section.get('index', 0) + 1
            title = section.get('title', '未命名')
            filename = section.get('filename', f"{index:03d}_{title}.md")
            content.append(f"- [{index}. {title}]({filename})\n")

        return ''.join(content)

    def sanitize_filename(self, filename: str) -> str:
        """
        清理文件名，移除非法字符

        Args:
            filename: 原始文件名

        Returns:
            清理后的安全文件名
        """
        import re
        filename = re.sub(r'[<>:"/\\|?*]', '', filename)
        if len(filename) > 100:
            filename = filename[:100]
        return filename.strip()
