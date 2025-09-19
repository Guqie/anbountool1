#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV-Word转换工具包安装配置
支持将CSV数据转换为格式化的Word文档
"""

from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    """读取README文件内容"""
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "CSV到Word文档转换工具"

# 读取requirements.txt
def read_requirements():
    """读取依赖列表"""
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    requirements = []
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    # 移除版本注释
                    if '#' in line:
                        line = line.split('#')[0].strip()
                    requirements.append(line)
    return requirements

# 版本信息
VERSION = "1.0.0"

setup(
    name="csv-word-converter",
    version=VERSION,
    author="AI Development Team",
    author_email="dev@example.com",
    description="专业的CSV到Word文档转换工具",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-org/csv-word-converter",
    
    # 包配置
    packages=find_packages(exclude=['tests*', 'docs*', 'frontend*']),
    include_package_data=True,
    
    # 依赖配置
    install_requires=[
        # 核心依赖
        "pandas>=2.0.0",
        "python-docx>=1.1.0",
        "docxcompose>=1.4.0",
        "PyYAML>=6.0.0",
        "Pillow>=10.0.0",
        "requests>=2.28.0",
        
        # 工具依赖
        "pathvalidate>=3.0.0",
        "openpyxl>=3.1.0",
        "lxml>=4.9.0",
    ],
    
    # 额外依赖组
    extras_require={
        'dev': [
            'pytest>=7.0.0',
            'flake8>=6.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'pylint>=2.17.0',
            'bandit>=1.7.0',
            'safety>=2.3.0',
            'isort>=5.12.0',
            'radon>=6.0.0',
        ],
        'api': [
            'fastapi>=0.100.0',
            'uvicorn>=0.20.0',
            'pydantic>=2.0.0',
            'python-multipart>=0.0.6',
        ],
        'web': [
            'streamlit>=1.28.0',
        ],
        'all': [
            'pytest>=7.0.0',
            'flake8>=6.0.0',
            'black>=23.0.0',
            'mypy>=1.0.0',
            'fastapi>=0.100.0',
            'uvicorn>=0.20.0',
            'streamlit>=1.28.0',
        ]
    },
    
    # 命令行工具
    entry_points={
        'console_scripts': [
            'csv2word=csv_word_converter.cli:main',
            'csv-word-convert=csv_word_converter.cli:main',
        ],
    },
    
    # 包数据
    package_data={
        'csv_word_converter': [
            'templates/*.docx',
            'templates/*.yaml',
            'config/*.yaml',
            'config/*.json',
        ],
    },
    
    # 分类信息
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Office Suites",
        "Topic :: Text Processing :: Markup",
        "Topic :: Utilities",
    ],
    
    # Python版本要求
    python_requires=">=3.8",
    
    # 项目URL
    project_urls={
        "Bug Reports": "https://github.com/your-org/csv-word-converter/issues",
        "Source": "https://github.com/your-org/csv-word-converter",
        "Documentation": "https://csv-word-converter.readthedocs.io/",
    },
    
    # 关键词
    keywords="csv word document conversion office automation",
    
    # 许可证
    license="MIT",
    
    # 是否zip安全
    zip_safe=False,
)