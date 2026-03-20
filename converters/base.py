"""
转换器基类
"""
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional
import io


class BaseConverter(ABC):
    """文档转换器基类"""

    def __init__(self, file_path: str):
        """
        初始化转换器

        Args:
            file_path: 文件路径
        """
        self.file_path = Path(file_path)
        self.sections: List[Dict] = []

    @abstractmethod
    def convert(self, options: Dict) -> str:
        """
        转换文件，返回ZIP文件的路径

        Args:
            options: 转换选项

        Returns:
            ZIP文件路径
        """
        pass

    @abstractmethod
    def get_preview_text(self, options: Dict) -> str:
        """
        获取预览文本（返回第一个文件的内容）

        Args:
            options: 转换选项

        Returns:
            Markdown预览文本
        """
        pass

    @abstractmethod
    def get_output_filename(self) -> str:
        """
        获取输出文件名

        Returns:
            ZIP文件名
        """
        pass

    def get_sections(self) -> List[Dict]:
        """
        获取转换后的章节列表

        Returns:
            章节列表
        """
        return self.sections

    def cleanup(self):
        """清理资源"""
        pass
