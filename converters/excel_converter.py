"""
Excel转换器
将Excel文件转换为Markdown，每个sheet独立文件
"""
import pandas as pd
from pathlib import Path
from typing import Dict, List
from converters.base import BaseConverter
from utils.zip_helper import ZipHelper


class ExcelConverter(BaseConverter):
    """Excel转Markdown转换器"""

    def __init__(self, file_path: str):
        """
        初始化Excel转换器

        Args:
            file_path: Excel文件路径
        """
        super().__init__(file_path)
        self.data: Dict[str, pd.DataFrame] = {}
        self.zip_helper = ZipHelper(Path(file_path).parent.parent / 'downloads')

    def load_excel(self):
        """加载Excel文件"""
        if not self.file_path.exists():
            raise FileNotFoundError(f"文件不存在: {self.file_path}")

        # 根据文件扩展名选择引擎
        engine = 'openpyxl' if self.file_path.suffix.lower() == '.xlsx' else 'xlrd'

        xl = pd.ExcelFile(self.file_path, engine=engine)

        self.data = {}
        for sheet_name in xl.sheet_names:
            df = xl.parse(sheet_name, header=None)
            self.data[sheet_name] = df  # type: ignore

    def convert(self, options: Dict) -> str:
        """
        转换Excel文件为ZIP

        Args:
            options: 转换选项（暂无）

        Returns:
            ZIP文件路径
        """
        self.load_excel()

        # 准备输出文件
        files = {}
        sections = []

        # 转换每个sheet
        for idx, (sheet_name, df) in enumerate(self.data.items(), 1):
            md_content = self._convert_sheet_to_md(sheet_name, df)

            # 生成文件名
            safe_name = self.zip_helper.sanitize_filename(sheet_name)
            filename = f"{idx:03d}_{safe_name}.md"

            files[filename] = md_content

            # 添加到章节列表
            sections.append({
                'index': idx - 1,
                'title': sheet_name,
                'filename': filename,
                'content': md_content
            })

        self.sections = sections

        # 添加索引文件
        index_content = self.zip_helper.create_index(
            original_filename=self.file_path.name,
            file_type='excel',
            sections=sections,
            options={}
        )
        files['00_index.md'] = index_content

        # 创建ZIP文件
        zip_name = self.get_output_filename()
        self.zip_helper = ZipHelper(self.file_path.parent / 'downloads')
        zip_path = self.zip_helper.create_zip(files, zip_name)

        return str(zip_path)

    def get_preview_text(self, options: Dict) -> str:
        """
        获取预览文本（第一个sheet的内容）

        Args:
            options: 转换选项

        Returns:
            Markdown预览文本
        """
        self.load_excel()

        if not self.data:
            return "# 空文件"

        # 设置章节列表（用于文件计数）
        sections = []
        for idx, (sheet_name, df) in enumerate(self.data.items(), 1):
            safe_name = self.zip_helper.sanitize_filename(sheet_name)
            filename = f"{idx:03d}_{safe_name}.md"
            sections.append({
                'index': idx - 1,
                'title': sheet_name,
                'filename': filename,
                'content': self._convert_sheet_to_md(sheet_name, df)
            })
        self.sections = sections

        # 返回第一个sheet的内容
        first_sheet_name = list(self.data.keys())[0]
        first_sheet_df = self.data[first_sheet_name]

        return self._convert_sheet_to_md(first_sheet_name, first_sheet_df)

    def _convert_sheet_to_md(self, sheet_name: str, df: pd.DataFrame) -> str:
        """
        将单个sheet转换为Markdown

        Args:
            sheet_name: Sheet名称
            df: DataFrame

        Returns:
            Markdown内容
        """
        lines = []
        lines.append(f"## {sheet_name}\n\n")

        if df.empty:
            lines.append("*空工作表*\n\n")
            return ''.join(lines)

        # 转换为Markdown表格
        for idx, row in df.iterrows():
            cells = []
            for cell in row.values:
                if pd.isna(cell):
                    cells.append("")
                else:
                    # 清理单元格内容：移除换行符和多余空格
                    cell_str = str(cell).replace('\n', ' ').replace('\r', ' ').strip()
                    cells.append(cell_str)

            # 跳过空行
            if all(cell in ("", " ") for cell in cells):
                continue

            # 生成表格行
            row_md = "|" + "|".join(cells) + "|"
            lines.append(row_md + "\n")

            # 添加分隔线（第一行之后）
            if idx == 0:
                separator = "|" + "|".join(["---"] * len(cells)) + "|"
                lines.append(separator + "\n")

        result = ''.join(lines) + '\n'

        return result

    def get_output_filename(self) -> str:
        """
        获取输出文件名

        Returns:
            ZIP文件名
        """
        return f"converted_{self.file_path.stem}.zip"
