# AlltoMarkdown MCP 服务器

将 AlltoMarkdown 文档转换服务封装为 MCP (Model Context Protocol) 服务器，使 LLM 能够直接调用文档转换功能。

## 功能特性

- **文件类型支持**
  - Word 文档 (.docx) - 支持按章节切片
  - Excel 表格 (.xlsx, .xls) - 按 sheet 切片
  - PDF 文档 (.pdf) - 按页切片（需要 OCR）
  - 图片文件 (.png, .jpg, .jpeg) - OCR 识别文字

- **可用工具**
  - `analyze_file` - 分析文件信息
  - `convert_file` - 转换文件为指定格式
  - `list_sections` - 列出文档切片
  - `convert_batch` - 批量转换文件

## 安装

### 1. 安装依赖

```bash
# 安装项目基础依赖
pip install -r requirements.txt

# 安装 MCP 相关依赖
pip install -r requirements_mcp.txt

# 或者使用国内镜像
pip install -i https://pypi.tuna.tsinghua.edu.cn/simple -r requirements_mcp.txt
```

### 2. 配置环境变量

在项目根目录创建 `.env` 文件，配置以下环境变量：

```env
# 千问 OCR API（PDF 和图片转换必需）
QWEN_VL_API_KEY=your_api_key_here
QWEN_VL_BASE_URL=https://ai-model.chint.com/api

# LLM 图片识别 API（Word 文档图片识别可选）
LLM_API_ENDPOINT=https://ai-model.chint.com/api/chat/completions
LLM_API_KEY=your_llm_api_key_here
LLM_MODEL=qwen-vl
```

## 使用方法

### 直接运行 MCP 服务器

```bash
python3 alltomarkdown_mcp.py
```

### 使用 MCP Inspector 测试

```bash
# 安装 inspector
npm install -g @modelcontextprotocol/inspector

# 运行 inspector
npx @modelcontextprotocol/inspector python3 alltomarkdown_mcp.py
```

### 在 Claude Desktop 中使用

在 Claude Desktop 的配置文件中添加：

```json
{
  "mcpServers": {
    "alltomarkdown": {
      "command": "python3",
      "args": [
        "/Users/kyle/Projects/AlltoMarkdown/alltomarkdown_mcp.py"
      ],
      "env": {
        "QWEN_VL_API_KEY": "your_api_key_here",
        "QWEN_VL_BASE_URL": "https://ai-model.chint.com/api",
        "LLM_API_KEY": "your_llm_api_key_here"
      }
    }
  }
}
```

## 工具说明

每个工具都有两个版本：
- **简短名称**：便于快速输入，如 `analyze`、`convert`
- **完整名称**：便于理解和自动补全，如 `analyze_file`、`convert_file`

### 简短名称工具（推荐日常使用）

#### analyze
分析文件信息，获取文件类型、大小等元数据。

**参数：**
- `file_path` (必需): 文件路径

**返回：**
```json
{
  "file_path": "/path/to/file.docx",
  "filename": "file.docx",
  "file_type": "word",
  "file_size": 12345,
  "file_size_mb": 0.01
}
```

#### convert
将文件转换为指定格式。

**参数：**
- `file_path` (必需): 文件路径
- `output_format` (可选): 输出格式
  - `markdown`: 完整 Markdown 文本
  - `json`: 结构化 JSON 数据
  - `sections`: 切片列表
- `max_level` (可选, 仅 Word): 切片级别
  - `0`: 整个文档
  - `1`: 一级标题
  - `2`: 二级标题
  - `3`: 三级标题
  - `all`: 全部

**返回：** 根据 output_format 返回相应内容

#### sections
列出文档的切片信息（不包含完整内容）。

**参数：**
- `file_path` (必需): 文件路径
- `max_level` (可选, 仅 Word): 切片级别

**返回：**
```json
[
  {
    "index": 0,
    "title": "章节标题",
    "filename": "001_章节标题.md"
  }
]
```

#### batch
批量转换多个文件。

