"""
OCR识别服务 - 支付宝持仓截图识别
使用 GPT-4 Vision 或本地 OCR 引擎识别持仓信息
"""

import os
import re
import json
import base64
from typing import List, Dict, Optional
import logging

# 根据可用库选择OCR方案
try:
    from openai import OpenAI
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False
    print("⚠️  未安装openai库，将使用模拟识别模式")

logger = logging.getLogger(__name__)


class HoldingsOCR:
    """持仓OCR识别器"""
    
    def __init__(self, config: dict):
        self.config = config
        self.openai_config = config.get('openai', {})
        
        if HAS_OPENAI and self.openai_config.get('api_key'):
            self.client = OpenAI(
                api_key=self.openai_config['api_key'],
                base_url=self.openai_config.get('base_url', 'https://api.openai.com/v1')
            )
            self.use_gpt_vision = True
            logger.info("✅ 使用 GPT-4 Vision 进行OCR识别")
        else:
            self.use_gpt_vision = False
            logger.warning("⚠️  未配置OpenAI API，使用模拟识别模式")
    
    def recognize_from_base64(self, image_base64: str) -> List[Dict]:
        """
        从base64图片识别持仓信息
        
        Args:
            image_base64: base64编码的图片（包含data:image/xxx;base64,前缀）
        
        Returns:
            持仓列表
        """
        if self.use_gpt_vision:
            return self._recognize_with_gpt_vision(image_base64)
        else:
            return self._simulate_recognition()
    
    def _recognize_with_gpt_vision(self, image_base64: str) -> List[Dict]:
        """使用GPT-4 Vision识别"""
        try:
            prompt = """
你是一个专业的金融数据提取助手。请从这张支付宝基金持仓截图中提取所有基金的持仓信息。

请按以下JSON格式返回数据（只返回JSON，不要其他说明）：
[
  {
    "name": "基金名称",
    "code": "基金代码（6位数字）",
    "amount": 持仓金额（数字，单位元）,
    "cost": 持仓成本（数字，单位元）,
    "return_rate": 收益率（数字，百分比，如-15.5表示-15.5%）
  }
]

注意事项：
1. 所有金额去掉千分位逗号，转为数字
2. 收益率带符号，正数用+，负数用-
3. 如果截图中某些信息缺失，尽量推算或标记为0
4. 确保返回的是有效的JSON数组
"""
            
            response = self.client.chat.completions.create(
                model=self.openai_config.get('model', 'gpt-4o'),
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_base64,
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )
            
            # 解析返回的JSON
            result_text = response.choices[0].message.content.strip()
            
            # 清理markdown代码块标记
            result_text = re.sub(r'```json\s*', '', result_text)
            result_text = re.sub(r'```\s*$', '', result_text)
            result_text = result_text.strip()
            
            holdings = json.loads(result_text)
            
            logger.info(f"✅ GPT-4 Vision识别成功，共{len(holdings)}只基金")
            return holdings
            
        except Exception as e:
            logger.error(f"❌ GPT-4 Vision识别失败: {e}")
            raise Exception(f"OCR识别失败: {str(e)}")
    
    def _simulate_recognition(self) -> List[Dict]:
        """模拟识别（用于演示）"""
        logger.info("🔄 使用模拟识别模式")
        
        # 返回示例数据
        return [
            {
                "name": "广发医疗保健股票A",
                "code": "004851",
                "amount": 9069.40,
                "cost": 14000.00,
                "return_rate": -35.22
            },
            {
                "name": "国泰黄金ETF联接A",
                "code": "000218",
                "amount": 4110.88,
                "cost": 4800.00,
                "return_rate": -14.36
            },
            {
                "name": "大成高鑫股票A",
                "code": "000628",
                "amount": 5163.51,
                "cost": 5399.75,
                "return_rate": -4.37
            },
            {
                "name": "信澳新能源产业股票A",
                "code": "001410",
                "amount": 6568.53,
                "cost": 4819.98,
                "return_rate": 36.28
            }
        ]
    
    def recognize_from_file(self, image_path: str) -> List[Dict]:
        """
        从图片文件识别持仓信息
        
        Args:
            image_path: 图片文件路径
        
        Returns:
            持仓列表
        """
        # 读取图片并转为base64
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 判断图片类型
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')
        
        image_base64 = f"data:{mime_type};base64,{base64.b64encode(image_data).decode()}"
        
        return self.recognize_from_base64(image_base64)


# Flask API 服务（可选）
def create_ocr_api():
    """创建OCR识别API服务"""
    try:
        from flask import Flask, request, jsonify
        from flask_cors import CORS
    except ImportError:
        print("⚠️  未安装flask/flask-cors，无法启动API服务")
        print("安装方法: pip install flask flask-cors")
        return None
    
    app = Flask(__name__)
    CORS(app)  # 允许跨域
    
    # 加载配置
    import yaml
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    ocr_service = HoldingsOCR(config)
    
    @app.route('/api/ocr/recognize', methods=['POST'])
    def recognize():
        """OCR识别接口"""
        try:
            data = request.json
            image_base64 = data.get('image')
            
            if not image_base64:
                return jsonify({'error': '缺少图片数据'}), 400
            
            # 执行识别
            holdings = ocr_service.recognize_from_base64(image_base64)
            
            return jsonify({
                'success': True,
                'data': holdings,
                'count': len(holdings)
            })
            
        except Exception as e:
            logger.error(f"识别失败: {e}", exc_info=True)
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """健康检查"""
        return jsonify({
            'status': 'ok',
            'service': 'OCR Recognition Service',
            'gpt_vision_enabled': ocr_service.use_gpt_vision
        })
    
    return app


# 命令行测试
if __name__ == '__main__':
    import sys
    import yaml
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 加载配置
    with open('config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    ocr_service = HoldingsOCR(config)
    
    if len(sys.argv) > 1 and sys.argv[1] == 'server':
        # 启动API服务器
        app = create_ocr_api()
        if app:
            print("="*50)
            print("🚀 OCR识别服务已启动")
            print("📍 访问地址: http://localhost:5001")
            print("📡 API接口: POST http://localhost:5001/api/ocr/recognize")
            print("="*50)
            app.run(host='0.0.0.0', port=5001, debug=True)
        else:
            print("❌ 无法启动服务，请先安装依赖: pip install flask flask-cors")
    
    elif len(sys.argv) > 1:
        # 测试识别单张图片
        image_path = sys.argv[1]
        print(f"📷 识别图片: {image_path}")
        
        try:
            holdings = ocr_service.recognize_from_file(image_path)
            print("\n✅ 识别成功！\n")
            print(json.dumps(holdings, indent=2, ensure_ascii=False))
        except Exception as e:
            print(f"\n❌ 识别失败: {e}")
    
    else:
        print("用法:")
        print("  测试图片识别: python ocr_service.py <图片路径>")
        print("  启动API服务: python ocr_service.py server")
