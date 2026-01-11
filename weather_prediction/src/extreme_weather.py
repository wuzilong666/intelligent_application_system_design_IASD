"""
极端天气识别模块
用于检测和预警极端天气事件
"""

import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import config
from utils.api_client import api_client
from utils.helpers import log_message, get_alert_level_name


class ExtremeWeatherDetector:
    """极端天气检测器"""
    
    def __init__(self):
        """初始化检测器"""
        self.thresholds = config.EXTREME_WEATHER_THRESHOLDS
        log_message("极端天气检测器初始化完成")
    
    def detect_all_extremes(self, weather_data: Dict[str, Any],
                           forecast_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        检测所有类型的极端天气
        
        参数:
            weather_data: 当前天气数据
            forecast_data: 预测数据（可选）
            
        返回:
            检测结果字典
        """
        log_message("开始极端天气综合检测")
        
        results = {
            "timestamp": datetime.now().isoformat(),
            "current_weather": weather_data,
            "detections": [],
            "has_extreme": False,
            "max_severity": 0
        }
        
        # 检测各类极端天气
        typhoon = self.detect_typhoon(weather_data)
        if typhoon["detected"]:
            results["detections"].append(typhoon)
        
        heavy_rain = self.detect_heavy_rain(weather_data)
        if heavy_rain["detected"]:
            results["detections"].append(heavy_rain)
        
        high_temp = self.detect_high_temperature(weather_data, forecast_data)
        if high_temp["detected"]:
            results["detections"].append(high_temp)
        
        low_temp = self.detect_low_temperature(weather_data, forecast_data)
        if low_temp["detected"]:
            results["detections"].append(low_temp)
        
        heavy_snow = self.detect_heavy_snow(weather_data)
        if heavy_snow["detected"]:
            results["detections"].append(heavy_snow)
        
        # 使用API进行智能分析
        api_detection = self._detect_with_api(weather_data)
        if api_detection["success"]:
            results["ai_analysis"] = api_detection["detection"]
        
        # 更新总体结果
        if results["detections"]:
            results["has_extreme"] = True
            results["max_severity"] = max(d["severity"] for d in results["detections"])
        
        log_message(f"检测完成，发现 {len(results['detections'])} 个极端天气事件")
        return results
    
    def detect_typhoon(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测台风
        
        参数:
            weather_data: 天气数据
            
        返回:
            检测结果
        """
        wind_speed = weather_data.get("wind_speed", 0)
        pressure = weather_data.get("pressure", 1013)
        
        threshold = self.thresholds["typhoon"]
        
        detected = (wind_speed >= threshold["wind_speed"] or 
                   pressure < threshold["pressure"])
        
        if detected:
            # 确定台风等级
            if wind_speed >= 51:
                severity = 4  # 超强台风
                level_name = "超强台风"
            elif wind_speed >= 41.5:
                severity = 4  # 强台风
                level_name = "强台风"
            elif wind_speed >= 32.7:
                severity = 3  # 台风
                level_name = "台风"
            else:
                severity = 2  # 热带风暴
                level_name = "热带风暴"
            
            return {
                "detected": True,
                "type": "typhoon",
                "type_name": "台风",
                "severity": severity,
                "level": level_name,
                "wind_speed": wind_speed,
                "pressure": pressure,
                "description": f"检测到{level_name}，风速{wind_speed} m/s，气压{pressure} hPa",
                "suggestions": [
                    "立即停止户外活动",
                    "关闭门窗，加固设施",
                    "储备应急物资",
                    "关注官方预警信息",
                    "必要时转移到安全地带"
                ]
            }
        
        return {"detected": False, "type": "typhoon"}
    
    def detect_heavy_rain(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测暴雨
        
        参数:
            weather_data: 天气数据
            
        返回:
            检测结果
        """
        precipitation = weather_data.get("precipitation", 0)
        threshold = self.thresholds["heavy_rain"]["precipitation"]
        
        detected = precipitation >= threshold
        
        if detected:
            # 确定暴雨等级
            if precipitation >= 100:
                severity = 4  # 特大暴雨
                level_name = "特大暴雨"
            elif precipitation >= 50:
                severity = 3  # 大暴雨
                level_name = "大暴雨"
            elif precipitation >= 25:
                severity = 2  # 暴雨
                level_name = "暴雨"
            else:
                severity = 1  # 大雨
                level_name = "大雨"
            
            return {
                "detected": True,
                "type": "heavy_rain",
                "type_name": "暴雨",
                "severity": severity,
                "level": level_name,
                "precipitation": precipitation,
                "description": f"检测到{level_name}，降水量{precipitation} mm/h",
                "suggestions": [
                    "避免外出，远离低洼地区",
                    "注意防范城市内涝",
                    "检查排水系统",
                    "准备应急照明设备",
                    "关注交通信息"
                ]
            }
        
        return {"detected": False, "type": "heavy_rain"}
    
    def detect_high_temperature(self, weather_data: Dict[str, Any],
                               forecast_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        检测高温
        
        参数:
            weather_data: 当前天气数据
            forecast_data: 预测数据
            
        返回:
            检测结果
        """
        temperature = weather_data.get("temperature", 25)
        threshold = self.thresholds["high_temperature"]["temperature"]
        
        detected = temperature >= threshold
        
        if detected:
            # 确定高温等级
            if temperature >= 40:
                severity = 4  # 特别严重
                level_name = "极端高温"
            elif temperature >= 38:
                severity = 3  # 严重
                level_name = "严重高温"
            else:
                severity = 2  # 一般
                level_name = "高温"
            
            return {
                "detected": True,
                "type": "high_temperature",
                "type_name": "高温",
                "severity": severity,
                "level": level_name,
                "temperature": temperature,
                "description": f"检测到{level_name}天气，温度{temperature}°C",
                "suggestions": [
                    "避免在高温时段外出",
                    "及时补充水分",
                    "注意防暑降温",
                    "关注老人和儿童健康",
                    "减少剧烈运动"
                ]
            }
        
        return {"detected": False, "type": "high_temperature"}
    
    def detect_low_temperature(self, weather_data: Dict[str, Any],
                              forecast_data: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        检测低温
        
        参数:
            weather_data: 当前天气数据
            forecast_data: 预测数据
            
        返回:
            检测结果
        """
        temperature = weather_data.get("temperature", 25)
        threshold = self.thresholds["low_temperature"]["temperature"]
        
        detected = temperature <= threshold
        
        if detected:
            # 确定低温等级
            if temperature <= -20:
                severity = 4
                level_name = "极端低温"
            elif temperature <= -15:
                severity = 3
                level_name = "严重低温"
            else:
                severity = 2
                level_name = "低温"
            
            return {
                "detected": True,
                "type": "low_temperature",
                "type_name": "低温",
                "severity": severity,
                "level": level_name,
                "temperature": temperature,
                "description": f"检测到{level_name}天气，温度{temperature}°C",
                "suggestions": [
                    "注意保暖，防止冻伤",
                    "检查供暖设施",
                    "保护水管防冻",
                    "减少户外活动时间",
                    "关注弱势群体安全"
                ]
            }
        
        return {"detected": False, "type": "low_temperature"}
    
    def detect_heavy_snow(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        检测大雪
        
        参数:
            weather_data: 天气数据
            
        返回:
            检测结果
        """
        snowfall = weather_data.get("snowfall", 0)
        threshold = self.thresholds["heavy_snow"]["snowfall"]
        
        detected = snowfall >= threshold
        
        if detected:
            # 确定大雪等级
            if snowfall >= 30:
                severity = 4
                level_name = "特大暴雪"
            elif snowfall >= 20:
                severity = 3
                level_name = "大暴雪"
            elif snowfall >= 10:
                severity = 2
                level_name = "暴雪"
            else:
                severity = 1
                level_name = "大雪"
            
            return {
                "detected": True,
                "type": "heavy_snow",
                "type_name": "大雪",
                "severity": severity,
                "level": level_name,
                "snowfall": snowfall,
                "description": f"检测到{level_name}，降雪量{snowfall} mm",
                "suggestions": [
                    "减少外出，注意交通安全",
                    "清除积雪，防止道路结冰",
                    "注意防滑防冻",
                    "检查供电供暖设施",
                    "储备生活必需品"
                ]
            }
        
        return {"detected": False, "type": "heavy_snow"}
    
    def _detect_with_api(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        使用Gemini API进行智能检测
        
        参数:
            weather_data: 天气数据
            
        返回:
            API检测结果
        """
        return api_client.detect_extreme_weather(weather_data)


if __name__ == "__main__":
    # 测试代码
    detector = ExtremeWeatherDetector()
    
    # 测试高温检测
    test_data_hot = {
        "temperature": 39,
        "humidity": 65,
        "pressure": 1010,
        "wind_speed": 3
    }
    
    result = detector.detect_all_extremes(test_data_hot)
    print(f"✓ 极端天气检测完成")
    print(f"  发现极端天气: {result['has_extreme']}")
    print(f"  检测数量: {len(result['detections'])}")
    if result['detections']:
        print(f"  第一个检测: {result['detections'][0]}")