**参数：**
- `file_paths` (必需): 文件路径列表
- `max_level` (可选, 仅 Word): 切片级别

**返回：**
```json
[
  {
    "file_path": "/path/to/file.docx",
    "success": true,
    "error": null,
    "output": "Markdown 内容..."
  }
]
```

### 完整名称工具（便于理解和自动补全）

#### analyze_file

分析文件信息，获取文件类型、大小等元数据。

**参数：**
- `file_path` (必需): 文件路径

**返回：**
```json
{
  "file_path": "/path/to/file.docx",
  "filename": "file.docx",
  "file_type": "word",
  "file_size": 12345,
  "file_size_mb": 0.01,
  "word_options": {
    "max_levels": "0, 1, 2, 3, or \"all\"",
    "description": "切片级别控制文档拆分方式"
  }
}
```

### convert_file

将文件转换为指定格式。

**参数：**
- `file_path` (必需): 文件路径
- `output_format` (可选): 输出格式
  - `markdown`: 完整 Markdown 文本
  - `json`: 结构化 JSON 数据
  - `sections`: 切片列表
- `max_level` (可选, 仅 Word): 切片级别
  - `0`: 整个文档
  - `1`: 一级标题
  - `2`: 二级标题
  - `3`: 三级标题
  - `all`: 全部

**返回：** 根据 output_format 返回相应内容

### list_sections

列出文档的切片信息（不包含完整内容）。

**参数：**
- `file_path` (必需): 文件路径
- `max_level` (可选, 仅 Word): 切片级别

**返回：**
```json
[
  {
    "index": 0,
    "title": "章节标题",
    "filename": "001_章节标题.md"
  }
]
```

### convert_batch

批量转换多个文件。

**参数：**
- `file_paths` (必需): 文件路径列表
- `max_level` (可选, 仅 Word): 切片级别

**返回：**
```json
[
  {
    "file_path": "/path/to/file.docx",
    "success": true,
    "error": null,
    "output": "Markdown 内容..."
  }
]
```

## 测试

运行快速验证测试：

```bash
python3 quick_test.py
```

运行完整测试：

```bash
python3 test_mcp.py
```

## 注意事项

1. **PDF 和图片转换需要配置千问 OCR API** (`QWEN_VL_API_KEY`)
2. **Word 文档的图片识别需要配置 LLM API** (`LLM_API_KEY`)
3. 转换大文件或包含大量图片的文件可能需要较长时间
4. 确保文件路径是绝对路径或相对于项目根目录的相对路径

## 错误处理

工具返回的错误格式：

```json
{
  "error": "错误描述",
  "code": "错误码"
}
```

常见错误码：
- `FILE_NOT_FOUND`: 文件不存在
- `INVALID_ARGUMENT`: 参数无效或不支持的文件类型
- `CONVERSION_ERROR`: 转换失败
- `BATCH_CONVERSION_ERROR`: 批量转换失败

## 支持的文件格式

| 格式 | 扩展名 | 切片方式 | API 需求 |
|------|--------|---------|---------|
| Word | .docx | 按标题级别 | LLM API（可选） |
| Excel | .xlsx, .xls | 按 sheet | 无 |
| PDF | .pdf | 按页 | 千问 OCR |
| 图片 | .png, .jpg, .jpeg | 单文件 | 千问 OCR |

## 开发

项目结构：

```
AlltoMarkdown/
├── alltomarkdown_mcp.py      # MCP 服务器主文件
├── config.py                   # 配置管理
├── requirements_mcp.txt        # MCP 依赖
├── quick_test.py              # 快速验证脚本
├── test_mcp.py               # 完整测试脚本
├── converters/                # 转换器模块
│   ├── base.py
│   ├── word_converter.py
│   ├── excel_converter.py
│   ├── pdf_converter.py
│   └── image_converter.py
├── services/                  # 服务模块
│   ├── qwen_ocr_service.py
│   └── llm_service.py
└── utils/                     # 工具模块
    └── zip_helper.py
```

## 许可证

与 AlltoMarkdown 主项目保持一致。
