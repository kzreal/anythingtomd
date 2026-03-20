# 任意文档转Markdown服务 - 开发计划

## 项目概述

将现有的Word转MD和Excel转MD两个独立服务集成到一个统一的Web服务中，提供一致的界面和输出格式。

**新增功能：**
- **MD内容预览**：转换后即时预览Markdown内容
- **一键复制**：快速复制MD内容到剪贴板，方便粘贴到其他工具
- **双模式输出**：预览模式（快速查看）和下载模式（完整ZIP）

## 参考项目分析

### 1. Word转MD服务 (/Users/kyle/Projects/Word文件切片)

**核心功能：**
- Word文档(.docx)转Markdown
- 保留文档层级结构切片能力
- 图片提取和LLM识别
- 行编号功能 (`<!-- N -->`)
- 输出为ZIP文件（多个MD文件）

**技术栈：**
- Flask 2.0+
- python-docx
- requests (LLM API调用)
- python-dotenv (环境变量管理)

**关键特性：**
- 支持切分层级选择（0=全部，1=一级，2=二级，3=三级，all=全部层级）
- 拖拽上传，带进度条
- LLM图片识别（可选，通过环境变量配置）
- 自动检测标题级别（样式名称、大纲级别、字体大小）
- 表格转Markdown表格
- 错误处理和降级机制
- ❌ 当前无预览功能（需要新增）
- ❌ 当前无复制功能（需要新增）

### 2. Excel转MD服务 (/Users/kyle/Projects/Excel数据填入word/Excel解析工具/excel转文本工具)

**核心功能：**
- Excel文件(.xlsx, .xls)转Markdown
- 支持多sheet处理
- 表格转Markdown格式

**技术栈：**
- Flask 2.3+
- pandas
- openpyxl
- werkzeug

**关键特性：**
- 拖拽上传
- 实时预览 ✅（参考实现）
- 自动识别表格结构
- 输出为文本格式
- 复制功能 ✅（参考实现：copyContent函数）

## 集成方案

### 架构设计

```
anydocumenttomd/
├── app.py                      # 主Flask应用
├── requirements.txt            # 统一依赖
├── .env.example               # 环境变量模板
├── config.py                  # 配置管理
├── utils/
│   ├── __init__.py
│   ├── file_detector.py       # 文件类型检测
│   └── zip_helper.py          # ZIP文件处理
├── converters/
│   ├── __init__.py
│   ├── base.py               # 转换器基类
│   ├── word_converter.py     # Word转换器
│   └── excel_converter.py     # Excel转换器
├── services/
│   ├── __init__.py
│   └── llm_service.py        # LLM图片识别服务
├── static/
│   └── css/
│       └── style.css         # 统一样式
├── templates/
│   └── index.html            # 统一Web界面
├── uploads/                  # 上传文件临时目录
├── downloads/                # 下载文件目录
└── logs/                     # 日志目录
```

### 核心功能设计

#### 1. 统一Web界面

**界面元素：**
- 统一的上传区域（支持Word和Excel）
- 自动文件类型识别和显示
- 针对不同文件类型的选项：
  - Word：切分层级选择（0/1/2/3/all）
  - Excel：无额外选项（每个sheet独立文件）
- 统一的进度显示
- **预览区域**：显示转换后的Markdown内容
- **复制按钮**：一键复制MD内容到剪贴板
- **下载按钮**：下载完整的ZIP文件（包含所有MD文件）

**技术实现：**
- 单页面应用
- 前端JavaScript自动检测文件类型
- 根据文件类型显示对应的转换选项
- 统一的API调用接口
- 使用 `navigator.clipboard.writeText()` 实现复制功能
- 预览支持滚动和语法高亮（可选）

**预览策略：**
- Word：显示合并的完整MD内容（如果切分层级>0，显示第一个切片）
- Excel：显示第一个sheet的MD内容
- 支持切换预览不同的章节/sheet（可选）

#### 2. 文件类型检测

**实现逻辑：**
```python
def detect_file_type(filename):
    """检测文件类型"""
    ext = Path(filename).suffix.lower()
    if ext == '.docx':
        return 'word'
    elif ext in ['.xlsx', '.xls']:
        return 'excel'
    else:
        return 'unknown'
```

#### 3. 统一转换器接口

**基类设计：**
```python
class BaseConverter(ABC):
    @abstractmethod
    def convert(self, file_path, options):
        """转换文件，返回转换结果（ZIP文件路径）"""
        pass

    @abstractmethod
    def get_preview_text(self, file_path, options):
        """获取预览文本（返回单个MD文件的内容）"""
        pass

    @abstractmethod
    def get_output_filename(self):
        """获取输出文件名"""
        pass
```

**Word转换器：**
- 继承自BaseConverter
- 保持原有逻辑
- 输出格式：单个MD或多个MD（根据切分层级）

**Excel转换器：**
- 继承自BaseConverter
- 修改输出格式：每个sheet独立MD文件
- 输出格式：ZIP包含多个MD文件

#### 4. 统一输出格式

