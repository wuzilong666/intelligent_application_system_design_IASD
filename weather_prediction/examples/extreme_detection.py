"""
极端天气检测示例
演示如何检测和预警极端天气事件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_collector import WeatherDataCollector
from src.extreme_weather import ExtremeWeatherDetector
from src.alert_system import WeatherAlertSystem
from src.visualizer import WeatherVisualizer
from utils.helpers import create_directories

def main():
    """极端天气检测示例"""
    print("="*60)
    print("⚠️  极端天气检测与预警示例")
    print("="*60)
    print()
    
    create_directories()
    
    # 创建检测器和预警系统
    detector = ExtremeWeatherDetector()
    alert_system = WeatherAlertSystem()
    visualizer = WeatherVisualizer()
    
    # 测试场景1: 正常天气
    print("场景 1: 正常天气检测")
    print("-" * 60)
    normal_weather = {
        "temperature": 22,
        "humidity": 65,
        "pressure": 1013,
        "wind_speed": 3,
        "precipitation": 0,
        "snowfall": 0
    }
    
    result1 = detector.detect_all_extremes(normal_weather)
    print(f"检测结果: {'发现极端天气' if result1['has_extreme'] else '正常天气'}")
    print()
    
    # 测试场景2: 高温天气
    print("场景 2: 高温天气检测")
    print("-" * 60)
    hot_weather = {
        "temperature": 39,
        "humidity": 55,
        "pressure": 1010,
        "wind_speed": 2,
        "precipitation": 0,
        "snowfall": 0
    }
    
    result2 = detector.detect_all_extremes(hot_weather)
    if result2['has_extreme']:
        print(f"⚠️ 检测到 {len(result2['detections'])} 个极端天气事件:")
        for d in result2['detections']:
            print(f"\n  类型: {d['type_name']}")
            print(f"  级别: {d['level']}")
            print(f"  严重程度: {d['severity']}/4")
            print(f"  描述: {d['description']}")
            print(f"  建议:")
            for suggestion in d['suggestions']:
                print(f"    • {suggestion}")
        
        # 发布预警
        print("\n发布预警...")
        alert = alert_system.issue_alert(result2)
        
        # 生成可视化
        print("\n生成极端天气分析图...")
        plot_path = visualizer.plot_extreme_weather_analysis(result2)
        if plot_path:
            print(f"✓ 分析图已保存: {plot_path}")
    
    print()
    
    # 测试场景3: 暴雨天气
    print("场景 3: 暴雨天气检测")
    print("-" * 60)
    rainy_weather = {
        "temperature": 25,
        "humidity": 95,
        "pressure": 995,
        "wind_speed": 15,
        "precipitation": 65,  # 大暴雨
        "snowfall": 0
    }
    
    result3 = detector.detect_all_extremes(rainy_weather)
    if result3['has_extreme']:
        print(f"⚠️ 检测到暴雨天气!")
        for d in result3['detections']:
            print(f"\n  {d['description']}")
            print(f"  严重程度: {d['severity']}/4")
        
        # 发布预警
        alert = alert_system.issue_alert(result3)
    
    print()
    
    # 测试场景4: 台风天气
    print("场景 4: 台风天气检测")
    print("-" * 60)
    typhoon_weather = {
        "temperature": 28,
        "humidity": 85,
        "pressure": 970,  # 低气压
        "wind_speed": 35,  # 强风
        "precipitation": 30,
        "snowfall": 0
    }
    
    result4 = detector.detect_all_extremes(typhoon_weather)
    if result4['has_extreme']:
        print(f"⚠️ 检测到台风天气!")
        for d in result4['detections']:
            print(f"\n  {d['description']}")
            print(f"  严重程度: {d['severity']}/4")
            print(f"\n  应对建议:")
            for suggestion in d['suggestions'][:3]:  # 显示前3条
                print(f"    • {suggestion}")
        
        # 发布预警
        alert = alert_system.issue_alert(result4)
        
        # 生成可视化
        plot_path = visualizer.plot_extreme_weather_analysis(result4)
        if plot_path:
            print(f"\n✓ 台风分析图已保存: {plot_path}")
    
    print()
    
    # 预警历史统计
    print("="*60)
    print("预警历史统计")
    print("="*60)
    report = alert_system.generate_alert_report()
    print(f"总预警次数: {report['total_alerts']}")
    if report['total_alerts'] > 0:
        print(f"\n预警级别分布:")
        for level, count in report['level_distribution'].items():
            print(f"  {level}: {count} 次")
        
        print(f"\n事件类型分布:")
        for event, count in report['event_distribution'].items():
            print(f"  {event}: {count} 次")
    
    print("\n" + "="*60)
    print("极端天气检测示例完成！")
    print("="*60)
    print("\n提示: 查看 outputs/alerts/ 目录获取所有预警记录")


if __name__ == "__main__":
    main()
