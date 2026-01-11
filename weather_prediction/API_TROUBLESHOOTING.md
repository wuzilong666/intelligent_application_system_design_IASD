# API 故障排查指南

## 当前问题

你遇到的错误：
```
503 Server Error: Service Unavailable for url: https://api2.qiandao.mom/v1/chat/completions
```

或

```
ProxyError: Unable to connect to proxy
```

## 原因分析

### 1. **API服务不可用（503错误）**
- API服务器暂时宕机或维护
- API密钥可能已失效
- API端点地址可能已更改
- 请求频率过高被限流

### 2. **代理/网络问题**
- 系统配置了代理但无法连接
- SSL证书验证失败
- 防火墙阻止连接

## 解决方案

### ✅ 方案1：系统已自动切换到本地预测（推荐）

**已修复**：当API失败时，系统会自动使用本地算法生成预测，不会中断运行。

现在可以直接运行：
```bash
python main.py
```

系统会显示：
```
[WARNING] API预测失败: xxx，使用本地预测
```

### 方案2：检查并修复API配置

1. **验证API地址和密钥**

编辑 `config.py`：
```python
API_URL = "https://api2.qiandao.mom/v1"  # 确认地址正确
API_KEY = "sk-lClbTp1VbcVNfL76tQPdUQnmuSa9J1vMyovZKYI6JbLI7GfY"  # 确认密钥有效
```

2. **测试API连接**

在Python中测试：
```python
import requests

url = "https://api2.qiandao.mom/v1/chat/completions"
headers = {
    "Authorization": "Bearer sk-lClbTp1VbcVNfL76tQPdUQnmuSa9J1vMyovZKYI6JbLI7GfY",
    "Content-Type": "application/json"
}
data = {
    "model": "gemini-pro",
    "messages": [{"role": "user", "content": "Hello"}]
}

response = requests.post(url, headers=headers, json=data, timeout=10)
print(response.status_code)
print(response.text)
```

### 方案3：禁用代理

如果是代理问题，在运行前设置环境变量：

**Windows CMD:**
```cmd
set HTTP_PROXY=
set HTTPS_PROXY=
python main.py
```

**Windows PowerShell:**
```powershell
$env:HTTP_PROXY=""
$env:HTTPS_PROXY=""
python main.py
```

**或者在代码中禁用**，编辑 `utils/api_client.py`，在 `_call_api` 方法中添加：
```python
response = requests.post(
    endpoint,
    headers=self.headers,
    json=payload,
    timeout=30,
    proxies={"http": None, "https": None}  # 添加这行
)
```

### 方案4：使用本地深度学习模型

完全不依赖API，修改 `main.py`：
```python
# 将这行：
self.predictor = WeatherPredictor(use_model="api")

# 改为：
self.predictor = WeatherPredictor(use_model="convlstm")  # 或 "cnn3d"
```

### 方案5：更换API服务商

如果原API不可用，可以更换为其他AI服务：

**OpenAI GPT:**
```python
API_URL = "https://api.openai.com/v1"
API_KEY = "your-openai-key"
API_MODEL = "gpt-3.5-turbo"
```

**其他兼容OpenAI格式的服务:**
- Claude API
- 本地部署的LLM (Ollama等)

## 当前系统状态

✅ **已修复**：API失败不会导致程序崩溃  
✅ **自动降级**：API失败时使用本地数值预测  
✅ **日志记录**：记录API错误详情到日志文件  

## 验证修复

运行以下命令，应该能正常完成：
```bash
python examples/quick_start.py
python examples/hourly_forecast.py
python main.py
```

即使看到 `[WARNING] API预测失败`，程序也会继续运行并生成结果。

## 获取帮助

如果API持续失败：
1. 检查 `logs/weather_system.log` 查看详细错误
2. 联系API提供商确认服务状态
3. 使用本地模型作为永久替代方案
