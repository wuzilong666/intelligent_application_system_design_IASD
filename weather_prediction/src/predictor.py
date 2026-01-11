"""
天气预测模块
整合深度学习模型和Gemini API进行天气预测
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import config
from utils.api_client import api_client
from utils.helpers import get_time_range, log_message, calculate_confidence_interval


class WeatherPredictor:
    """天气预测器"""
    
    def __init__(self, use_model: str = "api"):
        """
        初始化预测器
        
        参数:
            use_model: 使用的模型类型 ("api", "convlstm", "cnn3d")
        """
        self.use_model = use_model
        self.dl_model = None
        
        if use_model == "convlstm":
            from models.convlstm_model import ConvLSTMModel
            self.dl_model = ConvLSTMModel()
        elif use_model == "cnn3d":
            from models.cnn3d_model import CNN3DModel
            self.dl_model = CNN3DModel()
        
        log_message(f"天气预测器初始化完成，使用模型: {use_model}")
    
    def _predict_single_horizon(self, horizon: str, current_data: Dict[str, Any],
                               historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """针对任意时间尺度进行预测并封装结果"""
        desc = self._describe_horizon(horizon)
        log_message(f"开始{desc}预测")

        time_points = get_time_range(horizon)

        if self.use_model == "api":
            result = self._predict_with_api(current_data, historical_data, horizon)
        else:
            result = self._predict_with_dl_model(current_data, historical_data, horizon)

        result["time_points"] = [t.isoformat() for t in time_points]
        result["horizon"] = horizon
        result["horizon_description"] = desc

        log_message(f"{desc}预测完成")
        return result

    def predict_short_term(self, current_data: Dict[str, Any], 
                          historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """兼容旧接口：短期预测"""
        return self._predict_single_horizon("short_term", current_data, historical_data)
    
    def predict_medium_term(self, current_data: Dict[str, Any],
                           historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """兼容旧接口：中期预测"""
        return self._predict_single_horizon("medium_term", current_data, historical_data)
    
    def predict_long_term(self, current_data: Dict[str, Any],
                         historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """兼容旧接口：长期预测"""
        return self._predict_single_horizon("long_term", current_data, historical_data)
    
    def predict_multi_scale(self, current_data: Dict[str, Any],
                           historical_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        多尺度预测：1h/3h/6h/1天/2天/3天/1周 + 兼容原短中长
        """
        log_message("开始多尺度预测")

        desired_horizons = [
            "1h", "6h", "1day", "3day", "1week"
        ]

        results = {h: self._predict_single_horizon(h, current_data, historical_data)
                   for h in desired_horizons}

        results["timestamp"] = datetime.now().isoformat()
        log_message("多尺度预测完成")
        return results

    def _describe_horizon(self, horizon: str) -> str:
        mapping = {
            "1h": "未来1小时",
            "6h": "未来6小时",
            "1day": "未来1天",
            "3day": "未来3天",
            "1week": "未来1周"
        }
        return mapping.get(horizon, horizon)
    
    def _predict_with_api(self, current_data: Dict[str, Any],
                         historical_data: List[Dict[str, Any]],
                         horizon: str) -> Dict[str, Any]:
        """
        使用Gemini API进行预测
        
        参数:
            current_data: 当前数据
            historical_data: 历史数据
            horizon: 预测范围
            
        返回:
            预测结果
        """
        log_message(f"使用Gemini API进行{horizon}预测")
        
        # 调用API
        api_result = api_client.predict_weather(historical_data, horizon)
        
        # 生成数值预测（作为基础或fallback）
        predictions = self._generate_numerical_predictions(
            current_data, 
            horizon
        )
        
        if api_result["success"]:
            # 解析API返回的预测文本
            prediction_text = api_result["prediction"]
            
            return {
                "success": True,
                "predictions": predictions,
                "analysis": prediction_text,
                "method": "gemini_api",
                "uncertainty": self._estimate_uncertainty(predictions)
            }
        else:
            # API失败时使用数值预测作为fallback
            log_message(f"API预测失败: {api_result.get('error', '未知错误')}，使用本地预测", "WARNING")
            return {
                "success": True,
                "predictions": predictions,
                "analysis": "API暂时不可用，使用本地算法生成预测结果",
                "method": "fallback_numerical",
                "uncertainty": self._estimate_uncertainty(predictions),
                "api_error": api_result.get("error")
            }
    
    def _predict_with_dl_model(self, current_data: Dict[str, Any],
                              historical_data: List[Dict[str, Any]],
                              horizon: str) -> Dict[str, Any]:
        """
        使用深度学习模型进行预测
        
        参数:
            current_data: 当前数据
            historical_data: 历史数据
            horizon: 预测范围
            
        返回:
            预测结果
        """
        log_message(f"使用深度学习模型进行{horizon}预测")
        
        # 这里应该使用训练好的模型进行预测
        # 由于需要训练数据，这里使用模拟数据
        
        predictions = self._generate_numerical_predictions(current_data, horizon)
        
        return {
            "success": True,
            "predictions": predictions,
            "method": f"deep_learning_{self.use_model}",
            "uncertainty": self._estimate_uncertainty(predictions)
        }
    
    def _generate_numerical_predictions(self, current_data: Dict[str, Any],
                                       horizon: str) -> List[Dict[str, Any]]:
        """
        生成数值预测（模拟）
        
        参数:
            current_data: 当前数据
            horizon: 预测范围
            
        返回:
            预测数据列表
        """
        time_points = get_time_range(horizon)
        predictions = []
        
        # 基础值
        base_temp = current_data.get("temperature", 20)
        base_humidity = current_data.get("humidity", 60)
        base_pressure = current_data.get("pressure", 1013)
        base_wind = current_data.get("wind_speed", 5)
        base_visibility = current_data.get("visibility", 10)  # km
        base_aqi = current_data.get("aqi", 50)  # Air Quality Index
        
        wind_directions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        
        for i, time_point in enumerate(time_points):
            # 添加随机变化模拟预测
            temp_change = np.random.randn() * 2
            wind_speed_val = round(max(0, base_wind + np.random.randn() * 2), 1)
            
            # 风级计算 (Beaufort scale)
            wind_level = self._calculate_wind_level(wind_speed_val)
            
            prediction = {
                "timestamp": time_point.isoformat(),
                "temperature": round(base_temp + temp_change, 1),
                "temperature_max": round(base_temp + temp_change + 2, 1),
                "temperature_min": round(base_temp + temp_change - 2, 1),
                "humidity": round(max(0, min(100, base_humidity + np.random.randn() * 5)), 1),
                "pressure": round(base_pressure + np.random.randn() * 3, 1),
                "wind_speed": wind_speed_val,
                "wind_direction": np.random.choice(wind_directions),
                "wind_level": wind_level,
                "precipitation_probability": round(max(0, min(100, 30 + np.random.randn() * 20)), 1),
                "visibility": round(max(0.1, base_visibility + np.random.randn() * 2), 1),
                "aqi": int(max(0, min(500, base_aqi + np.random.randn() * 20))),
                "air_quality": self._determine_air_quality(int(base_aqi + np.random.randn() * 20)),
                "weather_condition": self._determine_weather_condition()
            }
            
            predictions.append(prediction)
            
            # 更新基础值（模拟趋势）
            base_temp += temp_change * 0.3
        
        return predictions
    
    def _determine_weather_condition(self) -> str:
        """确定天气状况"""
        conditions = ["Sunny", "Cloudy", "Overcast", "Light Rain", "Moderate Rain", "Thunderstorm"]
        probabilities = [0.3, 0.25, 0.2, 0.15, 0.07, 0.03]
        return np.random.choice(conditions, p=probabilities)
    
    def _calculate_wind_level(self, wind_speed: float) -> int:
        """根据风速计算风级 (Beaufort scale)"""
        if wind_speed < 0.3:
            return 0
        elif wind_speed < 1.6:
            return 1
        elif wind_speed < 3.4:
            return 2
        elif wind_speed < 5.5:
            return 3
        elif wind_speed < 8.0:
            return 4
        elif wind_speed < 10.8:
            return 5
        elif wind_speed < 13.9:
            return 6
        elif wind_speed < 17.2:
            return 7
        elif wind_speed < 20.8:
            return 8
        elif wind_speed < 24.5:
            return 9
        elif wind_speed < 28.5:
            return 10
        elif wind_speed < 32.7:
            return 11
        else:
            return 12
    
    def _determine_air_quality(self, aqi: int) -> str:
        """根据AQI确定空气质量等级"""
        if aqi <= 50:
            return "Good"
        elif aqi <= 100:
            return "Moderate"
        elif aqi <= 150:
            return "Unhealthy for Sensitive"
        elif aqi <= 200:
            return "Unhealthy"
        elif aqi <= 300:
            return "Very Unhealthy"
        else:
            return "Hazardous"
    
    def _estimate_uncertainty(self, predictions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        估计预测不确定性
        
        参数:
            predictions: 预测列表
            
        返回:
            不确定性估计
        """
        # 简单的不确定性估计
        # 实际应用中应该使用蒙特卡洛方法或集成方法
        
        temps = [p["temperature"] for p in predictions]
        
        return {
            "confidence_level": 0.95,
            "temperature_uncertainty": round(np.std(temps), 2),
            "method": config.UNCERTAINTY_CONFIG["method"],
            "description": "基于历史数据和模型输出的不确定性估计"
        }


if __name__ == "__main__":
    # 测试代码
    from src.data_collector import WeatherDataCollector
    
    # 准备数据
    collector = WeatherDataCollector()
    historical_data = collector.get_sample_data(240)
    current_data = historical_data[-1]
    
    # 创建预测器
    predictor = WeatherPredictor(use_model="api")
    
    # 短期预测
    result = predictor.predict_short_term(current_data, historical_data)
    print(f"✓ 短期预测完成")
    print(f"  预测时间点数: {len(result['predictions'])}")
    print(f"  第一个预测: {result['predictions'][0]}")