**输出策略：**
- 所有输出统一为ZIP文件
- ZIP文件包含：
  - 00_index.md（索引文件）
  - 各章节/sheet对应的MD文件
  - 每个MD文件都包含行编号

**索引文件格式：**
```markdown
# 文档转换索引

原文件: example.docx
转换时间: 2026-03-20 10:00:00
文件类型: Word
转换选项: 切分层级=2

---

## 文件列表

- [1. 第一章节](001_第一章节.md)
- [2. 第二章节](002_第二章节.md)
```

### API接口设计

#### 1. 转换接口（支持预览和下载）

```
POST /api/convert
Content-Type: multipart/form-data

参数:
- file: 文件
- options: JSON字符串
  - word: { max_level: 0/1/2/3/all }
  - excel: {}
- mode: "preview" | "download" (默认为 "preview")

响应:
成功:
  - mode="preview": JSON {
      success: true,
      preview_text: "Markdown内容字符串",
      file_count: 3,  // 总文件数
      preview_info: {
        file_name: "001_第一章节.md",  // 当前预览的文件
        total_files: 3
      },
      zip_ready: true  // ZIP已准备好下载
    }
  - mode="download": 返回ZIP文件
失败: JSON { error: "错误信息" }
```

**转换流程：**
1. 用户上传文件并选择转换选项
2. 前端调用 `/api/convert?mode=preview` 获取预览内容
3. 显示预览，提供"复制内容"按钮
4. 提供"下载ZIP"按钮，调用 `/api/convert?mode=download` 下载完整文件

#### 2. 文件信息接口

```
POST /api/analyze
Content-Type: multipart/form-data

参数:
- file: 文件

响应:
JSON {
  success: true,
  file_type: "word" | "excel",
  filename: "example.docx",
  file_size: 1024000,
  word_info: { ... } | null,
  excel_info: { ... } | null
}
```

## 开发步骤

### 阶段1：项目初始化和基础架构（第1-2天）

1. **创建项目结构**
   - 创建目录结构
   - 初始化Git仓库
   - 创建requirements.txt

2. **基础配置**
   - 创建config.py
   - 创建.env.example
   - 配置日志系统

3. **基础工具类**
   - 实现file_detector.py
   - 实现zip_helper.py
   - 创建转换器基类

### 阶段2：Excel转换器迁移和改造（第3-4天）

1. **迁移Excel转换逻辑**
   - 从参考项目迁移ExcelToLLMText类
   - 实现BaseConverter接口
   - 改造输出格式为ZIP

2. **多sheet处理**
   - 实现每个sheet独立MD文件
   - 添加行编号功能
   - 生成索引文件

3. **测试Excel转换器**
   - 单元测试
   - 集成测试

### 阶段3：Word转换器迁移和改造（第5-6天）

1. **迁移Word转换逻辑**
   - 从参考项目迁移TenderSlicer类
   - 实现BaseConverter接口
   - 迁移LLM图片识别服务

2. **Word转换器改造**
   - 保持原有功能
   - 确保输出格式统一（ZIP）
   - 验证行编号功能

3. **测试Word转换器**
   - 单元测试
   - 集成测试
   - LLM服务测试（可选）

### 阶段4：统一Web服务（第7-8天）

1. **创建Flask应用**
   - 设置Flask路由
   - 实现文件上传
   - 实现转换API（支持preview和download模式）

2. **创建Web界面**
   - 设计统一的HTML模板
   - 实现文件类型自动检测
   - 实现动态选项显示
   - 实现进度跟踪

3. **实现预览和复制功能**
   - 添加预览区域UI组件
   - 实现Markdown内容预览（支持代码高亮）
   - 实现"复制内容"按钮功能
   - 实现"下载ZIP"按钮功能
   - 处理复制成功/失败的用户反馈

4. **错误处理**
   - 统一错误响应格式
   - 文件验证
   - 异常捕获和日志记录

### 阶段5：测试和优化（第9-10天）

1. **功能测试**
   - Word文件转换测试（各级别）
   - Excel文件转换测试（多sheet）
   - 边界情况测试

2. **性能优化**
   - 大文件处理优化
   - 内存管理优化
   - 响应时间优化

3. **文档编写**
   - README.md
   - API文档
   - 部署文档

## 技术难点和解决方案

### 1. 输出格式统一

**难点：**
- Word原有输出是ZIP（多个文件）
- Excel原有输出是单文件

**解决方案：**
- 统一输出为ZIP格式
- Excel也改为每个sheet独立文件
- 统一生成索引文件

### 2. 文件类型识别

**难点：**
- 需要在上传后立即识别文件类型
- 根据类型显示不同的转换选项

**解决方案：**
- 前端：文件选择后根据扩展名识别
- 后端：上传时验证文件类型
- 提供分析API返回文件信息

### 3. LLM服务集成

**难点：**
- Word需要LLM服务，Excel不需要
- 需要支持可选配置

**解决方案：**
- LLM服务作为可选组件
- 通过环境变量配置
- 缺少配置时降级处理

