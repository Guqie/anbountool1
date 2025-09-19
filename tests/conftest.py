#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV-Word转换工具包 - Pytest配置文件

定义测试夹具、配置和共享资源。
"""

import os
import tempfile
import shutil
from pathlib import Path
from typing import Generator

import pandas as pd
import pytest


@pytest.fixture(scope="session")
def test_data_dir() -> Generator[str, None, None]:
    """
    创建测试数据目录夹具
    
    返回:
        str: 临时测试数据目录路径
    """
    temp_dir = tempfile.mkdtemp(prefix="csv_word_test_")
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture(scope="function")
def sample_csv_file(test_data_dir: str) -> str:
    """
    创建示例CSV文件夹具
    
    参数:
        test_data_dir: 测试数据目录
        
    返回:
        str: 示例CSV文件路径
    """
    csv_file = os.path.join(test_data_dir, "sample_data.csv")
    
    # 创建示例数据
    sample_data = {
        "标题": [
            "第一个标题",
            "第二个标题", 
            "第三个标题"
        ],
        "内容": [
            "这是第一段内容，包含中文字符。",
            "这是第二段内容，包含数字123和英文ABC。",
            "这是第三段内容，包含特殊符号！@#$%。"
        ],
        "分类": ["重要", "一般", "重要"],
        "状态": ["完成", "进行中", "待开始"],
        "图片URL": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png", 
            "https://example.com/image3.gif"
        ]
    }
    
    df = pd.DataFrame(sample_data)
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    return csv_file


@pytest.fixture(scope="function")
def complex_csv_file(test_data_dir: str) -> str:
    """
    创建复杂CSV文件夹具（用于压力测试）
    
    参数:
        test_data_dir: 测试数据目录
        
    返回:
        str: 复杂CSV文件路径
    """
    csv_file = os.path.join(test_data_dir, "complex_data.csv")
    
    # 创建大量数据
    num_rows = 100
    complex_data = {
        "ID": list(range(1, num_rows + 1)),
        "标题": [f"标题{i}" for i in range(1, num_rows + 1)],
        "内容": [f"这是第{i}段内容，包含各种字符：中文、English、123、!@#$%^&*()" for i in range(1, num_rows + 1)],
        "分类": ["重要", "一般", "紧急"] * (num_rows // 3 + 1),
        "创建时间": ["2024-01-01", "2024-01-02", "2024-01-03"] * (num_rows // 3 + 1),
        "图片URL": [
            "https://example.com/image1.jpg",
            "https://example.com/image2.png",
            "https://example.com/image3.gif"
        ] * (num_rows // 3 + 1)
    }
    
    # 截取到指定行数
    for key in complex_data:
        complex_data[key] = complex_data[key][:num_rows]
    
    df = pd.DataFrame(complex_data)
    df.to_csv(csv_file, index=False, encoding='utf-8')
    
    return csv_file


@pytest.fixture(scope="function")
def empty_csv_file(test_data_dir: str) -> str:
    """
    创建空CSV文件夹具
    
    参数:
        test_data_dir: 测试数据目录
        
    返回:
        str: 空CSV文件路径
    """
    csv_file = os.path.join(test_data_dir, "empty_data.csv")
    
    # 创建只有表头的空数据
    empty_data = pd.DataFrame(columns=["标题", "内容", "分类"])
    empty_data.to_csv(csv_file, index=False, encoding='utf-8')
    
    return csv_file


@pytest.fixture(scope="function")
def malformed_csv_file(test_data_dir: str) -> str:
    """
    创建格式错误的CSV文件夹具
    
    参数:
        test_data_dir: 测试数据目录
        
    返回:
        str: 格式错误的CSV文件路径
    """
    csv_file = os.path.join(test_data_dir, "malformed_data.csv")
    
    # 创建格式错误的CSV内容
    malformed_content = """标题,内容,分类
"未闭合引号,内容1,分类1
标题2,"包含换行
的内容",分类2
标题3,内容3,分类3,额外列
"""
    
    with open(csv_file, 'w', encoding='utf-8') as f:
        f.write(malformed_content)
    
    return csv_file


@pytest.fixture(scope="function")
def output_dir(test_data_dir: str) -> str:
    """
    创建输出目录夹具
    
    参数:
        test_data_dir: 测试数据目录
        
    返回:
        str: 输出目录路径
    """
    output_path = os.path.join(test_data_dir, "outputs")
    os.makedirs(output_path, exist_ok=True)
    return output_path


@pytest.fixture(scope="session")
def project_root() -> str:
    """
    获取项目根目录夹具
    
    返回:
        str: 项目根目录路径
    """
    # 从当前文件位置向上查找项目根目录
    current_dir = Path(__file__).parent
    while current_dir.parent != current_dir:
        if (current_dir / "pyproject.toml").exists() or (current_dir / "setup.py").exists():
            return str(current_dir)
        current_dir = current_dir.parent
    
    # 如果找不到，返回当前目录的父目录
    return str(Path(__file__).parent.parent)


@pytest.fixture(autouse=True)
def setup_test_environment(project_root: str):
    """
    自动设置测试环境夹具
    
    参数:
        project_root: 项目根目录
    """
    # 添加src目录到Python路径
    src_path = os.path.join(project_root, "src")
    if src_path not in os.sys.path:
        os.sys.path.insert(0, src_path)


# 测试标记定义
def pytest_configure(config):
    """配置pytest标记"""
    config.addinivalue_line(
        "markers", "slow: 标记测试为慢速测试"
    )
    config.addinivalue_line(
        "markers", "integration: 标记测试为集成测试"
    )
    config.addinivalue_line(
        "markers", "unit: 标记测试为单元测试"
    )
    config.addinivalue_line(
        "markers", "performance: 标记测试为性能测试"
    )


# 测试收集钩子
def pytest_collection_modifyitems(config, items):
    """修改测试收集项"""
    # 为没有标记的测试添加unit标记
    for item in items:
        if not any(item.iter_markers()):
            item.add_marker(pytest.mark.unit)