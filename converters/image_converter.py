"""
图片转换器
将单张图片转换为Markdown
"""
import io
import logging
from pathlib import Path
from typing import Dict
from converters.base import BaseConverter
from utils.zip_helper import ZipHelper
from services.qwen_ocr_service import QwenOCRService

logger = logging.getLogger(__name__)


class ImageConverter(BaseConverter):
    """图片 转 Markdown 转换器"""

    def __init__(self, file_path: str, ocr_service: QwenOCRService):
        """
        初始化图片转换器

        Args:
            file_path: 图片文件路径
            ocr_service: OCR 服务实例
        """
        self.file_path = Path(file_path)
        self.ocr_service = ocr_service
        self.zip_helper = ZipHelper(self.file_path.parent.parent / 'downloads')
        self.sections: list = []

    def load_image(self):
        """加载图片"""
        from PIL import Image
        path_str = str(self.file_path).strip()
        logger.info(f"加载图片: {path_str}")
        try:
            self.image = Image.open(path_str)
            logger.info(f"图片加载成功: {self.image.size}")
        except Exception as e:
            logger.error(f"加载图片失败 {path_str}: {e}")
            raise

    def convert(self, options: Dict) -> str:
        """
        转换图片为 ZIP

        Args:
            options: 转换选项

        Returns:
            ZIP 文件路径
        """
        self.load_image()

        add_ln = options.get('add_line_numbers', True)
        files = {}

        # 将图片转为字节
        buffered = io.BytesIO()
        self.image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        # OCR 识别
        prompt = "完整提取图片中的全部内容，以 Markdown 格式输出"
        content = self.ocr_service.recognize_image(image_bytes, prompt)

        if content:
            output_content = self.ocr_service.add_line_numbers(content, 1) if add_ln else content

            safe_name = self.zip_helper.sanitize_filename(self.file_path.stem)
            filename = f"001_{safe_name}.md"
            files[filename] = output_content

            self.sections = [{
                'index': 0,
                'title': safe_name,
                'filename': filename,
                'content': output_content
            }]

        # 创建索引文件
        index_content = self.zip_helper.create_index(
            original_filename=safe_name,
            file_type='image',
            sections=self.sections,
            options=options
        )
        files['00_index.md'] = index_content

        # 创建 ZIP
        zip_path = self.zip_helper.create_zip(files, f'converted_{safe_name}.zip')

        return str(zip_path)

    def get_preview_text(self, options: Dict) -> tuple:
        """
        获取预览文本和切片列表

        Args:
            options: 转换选项

        Returns:
            (预览文本, 切片列表)
        """
        self.load_image()

        add_ln = options.get('add_line_numbers', True)

        # OCR 识别
        buffered = io.BytesIO()
        self.image.save(buffered, format="PNG")
        image_bytes = buffered.getvalue()

        prompt = "完整提取图片中的全部内容，以 Markdown 格式输出"
        content = self.ocr_service.recognize_image(image_bytes, prompt)

        if content:
            output_content = self.ocr_service.add_line_numbers(content, 1) if add_ln else content

            safe_name = self.zip_helper.sanitize_filename(self.file_path.stem)
            self.sections = [{
                'index': 0,
                'title': safe_name,
                'filename': f"001_{safe_name}.md",
                'content': output_content
            }]

            return output_content, self.sections

        return "# OCR识别失败", []

    def get_sections(self) -> list:
        """获取图片切片信息"""
        if not hasattr(self, 'sections') or not self.sections:
            self.load_image()
            safe_name = self.zip_helper.sanitize_filename(self.file_path.stem)
            self.sections = [{
                'index': 0,
                'title': safe_name,
                'filename': f"001_{safe_name}.md"
            }]

        return self.sections

    def get_output_filename(self) -> str:
        """获取输出文件名"""
        safe_name = self.zip_helper.sanitize_filename(self.file_path.stem)
        return f"converted_{safe_name}.zip"

    def cleanup(self):
        """清理资源"""
        self.image = None
        # 删除上传的图片文件
        try:
            self.file_path.unlink()
        except Exception as e:
            logger.warning(f"删除文件失败 {self.file_path}: {e}")
