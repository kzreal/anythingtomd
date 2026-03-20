"""
配置管理模块
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径
BASE_DIR = Path(__file__).parent

# Flask配置
FLASK_HOST = os.getenv('FLASK_HOST', '0.0.0.0')
FLASK_PORT = int(os.getenv('FLASK_PORT', 8080))
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'

# 文件上传配置
MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', 1073741824))  # 1GB
UPLOAD_FOLDER = BASE_DIR / 'uploads'
DOWNLOAD_FOLDER = Path(os.getenv('DOWNLOAD_FOLDER', '/Users/kyle/Downloads'))
ALLOWED_EXTENSIONS = {'docx', 'xlsx', 'xls'}

# 确保目录存在
UPLOAD_FOLDER.mkdir(exist_ok=True)
DOWNLOAD_FOLDER.mkdir(exist_ok=True)

# LLM API配置
LLM_API_ENDPOINT = os.getenv('LLM_API_ENDPOINT', '').strip()
LLM_API_KEY = os.getenv('LLM_API_KEY', '').strip()
LLM_MODEL = os.getenv('LLM_MODEL', 'vision-model').strip()
LLM_TIMEOUT = int(os.getenv('LLM_TIMEOUT', 30))
LLM_MAX_RETRIES = int(os.getenv('LLM_MAX_RETRIES', 3))

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = BASE_DIR / 'logs' / 'app.log'

# 确保日志目录存在
LOG_FILE.parent.mkdir(exist_ok=True)

# LLM可用性检查
LLM_AVAILABLE = bool(LLM_API_ENDPOINT and LLM_API_KEY)
