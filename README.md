# CSV-Word转换工具

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/badge/version-1.0.0-orange.svg)](https://github.com/your-repo/csv-word-converter)

专业的CSV到Word文档转换工具，支持多种模板和自定义配置。

## 🚀 特性

- **多模板支持**: 内置5种专业模板（国资委、新能源、房地产、科技、电力）
- **智能数据处理**: 自动识别CSV结构，智能填充Word模板
- **图片处理**: 支持网络图片下载和嵌入
- **批量转换**: 支持大批量CSV文件处理
- **命令行工具**: 提供完整的CLI接口
- **Python API**: 支持编程调用
- **高度可配置**: 支持自定义模板和样式

## 📦 安装

### 从源码安装
```bash
git clone <repository-url>
cd clientab-main
pip install -r requirements.txt
pip install .
```

### 开发模式安装
```bash
pip install -e .
```

## 🎯 快速开始

### 命令行使用
```bash
# 基本转换
python -m csv_word_converter input.csv --template guoziwei

# 指定输出目录
python -m csv_word_converter input.csv --template technology --output-dir ./reports

# 查看帮助
python -m csv_word_converter --help
```

### Python API使用
```python
from csv_word_converter import csv_to_word_universal

# 转换CSV到Word
result = csv_to_word_universal(
    csv_file="data.csv",
    template_type="guoziwei",
    output_dir="./outputs"
)

print(f"生成的文档: {result}")
```

## 📋 支持的模板

| 模板名称 | 描述 | 适用场景 |
|---------|------|----------|
| `guoziwei` | 国资委标准模板 | 政府报告、公文 |
| `new_energy` | 新能源行业模板 | 新能源项目报告 |
| `realty` | 房地产行业模板 | 房地产分析报告 |
| `technology` | 科技行业模板 | 技术报告、产品文档 |
| `electricity` | 电力行业模板 | 电力系统报告 |

## 🛠️ 命令行选项

```bash
python -m csv_word_converter [OPTIONS] CSV_FILE

选项:
  -t, --template TEXT     模板类型 [required]
  -o, --output-dir TEXT   输出目录 [default: temp-data]
  -q, --quiet            静默模式
  -v, --verbose          详细输出
  --validate-only        仅验证CSV文件
  --version              显示版本信息
  --help                 显示帮助信息
```

## 📁 项目结构

```
csv-word-converter/
├── src/
│   └── csv_word_converter/
│       ├── __init__.py          # 包初始化
│       ├── __main__.py          # 命令行入口
│       ├── core.py              # 核心转换逻辑
│       └── utils/               # 工具模块
│           ├── doc_utils.py     # 文档处理工具
│           ├── image_utils.py   # 图片处理工具
│           └── validation.py    # 数据验证工具
├── ab_doc_temps/                # 文档模板
├── ab_response_formats/         # 响应格式模板
├── tests/                       # 测试文件
├── outputs/                     # 输出目录
├── requirements.txt             # 依赖列表
├── setup.py                     # 安装配置
├── pyproject.toml              # 项目配置
└── README.md                   # 项目说明
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_core.py

# 生成覆盖率报告
pytest --cov=csv_word_converter
```

## 📖 文档

- [部署指南](部署指南.md) - 详细的部署说明
- [API文档](docs/) - 完整的API参考
- [模板开发指南](docs/template-development.md) - 自定义模板开发

## 🤝 贡献

欢迎贡献代码！请遵循以下步骤：

1. Fork 项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 更新日志

### v1.0.0 (2025-09-20)
- 初始版本发布
- 支持5种内置模板
- 完整的命令行工具
- Python API支持
- 图片处理功能
- 批量转换支持

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 🆘 支持

如果您遇到问题或有建议，请：

1. 查看 [FAQ](docs/faq.md)
2. 搜索 [Issues](https://github.com/your-repo/csv-word-converter/issues)
3. 创建新的 Issue
4. 联系开发团队

## 👥 作者

- **AI Development Team** - *初始开发* - [GitHub](https://github.com/ai-dev-team)

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者和用户！

---

**⭐ 如果这个项目对您有帮助，请给我们一个星标！**