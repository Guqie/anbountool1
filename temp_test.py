# temp_test.py
import sys
import os

# 将 src 目录添加到 Python 路径，以允许绝对导入
# 这是在项目根目录运行需要导入 'src' 目录中模块的脚本时的常见模式。
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))

from csv_word_converter import csv_to_word_universal

def run_test():
    """
    一个用于从后端直接测试CSV转Word功能的函数。

    该函数会：
    1. 定义输入CSV文件、输出Word文件及使用的模板名称。
    2. 调用核心转换函数 `csv_to_word_universal`。
    3. 打印转换结果，成功或失败。
    """
    input_csv = 'demo_input.csv'
    output_word = 'outputs/temp_test_output.docx'
    template_name = 'guoziwei' # 使用“国资委”模板进行测试

    print(f"开始转换: {input_csv} -> {output_word} (使用模板: {template_name})")

    try:
        # 调用核心转换函数
        csv_to_word_universal(
            csv_file_path=input_csv,
            output_docx_path=output_word,
            template_name=template_name,
            config_path='templates_config.yaml'
        )
        print("转换成功！")
        print(f"输出文件位于: {os.path.abspath(output_word)}")
    except Exception as e:
        print(f"转换失败: {e}")
        # 打印更详细的错误信息以供调试
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()