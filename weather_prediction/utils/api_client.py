"""
Gemini API 客户端
用于与Gemini API进行通信，获取天气分析和预测
"""

import requests
import json
from typing import Dict, List, Any, Optional
import config


class GeminiAPIClient:
    """Gemini API 客户端类"""
    
    def __init__(self, api_url: str = None, api_key: str = None):
        """
        初始化API客户端
        
        参数:
            api_url: API端点URL
            api_key: API密钥
        """
        self.api_url = api_url or config.API_URL
        self.api_key = api_key or config.API_KEY
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
    
    def analyze_weather_data(self, weather_data: Dict[str, Any], 
                           analysis_type: str = "general") -> Dict[str, Any]:
        """
        使用Gemini API分析天气数据
        
        参数:
            weather_data: 天气数据字典
            analysis_type: 分析类型 ("general", "extreme", "trend")
            
        返回:
            分析结果字典
        """
        try:
            # 构建提示词
            prompt = self._build_analysis_prompt(weather_data, analysis_type)
            
            # 调用API
            response = self._call_api(prompt)
            
            # 解析响应
            result = self._parse_response(response)
            
            return {
                "success": True,
                "analysis": result,
                "data": weather_data
            }
            
        except Exception as e:
            print(f"API调用失败: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "分析失败"
            }
    
    def predict_weather(self, historical_data: List[Dict], 
                       prediction_horizon: str = "short_term") -> Dict[str, Any]:
        """
        使用Gemini API进行天气预测
        
        参数:
            historical_data: 历史天气数据列表
            prediction_horizon: 预测时间范围
            
        返回:
            预测结果字典
        """
        try:
            prompt = self._build_prediction_prompt(historical_data, prediction_horizon)
            response = self._call_api(prompt)
            result = self._parse_response(response)
            
            return {
                "success": True,
                "prediction": result,
                "horizon": prediction_horizon
            }
            
        except Exception as e:
            print(f"预测失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def detect_extreme_weather(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测极端天气事件
        
        参数:
            weather_data: 当前天气数据
            
        返回:
            检测结果字典
        """
        try:
            prompt = f"""
            请分析以下天气数据，识别是否存在极端天气事件（台风、暴雨、高温、低温、大雪等）：
            
            天气数据：
            {json.dumps(weather_data, ensure_ascii=False, indent=2)}
            
            极端天气阈值：
            {json.dumps(config.EXTREME_WEATHER_THRESHOLDS, ensure_ascii=False, indent=2)}
            
            请返回JSON格式的结果，包括：
            1. is_extreme: 是否为极端天气（true/false）
            2. event_type: 极端天气类型
            3. severity: 严重程度（1-4级）
            4. description: 详细描述
            5. suggestions: 应对建议
            """
            
            response = self._call_api(prompt)
            result = self._parse_response(response)
            
            return {
                "success": True,
                "detection": result
            }
            
        except Exception as e:
            print(f"极端天气检测失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _call_api(self, prompt: str) -> Dict[str, Any]:
        """
        调用Gemini API
        
        参数:
            prompt: 提示词
            
        返回:
            API响应
        """
        # 根据API文档构建请求
        # 注意：这里使用通用的OpenAI兼容格式
        endpoint = f"{self.api_url}/chat/completions"
        
        payload = {
            "model": config.API_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        response = requests.post(
            endpoint,
            headers=self.headers,
            json=payload,
            timeout=30
        )
        
        response.raise_for_status()
        return response.json()
    
    def _parse_response(self, response: Dict[str, Any]) -> str:
        """
        解析API响应
        
        参数:
            response: API原始响应
            
        返回:
            解析后的文本内容
        """
        try:
            # 提取消息内容
            if "choices" in response and len(response["choices"]) > 0:
                return response["choices"][0]["message"]["content"]
            else:
                return "无法解析响应"
        except Exception as e:
            print(f"响应解析错误: {str(e)}")
            return f"解析失败: {str(e)}"
    
    def _build_analysis_prompt(self, weather_data: Dict, 
                              analysis_type: str) -> str:
        """
        构建天气分析提示词
        
        参数:
            weather_data: 天气数据
            analysis_type: 分析类型
            
        返回:
            提示词字符串
        """
        base_prompt = f"""
        请分析以下天气数据：
        
        {json.dumps(weather_data, ensure_ascii=False, indent=2)}
        
        """
        
        if analysis_type == "general":
            base_prompt += """
            请提供：
            1. 当前天气状况总结
            2. 主要天气特征
            3. 未来趋势预判
            4. 建议和注意事项
            """
        elif analysis_type == "extreme":
            base_prompt += """
            请重点分析：
            1. 是否存在极端天气风险
            2. 极端天气类型和强度
            3. 影响范围和持续时间
            4. 防范措施建议
            """
        elif analysis_type == "trend":
            base_prompt += """
            请分析天气趋势：
            1. 温度变化趋势
            2. 降水概率趋势
            3. 风力变化趋势
            4. 整体天气演变方向
            """
        
        return base_prompt
    
    def _build_prediction_prompt(self, historical_data: List[Dict], 
                                prediction_horizon: str) -> str:
        """
        构建天气预测提示词
        
        参数:
            historical_data: 历史数据
            prediction_horizon: 预测范围
            
        返回:
            提示词字符串
        """
        horizon_desc = {
            "short_term": "未来6小时",
            "medium_term": "未来3天",
            "long_term": "未来7天"
        }
        
        prompt = f"""
        基于以下历史天气数据，预测{horizon_desc.get(prediction_horizon, '未来')}的天气情况：
        
        历史数据（最近10个时间点）：
        {json.dumps(historical_data[-10:], ensure_ascii=False, indent=2)}
        
        请提供预测结果，包括：
        1. 温度范围
        2. 降水概率
        3. 风力风向
        4. 天气现象
        5. 置信度
        
        请以JSON格式返回预测结果。
        """
        
        return prompt


# 创建全局API客户端实例
api_client = GeminiAPIClient()
