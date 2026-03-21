"""
快速验证 MCP 工具功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from alltomarkdown_mcp import (
    _analyze_file_internal,
    _convert_file_internal,
    _list_sections_internal
)


def test_analyze():
    """测试文件分析"""
    print("=" * 60)
    print("测试 analyze_file")
    print("=" * 60)

    # 测试 Excel 文件（没有图片，处理更快）
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        info = _analyze_file_internal(str(excel_file))
        print(f"✅ Excel 文件分析成功:")
        print(f"   文件名: {info['filename']}")
        print(f"   文件类型: {info['file_type']}")
        print(f"   文件大小: {info['file_size_mb']} MB")
    else:
        print(f"⚠️ 测试文件不存在: {excel_file}")


def test_list_sections():
    """测试列出切片"""
    print("\n" + "=" * 60)
    print("测试 list_sections")
    print("=" * 60)

    # 测试 Excel 文件
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        try:
            sections = _list_sections_internal(str(excel_file), max_level=0)
            print(f"✅ Excel 文件切片列表成功:")
            for section in sections[:5]:  # 只显示前5个
                print(f"   - [{section['index']}] {section['title']}")
            if len(sections) > 5:
                print(f"   ... 还有 {len(sections) - 5} 个切片")
        except Exception as e:
            print(f"❌ 列出切片失败: {e}")
    else:
        print(f"⚠️ 测试文件不存在: {excel_file}")


def test_convert_markdown():
    """测试转换为 Markdown"""
    print("\n" + "=" * 60)
    print("测试 convert_file (Markdown)")
    print("=" * 60)

    # 测试 Excel 文件
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        try:
            result = _convert_file_internal(str(excel_file), output_format='markdown', max_level=0)
            # 只显示前 500 个字符
            preview = result[:500] if len(result) > 500 else result
            print(f"✅ Excel 转 Markdown 成功:")
            print(f"   内容预览 (前 {len(preview)} 字符):")
            print(f"   {preview}")
            if len(result) > 500:
                print(f"   ... (总共 {len(result)} 字符)")
        except Exception as e:
            print(f"❌ 转换失败: {e}")
    else:
        print(f"⚠️ 测试文件不存在: {excel_file}")


def test_convert_json():
    """测试转换为 JSON"""
    print("\n" + "=" * 60)
    print("测试 convert_file (JSON)")
    print("=" * 60)

    # 测试 Excel 文件
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        try:
            result = _convert_file_internal(str(excel_file), output_format='json', max_level=0)
            print(f"✅ Excel 转 JSON 成功:")
            print(f"   文件路径: {result['file_path']}")
            print(f"   文件类型: {result['file_type']}")
            print(f"   切片数量: {len(result['sections'])}")
        except Exception as e:
            print(f"❌ 转换失败: {e}")
    else:
        print(f"⚠️ 测试文件不存在: {excel_file}")


def test_convert_sections():
    """测试获取切片列表"""
    print("\n" + "=" * 60)
    print("测试 convert_file (sections)")
    print("=" * 60)

    # 测试 Excel 文件
    excel_file = Path(__file__).parent / "filled_table.xlsx"
    if excel_file.exists():
        try:
            result = _convert_file_internal(str(excel_file), output_format='sections', max_level=0)
            print(f"✅ 获取切片列表成功:")
            for section in result[:5]:  # 只显示前5个
                print(f"   - [{section['index']}] {section['title']} ({section['filename']})")
            if len(result) > 5:
                print(f"   ... 还有 {len(result) - 5} 个切片")
        except Exception as e:
            print(f"❌ 获取切片列表失败: {e}")
    else:
        print(f"⚠️ 测试文件不存在: {excel_file}")


def main():
    """运行所有测试"""
    print("AlltoMarkdown MCP 工具快速验证")
    print()

    test_analyze()
    test_list_sections()
    test_convert_markdown()
    test_convert_json()
    test_convert_sections()

    print("\n" + "=" * 60)
    print("验证完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
