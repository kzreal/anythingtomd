"""
MCP 服务器测试脚本
用于验证 AlltoMarkdown MCP 服务器的功能
"""
import asyncio
import sys
from pathlib import Path
import json

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from alltomarkdown_mcp import (
    analyze_file_internal,
    convert_file_internal,
    convert_batch_internal,
    list_sections_internal
)


def print_separator():
    """打印分隔线"""
    print("\n" + "=" * 60 + "\n")


async def test_analyze_file(file_path: str):
    """测试 analyze_file 工具"""
    print(f"测试 analyze_file: {file_path}")
    print_separator()

    try:
        result = analyze_file_internal(file_path)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n✅ analyze_file 测试通过")
    except Exception as e:
        print(f"\n❌ analyze_file 测试失败: {e}")


async def test_convert_file(file_path: str, output_format: str = "markdown"):
    """测试 convert_file 工具"""
    print(f"测试 convert_file: {file_path}, 输出格式: {output_format}")
    print_separator()

    try:
        result = convert_file_internal(file_path, output_format=output_format)
        if isinstance(result, dict):
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            # 限制输出长度
            if len(result) > 1000:
                print(result[:1000] + "\n... (内容已截断)")
            else:
                print(result)
        print("\n✅ convert_file 测试通过")
    except Exception as e:
        print(f"\n❌ convert_file 测试失败: {e}")


async def test_list_sections(file_path: str, max_level: int = 0):
    """测试 list_sections 工具"""
    print(f"测试 list_sections: {file_path}, 切片级别: {max_level}")
    print_separator()

    try:
        result = list_sections_internal(file_path, max_level)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        print("\n✅ list_sections 测试通过")
    except Exception as e:
        print(f"\n❌ list_sections 测试失败: {e}")


async def test_convert_batch(file_paths: list):
    """测试 convert_batch 工具"""
    print(f"测试 convert_batch: {len(file_paths)} 个文件")
    print_separator()

    try:
        results = convert_batch_internal(file_paths)
        for result in results:
            status = "✅" if result["success"] else "❌"
            print(f"{status} {result['file_path']}")
            if not result["success"]:
                print(f"   错误: {result.get('error')}")
        print("\n✅ convert_batch 测试完成")
    except Exception as e:
        print(f"\n❌ convert_batch 测试失败: {e}")


async def main():
    """运行所有测试"""
    print("AlltoMarkdown MCP 服务器测试")
    print("=" * 60)

    # 测试 Word 文件
    word_file = Path(__file__).parent / "商务文件.docx"
    if word_file.exists():
        print("\n【Word 文件测试】")
        await test_analyze_file(str(word_file))
        await test_convert_file(str(word_file), output_format="json")
        await test_list_sections(str(word_file), max_level=1)
    else:
        print(f"\n⚠️ Word 测试文件不存在: {word_file}")

    # 测试 Excel 文件
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        print("\n【Excel 文件测试】")
        await test_analyze_file(str(excel_file))
        await test_convert_file(str(excel_file))
    else:
        print(f"\n⚠️ Excel 测试文件不存在: {excel_file}")

    # 测试 PDF 文件
    pdf_file = Path(__file__).parent / "测试.pdf"
    if pdf_file.exists():
        print("\n【PDF 文件测试】")
        await test_analyze_file(str(pdf_file))
        await test_convert_file(str(pdf_file))
        await test_list_sections(str(pdf_file))
    else:
        print(f"\n⚠️ PDF 测试文件不存在: {pdf_file}")

    # 测试批量转换
    test_files = []
    if word_file.exists():
        test_files.append(str(word_file))
    if excel_file.exists():
        test_files.append(str(excel_file))

    if test_files:
        print("\n【批量转换测试】")
        await test_convert_batch(test_files)

    print("\n" + "=" * 60)
    print("测试完成")


if __name__ == "__main__":
    asyncio.run(main())
