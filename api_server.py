"""
投资顾问系统 - Flask API服务
提供OCR识别、AI分析等接口
"""

import os
import sys
import yaml
import logging
from flask import Flask, request, jsonify, send_from_directory
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
app = Flask(__name__, static_folder='web', static_url_path='')
CORS(app)  # 允许跨域

# 加载配置
def load_config():
    """加载配置（优先使用环境变量）"""
    config_path = 'config.yaml'
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
    else:
        # 如果配置文件不存在，使用默认配置
        config = {
            'openai': {
                'api_key': '',
                'model': 'deepseek-ai/DeepSeek-V3',
                'base_url': 'https://api.siliconflow.cn/v1',
                'max_tokens': 4000,
                'temperature': 0.7
            }
        }
    
    # 从环境变量覆盖API Key
    openai_key = os.getenv('OPENAI_API_KEY')
    if openai_key:
        config['openai']['api_key'] = openai_key
        logger.info("✅ 使用环境变量中的API Key")
    
    return config

config = load_config()

# 初始化服务
ocr_service = HoldingsOCR(config)
ai_analyzer = AIInvestmentAnalyzer(config)


@app.route('/')
def index():
    """首页"""
    return send_from_directory('web', 'index.html')


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
    port = int(os.getenv('PORT', 5001))
    debug = os.getenv('FLASK_ENV') != 'production'
    
    print("=" * 60)
    print("🚀 投资顾问API服务启动")
    print("=" * 60)
    print(f"📍 端口: {port}")
    print(f"📡 模式: {'生产环境' if not debug else '开发环境'}")
    
    # 检查配置
    openai_config = config.get('openai', {})
    api_key = openai_config.get('api_key', '')
    
    if api_key and api_key.strip():
        print("✅ AI功能已启用")
        print(f"   模型: {openai_config.get('model', 'unknown')}")
        print(f"   服务商: {'硅基流动' if 'siliconflow' in openai_config.get('base_url', '') else 'OpenAI'}")
    else:
        print("⚠️  AI功能未启用（使用规则引擎）")
        print("   提示：设置环境变量 OPENAI_API_KEY 启用AI分析")
    
    print("=" * 60)
    print()
    
    app.run(host='0.0.0.0', port=port, debug=debug)
