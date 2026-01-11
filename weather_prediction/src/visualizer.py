"""
可视化模块
用于生成天气预报的图表和动画
"""

import matplotlib
matplotlib.use('Agg')  # 使用非交互式后端
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import seaborn as sns
import numpy as np
from datetime import datetime
from typing import Dict, List, Any
import config
from utils.helpers import log_message
import os


class WeatherVisualizer:
    """天气可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        # Use English-friendly fonts to avoid missing glyphs in exports
        plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Arial']
        plt.rcParams['axes.unicode_minus'] = False

        # 设置样式
        sns.set_style(config.PLOT_CONFIG.get("style", "whitegrid"))

        self.output_dir = "outputs/plots"
        self.animation_dir = "outputs/animations"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.animation_dir, exist_ok=True)

        log_message("可视化器初始化完成")
    
    def plot_weather_map(self, predictions: List[Dict[str, Any]], 
                        region_info: Dict[str, Any],
                        save_path: str = None) -> str:
        """
        绘制天气地图（空间分布图）
        
        参数:
            predictions: 预测数据列表
            region_info: 区域信息
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制天气地图", "DEBUG")
        
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        fig.suptitle(f'Weather Map - {region_info.get("name_en", "Region")}', fontsize=16, fontweight='bold')
        
        # 获取最新预测数据
        latest = predictions[0] if predictions else {}
        
        # 1. Temperature distribution (simulated spatial)
        ax1 = axes[0, 0]
        lat_center = region_info.get('lat', 30.9)
        lon_center = region_info.get('lon', 118.8)
        
        # Create grid for spatial visualization
        x = np.linspace(lon_center - 0.5, lon_center + 0.5, 20)
        y = np.linspace(lat_center - 0.5, lat_center + 0.5, 20)
        X, Y = np.meshgrid(x, y)
        
        base_temp = latest.get('temperature', 20)
        Z_temp = base_temp + np.random.randn(20, 20) * 2
        
        im1 = ax1.contourf(X, Y, Z_temp, levels=15, cmap='RdYlBu_r')
        plt.colorbar(im1, ax=ax1, label='Temperature (°C)')
        ax1.set_xlabel('Longitude')
        ax1.set_ylabel('Latitude')
        ax1.set_title('Temperature Distribution', fontweight='bold')
        ax1.plot(lon_center, lat_center, 'k*', markersize=15, label='Center')
        ax1.legend()
        
        # 2. Humidity distribution
        ax2 = axes[0, 1]
        base_humidity = latest.get('humidity', 60)
        Z_humidity = base_humidity + np.random.randn(20, 20) * 10
        Z_humidity = np.clip(Z_humidity, 0, 100)
        
        im2 = ax2.contourf(X, Y, Z_humidity, levels=15, cmap='Blues')
        plt.colorbar(im2, ax=ax2, label='Humidity (%)')
        ax2.set_xlabel('Longitude')
        ax2.set_ylabel('Latitude')
        ax2.set_title('Humidity Distribution', fontweight='bold')
        ax2.plot(lon_center, lat_center, 'k*', markersize=15)
        
        # 3. Wind field (vector plot)
        ax3 = axes[1, 0]
        x_sparse = np.linspace(lon_center - 0.5, lon_center + 0.5, 10)
        y_sparse = np.linspace(lat_center - 0.5, lat_center + 0.5, 10)
        X_s, Y_s = np.meshgrid(x_sparse, y_sparse)
        
        U = np.random.randn(10, 10) * 3 + 2
        V = np.random.randn(10, 10) * 3
        speed = np.sqrt(U**2 + V**2)
        
        q = ax3.quiver(X_s, Y_s, U, V, speed, cmap='viridis', scale=50)
        plt.colorbar(q, ax=ax3, label='Wind Speed (m/s)')
        ax3.set_xlabel('Longitude')
        ax3.set_ylabel('Latitude')
        ax3.set_title('Wind Field', fontweight='bold')
        ax3.plot(lon_center, lat_center, 'r*', markersize=15)
        
        # 4. Precipitation probability
        ax4 = axes[1, 1]
        base_precip = latest.get('precipitation_probability', 30)
        Z_precip = base_precip + np.random.randn(20, 20) * 15
        Z_precip = np.clip(Z_precip, 0, 100)
        
        im4 = ax4.contourf(X, Y, Z_precip, levels=15, cmap='YlGnBu')
        plt.colorbar(im4, ax=ax4, label='Probability (%)')
        ax4.set_xlabel('Longitude')
        ax4.set_ylabel('Latitude')
        ax4.set_title('Precipitation Probability', fontweight='bold')
        ax4.plot(lon_center, lat_center, 'k*', markersize=15)
        
        # Save
        if save_path is None:
            save_path = f"{self.output_dir}/weather_map_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"天气地图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def plot_trend_chart(self, predictions: List[Dict[str, Any]], 
                        save_path: str = None) -> str:
        """
        绘制多参数趋势图
        
        参数:
            predictions: 预测数据列表
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制趋势图", "DEBUG")
        
        # 提取数据
        timestamps = [datetime.fromisoformat(p["timestamp"]) for p in predictions]
        temps = [p["temperature"] for p in predictions]
        humidity = [p["humidity"] for p in predictions]
        pressure = [p["pressure"] for p in predictions]
        wind_speed = [p["wind_speed"] for p in predictions]
        visibility = [p.get("visibility", 10) for p in predictions]
        aqi = [p.get("aqi", 50) for p in predictions]
        precipitation = [p["precipitation_probability"] for p in predictions]
        
        # 创建6个子图
        fig, axes = plt.subplots(3, 2, figsize=(16, 14))
        fig.suptitle('Weather Parameters Trend Chart', fontsize=18, fontweight='bold')
        
        # Temperature trend
        ax = axes[0, 0]
        ax.plot(timestamps, temps, 'o-', color='red', linewidth=2, label='Temperature')
        ax.fill_between(timestamps, 
                       [t - 2 for t in temps], 
                       [t + 2 for t in temps], 
                       alpha=0.2, color='red', label='Uncertainty')
        ax.set_ylabel('Temperature (°C)')
        ax.set_title('Temperature Trend', fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Humidity trend
        ax = axes[0, 1]
        ax.plot(timestamps, humidity, 'o-', color='blue', linewidth=2)
        ax.set_ylabel('Humidity (%)')
        ax.set_title('Humidity Trend', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Pressure trend
        ax = axes[1, 0]
        ax.plot(timestamps, pressure, 'o-', color='purple', linewidth=2)
        ax.set_ylabel('Pressure (hPa)')
        ax.set_title('Atmospheric Pressure Trend', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Wind speed trend
        ax = axes[1, 1]
        ax.plot(timestamps, wind_speed, 'o-', color='green', linewidth=2)
        ax.set_ylabel('Wind Speed (m/s)')
        ax.set_title('Wind Speed Trend', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Visibility trend
        ax = axes[2, 0]
        ax.plot(timestamps, visibility, 'o-', color='orange', linewidth=2)
        ax.set_ylabel('Visibility (km)')
        ax.set_title('Visibility Trend', fontweight='bold')
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        # Air Quality Index trend
        ax = axes[2, 1]
        colors = ['green' if a <= 50 else 'yellow' if a <= 100 else 'orange' if a <= 150 else 'red' for a in aqi]
        ax.bar(timestamps, aqi, color=colors, alpha=0.7)
        ax.axhline(y=50, color='green', linestyle='--', linewidth=1, label='Good')
        ax.axhline(y=100, color='yellow', linestyle='--', linewidth=1, label='Moderate')
        ax.axhline(y=150, color='orange', linestyle='--', linewidth=1, label='Unhealthy')
        ax.set_ylabel('AQI')
        ax.set_title('Air Quality Index Trend', fontweight='bold')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='x', rotation=45)
        
        # Save
        if save_path is None:
            save_path = f"{self.output_dir}/trend_chart_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"趋势图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def create_weather_map_evolution_animation(self, predictions: List[Dict[str, Any]],
                                               region_info: Dict[str, Any],
                                               save_path: str = None) -> str:
        """
        创建天气地图演变动画 - 展示温度场和降水场的时空演变
        
        参数:
            predictions: 预测数据列表
            region_info: 区域信息
            save_path: 保存路径
            
        返回:
            动画保存路径
        """
        log_message("创建天气地图演变动画", "DEBUG")
        
        region_name = region_info.get('name_en', 'Region')
        lat_center = region_info.get('lat', 30.9)
        lon_center = region_info.get('lon', 118.8)
        
        # 创建空间网格
        x = np.linspace(lon_center - 0.5, lon_center + 0.5, 30)
        y = np.linspace(lat_center - 0.5, lat_center + 0.5, 30)
        X, Y = np.meshgrid(x, y)
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))
        
        def animate(frame):
            ax1.clear()
            ax2.clear()
            
            # 获取当前帧的数据
            pred = predictions[frame]
            timestamp = datetime.fromisoformat(pred['timestamp'])
            
            # 温度场
            base_temp = pred['temperature']
            # 生成温度场的空间分布（模拟温度梯度）
            Z_temp = base_temp + np.random.randn(30, 30) * 1.5
            
            im1 = ax1.contourf(X, Y, Z_temp, levels=20, cmap='RdYlBu_r', alpha=0.8)
            ax1.contour(X, Y, Z_temp, levels=10, colors='black', linewidths=0.5, alpha=0.3)
            ax1.plot(lon_center, lat_center, 'k*', markersize=20, label='Center')
            ax1.set_xlabel('Longitude', fontsize=11)
            ax1.set_ylabel('Latitude', fontsize=11)
            ax1.set_title(f'Temperature Field (°C)\n{timestamp.strftime("%Y-%m-%d %H:%M")}', 
                         fontsize=13, fontweight='bold')
            ax1.legend(loc='upper right')
            
            # 添加色标
            cbar1 = plt.colorbar(im1, ax=ax1, label='Temperature (°C)')
            
            # 降水场
            base_precip = pred['precipitation_probability']
            # 生成降水场的空间分布
            Z_precip = base_precip + np.random.randn(30, 30) * 10
            Z_precip = np.clip(Z_precip, 0, 100)
            
            im2 = ax2.contourf(X, Y, Z_precip, levels=20, cmap='YlGnBu', alpha=0.8)
            ax2.contour(X, Y, Z_precip, levels=10, colors='darkblue', linewidths=0.5, alpha=0.3)
            ax2.plot(lon_center, lat_center, 'r*', markersize=20, label='Center')
            ax2.set_xlabel('Longitude', fontsize=11)
            ax2.set_ylabel('Latitude', fontsize=11)
            ax2.set_title(f'Precipitation Probability (%)\n{timestamp.strftime("%Y-%m-%d %H:%M")}', 
                         fontsize=13, fontweight='bold')
            ax2.legend(loc='upper right')
            
            # 添加色标
            cbar2 = plt.colorbar(im2, ax=ax2, label='Probability (%)')
            
            fig.suptitle(f'Weather Map Evolution - {region_name}', 
                        fontsize=16, fontweight='bold', y=0.98)
            
            plt.tight_layout(rect=[0, 0, 1, 0.96])
        
        # 创建动画
        fps = config.ANIMATION_CONFIG.get("fps", 5)  # 降低帧率使动画更流畅
        frames = min(len(predictions), 24)  # 最多24帧（24小时）
        
        anim = animation.FuncAnimation(fig, animate, frames=frames, 
                                       interval=1000/fps, repeat=True)
        
        # 保存动画
        if save_path is None:
            save_path = f"{self.animation_dir}/weather_map_evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.gif"
        
        try:
            anim.save(save_path, writer='pillow', fps=fps)
            log_message(f"天气地图演变动画已保存到 {save_path}", "DEBUG")
        except Exception as e:
            log_message(f"动画保存失败: {str(e)}，保存为静态图", "WARNING")
            save_path = save_path.replace('.gif', '.png')
            animate(len(predictions) - 1)
            plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        
        plt.close()
        return save_path
    
    def plot_temperature_forecast(self, predictions: List[Dict[str, Any]], 
                                 save_path: str = None) -> str:
        """
        绘制温度预测图
        
        参数:
            predictions: 预测数据列表
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制温度预测图", "DEBUG")
        
        # 提取数据
        timestamps = [datetime.fromisoformat(p["timestamp"]) for p in predictions]
        temps = [p["temperature"] for p in predictions]
        temp_max = [p.get("temperature_max", p["temperature"] + 2) for p in predictions]
        temp_min = [p.get("temperature_min", p["temperature"] - 2) for p in predictions]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=config.PLOT_CONFIG["figure_size"])
        
        # 绘制温度曲线
        ax.plot(timestamps, temps, 'o-', linewidth=2, label='Predicted Temperature', color='red')
        
        # 绘制置信区间
        ax.fill_between(timestamps, temp_min, temp_max, alpha=0.3, color='red', label='Confidence Range')
        
        # 设置标签
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('Temperature Forecast Trend', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 旋转x轴标签
        plt.xticks(rotation=45, ha='right')
        
        # 保存图表
        if save_path is None:
            save_path = f"{self.output_dir}/temperature_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"温度预测图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def plot_multi_parameter_forecast(self, predictions: List[Dict[str, Any]],
                                     save_path: str = None) -> str:
        """
        绘制多参数预测图
        
        参数:
            predictions: 预测数据列表
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制多参数预测图", "DEBUG")
        
        # 提取数据
        timestamps = [datetime.fromisoformat(p["timestamp"]) for p in predictions]
        temps = [p["temperature"] for p in predictions]
        humidity = [p["humidity"] for p in predictions]
        wind_speed = [p["wind_speed"] for p in predictions]
        precipitation = [p["precipitation_probability"] for p in predictions]
        
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('Comprehensive Weather Forecast', fontsize=16, fontweight='bold')
        
        # 温度
        axes[0, 0].plot(timestamps, temps, 'o-', color='red', linewidth=2)
        axes[0, 0].set_ylabel('Temperature (°C)', fontsize=11)
        axes[0, 0].set_title('Temperature', fontweight='bold')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # 湿度
        axes[0, 1].plot(timestamps, humidity, 'o-', color='blue', linewidth=2)
        axes[0, 1].set_ylabel('Humidity (%)', fontsize=11)
        axes[0, 1].set_title('Humidity', fontweight='bold')
        axes[0, 1].grid(True, alpha=0.3)
        axes[0, 1].tick_params(axis='x', rotation=45)
        
        # 风速
        axes[1, 0].plot(timestamps, wind_speed, 'o-', color='green', linewidth=2)
        axes[1, 0].set_ylabel('Wind Speed (m/s)', fontsize=11)
        axes[1, 0].set_title('Wind Speed', fontweight='bold')
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].tick_params(axis='x', rotation=45)
        
        # 降水概率
        axes[1, 1].bar(timestamps, precipitation, color='skyblue', alpha=0.7)
        axes[1, 1].set_ylabel('Precipitation Probability (%)', fontsize=11)
        axes[1, 1].set_title('Precipitation Probability', fontweight='bold')
        axes[1, 1].grid(True, alpha=0.3, axis='y')
        axes[1, 1].tick_params(axis='x', rotation=45)
        
        # 保存图表
        if save_path is None:
            save_path = f"{self.output_dir}/multi_param_forecast_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"多参数预测图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def plot_extreme_weather_analysis(self, detection_results: Dict[str, Any],
                                     save_path: str = None) -> str:
        """
        绘制极端天气分析图
        
        参数:
            detection_results: 极端天气检测结果
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制极端天气分析图", "DEBUG")
        
        detections = detection_results.get("detections", [])
        
        if not detections:
            log_message("未检测到极端天气，跳过绘图", "DEBUG")
            return None
        
        # 创建图表
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Extreme Weather Analysis', fontsize=16, fontweight='bold')
        
        # 极端天气类型分布
        types = [d["type_name"] for d in detections]
        severities = [d["severity"] for d in detections]
        
        type_counts = {}
        for t in types:
            type_counts[t] = type_counts.get(t, 0) + 1
        
        # 饼图
        colors = plt.cm.Set3(range(len(type_counts)))
        ax1.pie(type_counts.values(), labels=type_counts.keys(), autopct='%1.1f%%',
                colors=colors, startangle=90)
        ax1.set_title('Extreme Weather Type Distribution', fontweight='bold')
        
        # 严重程度柱状图
        severity_names = ['Minor', 'Moderate', 'Severe', 'Extreme']
        severity_counts = [severities.count(i) for i in range(1, 5)]
        colors = ['blue', 'yellow', 'orange', 'red']
        
        bars = ax2.bar(severity_names, severity_counts, color=colors, alpha=0.7)
        ax2.set_ylabel('Count', fontsize=11)
        ax2.set_title('Severity Distribution', fontweight='bold')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # 在柱子上显示数值
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}',
                        ha='center', va='bottom')
        
        # 保存图表
        if save_path is None:
            save_path = f"{self.output_dir}/extreme_weather_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"极端天气分析图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def plot_comparison_chart(self, actual_data: List[Dict[str, Any]],
                             predicted_data: List[Dict[str, Any]],
                             save_path: str = None) -> str:
        """
        绘制实际值与预测值对比图
        
        参数:
            actual_data: 实际数据
            predicted_data: 预测数据
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("绘制对比图", "DEBUG")
        
        # 提取数据
        actual_times = [datetime.fromisoformat(d["timestamp"]) for d in actual_data]
        actual_temps = [d["temperature"] for d in actual_data]
        
        pred_times = [datetime.fromisoformat(d["timestamp"]) for d in predicted_data]
        pred_temps = [d["temperature"] for d in predicted_data]
        
        # 创建图表
        fig, ax = plt.subplots(figsize=config.PLOT_CONFIG["figure_size"])
        
        # 绘制曲线
        ax.plot(actual_times, actual_temps, 'o-', label='Actual Temperature', linewidth=2, color='blue')
        ax.plot(pred_times, pred_temps, 's--', label='Predicted Temperature', linewidth=2, color='red')
        
        # 设置标签
        ax.set_xlabel('Time', fontsize=12)
        ax.set_ylabel('Temperature (°C)', fontsize=12)
        ax.set_title('Actual vs Forecast', fontsize=14, fontweight='bold')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        plt.xticks(rotation=45, ha='right')
        
        # 保存图表
        if save_path is None:
            save_path = f"{self.output_dir}/comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"对比图已保存到 {save_path}", "DEBUG")
        return save_path
    
    def create_weather_dashboard(self, predictions: List[Dict[str, Any]],
                                detection_results: Dict[str, Any],
                                save_path: str = None) -> str:
        """
        创建天气仪表板
        
        参数:
            predictions: 预测数据
            detection_results: 极端天气检测结果
            save_path: 保存路径
            
        返回:
            图片保存路径
        """
        log_message("创建天气仪表板", "DEBUG")
        
        # 创建大图
        fig = plt.figure(figsize=(16, 10))
        fig.suptitle('Weather Forecast Dashboard', fontsize=18, fontweight='bold')
        
        # 创建网格布局
        gs = fig.add_gridspec(3, 3, hspace=0.3, wspace=0.3)
        
        # 提取数据
        timestamps = [datetime.fromisoformat(p["timestamp"]) for p in predictions]
        temps = [p["temperature"] for p in predictions]
        humidity = [p["humidity"] for p in predictions]
        wind_speed = [p["wind_speed"] for p in predictions]
        precipitation = [p["precipitation_probability"] for p in predictions]
        
        # 1. Temperature Trend
        ax1 = fig.add_subplot(gs[0, :])
        ax1.plot(timestamps, temps, 'o-', linewidth=2, color='red')
        ax1.set_ylabel('Temperature (°C)')
        ax1.set_title('Temperature Forecast Trend', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # 2. Humidity
        ax2 = fig.add_subplot(gs[1, 0])
        ax2.plot(timestamps, humidity, 'o-', linewidth=2, color='blue')
        ax2.set_ylabel('Humidity (%)')
        ax2.set_title('Humidity', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. Wind Speed
        ax3 = fig.add_subplot(gs[1, 1])
        ax3.plot(timestamps, wind_speed, 'o-', linewidth=2, color='green')
        ax3.set_ylabel('Wind Speed (m/s)')
        ax3.set_title('Wind Speed', fontweight='bold')
        ax3.grid(True, alpha=0.3)
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. Precipitation Probability
        ax4 = fig.add_subplot(gs[1, 2])
        ax4.bar(timestamps, precipitation, color='skyblue', alpha=0.7)
        ax4.set_ylabel('Probability (%)')
        ax4.set_title('Precipitation Probability', fontweight='bold')
        ax4.grid(True, alpha=0.3, axis='y')
        ax4.tick_params(axis='x', rotation=45)
        
        # 5. Extreme Weather Alert
        ax5 = fig.add_subplot(gs[2, :])
        detections = detection_results.get("detections", [])
        if detections:
            alert_text = "WARNING - Extreme Weather Alert:\n\n"
            for d in detections:
                alert_text += f"* {d['type_name']}: {d['description']}\n"
            ax5.text(0.5, 0.5, alert_text, ha='center', va='center',
                    fontsize=12, bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.5))
        else:
            ax5.text(0.5, 0.5, 'No Extreme Weather Detected', ha='center', va='center',
                    fontsize=14, bbox=dict(boxstyle='round', facecolor='lightgreen', alpha=0.5))
        ax5.axis('off')
        
        # 保存图表
        if save_path is None:
            save_path = f"{self.output_dir}/dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        plt.savefig(save_path, dpi=config.PLOT_CONFIG["dpi"], bbox_inches='tight')
        plt.close()
        
        log_message(f"天气仪表板已保存到 {save_path}", "DEBUG")
        return save_path


if __name__ == "__main__":
    # 测试代码
    visualizer = WeatherVisualizer()
    
    # 创建测试数据
    from datetime import timedelta
    now = datetime.now()
    test_predictions = []
    for i in range(24):
        test_predictions.append({
            "timestamp": (now + timedelta(hours=i)).isoformat(),
            "temperature": 20 + np.random.randn() * 3,
            "temperature_max": 22 + np.random.randn() * 2,
            "temperature_min": 18 + np.random.randn() * 2,
            "humidity": 60 + np.random.randn() * 10,
            "wind_speed": 5 + np.random.randn() * 2,
            "precipitation_probability": max(0, 30 + np.random.randn() * 20)
        })
    
    # 测试绘图
    visualizer.plot_temperature_forecast(test_predictions)
    visualizer.plot_multi_parameter_forecast(test_predictions)
    
    print("✓ 可视化测试完成")

