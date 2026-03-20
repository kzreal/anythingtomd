# 任意文档转Markdown服务

将Word和Excel文档转换为Markdown格式，支持预览和复制功能。

## ✅ 已完成功能

### 核心功能
- ✅ **Word转MD**
  - 保留文档层级结构
  - 支持切片功能（0/1/2/3/all级别）
  - 自动行编号（<!-- N -->）
  - 表格转Markdown表格
  - 输出为ZIP文件
  - **直接下载（无预览）**

- ✅ **Excel转MD**
  - 支持多sheet处理
  - 每个sheet独立MD文件
  - 自动行编号（<!-- N -->）
  - 输出为ZIP文件
  - **支持内容预览**
  - **一键复制到剪贴板**

- ✅ **Web界面**
  - 统一的上传区域
  - 文件类型自动检测
  - 动态选项显示（Word：切分层级；Excel：无额外选项）
  - **MD内容预览**
  - **一键复制到剪贴板**
  - 下载ZIP文件
  - 进度显示
  - 错误处理

### 技术架构
- ✅ **Flask Web应用** - 完整的API接口
- ✅ **转换器基类** - 统一的接口设计
- ✅ **Word转换器** - 支持切片和预览
- ✅ **Excel转换器** - 支持多sheet和预览
- ✅ **LLM服务** - 图片识别（可选，需配置）
- ✅ **ZIP处理工具** - 统一的输出格式

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量（可选）

```bash
cp .env.example .env
# 编辑.env文件
# - 下载路径：DOWNLOAD_FOLDER=/Users/kyle/Downloads（默认值）
# - LLM API：如果需要图片识别功能
```

### 3. 启动服务

```bash
python3 app.py
```

### 4. 访问服务

在浏览器中打开：http://localhost:8080

## 使用说明

### Word文档转换

1. 上传 `.docx` 文件
2. 选择切分层级：
   - **零级**：整个文档转成一个MD文件
   - **一级/二级/三级**：按对应标题级别切片
   - **全部**：按所有标题层级切片
3. 点击"开始转换"
4. **自动下载ZIP文件**（包含所有切片的MD文件）

**注意**：Word文档转换后**不显示预览**，直接下载ZIP文件。

### Excel文档转换

1. 上传 `.xlsx` 或 `.xls` 文件
2. 点击"开始转换"
3. **预览**第一个sheet的MD内容
4. **复制**内容到剪贴板，或**下载**ZIP文件（包含所有sheet）

## 项目结构

```
anydocumenttomd/
├── app.py                      # Flask主应用
├── config.py                   # 配置管理
├── requirements.txt             # 依赖管理
├── .env.example                # 环境变量模板
├── plan.md                     # 详细开发计划
├── utils/
│   ├── file_detector.py        # 文件类型检测
│   └── zip_helper.py           # ZIP文件处理
├── converters/
│   ├── base.py                 # 转换器基类
│   ├── word_converter.py       # Word转换器
│   └── excel_converter.py     # Excel转换器
├── services/
│   └── llm_service.py          # LLM图片识别服务
├── templates/
│   └── index.html              # Web界面
├── uploads/                    # 上传文件目录
├── downloads/                  # 下载文件目录
└── logs/                       # 日志目录
```

## 技术栈

- **Web框架**: Flask 2.0+
- **Word处理**: python-docx
- **Excel处理**: pandas & openpyxl
- **LLM API**: requests
- **环境变量**: python-dotenv

## API接口

### 分析文件
```
POST /api/analyze
Content-Type: multipart/form-data

参数:
- file: 文件

响应:
{
  "success": true,
  "file_type": "word" | "excel",
  "filename": "example.docx",
  "file_size": 1024000,
  "word_options": { ... } | null,
  "excel_options": { ... } | null
}
```

### 转换文件（预览）
```
POST /api/convert?mode=preview
Content-Type: multipart/form-data

参数:
- file: 文件
- options: JSON字符串
- mode: "preview"

响应:
{
  "success": true,
  "preview_text": "Markdown内容",
  "file_count": 3,
  "preview_info": {
    "file_name": "001_第一章节.md",
    "total_files": 3
  },
  "zip_ready": true
}
```

### 下载文件
```
POST /api/download
Content-Type: multipart/form-data

参数:
- file: 文件
- options: JSON字符串

响应:
ZIP文件（application/zip）
```

## LLM图片识别（可选）

如果需要使用LLM识别Word文档中的图片，请配置环境变量：

```bash
# .env 文件
LLM_API_ENDPOINT=https://your-api-endpoint.com/v1/analyze-image
LLM_API_KEY=your-api-key
LLM_MODEL=vision-model
```

## 功能特性对比

| 功能 | Word转MD | Excel转MD |
|------|---------|----------|
| 自动行编号 | ✅ | ✅ |
| 输出为ZIP | ✅ | ✅ |
| MD内容预览 | ❌ | ✅ |
| 复制功能 | ❌ | ✅ |
| 文档切片 | ✅ | - |
| 多文件输出 | ✅ | ✅（多sheet） |
| LLM图片识别 | ⏳ 需配置 | - |

## 开发计划

详细开发计划请参考 [plan.md](plan.md)

## 注意事项

1. 文件大小限制：最大1GB
2. 支持的格式：.docx, .xlsx, .xls
3. LLM图片识别需要额外的API配置（可选）
4. 所有输出文件都包含行编号（<!-- N -->）
5. **Word文档转换后不显示预览，直接下载ZIP文件**
6. **Excel文档支持预览和复制功能**
7. **默认下载路径**：`/Users/kyle/Downloads`（可通过环境变量修改）
