"""
数据采集模块
用于采集和生成气象数据
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any
import config
from utils.helpers import save_json, log_message


class WeatherDataCollector:
    """天气数据采集器"""
    
    def __init__(self):
        """初始化数据采集器"""
        self.data_sources = config.DATA_SOURCES
        log_message("数据采集器初始化完成")
    
    def collect_real_data(self, region: str, start_time: datetime, 
                         end_time: datetime) -> List[Dict[str, Any]]:
        """
        采集真实气象数据
        
        注意：这是一个示例实现，实际应用中需要接入真实的气象数据API
        
        参数:
            region: 区域名称
            start_time: 开始时间
            end_time: 结束时间
            
        返回:
            气象数据列表
        """
        log_message(f"开始采集 {region} 的气象数据")
        
        # 这里应该调用真实的气象数据API
        # 例如：中国气象局API、OpenWeatherMap等
        
        # 示例：返回模拟数据
        data = self.generate_simulated_data(region, start_time, end_time)
        
        log_message(f"采集完成，共 {len(data)} 条数据")
        return data
    
    def generate_simulated_data(self, region: str, start_time: datetime, 
                               end_time: datetime) -> List[Dict[str, Any]]:
        """
        生成模拟的气象数据（用于演示和测试）
        
        参数:
            region: 区域名称
            start_time: 开始时间
            end_time: 结束时间
            
        返回:
            模拟的气象数据列表
        """
        data_list = []
        current_time = start_time
        
        # 获取区域信息
        # 获取区域信息，如果不存在则使用第一个可用区域
        if region not in config.REGIONS:
            region = list(config.REGIONS.keys())[0] if config.REGIONS else "xuancheng"
        region_info = config.REGIONS.get(region, {"name": region, "lat": 30.9, "lon": 118.8})
        
        # 基础温度（根据季节调整）
        month = start_time.month
        if month in [12, 1, 2]:  # 冬季
            base_temp = 0
        elif month in [3, 4, 5]:  # 春季
            base_temp = 15
        elif month in [6, 7, 8]:  # 夏季
            base_temp = 28
        else:  # 秋季
            base_temp = 18
        
        while current_time <= end_time:
            # 生成随机波动
            temp_variation = np.random.randn() * 3
            
            # 生成一条数据记录
            data_point = {
                "timestamp": current_time.isoformat(),
                "region": region,
                "latitude": region_info["lat"],
                "longitude": region_info["lon"],
                "temperature": round(base_temp + temp_variation, 1),
                "humidity": round(np.random.uniform(40, 90), 1),
                "pressure": round(np.random.uniform(990, 1020), 1),
                "wind_speed": round(np.random.uniform(0, 15), 1),
                "wind_direction": np.random.choice(["北", "东北", "东", "东南", "南", "西南", "西", "西北"]),
                "precipitation": round(max(0, np.random.exponential(2)), 1),
                "cloud_cover": round(np.random.uniform(0, 100), 1),
                "visibility": round(np.random.uniform(5, 20), 1)
            }
            
            data_list.append(data_point)
            
            # 增加时间步长（1小时）
            current_time += timedelta(hours=1)
        
        return data_list
    
    def collect_satellite_data(self, region: str, timestamp: datetime) -> Dict[str, Any]:
        """
        采集卫星云图数据
        
        参数:
            region: 区域
            timestamp: 时间戳
            
        返回:
            卫星数据字典
        """
        # 模拟卫星云图数据（实际应该是图像数据）
        cloud_image = np.random.rand(64, 64, 3) * 255
        
        return {
            "timestamp": timestamp.isoformat(),
            "region": region,
            "type": "satellite",
            "image_shape": cloud_image.shape,
            "image_data": cloud_image.tolist()  # 转为列表以便JSON序列化
        }
    
    def collect_radar_data(self, region: str, timestamp: datetime) -> Dict[str, Any]:
        """
        采集雷达数据
        
        参数:
            region: 区域
            timestamp: 时间戳
            
        返回:
            雷达数据字典
        """
        # 模拟雷达回波数据
        radar_echo = np.random.rand(64, 64) * 100
        
        return {
            "timestamp": timestamp.isoformat(),
            "region": region,
            "type": "radar",
            "echo_intensity": radar_echo.tolist(),
            "max_intensity": float(np.max(radar_echo)),
            "mean_intensity": float(np.mean(radar_echo))
        }
    
    def save_collected_data(self, data: List[Dict[str, Any]], filename: str):
        """
        保存采集的数据
        
        参数:
            data: 数据列表
            filename: 文件名
        """
        filepath = f"{config.RAW_DATA_DIR}/{filename}"
        save_json(data, filepath)
        log_message(f"数据已保存到 {filepath}")
    
    def get_sample_data(self, num_hours: int = 240) -> List[Dict[str, Any]]:
        """
        获取示例数据（10天的小时数据）
        
        参数:
            num_hours: 数据小时数
            
        返回:
            示例数据列表
        """
        end_time = datetime.now()
        start_time = end_time - timedelta(hours=num_hours)
        
        # 使用第一个可用区域或默认值
        default_region = list(config.REGIONS.keys())[0] if config.REGIONS else "xuancheng"
        return self.generate_simulated_data(default_region, start_time, end_time)


if __name__ == "__main__":
    # 测试代码
    collector = WeatherDataCollector()
    
    # 生成示例数据
    sample_data = collector.get_sample_data(240)  # 10天数据
    
    # 保存数据
    collector.save_collected_data(sample_data, "sample_weather_data.json")
    
    print(f"✓ 生成了 {len(sample_data)} 条示例数据")
    print(f"✓ 数据时间范围: {sample_data[0]['timestamp']} 到 {sample_data[-1]['timestamp']}")