### 4. 行编号一致性

**难点：**
- 确保所有MD文件的行编号格式一致
- Word已有行编号，Excel需要添加

**解决方案：**
- 在转换器基类中定义行编号方法
- Excel转换器添加行编号逻辑
- 统一使用`<!-- N -->`格式

### 5. 预览性能优化

**难点：**
- 大文件转换时间较长，预览响应慢
- 预览需要先完成转换，可能影响用户体验

**解决方案：**
- 预览模式只转换第一个章节/sheet
- 缓存转换结果，避免重复转换
- 提供进度显示，让用户了解处理状态
- 考虑异步处理大文件

### 6. 复制功能兼容性

**难点：**
- `navigator.clipboard.writeText()` API在某些浏览器中可能不支持
- 需要提供降级方案

**解决方案：**
- 检测API是否可用，不可用时使用传统方法（document.execCommand）
- 显示友好的错误提示
- 提供手动复制的备用方案（选中所有文本）

## 依赖管理

### requirements.txt

```
# Web框架
flask>=2.0.0
werkzeug>=2.0.0

# Word处理
python-docx>=0.8.11

# Excel处理
pandas>=2.0.0
openpyxl>=3.0.0

# LLM服务
requests>=2.28.0

# 环境变量
python-dotenv>=1.0.0
```

## 环境配置

### .env.example

```bash
# Flask配置
FLASK_HOST=0.0.0.0
FLASK_PORT=8000
FLASK_DEBUG=True

# 文件上传配置
MAX_CONTENT_LENGTH=1073741824  # 1GB

# LLM API配置（可选）
LLM_API_ENDPOINT=
LLM_API_KEY=
LLM_MODEL=vision-model
LLM_TIMEOUT=30
LLM_MAX_RETRIES=3

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 测试计划

### 单元测试

1. **文件类型检测测试**
2. **Word转换器测试**
3. **Excel转换器测试**
4. **ZIP生成测试**
5. **LLM服务测试（可选）**

### 集成测试

1. **端到端转换流程**
2. **大文件处理**
3. **错误场景处理**
4. **并发请求处理**

### 性能测试

1. **大Word文件转换性能**
2. **大Excel文件转换性能**
3. **多sheet Excel处理性能**
4. **LLM API调用性能（可选）**

## 部署计划

### 开发环境

```bash
# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑.env文件

# 启动服务
python app.py
```

### 生产环境

1. 使用WSGI服务器（Gunicorn）
2. 配置Nginx反向代理
3. 设置文件上传大小限制
4. 配置日志轮转
5. 配置进程管理（systemd）

## 未来扩展

### 短期（v1.1）

1. 支持PDF文件转换
2. 添加转换进度 WebSocket
3. 支持批量文件上传
4. 添加转换历史记录

### 中期（v1.2）

1. 支持PowerPoint文件转换
2. 添加OCR功能（扫描文档）
3. 提供REST API文档
4. 添加用户认证

### 长期（v2.0）

1. 支持更多文件格式
2. 云存储集成
3. 转换模板系统
4. API限流和监控

## 风险评估

### 技术风险

1. **LLM API稳定性**
   - 风险：LLM API可能不稳定或收费
   - 缓解：添加降级机制，提供开关

2. **大文件处理**
   - 风险：大文件可能导致内存溢出
   - 缓解：流式处理，文件大小限制

3. **兼容性问题**
   - 风险：不同版本的Word/Excel格式兼容
   - 缓解：充分测试，错误提示

### 业务风险

1. **用户体验**
   - 风险：界面复杂，用户不易理解
   - 缓解：简洁设计，清晰引导

2. **性能问题**
   - 风险：转换时间过长
   - 缓解：进度显示，性能优化

## 成功标准

1. ✅ 支持Word和Excel文件转换
2. ✅ 统一的Web界面
3. ✅ 统一的输出格式（ZIP）
4. ✅ 保留Word的所有核心功能
5. ✅ Excel每个sheet独立文件
6. ✅ 所有MD文件包含行编号
7. ✅ 支持大文件处理（1GB）
8. ✅ **支持MD内容预览（Word和Excel）**
9. ✅ **支持一键复制MD内容到剪贴板**
10. ✅ 完善的错误处理
11. ✅ 完整的文档
12. ✅ 通过测试用例

## 时间估算

- 总开发时间：10个工作日
- 测试时间：2-3个工作日
- 文档编写：1-2个工作日
- 总计：13-15个工作日

## 资源需求

1. **开发人员**：1人
2. **测试人员**：1人（兼职）
3. **服务器**：
   - 开发：本地机器
   - 测试：小型云服务器（2核4G）
   - 生产：根据需求配置
4. **LLM API**（可选）：根据使用情况配置配额

## 总结

本开发计划详细描述了如何将两个独立的文档转换服务集成为一个统一的Web服务。通过模块化设计、统一接口和一致的输出格式，我们可以提供一个用户友好、功能强大的文档转换平台。计划分阶段实施，每个阶段都有明确的目标和可交付成果，确保项目按时高质量完成。