"""
LLM图片识别服务
"""
import logging
import requests
import base64
from typing import Optional


class ImageRecognitionService:
    """图像识别服务 - 通过 LLM API 识别图像内容"""

    def __init__(self, endpoint: str, api_key: str, model: str,
                 timeout: int = 30, max_retries: int = 3):
        """
        初始化LLM服务

        Args:
            endpoint: API端点
            api_key: API密钥
            model: 模型名称
            timeout: 超时时间（秒）
            max_retries: 最大重试次数
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        # 创建 HTTP session
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        })

        # 重试配置
        retry_adapter = requests.adapters.HTTPAdapter(
            max_retries=max_retries,
            pool_connections=10,
            pool_maxsize=100
        )
        self.session.mount('http://', retry_adapter)
        self.session.mount('https://', retry_adapter)

    def describe_image(self, image_data: bytes, image_format: str) -> Optional[str]:
        """
        发送图像到 LLM API 获取描述

        Args:
            image_data: 图像二进制数据
            image_format: 图像格式（如 'png', 'jpeg'）

        Returns:
            图像描述文本，失败返回 None
        """
        # 重试逻辑
        for attempt in range(self.max_retries):
            try:
                # 编码图像为 base64
                base64_image = base64.b64encode(image_data).decode('utf-8')

                # 构建请求体
                request_data = {
                    'model': self.model,
                    'messages': [
                        {
                            'role': 'user',
                            'content': [
                                {
                                    'type': 'text',
                                    'text': '十字以内直接概括图片的内容，不用加"图片展示..."、"这是...图片"等叙述'
                                },
                                {
                                    'type': 'image_url',
                                    'image_url': {
                                        'url': f'data:image/{image_format};base64,{base64_image}'
                                    }
                                }
                            ]
                        }
                    ],
                    'max_tokens': 100
                }

                # 发送请求
                response = self.session.post(
                    self.endpoint,
                    json=request_data,
                    timeout=self.timeout
                )

                response.raise_for_status()

                # 解析响应
                result = response.json()
                content = result['choices'][0]['message']['content'].strip()

                # 只返回纯文本描述
                return content

            except requests.exceptions.RequestException as e:
                logging.error(f"LLM API request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt == self.max_retries - 1:
                    # 重试次数用完，返回失败
                    logging.error(f"LLM API failed after {self.max_retries} attempts")
                    return None
                # 等待一段时间再重试
                import time
                wait_time = 2 ** attempt
                logging.info(f"Waiting {wait_time}s before retry...")
                time.sleep(wait_time)

            except (KeyError, IndexError) as e:
                logging.error(f"LLM API response parsing failed: {e}")
                logging.error(f"Response content: {response.text[:200]}...")
                return None

        return None

    def close(self):
        """关闭 session"""
        self.session.close()
