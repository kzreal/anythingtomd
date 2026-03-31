"""
PDF转换器
将PDF文档转换为Markdown，按页切片
"""
import io
import logging
from pathlib import Path
from typing import Dict, List
from converters.base import BaseConverter
from utils.zip_helper import ZipHelper
from services.qwen_ocr_service import QwenOCRService

logger = logging.getLogger(__name__)


class PDFConverter(BaseConverter):
    """PDF 转 Markdown 转换器"""

    def __init__(self, file_path: str, ocr_service: QwenOCRService):
        """
        初始化 PDF 转换器

        Args:
            file_path: PDF 文件路径
            ocr_service: OCR 服务实例
        """
        super().__init__(file_path)
        self.ocr_service = ocr_service
        self.zip_helper = ZipHelper(Path(file_path).parent.parent / 'downloads')
        self.doc = None
        self.images = None

    def load_document(self):
        """加载 PDF 文档并转换为图片"""
        try:
            from pdf2image import convert_from_path
        except ImportError:
            raise ImportError("pdf2image库未安装，请运行: pip install pdf2image")

        logger.info(f"开始转换PDF为图片: {self.file_path}")
        logger.info(f"检查文件是否存在: {Path(self.file_path).exists()}")
        logger.info(f"文件大小: {Path(self.file_path).stat().st_size if Path(self.file_path).exists() else 'N/A'} 字节")

        # 使用 DPI=100 以减少图片大小，加快 OCR 速度
        # 注意：较低的 DPI 可能影响 OCR 准确率
        self.images = convert_from_path(str(self.file_path), dpi=100)
        logger.info(f"成功转换 {len(self.images)} 页PDF为图片 (DPI=100)")

    def convert(self, options: Dict) -> str:
        """
        转换 PDF 为 ZIP

        Args:
            options: 转换选项

        Returns:
            ZIP 文件路径
        """
        self.load_document()

        add_ln = options.get('add_line_numbers', True)
        files = {}
        sections = []

        line_no = 1
        for idx, image in enumerate(self.images):
            # 将图片转为字节
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_bytes = buffered.getvalue()

            # OCR 识别，提示词要求保留格式
            prompt = "完整提取图片中的全部内容，保留表格、标题层级等格式，以 Markdown 格式输出"
            content = self.ocr_service.recognize_image(image_bytes, prompt)

            if content:
                # 添加行号
                output_content = self.ocr_service.add_line_numbers(content, line_no) if add_ln else content
                line_no = line_no + content.count('\n') + 1

                filename = f"{idx + 1:03d}.md"
                files[filename] = output_content

                sections.append({
                    'index': idx,
                    'title': f'第 {idx + 1} 页',
                    'filename': filename,
                    'content': output_content
                })

        self.sections = sections

        # 创建索引文件
        index_content = self.zip_helper.create_index(
            original_filename=self.file_path.name,
            file_type='pdf',
            sections=sections,
            options=options
        )
        files['00_index.md'] = index_content

        # 创建 ZIP
        zip_path = self.zip_helper.create_zip(files, self.get_output_filename())

        return str(zip_path)

    def get_preview_text(self, options: Dict) -> tuple[str, List[Dict]]:
        """
        获取预览文本和切片列表

        Args:
            options: 转换选项

        Returns:
            (预览文本, 切片列表)
        """
        self.load_document()

        if not self.images:
            logger.warning("PDF 转换为图片失败，images 为空")
            return "# 空文档", []

        add_ln = options.get('add_line_numbers', True)
        logger.info(f"开始处理 {len(self.images)} 页 PDF 进行 OCR 识别")

        sections = []

        line_no = 1
        all_contents = []

        for idx, image in enumerate(self.images):
            logger.info(f"正在处理第 {idx + 1}/{len(self.images)} 页...")

            # OCR 识别
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            image_bytes = buffered.getvalue()

            logger.info(f"第 {idx + 1} 页图片大小: {len(image_bytes)} 字节")

            prompt = "完整提取图片中的全部内容，保留表格、标题层级等格式，以 Markdown 格式输出"
            content = self.ocr_service.recognize_image(image_bytes, prompt)

            if content:
                logger.info(f"第 {idx + 1} 页 OCR 成功，文本长度: {len(content)} 字符")
                output_content = self.ocr_service.add_line_numbers(content, line_no) if add_ln else content
                line_no = line_no + content.count('\n') + 1
                all_contents.append(output_content)

                sections.append({
                    'index': idx,
                    'title': f'第 {idx + 1} 页',
                    'filename': f"{idx + 1:03d}.md",
                    'content': output_content
                })
            else:
                logger.warning(f"第 {idx + 1} 页 OCR 失败，返回 None")

        self.sections = sections
        logger.info(f"OCR 完成，成功识别 {len(sections)}/{len(self.images)} 页")

        # 返回第一页内容和所有切片信息
        preview_text = all_contents[0] if all_contents else "# 空文档"

        return preview_text, sections

    def get_sections(self) -> List[Dict]:
        """获取所有页面切片信息"""
        if not hasattr(self, 'sections') or not self.sections:
            self.load_document()
            # 默认值，执行转换获取sections
            self.load_document()

        return [{
            'index': s['index'],
            'title': s['title'],
            'filename': s.get('filename', f"{s['index']:03d}.md")
        } for s in self.sections]

    def get_output_filename(self) -> str:
        """获取输出文件名"""
        return f"converted_{self.file_path.stem}.zip"

    def cleanup(self):
        """清理资源"""
        self.doc = None
        self.images = None
