"""
投资顾问系统 - Flask API服务
提供OCR识别、AI分析等接口
"""

import os
import sys
import yaml
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS

# 导入自定义模块
from ocr_service import HoldingsOCR
from ai_analyzer import AIInvestmentAnalyzer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 创建Flask应用
app = Flask(__name__)
CORS(app)  # 允许跨域

# 加载配置
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.safe_load(f)

# 初始化服务
ocr_service = HoldingsOCR(config)
ai_analyzer = AIInvestmentAnalyzer(config)


@app.route('/api/health', methods=['GET'])
def health():
    """健康检查"""
    return jsonify({
        'status': 'ok',
        'service': 'Investment Advisor API',
        'version': '2.0',
        'features': {
            'ocr_enabled': ocr_service.use_gpt_vision,
            'ai_analysis_enabled': ai_analyzer.use_ai
        }
    })


@app.route('/api/ocr/recognize', methods=['POST'])
def recognize_screenshot():
    """OCR识别接口"""
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({'error': '缺少图片数据'}), 400
        
        logger.info("📷 收到OCR识别请求")
        
        # 执行识别
        holdings = ocr_service.recognize_from_base64(image_base64)
        
        logger.info(f"✅ OCR识别成功，共{len(holdings)}只基金")
        
        return jsonify({
            'success': True,
            'data': holdings,
            'count': len(holdings)
        })
        
    except Exception as e:
        logger.error(f"❌ OCR识别失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze', methods=['POST'])
def analyze_portfolio():
    """AI投资分析接口"""
    try:
        data = request.json
        holdings = data.get('holdings')
        
        if not holdings or not isinstance(holdings, list):
            return jsonify({'error': '缺少持仓数据或格式错误'}), 400
        
        logger.info(f"🤖 收到分析请求，持仓数量: {len(holdings)}")
        
        # 执行AI分析
        analysis_result = ai_analyzer.analyze_portfolio(holdings)
        
        logger.info("✅ 分析完成")
        
        return jsonify({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        logger.error(f"❌ 分析失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/analyze/quick', methods=['POST'])
def quick_analyze():
    """快速分析接口（OCR + 分析一体）"""
    try:
        data = request.json
        image_base64 = data.get('image')
        
        if not image_base64:
            return jsonify({'error': '缺少图片数据'}), 400
        
        logger.info("📸 收到快速分析请求（OCR + AI分析）")
        
        # 1. OCR识别
        logger.info("步骤1: OCR识别...")
        holdings = ocr_service.recognize_from_base64(image_base64)
        logger.info(f"✅ 识别到{len(holdings)}只基金")
        
        # 2. AI分析
        logger.info("步骤2: AI分析...")
        analysis_result = ai_analyzer.analyze_portfolio(holdings)
        logger.info("✅ 分析完成")
        
        return jsonify({
            'success': True,
            'data': analysis_result
        })
        
    except Exception as e:
        logger.error(f"❌ 快速分析失败: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/config/check', methods=['GET'])
def check_config():
    """检查配置状态"""
    openai_config = config.get('openai', {})
    api_key = openai_config.get('api_key', '')
    
    return jsonify({
        'openai_configured': bool(api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE' and api_key.strip()),
        'openai_model': openai_config.get('model', 'gpt-4o'),
        'ocr_mode': 'GPT-4 Vision' if ocr_service.use_gpt_vision else '模拟识别',
        'analysis_mode': 'GPT-4 AI' if ai_analyzer.use_ai else '规则引擎',
        'message': 'OpenAI API已配置，使用真实AI分析' if ai_analyzer.use_ai else '未配置OpenAI API，使用规则引擎'
    })


if __name__ == '__main__':
    print("=" * 60)
    print("🚀 投资顾问API服务启动")
    print("=" * 60)
    print(f"📍 访问地址: http://localhost:5001")
    print(f"📡 API接口:")
    print(f"   - GET  /api/health          健康检查")
    print(f"   - POST /api/ocr/recognize   OCR识别")
    print(f"   - POST /api/analyze         AI分析")
    print(f"   - POST /api/analyze/quick   快速分析（OCR+AI）")
    print(f"   - GET  /api/config/check    配置检查")
    print("=" * 60)
    
    # 检查配置
    openai_config = config.get('openai', {})
    api_key = openai_config.get('api_key', '')
    
    if api_key and api_key != 'YOUR_OPENAI_API_KEY_HERE' and api_key.strip():
        print("✅ OpenAI API已配置")
        print(f"   模型: {openai_config.get('model', 'gpt-4o')}")
        print(f"   OCR: GPT-4 Vision")
        print(f"   分析: GPT-4 AI")
    else:
        print("⚠️  OpenAI API未配置")
        print("   OCR: 模拟识别（返回示例数据）")
        print("   分析: 规则引擎（基于if-else）")
        print("\n💡 配置方法:")
        print("   1. 编辑 config.yaml")
        print("   2. 填入 openai.api_key")
        print("   3. 重启服务")
    
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=5001, debug=False)
