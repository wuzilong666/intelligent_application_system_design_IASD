"""
数据处理模块
用于处理和预处理气象数据
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from datetime import datetime
import config
from utils.helpers import normalize_data, save_json, load_json, log_message


class WeatherDataProcessor:
    """天气数据处理器"""
    
    def __init__(self):
        """初始化数据处理器"""
        self.normalization_params = {}
        log_message("数据处理器初始化完成")
    
    def preprocess_data(self, raw_data: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        预处理原始气象数据
        
        参数:
            raw_data: 原始数据列表
            
        返回:
            处理后的数据字典
        """
        log_message(f"开始预处理 {len(raw_data)} 条数据")
        
        # 提取特征
        features = self._extract_features(raw_data)
        
        # 标准化
        normalized_features = self._normalize_features(features)
        
        # 创建时间序列
        sequences = self._create_sequences(normalized_features)
        
        log_message("数据预处理完成")
        
        return {
            "sequences": sequences,
            "features": normalized_features,
            "raw_data": raw_data
        }
    
    def _extract_features(self, data: List[Dict[str, Any]]) -> Dict[str, np.ndarray]:
        """
        从原始数据中提取特征
        
        参数:
            data: 原始数据列表
            
        返回:
            特征字典
        """
        # 提取数值特征
        temperature = np.array([d["temperature"] for d in data])
        humidity = np.array([d["humidity"] for d in data])
        pressure = np.array([d["pressure"] for d in data])
        wind_speed = np.array([d["wind_speed"] for d in data])
        precipitation = np.array([d["precipitation"] for d in data])
        cloud_cover = np.array([d["cloud_cover"] for d in data])
        visibility = np.array([d["visibility"] for d in data])
        
        # 时间特征（小时、星期几等）
        timestamps = [datetime.fromisoformat(d["timestamp"]) for d in data]
        hour_of_day = np.array([t.hour for t in timestamps])
        day_of_week = np.array([t.weekday() for t in timestamps])
        month = np.array([t.month for t in timestamps])
        
        features = {
            "temperature": temperature,
            "humidity": humidity,
            "pressure": pressure,
            "wind_speed": wind_speed,
            "precipitation": precipitation,
            "cloud_cover": cloud_cover,
            "visibility": visibility,
            "hour_of_day": hour_of_day,
            "day_of_week": day_of_week,
            "month": month
        }
        
        return features
    
    def _normalize_features(self, features: Dict[str, np.ndarray]) -> Dict[str, np.ndarray]:
        """
        标准化特征
        
        参数:
            features: 原始特征字典
            
        返回:
            标准化后的特征字典
        """
        normalized = {}
        
        for key, values in features.items():
            if key in ["hour_of_day", "day_of_week", "month"]:
                # 时间特征使用周期性编码
                if key == "hour_of_day":
                    max_val = 24
                elif key == "day_of_week":
                    max_val = 7
                else:  # month
                    max_val = 12
                
                # Sin/Cos编码
                normalized[f"{key}_sin"] = np.sin(2 * np.pi * values / max_val)
                normalized[f"{key}_cos"] = np.cos(2 * np.pi * values / max_val)
            else:
                # 数值特征使用标准化
                norm_values, params = normalize_data(values)
                normalized[key] = norm_values
                self.normalization_params[key] = params
        
        return normalized
    
    def _create_sequences(self, features: Dict[str, np.ndarray], 
                         sequence_length: int = 10) -> np.ndarray:
        """
        创建时间序列数据
        
        参数:
            features: 特征字典
            sequence_length: 序列长度
            
        返回:
            序列数组 (样本数, 时间步, 特征数)
        """
        # 合并所有特征
        feature_list = []
        for key in sorted(features.keys()):
            feature_list.append(features[key].reshape(-1, 1))
        
        combined_features = np.concatenate(feature_list, axis=1)
        
        # 创建滑动窗口序列
        sequences = []
        for i in range(len(combined_features) - sequence_length):
            seq = combined_features[i:i + sequence_length]
            sequences.append(seq)
        
        return np.array(sequences)
    
    def create_image_data(self, data: List[Dict[str, Any]], 
                         image_size: Tuple[int, int] = (64, 64)) -> np.ndarray:
        """
        创建图像格式的气象数据（用于卷积神经网络）
        
        参数:
            data: 气象数据
            image_size: 图像尺寸
            
        返回:
            图像数据数组 (样本数, 高度, 宽度, 通道数)
        """
        images = []
        
        for d in data:
            # 创建3通道图像（温度、湿度、气压）
            temp_channel = np.full(image_size, d["temperature"] / 40.0)
            humidity_channel = np.full(image_size, d["humidity"] / 100.0)
            pressure_channel = np.full(image_size, (d["pressure"] - 980) / 40.0)
            
            # 添加随机纹理以模拟空间变化
            temp_channel += np.random.randn(*image_size) * 0.1
            humidity_channel += np.random.randn(*image_size) * 0.1
            pressure_channel += np.random.randn(*image_size) * 0.1
            
            # 合并通道
            image = np.stack([temp_channel, humidity_channel, pressure_channel], axis=-1)
            images.append(image)
        
        return np.array(images)
    
    def create_spatiotemporal_data(self, data: List[Dict[str, Any]], 
                                   sequence_length: int = 10,
                                   image_size: Tuple[int, int] = (64, 64)) -> np.ndarray:
        """
        创建时空数据（用于ConvLSTM和3D CNN）
        
        参数:
            data: 气象数据
            sequence_length: 时间序列长度
            image_size: 空间尺寸
            
        返回:
            时空数据 (样本数, 时间步, 高度, 宽度, 通道数)
        """
        # 创建图像序列
        images = self.create_image_data(data, image_size)
        
        # 创建时间序列
        sequences = []
        for i in range(len(images) - sequence_length):
            seq = images[i:i + sequence_length]
            sequences.append(seq)
        
        return np.array(sequences)
    
    def save_processed_data(self, processed_data: Dict[str, Any], filename: str):
        """
        保存处理后的数据
        
        参数:
            processed_data: 处理后的数据
            filename: 文件名
        """
        # 将numpy数组转换为列表以便JSON序列化
        serializable_data = {}
        for key, value in processed_data.items():
            if isinstance(value, np.ndarray):
                serializable_data[key] = {
                    "data": value.tolist(),
                    "shape": value.shape,
                    "dtype": str(value.dtype)
                }
            else:
                serializable_data[key] = value
        
        filepath = f"{config.PROCESSED_DATA_DIR}/{filename}"
        save_json(serializable_data, filepath)
        log_message(f"处理后的数据已保存到 {filepath}")


if __name__ == "__main__":
    # 测试代码
    from src.data_collector import WeatherDataCollector
    
    # 采集数据
    collector = WeatherDataCollector()
    raw_data = collector.get_sample_data(240)
    
    # 处理数据
    processor = WeatherDataProcessor()
    processed = processor.preprocess_data(raw_data)
    
    print(f"✓ 处理完成")
    print(f"  序列形状: {processed['sequences'].shape}")
    
    # 创建时空数据
    spatiotemporal = processor.create_spatiotemporal_data(raw_data)
    print(f"  时空数据形状: {spatiotemporal.shape}")
