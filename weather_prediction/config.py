"""
配置文件 - 天气预测系统的所有配置参数
Configuration File - All configuration parameters for the weather prediction system
"""

# ============================================
# API 配置 / API Configuration
# ============================================

# Gemini API 配置
API_URL = "https://api2.qiandao.mom/v1"
API_KEY = "sk-lClbTp1VbcVNfL76tQPdUQnmuSa9J1vMyovZKYI6JbLI7GfY"
API_MODEL = "gemini-3-pro-preview-h"  # 使用的模型名称

# ============================================
# 数据配置 / Data Configuration
# ============================================

# 数据路径
DATA_DIR = "data"
RAW_DATA_DIR = "data/raw"
PROCESSED_DATA_DIR = "data/processed"
SAMPLE_DATA_DIR = "data/sample"

# 数据源配置
DATA_SOURCES = {
    "satellite": True,      # 卫星云图
    "ground": True,         # 地面观测
    "radar": True,          # 雷达数据
    "simulation": True      # 模拟数据（用于演示）
}

# ============================================
# 模型配置 / Model Configuration
# ============================================

# 模型保存路径
MODEL_DIR = "models/saved_models"

# ConvLSTM 模型参数
CONVLSTM_CONFIG = {
    "input_shape": (10, 64, 64, 3),  # (时间步, 高度, 宽度, 通道数)
    "filters": [64, 64, 64],          # 每层的卷积核数量
    "kernel_size": (3, 3),            # 卷积核大小
    "dropout": 0.2,                   # Dropout比例
    "learning_rate": 0.001            # 学习率
}

# 3D CNN 模型参数
CNN3D_CONFIG = {
    "input_shape": (10, 64, 64, 3),   # (时间步, 高度, 宽度, 通道数)
    "filters": [32, 64, 128],         # 每层的卷积核数量
    "kernel_size": (3, 3, 3),         # 3D卷积核大小
    "dropout": 0.3,                   # Dropout比例
    "learning_rate": 0.001            # 学习率
}

# ============================================
# 预测配置 / Prediction Configuration
# ============================================

# 预测时间范围
PREDICTION_HORIZONS = {
    "1h": 1,              # 1小时预测
    "6h": 6,              # 6小时预测
    "1day": 1,            # 1天预测
    "3day": 3,            # 3天预测
    "1week": 7,           # 1周预测
    # 保留原有配置以兼容
    "short_term": 6,
    "medium_term": 3,
    "long_term": 7
}

# 预测区域配置
REGIONS = {
    "xuancheng": {"lat": 30.9, "lon": 118.8, "name": "宣城", "name_en": "Xuancheng", "level": "city"},
    "xuanzhou": {"lat": 30.9, "lon": 118.75, "name": "宣城宣州区", "name_en": "Xuanzhou District", "level": "district"}
}

# ============================================
# 极端天气配置 / Extreme Weather Configuration
# ============================================

# 极端天气阈值
EXTREME_WEATHER_THRESHOLDS = {
    "typhoon": {
        "wind_speed": 32.7,        # 台风：风速 >= 32.7 m/s
        "pressure": 980            # 气压 < 980 hPa
    },
    "heavy_rain": {
        "precipitation": 50,       # 暴雨：降水量 >= 50 mm/h
        "duration": 3              # 持续时间 >= 3小时
    },
    "high_temperature": {
        "temperature": 37,         # 高温：温度 >= 37°C
        "duration": 3              # 持续时间 >= 3天
    },
    "low_temperature": {
        "temperature": -10,        # 低温：温度 <= -10°C
        "duration": 2              # 持续时间 >= 2天
    },
    "heavy_snow": {
        "snowfall": 10,            # 大雪：降雪量 >= 10 mm
        "duration": 12             # 持续时间 >= 12小时
    }
}

# ============================================
# 可视化配置 / Visualization Configuration
# ============================================

# 图表配置
PLOT_CONFIG = {
    "figure_size": (12, 8),
    "dpi": 100,
    "style": "whitegrid",
    "color_map": "coolwarm"
}

# 动画配置
ANIMATION_CONFIG = {
    "fps": 10,                    # 帧率
    "duration": 5,                # 持续时间（秒）
    "format": "mp4"               # 输出格式
}

# ============================================
# 预警系统配置 / Alert System Configuration
# ============================================

# 预警级别
ALERT_LEVELS = {
    "blue": 1,      # 蓝色预警：一般
    "yellow": 2,    # 黄色预警：较重
    "orange": 3,    # 橙色预警：严重
    "red": 4        # 红色预警：特别严重
}

# 预警发布配置
ALERT_CONFIG = {
    "enable_email": False,        # 是否启用邮件预警
    "enable_sms": False,          # 是否启用短信预警
    "enable_console": True,       # 是否启用控制台输出
    "enable_file": True           # 是否保存到文件
}

# ============================================
# 系统配置 / System Configuration
# ============================================

# 日志配置
LOGGING_CONFIG = {
    "level": "INFO",              # 日志级别：DEBUG, INFO, WARNING, ERROR
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "file": "logs/weather_system.log"
}

# 性能配置
PERFORMANCE_CONFIG = {
    "batch_size": 32,             # 批处理大小
    "num_workers": 4,             # 数据加载线程数
    "use_gpu": True,              # 是否使用GPU
    "mixed_precision": False      # 是否使用混合精度训练
}

# 不确定性量化配置
UNCERTAINTY_CONFIG = {
    "method": "monte_carlo",      # 方法：monte_carlo, ensemble, bayesian
    "num_samples": 100,           # 采样次数
    "confidence_level": 0.95      # 置信水平
}
