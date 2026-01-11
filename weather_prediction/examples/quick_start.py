"""
快速开始示例
演示如何使用天气预测系统的基本功能
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import WeatherDataCollector
from src.predictor import WeatherPredictor
from utils.helpers import create_directories

def main():
    """快速开始示例"""
    print("="*60)
    print("🌤️  天气预测系统 - 快速开始示例")
    print("="*60)
    print()
    
    # 创建必要的目录
    create_directories()
    
    # 1. 采集数据
    print("步骤 1: 采集气象数据")
    print("-" * 40)
    collector = WeatherDataCollector()
    historical_data = collector.get_sample_data(48)  # 获取2天的数据
    current_data = historical_data[-1]
    
    print(f"✓ 已采集 {len(historical_data)} 条历史数据")
    print(f"✓ 当前温度: {current_data['temperature']}°C")
    print(f"✓ 当前湿度: {current_data['humidity']}%")
    print()
    
    # 2. 创建预测器（使用Gemini API）
    print("步骤 2: 使用Gemini API进行预测")
    print("-" * 40)
    predictor = WeatherPredictor(use_model="api")
    
    # 3. 短期预测
    print("正在预测未来6小时的天气...")
    result = predictor.predict_short_term(current_data, historical_data)
    
    if result['success']:
        print("✓ 预测成功！\n")
        
        # 显示预测结果
        predictions = result['predictions']
        print("未来6小时天气预测:")
        print("-" * 40)
        
        for i, pred in enumerate(predictions[:6], 1):
            print(f"{i}小时后:")
            print(f"  温度: {pred['temperature']}°C ({pred['temperature_min']}°C ~ {pred['temperature_max']}°C)")
            print(f"  湿度: {pred['humidity']}%")
            print(f"  风速: {pred['wind_speed']} m/s")
            print(f"  降水概率: {pred['precipitation_probability']}%")
            print(f"  天气: {pred['weather_condition']}")
            print()
        
        # 显示AI分析（如果有）
        if 'analysis' in result:
            print("AI分析:")
            print("-" * 40)
            print(result['analysis'])
            print()
    else:
        print(f"❌ 预测失败: {result.get('error', '未知错误')}")
    
    print("="*60)
    print("快速开始示例完成！")
    print("="*60)
    print("\n提示:")
    print("  - 运行 main.py 体验完整功能")
    print("  - 查看 examples/ 目录了解更多示例")
    print("  - 阅读 TUTORIAL.md 获取详细教程")


if __name__ == "__main__":
    main()
