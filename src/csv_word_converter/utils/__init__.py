#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV-Word转换工具包 - 工具模块

包含文档处理、图片下载、数据验证等工具函数。

模块:
- doc_utils: 文档处理工具
- image_downloader: 图片下载工具
- data_utils: 数据处理工具
- validation: 数据验证工具
"""

from .doc_utils import (
    create_target_bookmark_by_keyword_enhanced,
    apply_paragraph_format,
    add_return_directory_placeholder,
    create_target_bookmark_by_keyword,
    convert_return_placeholders_to_hyperlinks,
    add_bookmark_to_paragraph_xml,
    compute_heading_level,
    format_title_text,
    add_internal_hyperlink,
    add_bookmark,
    process_lines,
    process_all_text_paragraphs,
    add_hyperlinks_post_processing,
    replace_halfwidth_quotes_with_fullwidth,
    normalize_spaces_and_convert_punct_except_period,
    remove_special_symbols,
    change_digits_letters_punctuation_to_times_new_roman,
    remove_space_between_chinese_and_digits_letters_punctuation,
    center_image_description_paragraphs,
)
from .image_downloader import EnhancedImageDownloader

__all__ = [
    "create_target_bookmark_by_keyword_enhanced",
    "apply_paragraph_format",
    "add_return_directory_placeholder", 
    "create_target_bookmark_by_keyword",
    "convert_return_placeholders_to_hyperlinks",
    "add_bookmark_to_paragraph_xml",
    "compute_heading_level",
    "format_title_text",
    "add_internal_hyperlink",
    "add_bookmark",
    "process_lines",
    "process_all_text_paragraphs",
    "add_hyperlinks_post_processing",
    "replace_halfwidth_quotes_with_fullwidth",
    "normalize_spaces_and_convert_punct_except_period",
    "remove_special_symbols",
    "change_digits_letters_punctuation_to_times_new_roman",
    "remove_space_between_chinese_and_digits_letters_punctuation",
    "center_image_description_paragraphs",
    "EnhancedImageDownloader",
]