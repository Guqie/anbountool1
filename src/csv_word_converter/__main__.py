#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV-Word转换工具 - 模块执行入口

支持使用 python -m csv_word_converter 方式执行命令行工具。

使用示例:
    python -m csv_word_converter input.csv --template guoziwei --output ./reports/
    python -m csv_word_converter --list-templates
    python -m csv_word_converter --help
"""

import sys
from .cli import main

if __name__ == "__main__":
    """
    模块级执行入口点
    
    当使用 python -m csv_word_converter 执行时，会调用此入口点。
    直接委托给 cli.main() 函数处理所有命令行逻辑。
    """
    sys.exit(main())