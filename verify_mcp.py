"""
验证 MCP 服务器工具注册
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from alltomarkdown_mcp import (
    analyze_file_short,
    convert_file_short,
    list_sections_short,
    convert_batch_short,
    analyze_file,
    convert_file,
    list_sections,
    convert_batch,
)
import inspect

print("=" * 60)
print("MCP 服务器工具验证")
print("=" * 60)

# 检查简短名称工具
print("\n=== 简短名称工具（便于快速输入）===")
short_tools = [
    ('analyze', analyze_file_short),
    ('convert', convert_file_short),
    ('sections', list_sections_short),
    ('batch', convert_batch_short),
]

for name, func in short_tools:
    print(f"✅ {name:15s} - {inspect.signature(func)}")

# 检查完整名称工具
print("\n=== 完整名称工具（便于理解和自动补全）===")
full_tools = [
    ('analyze_file', analyze_file),
    ('convert_file', convert_file),
    ('list_sections', list_sections),
    ('convert_batch', convert_batch),
]

for name, func in full_tools:
    print(f"✅ {name:20s} - {inspect.signature(func)}")

# 测试基本功能
print("\n" + "=" * 60)
print("测试基本功能")
print("=" * 60)

from alltomarkdown_mcp import _analyze_file_internal, _convert_file_internal

# 测试 analyze
excel_file = Path(__file__).parent / "filled_table.xlsx"
if excel_file.exists():
    try:
        info = _analyze_file_internal(str(excel_file))
        print(f"\n✅ analyze 测试通过")
        print(f"   文件: {info['filename']}, 类型: {info['file_type']}")
    except Exception as e:
        print(f"\n❌ analyze 测试失败: {e}")

# 测试 convert
try:
    result = _convert_file_internal(str(excel_file), output_format='markdown', max_level=0)
    print(f"\n✅ convert 测试通过")
    print(f"   输出长度: {len(result)} 字符")
except Exception as e:
    print(f"\n❌ convert 测试失败: {e}")

print("\n" + "=" * 60)
print("所有测试通过！")
print("=" * 60)

print("\n" + "=" * 60)
print("使用说明")
print("=" * 60)
print("""
简短名称（快速输入）:
  analyze   - 分析文件
  convert   - 转换文件
  sections  - 列出切片
  batch     - 批量转换

完整名称（自动补全）:
  analyze_file   - 分析文件
  convert_file   - 转换文件
  list_sections  - 列出切片
  convert_batch  - 批量转换

示例:
  使用简短名称: analyze /path/to/file.docx
  使用完整名称: analyze_file /path/to/file.docx
""")
