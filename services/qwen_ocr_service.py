"""
千问视觉模型 OCR 服务
"""
import base64
import io
import logging
from openai import OpenAI
from typing import Optional

logger = logging.getLogger(__name__)


class QwenOCRService:
    """千问视觉模型 OCR 服务"""

    def __init__(self, api_key: str, base_url: str = "https://ai-model.chint.com/api"):
        """
        初始化千问 OCR 服务

        Args:
            api_key: API 密钥
            base_url: API 基础 URL
        """
        self.client = OpenAI(api_key=api_key, base_url=base_url)

    def encode_image_bytes(self, image_bytes: bytes) -> str:
        """
        将图片字节转换为 base64 编码

        Args:
            image_bytes: 图片字节数据

        Returns:
            base64 编码的字符串
        """
        return base64.b64encode(image_bytes).decode("utf-8")

    def recognize_image(self, image_bytes: bytes, prompt: str, max_retries: int = 3) -> Optional[str]:
        """
        识别图片中的文字内容

        Args:
            image_bytes: 图片字节数据
            prompt: 识别提示词
            max_retries: 最大重试次数

        Returns:
            识别的文字内容，失败返回 None
        """
        base64_image = self.encode_image_bytes(image_bytes)
        logger.info(f"开始OCR识别，图片大小: {len(image_bytes)} 字节")

        for attempt in range(max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model="qwen-vl",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant specialized in OCR tasks."},
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/png;base64,{base64_image}"
                                    }
                                }
                            ],
                        }
                    ],
                    temperature=0.3,
                    max_tokens=2000,
                    timeout=300.0  # 设置300秒超时（5分钟）
                )

                result = completion.choices[0].message.content
                logger.info(f"OCR识别成功（尝试 {attempt + 1}/{max_retries}），结果长度: {len(result) if result else 0} 字符")
                return result
            except Exception as e:
                logger.warning(f"OCR识别失败（尝试 {attempt + 1}/{max_retries}）: {type(e).__name__}: {e}")
                if attempt == max_retries - 1:
                    logger.error(f"OCR识别最终失败，已达到最大重试次数")
                    import traceback
                    logger.error(f"详细错误信息:\n{traceback.format_exc()}")
                    return None
                # 等待后重试
                import time
                time.sleep(2)

    def add_line_numbers(self, text: str, start_no: int = 1) -> str:
        """
        为文本添加行号注释 <!-- N -->

        Args:
            text: 原始文本
            start_no: 起始行号

        Returns:
            添加了行号注释的文本
        """
        lines = text.split('\n')
        numbered_lines = []
        for i, line in enumerate(lines, start=start_no):
            numbered_lines.append(f"<!-- {i} --> {line}")
        return '\n'.join(numbered_lines)

    def close(self):
        """清理资源"""
        if hasattr(self, 'client'):
            self.client.close()
