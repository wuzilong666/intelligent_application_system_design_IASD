"""
重新生成天气地图演变动画（使用现有数据）
"""

import json
import os
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.visualizer import WeatherVisualizer
import config

def find_latest_results():
    """查找最新的预测结果文件"""
    output_dir = Path("outputs")
    result_files = list(output_dir.glob("prediction_results_*.json"))
    
    if not result_files:
        print("❌ 未找到预测结果文件")
        return None
    
    # 按修改时间排序，获取最新的
    latest_file = sorted(result_files, key=lambda x: x.stat().st_mtime, reverse=True)
    return latest_file

def regenerate_animations(fps=2):
    """
    重新生成动画
    
    参数:
        fps: 帧率（越小越慢，建议1-5）
    """
    print("="*60)
    print("🎬 重新生成天气地图演变动画")
    print("="*60)
    print(f"\n帧率设置: {fps} fps (越小越慢)\n")
    
    # 查找结果文件
    result_files = find_latest_results()
    
    if not result_files:
        return
    
    # 临时修改配置中的fps
    original_fps = config.ANIMATION_CONFIG.get("fps", 10)
    config.ANIMATION_CONFIG["fps"] = fps
    
    # 创建可视化器
    visualizer = WeatherVisualizer()
    
    # 处理每个结果文件
    for result_file in result_files:
        print(f"\n处理文件: {result_file.name}")
        
        # 读取结果
        with open(result_file, 'r', encoding='utf-8') as f:
            results = json.load(f)
        
        region = results.get('region', 'unknown')
        region_info = results.get('region_info', {})
        predictions = results.get('predictions', {})
        
        print(f"   区域: {region_info.get('name_en', region)}")
        
        # 使用1day预测数据生成动画（24小时演变）
        if '1day' in predictions and predictions['1day'].get('predictions'):
            pred_data = predictions['1day']['predictions']
            print(f"   数据点数: {len(pred_data)}")
            
            # 生成新动画
            animation_path = visualizer.create_weather_map_evolution_animation(
                pred_data,
                region_info,
                save_path=f"outputs/animations/weather_map_evolution_{region}_slow_{fps}fps.gif"
            )
            
            print(f"   ✅ 动画已生成: {animation_path}")
        else:
            print(f"   ⚠️ 未找到1day预测数据，跳过")
    
    # 恢复原始fps
    config.ANIMATION_CONFIG["fps"] = original_fps
    
    print("\n" + "="*60)
    print("✅ 动画重新生成完成！")
    print("="*60)
    print(f"\n📁 动画保存位置: outputs/animations/")
    print(f"   文件名格式: weather_map_evolution_<region>_slow_{fps}fps.gif")

if __name__ == "__main__":
    # 可以修改这里的fps值来控制动画速度
    # fps=1: 非常慢，适合详细观察
    # fps=2: 慢速，推荐
    # fps=3-5: 适中速度
    regenerate_animations(fps=2)
