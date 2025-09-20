"""
Web服务器模块 - 为Heroku等云平台提供HTTP接口

该模块提供基于Flask的Web服务器，用于在云平台上部署CSV转Word服务。
支持通过HTTP接口上传CSV文件并获取转换后的Word文档。

作者: AI智学导师
创建时间: 2025-01-17
"""

import os
import logging
from typing import Optional
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import tempfile
from pathlib import Path

from . import csv_to_word_universal

# 配置日志
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB最大文件大小

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {'csv'}


def allowed_file(filename: str) -> bool:
    """
    检查文件扩展名是否允许
    
    参数:
        filename: 文件名
        
    返回:
        bool: 是否允许该文件类型
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET'])
def health_check():
    """
    健康检查接口
    
    返回:
        dict: 服务状态信息
    """
    return jsonify({
        'status': 'healthy',
        'service': 'CSV to Word Converter',
        'version': '1.0.0'
    })


@app.route('/convert', methods=['POST'])
def convert_csv():
    """
    CSV转Word接口
    
    接受POST请求，包含CSV文件和可选的模板类型参数
    
    返回:
        Response: 转换后的Word文档或错误信息
    """
    try:
        # 检查是否有文件上传
        if 'file' not in request.files:
            return jsonify({'error': '未找到上传文件'}), 400
        
        file = request.files['file']
        
        # 检查文件名
        if file.filename == '':
            return jsonify({'error': '未选择文件'}), 400
        
        # 检查文件类型
        if not allowed_file(file.filename):
            return jsonify({'error': '不支持的文件类型，请上传CSV文件'}), 400
        
        # 获取模板类型参数
        template_type = request.form.get('template', 'default')
        
        # 创建临时目录
        with tempfile.TemporaryDirectory() as temp_dir:
            # 保存上传的文件
            filename = secure_filename(file.filename)
            input_path = os.path.join(temp_dir, filename)
            file.save(input_path)
            
            logger.info(f"处理文件: {filename}, 模板: {template_type}")
            
            # 执行转换
            output_path = csv_to_word_universal(
                csv_file=input_path,
                template_type=template_type
            )
            
            if output_path and os.path.exists(output_path):
                # 返回生成的Word文档
                return send_file(
                    output_path,
                    as_attachment=True,
                    download_name=f"converted_{Path(filename).stem}.docx",
                    mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
            else:
                return jsonify({'error': '转换失败，未生成输出文件'}), 500
                
    except Exception as e:
        logger.error(f"转换过程中出现错误: {e}")
        return jsonify({'error': f'服务器内部错误: {str(e)}'}), 500


@app.route('/templates', methods=['GET'])
def list_templates():
    """
    获取可用模板列表
    
    返回:
        dict: 可用模板列表
    """
    try:
        from .core import get_available_templates
        templates = get_available_templates()
        return jsonify({
            'templates': templates,
            'count': len(templates)
        })
    except Exception as e:
        logger.error(f"获取模板列表失败: {e}")
        return jsonify({'error': '获取模板列表失败'}), 500


def start_web_server(port: int = 5000, host: str = '0.0.0.0', debug: bool = False) -> None:
    """
    启动Web服务器
    
    参数:
        port: 端口号，默认5000
        host: 主机地址，默认0.0.0.0（监听所有接口）
        debug: 是否启用调试模式，默认False
    """
    logger.info(f"启动CSV转Word Web服务器")
    logger.info(f"监听地址: {host}:{port}")
    logger.info(f"调试模式: {debug}")
    
    # 从环境变量获取端口（Heroku会设置PORT环境变量）
    port = int(os.environ.get('PORT', port))
    
    app.run(host=host, port=port, debug=debug)


if __name__ == '__main__':
    # 直接运行时的默认配置
    start_web_server()