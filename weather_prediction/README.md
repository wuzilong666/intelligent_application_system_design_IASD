# 基于深度学习的天气预测系统

## 📚 项目简介

这是一个基于深度学习和Gemini API的智能天气预测系统，能够实现多尺度的天气预测、极端天气识别和可视化展示。

## ⭐ 核心功能

1. **多源气象数据集成** - 整合多种气象数据源
2. **时空序列建模** - 使用ConvLSTM、3D CNN等先进网络
3. **多尺度预测** - 支持短期（小时级）、中期（天级）、长期（周级）预测
4. **极端天气识别** - 自动识别台风、暴雨、高温等极端天气
5. **区域精细化预测** - 城市级、区县级精细化预测
6. **不确定性量化** - 提供置信区间和概率分布
7. **可视化展示** - 天气图、动画、趋势图等
8. **预警发布** - 自动化天气预警和推送

## 📁 项目结构

```
weather_prediction/
│
├── README.md                    # 项目说明文档（你正在看的文件）
├── TUTORIAL.md                  # 详细使用教程
├── requirements.txt             # Python依赖包列表
├── config.py                    # 配置文件（包含API密钥）
│
├── data/                        # 数据目录
│   ├── raw/                    # 原始数据
│   ├── processed/              # 处理后的数据
│   └── sample/                 # 示例数据
│
├── models/                      # 模型目录
│   ├── convlstm_model.py       # ConvLSTM模型
│   ├── cnn3d_model.py          # 3D CNN模型
│   └── saved_models/           # 保存的模型权重
│
├── src/                         # 源代码目录
│   ├── data_collector.py       # 数据采集模块
│   ├── data_processor.py       # 数据处理模块
│   ├── predictor.py            # 预测模块
│   ├── extreme_weather.py      # 极端天气识别模块
│   ├── visualizer.py           # 可视化模块
│   └── alert_system.py         # 预警系统模块
│
├── utils/                       # 工具函数
│   ├── api_client.py           # Gemini API客户端
│   └── helpers.py              # 辅助函数
│
├── examples/                    # 示例代码
│   ├── quick_start.py          # 快速开始示例
│   ├── hourly_forecast.py      # 小时级预测示例
│   └── extreme_detection.py    # 极端天气检测示例
│
└── main.py                      # 主程序入口
```

## 🚀 快速开始

### 第一步：安装Python环境

确保你已经安装了Python 3.8或更高版本。检查方法：
```bash
python --version
```

### 第二步：安装依赖包

在项目根目录下打开命令行，执行：
```bash
pip install -r requirements.txt
```

### 第三步：配置API密钥

编辑 `config.py` 文件，你的API密钥已经预填好了，无需修改。

### 第四步：运行示例程序

```bash
# 快速开始示例
python examples/quick_start.py

# 小时级天气预测
python examples/hourly_forecast.py

# 极端天气检测
python examples/extreme_detection.py
```

### 第五步：运行完整系统

```bash
python main.py
```

## 📖 详细教程

请查看 [TUTORIAL.md](TUTORIAL.md) 获取详细的使用教程和说明。

## ⚙️ 配置说明

所有配置都在 `config.py` 文件中，包括：
- API端点和密钥
- 模型参数
- 预测时间范围
- 预警阈值

## 🔧 常见问题

### 1. 安装依赖包失败？
- 尝试使用国内镜像源：`pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple`

### 2. API调用失败？
- 检查网络连接
- 确认API密钥是否正确
- 查看config.py中的API_URL是否正确

### 3. 缺少训练数据？
- 运行 `python src/data_collector.py` 下载示例数据
- 或使用系统内置的模拟数据

## 📝 系统工作流程

1. **数据采集** → 从多个来源获取气象数据
2. **数据处理** → 清洗、标准化、特征工程
3. **模型训练** → 使用深度学习模型学习天气模式
4. **预测生成** → 生成多时间尺度的天气预测
5. **极端识别** → 检测极端天气事件
6. **可视化** → 生成图表和动画
7. **预警发布** → 自动发布预警信息

## 🎯 使用场景

- **农业**: 帮助农民安排农事活动
- **交通**: 提前预知恶劣天气，调整运输计划
- **能源**: 预测能源需求，优化调度
- **公共安全**: 极端天气预警，减少灾害损失

## 📞 技术支持

如有问题，请查看：
1. `TUTORIAL.md` - 详细教程
2. 代码注释 - 每个文件都有详细注释
3. 示例代码 - examples目录下的示例

## 📄 许可证

本项目仅用于学习和研究目的。

---

**祝你使用愉快！🌤️**
