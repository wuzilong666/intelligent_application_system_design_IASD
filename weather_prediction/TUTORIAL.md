# 天气预测系统使用教程

> 本教程手把手带你完成环境配置、运行示例、查看结果。即使你是小白，也能顺利上手。

## 1. 环境准备

1. 安装 Python 3.8+（推荐 3.10）。
2. 打开终端/命令行，切换到项目根目录 `weather_prediction`。
3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```
   如果下载慢，可使用清华镜像：
   ```bash
   pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
   ```

## 2. 配置 API

- 已在 `config.py` 里预填了你的地址和密钥：
  - API_URL: https://api2.qiandao.mom/v1
  - API_KEY: 已写入文件
- 模型名默认 `gemini-pro`，如需修改可编辑 `config.py`。

## 3. 目录说明

- README.md：项目概览
- TUTORIAL.md：本教程
- requirements.txt：依赖列表
- config.py：配置（API、阈值、模型参数）
- data/：数据目录（raw/processed/sample）
- models/：模型文件（ConvLSTM、3D CNN）
- src/：核心代码
- utils/：工具函数、API 客户端
- examples/：示例脚本
- outputs/：运行后生成的图表、预警、JSON 结果
- logs/：日志

## 4. 快速运行

### 4.1 运行快速示例
```bash
python examples/quick_start.py
```
看到 6 小时预测输出即成功。

### 4.2 运行小时级预测
```bash
python examples/hourly_forecast.py
```
会生成温度趋势图、多参数图，保存在 `outputs/plots/`。

### 4.3 运行极端天气检测
```bash
python examples/extreme_detection.py
```
会输出预警文本，并生成分析图（如有）。预警保存在 `outputs/alerts/`。

### 4.4 运行完整系统
```bash
python main.py
```
完整流程：采集→处理→预测（短/中/长期）→极端识别→可视化→预警→保存结果。

## 5. 使用步骤详解

1) **采集数据**：示例用模拟数据 `WeatherDataCollector.get_sample_data()`；如需真实数据，可改写 `collect_real_data` 接入气象 API。
2) **数据预处理**：`WeatherDataProcessor.preprocess_data` 完成特征提取、标准化、序列构建。
3) **预测**：`WeatherPredictor` 默认用 Gemini API，也可设 `use_model='convlstm'` 或 `use_model='cnn3d'` 使用本地模型。
4) **极端识别**：`ExtremeWeatherDetector` 基于阈值 + Gemini API 分析。
5) **可视化**：`WeatherVisualizer` 生成温度曲线、多参数图、仪表板、极端分析图。
6) **预警发布**：`WeatherAlertSystem` 输出控制台/文件，预留邮件、短信接口。

## 6. 常见问题

- **依赖安装失败**：用镜像源；或升级 pip：`python -m pip install --upgrade pip`。
- **API 调用失败**：检查网络；确认 `config.py` 的 API_URL/API_KEY；稍后重试。
- **图表中文乱码**：系统需有中文字体（SimHei/微软雅黑），否则改用英文字体。
- **GPU 加速**：已在 config 中启用 `use_gpu=True`，需本机有支持的 GPU + CUDA；否则 TensorFlow 会自动退回 CPU。

## 7. 进阶自定义

- **改区域**：编辑 `config.py` 里的 `REGIONS` 字典。
- **调预测范围**：`PREDICTION_HORIZONS` 控制短/中/长期的小时/天数。
- **调极端阈值**：`EXTREME_WEATHER_THRESHOLDS`。
- **改模型超参**：`CONVLSTM_CONFIG`、`CNN3D_CONFIG`。
- **改预警渠道**：`ALERT_CONFIG`，开启邮箱/短信后填入你的服务逻辑。

## 8. 结果查看

- 图表：`outputs/plots/`
- 仪表板：`outputs/plots/dashboard_*.png`
- 预警：`outputs/alerts/`
- 预测结果 JSON：`outputs/prediction_results_*.json`
- 日志：`logs/weather_system.log`

## 9. 下一步

- 接入真实气象 API（国家气象局、OpenWeatherMap 等）填充 `collect_real_data`
- 使用真实历史数据训练本地模型，提高精度
- 将可视化与预警集成到 Web 界面（Flask）

祝你使用愉快！🌤️
