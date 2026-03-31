"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
# 检查是否指定了自定义 .env 文件路径（用于 bid-review-system 项目）
dotenv_path = os.getenv('DOTENV_PATH')
if dotenv_path and Path(dotenv_path).exists():
    load_dotenv(dotenv_path)
    print(f"[AlltoMarkdown] 使用自定义 .env 文件: {dotenv_path}")
else:
    load_dotenv()
    print(f"[AlltoMarkdown] 使用默认 .env 文件")

# 基础路径
BASE_DIR = Path(__file__).parent

# Flask配置
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'false').lower() == 'true'

# 文件上传配置
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 1073741824))  # 1GB
UPLOAD_FOLDER = BASE_DIR / 'uploads'
DOWNLOAD_FOLDER = Path(os.getenv('DOWNLOAD_FOLDER', '/Users/kyle/Downloads'))
ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'xls', 'pdf', 'png', 'jpg', 'jpeg'}

# 千问 OCR API 配置
QWEN_VL_API_KEY = os.getenv('QWEN_VL_API_KEY', 'sk-a1cd42b6-591e-4fb9-9af6-eb980060eb73').strip()
QWEN_VL_BASE_URL = os.getenv('QWEN_VL_BASE_URL', 'https://ai-model.chint.com/api').strip()

# 确保目录存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# LLM API配置
LLM_API_ENDPOINT = os.getenv('LLM_API_ENDPOINT', 'https://ai-model.chint.com/api/chat/completions').strip()
LLM_API_KEY = os.getenv('LLM_API_KEY', 'sk-4925e3a5-502c-4279-80a4-a480a7d01dca').strip()
LLM_MODEL = os.getenv('LLM_MODEL', 'qwen-vl').strip()
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', 3600))
LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', 3))

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'

# 确保日志目录存在
LOG_FILE.parent.mkdir(exist_ok=True)

# LLM可用性检查
LLM_AVAILABLE = bool(LLM_API_ENDPOINT and LLM_API_KEY)
