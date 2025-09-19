#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV-Word转换工具 - 命令行接口

提供命令行方式调用CSV到Word转换功能。

使用示例:
    csv2word input.csv --template guoziwei --output ./reports/
    csv-word-convert data.csv -t default -o output.docx --verbose
"""

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import List, Optional

from . import (
    __version__,
    configure_logging,
    csv_to_word_universal,
    get_available_templates,
    validate_csv_file,
)


def setup_argument_parser() -> argparse.ArgumentParser:
    """
    设置命令行参数解析器

    返回:
        argparse.ArgumentParser: 配置好的参数解析器
    """
    parser = argparse.ArgumentParser(
        prog="csv2word",
        description="CSV到Word文档转换工具",
        epilog=f"版本: {__version__} | 更多信息请访问项目主页",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 位置参数
    parser.add_argument(
        "csv_file",
        nargs="?",  # 使CSV文件参数可选
        help="输入的CSV文件路径",
        type=str,
    )

    # 可选参数
    parser.add_argument(
        "-t",
        "--template",
        dest="template_type",
        default="default",
        choices=get_available_templates(),
        help="Word文档模板类型 (默认: default)",
    )

    parser.add_argument(
        "-o",
        "--output",
        dest="output_path",
        help="输出文件路径或目录 (默认: 自动生成)",
        type=str,
    )

    parser.add_argument(
        "--output-dir",
        dest="output_dir",
        help="输出目录 (默认: ./outputs/)",
        type=str,
        default="./outputs/",
    )

    # 处理选项
    parser.add_argument(
        "--no-images",
        dest="download_images",
        action="store_false",
        default=True,
        help="禁用图片下载",
    )

    parser.add_argument(
        "--image-timeout",
        dest="image_timeout",
        type=int,
        default=30,
        help="图片下载超时时间(秒) (默认: 30)",
    )

    parser.add_argument(
        "--max-retries",
        dest="max_retries",
        type=int,
        default=3,
        help="图片下载最大重试次数 (默认: 3)",
    )

    # 输出控制
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="详细输出模式",
    )

    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="静默模式，只输出错误信息",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="日志级别 (默认: INFO)",
    )

    # 验证选项
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="仅验证CSV文件，不进行转换",
    )

    parser.add_argument(
        "--list-templates",
        action="store_true",
        help="列出所有可用模板",
    )

    # 版本信息
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    return parser


def validate_arguments(args: argparse.Namespace) -> bool:
    """
    验证命令行参数的有效性

    参数:
        args: 解析后的命令行参数

    返回:
        bool: 参数是否有效
    """
    # 如果是列出模板或版本信息，跳过CSV文件检查
    if args.list_templates:
        return True
    
    # 检查是否提供了CSV文件
    if not args.csv_file:
        print("错误: 需要提供CSV文件路径", file=sys.stderr)
        return False
    
    # 检查CSV文件是否存在
    if not os.path.exists(args.csv_file):
        print(f"错误: CSV文件不存在: {args.csv_file}", file=sys.stderr)
        return False

    # 检查输出目录
    if args.output_dir:
        output_dir = Path(args.output_dir)
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            print(f"错误: 无法创建输出目录 {args.output_dir}: {e}", file=sys.stderr)
            return False

    # 检查冲突参数
    if args.verbose and args.quiet:
        print("错误: --verbose 和 --quiet 参数不能同时使用", file=sys.stderr)
        return False

    return True


def setup_logging_from_args(args: argparse.Namespace) -> None:
    """
    根据命令行参数设置日志配置

    参数:
        args: 解析后的命令行参数
    """
    if args.quiet:
        log_level = "ERROR"
    elif args.verbose:
        log_level = "DEBUG"
    else:
        log_level = args.log_level

    configure_logging(log_level)


def list_available_templates() -> None:
    """列出所有可用的模板"""
    templates = get_available_templates()
    print("可用的Word文档模板:")
    for i, template in enumerate(templates, 1):
        print(f"  {i}. {template}")


def validate_csv_and_report(csv_file: str) -> bool:
    """
    验证CSV文件并输出报告

    参数:
        csv_file: CSV文件路径

    返回:
        bool: 验证是否成功
    """
    try:
        result = validate_csv_file(csv_file)

        if result["is_valid"]:
            print(f"✓ CSV文件验证通过: {csv_file}")
            print(f"  - 文件大小: {result['file_size']} 字节")
            print(f"  - 行数: {result['row_count']}")
            print(f"  - 列数: {result['column_count']}")
            print(f"  - 列名: {', '.join(result['columns'])}")
            return True
        else:
            print(f"✗ CSV文件验证失败: {result.get('error', '未知错误')}")
            return False

    except Exception as e:
        print(f"✗ CSV文件验证出错: {e}")
        return False


def main() -> int:
    """
    主函数 - 命令行入口点

    返回:
        int: 退出代码 (0=成功, 1=失败)
    """
    parser = setup_argument_parser()
    args = parser.parse_args()

    # 设置日志
    setup_logging_from_args(args)
    logger = logging.getLogger(__name__)

    try:
        # 处理特殊命令
        if args.list_templates:
            list_available_templates()
            return 0

        # 验证参数
        if not validate_arguments(args):
            return 1

        # 仅验证模式
        if args.validate_only:
            success = validate_csv_and_report(args.csv_file)
            return 0 if success else 1

        # 执行转换
        logger.info(f"开始转换CSV文件: {args.csv_file}")
        logger.info(f"使用模板: {args.template_type}")

        # 准备转换参数
        convert_kwargs = {
            "csv_file": args.csv_file,
            "template_type": args.template_type,
        }

        # 添加可选参数
        if args.output_path:
            convert_kwargs["output_file"] = args.output_path

        # 注意：csv_to_word_universal函数目前只支持csv_file, template_type, config_path参数
        # 其他参数如download_images, image_timeout等暂时不传递

        # 执行转换
        result_path = csv_to_word_universal(**convert_kwargs)

        if result_path and os.path.exists(result_path):
            print(f"✓ 转换成功! 输出文件: {result_path}")

            # 显示文件信息
            file_size = os.path.getsize(result_path)
            print(f"  - 文件大小: {file_size} 字节")

            return 0
        else:
            print("✗ 转换失败: 未生成输出文件")
            return 1

    except KeyboardInterrupt:
        print("\n用户中断操作")
        return 1

    except Exception as e:
        logger.error(f"转换过程中出现错误: {e}")
        if args.verbose:
            import traceback

            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())