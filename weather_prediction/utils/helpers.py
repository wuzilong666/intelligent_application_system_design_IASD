"""
辅助函数模块
提供各种工具函数
"""

import os
import json
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Any, Tuple
import config


def create_directories():
    """创建必要的目录结构"""
    directories = [
        config.DATA_DIR,
        config.RAW_DATA_DIR,
        config.PROCESSED_DATA_DIR,
        config.SAMPLE_DATA_DIR,
        config.MODEL_DIR,
        "logs",
        "outputs",
        "outputs/plots",
        "outputs/animations",
        "outputs/alerts"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
    
    print("✓ 目录结构创建完成")


def save_json(data: Any, filepath: str):
    """
    保存数据为JSON文件
    
    参数:
        data: 要保存的数据
        filepath: 文件路径
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"✓ 数据已保存到: {filepath}")


def load_json(filepath: str) -> Any:
    """
    从JSON文件加载数据
    
    参数:
        filepath: 文件路径
        
    返回:
        加载的数据
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_time_range(horizon: str) -> List[datetime]:
    """
    获取预测时间范围
    
    参数:
        horizon: 预测范围（支持 1h/3h/6h/1day/2day/3day/1week 及兼容原 short/medium/long）
        
    返回:
        时间点列表
    """
    now = datetime.now()
    time_points = []

    # 兼容旧键
    if horizon == "short_term":
        hours = config.PREDICTION_HORIZONS.get("short_term", 6)
        for i in range(hours + 1):
            time_points.append(now + timedelta(hours=i))
    elif horizon == "medium_term":
        days = config.PREDICTION_HORIZONS.get("medium_term", 3)
        for i in range(days + 1):
            time_points.append(now + timedelta(days=i))
    elif horizon == "long_term":
        days = config.PREDICTION_HORIZONS.get("long_term", 7)
        for i in range(days + 1):
            time_points.append(now + timedelta(days=i))
    else:
        # 新键：小时/天/周
        val = config.PREDICTION_HORIZONS.get(horizon)
        if val is None:
            return time_points

        if horizon.endswith("h"):
            for i in range(val + 1):
                time_points.append(now + timedelta(hours=i))
        elif horizon.endswith("day"):
            for i in range(val + 1):
                time_points.append(now + timedelta(days=i))
        elif horizon.endswith("week"):
            for i in range(val + 1):
                time_points.append(now + timedelta(days=val * i))

    return time_points


def normalize_data(data: np.ndarray) -> Tuple[np.ndarray, Dict[str, float]]:
    """
    数据标准化
    
    参数:
        data: 原始数据
        
    返回:
        标准化后的数据和标准化参数
    """
    mean = np.mean(data)
    std = np.std(data)
    
    normalized = (data - mean) / (std + 1e-8)
    
    params = {
        "mean": float(mean),
        "std": float(std)
    }
    
    return normalized, params


def denormalize_data(data: np.ndarray, params: Dict[str, float]) -> np.ndarray:
    """
    反标准化数据
    
    参数:
        data: 标准化的数据
        params: 标准化参数
        
    返回:
        原始尺度的数据
    """
    return data * params["std"] + params["mean"]


def calculate_confidence_interval(predictions: np.ndarray, 
                                 confidence_level: float = 0.95) -> Tuple[np.ndarray, np.ndarray]:
    """
    计算置信区间
    
    参数:
        predictions: 预测值数组（多次采样）
        confidence_level: 置信水平
        
    返回:
        下界和上界
    """
    alpha = 1 - confidence_level
    lower_percentile = (alpha / 2) * 100
    upper_percentile = (1 - alpha / 2) * 100
    
    lower_bound = np.percentile(predictions, lower_percentile, axis=0)
    upper_bound = np.percentile(predictions, upper_percentile, axis=0)
    
    return lower_bound, upper_bound


def format_weather_report(prediction: Dict[str, Any]) -> str:
    """
    格式化天气预报文本
    
    参数:
        prediction: 预测结果字典
        
    返回:
        格式化的文本
    """
    report = "=" * 50 + "\n"
    report += "天气预报\n"
    report += "=" * 50 + "\n\n"
    
    if "temperature" in prediction:
        report += f"温度: {prediction['temperature']}°C\n"
    
    if "precipitation" in prediction:
        report += f"降水概率: {prediction['precipitation']}%\n"
    
    if "wind_speed" in prediction:
        report += f"风速: {prediction['wind_speed']} m/s\n"
    
    if "description" in prediction:
        report += f"\n{prediction['description']}\n"
    
    report += "\n" + "=" * 50 + "\n"
    
    return report


def get_alert_level_name(level: int) -> str:
    """
    获取预警级别名称
    
    参数:
        level: 预警级别数值
        
    返回:
        预警级别名称和颜色
    """
    level_names = {
        1: "蓝色预警（一般）",
        2: "黄色预警（较重）",
        3: "橙色预警（严重）",
        4: "红色预警（特别严重）"
    }
    
    return level_names.get(level, "未知级别")


def print_progress_bar(iteration: int, total: int, prefix: str = '', 
                       suffix: str = '', length: int = 50, fill: str = '█'):
    """
    打印进度条
    
    参数:
        iteration: 当前迭代
        total: 总迭代次数
        prefix: 前缀文本
        suffix: 后缀文本
        length: 进度条长度
        fill: 填充字符
    """
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    
    if iteration == total:
        print()


def log_message(message: str, level: str = "INFO"):
    """
    记录日志消息
    
    参数:
        message: 日志消息
        level: 日志级别
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}"
    
    # 打印到控制台
    print(log_entry)
    
    # 保存到文件
    log_file = config.LOGGING_CONFIG.get("file", "logs/system.log")
    os.makedirs(os.path.dirname(log_file), exist_ok=True)
    
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(log_entry + "\n")
