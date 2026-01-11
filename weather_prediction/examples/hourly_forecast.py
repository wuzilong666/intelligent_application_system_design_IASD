"""
小时级天气预测示例
演示如何进行短期（小时级）的详细预测
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from src.data_collector import WeatherDataCollector
from src.predictor import WeatherPredictor
from src.visualizer import WeatherVisualizer
from utils.helpers import create_directories

def main():
    """小时级预测示例"""
    print("="*60)
    print("⏰ 小时级天气预测示例")
    print("="*60)
    print()
    
    create_directories()
    
    # 采集数据
    print("采集历史数据...")
    collector = WeatherDataCollector()
    historical_data = collector.get_sample_data(72)  # 3天数据
    current_data = historical_data[-1]
    print(f"✓ 已采集 {len(historical_data)} 条数据")
    print()
    
    # 创建预测器
    print("初始化预测器...")
    predictor = WeatherPredictor(use_model="api")
    print("✓ 预测器就绪")
    print()
    
    # 执行预测
    print("正在预测未来6小时天气...")
    print("-" * 60)
    result = predictor.predict_short_term(current_data, historical_data)
    
    if result['success']:
        predictions = result['predictions']
        
        # 创建表格显示
        print(f"\n{'时间':<20} {'温度':<10} {'湿度':<10} {'风速':<10} {'降水':<10} {'天气':<10}")
        print("-" * 70)
        
        for pred in predictions:
            time_str = datetime.fromisoformat(pred['timestamp']).strftime('%m-%d %H:%M')
            print(f"{time_str:<20} {pred['temperature']:>6.1f}°C  {pred['humidity']:>6.1f}%  "
                  f"{pred['wind_speed']:>6.1f}m/s {pred['precipitation_probability']:>6.1f}%  "
                  f"{pred['weather_condition']:<10}")
        
        print()
        
        # 生成可视化
        print("生成可视化图表...")
        visualizer = WeatherVisualizer()
        
        # 温度趋势图
        temp_plot = visualizer.plot_temperature_forecast(predictions)
        print(f"✓ 温度趋势图已保存: {temp_plot}")
        
        # 多参数图
        multi_plot = visualizer.plot_multi_parameter_forecast(predictions)
        print(f"✓ 多参数图已保存: {multi_plot}")
        
        # 不确定性信息
        if 'uncertainty' in result:
            print(f"\n预测不确定性:")
            print(f"  置信水平: {result['uncertainty']['confidence_level']*100}%")
            print(f"  温度不确定性: ±{result['uncertainty']['temperature_uncertainty']}°C")
        
    else:
        print(f"❌ 预测失败: {result.get('error', '未知错误')}")
    
    print("\n" + "="*60)
    print("小时级预测完成！")
    print("="*60)


if __name__ == "__main__":
    main()
