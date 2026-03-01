# Model Provider Tester - Web UI 版本

🎨 **带有图形界面的模型 Provider 连通性测试工具**

支持 Anthropic、OpenAI、Google API 格式，可本地运行或部署到云端分享。

## ✨ 功能特性

- 🎨 **友好的 Web 界面**
- 🔒 **安全** - API Key 不会被保存或上传
- ⚡ **快速测试** - 几秒内验证连通性
- 📊 **详细报告** - 状态码、响应时间、错误详情
- 🌐 **易于分享** - 可部署到云端，分享给团队使用

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 启动应用

```bash
streamlit run app.py
```

应用会自动在浏览器打开（默认 `http://localhost:8501`）

## 📦 部署到云端

### 部署到 Streamlit Cloud（推荐，免费）

1. **准备代码**
   - 将 `app.py` 和 `requirements.txt` 上传到 GitHub 仓库

2. **部署到 Streamlit Cloud**
   - 访问 [share.streamlit.io](https://share.streamlit.io)
   - 连接你的 GitHub 账号
   - 选择仓库和文件（`app.py`）
   - 点击 Deploy

3. **分享**
   - 部署完成后会得到公开 URL，例如：`https://your-app.streamlit.app`
   - 分享这个链接给任何人使用

### 部署到 Railway / Render

#### Railway

```bash
# 安装 Railway CLI
npm install -g railway

# 登录
railway login

# 初始化项目
railway init

# 部署
railway up
```

#### Render

1. 连接 GitHub 仓库
2. 选择 "Web Service"
3. 设置启动命令：`streamlit run app.py --server.port=$PORT`
4. 部署

### 部署到 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

构建和运行：

```bash
docker build -t model-provider-tester .
docker run -p 8501:8501 model-provider-tester
```

## 📖 使用指南

### 本地使用

1. 启动应用后，在左侧填写配置：
   - 选择 API 类型（Anthropic / OpenAI / Google）
   - 输入 Provider 地址（只填基础 URL，如 `https://api.example.com`）
   - 输入 API Key
   - （可选）指定模型名称

2. 点击"开始测试"

3. 查看测试结果：
   - ✅ 成功：显示响应时间和响应详情
   - ❌ 失败：显示错误信息和诊断建议

### 分享给他人

如果部署到云端：

1. 分享 URL 给团队成员
2. 他们无需安装任何东西，浏览器即可使用
3. 每个人可以测试自己的 Provider 配置

**安全提示：**
- API Key 只在本地处理，不会发送到服务器
- 建议使用测试用的 API Key，不要用生产密钥
- 部署到公网时注意访问控制

## 🎨 界面预览

```
┌─────────────────────────────────────────┐
│  🔍 Model Provider 连通性测试            │
├─────────────────────────────────────────┤
│                                         │
│  ⚙️ 配置 (侧边栏)                        │
│  - API 类型: anthropic ▼                │
│  - Provider 地址: [输入框]              │
│  - API Key: [密码框]                    │
│  - 模型名称: [可选]                      │
│  [🚀 开始测试]                           │
│                                         │
│  主区域:                                 │
│  - 常见 Provider 配置示例                │
│  - 使用说明                             │
│  - 测试结果展示                          │
│                                         │
└─────────────────────────────────────────┘
```

## 🔧 进阶配置

### 修改端口

```bash
streamlit run app.py --server.port=8080
```

### 自定义主题

创建 `.streamlit/config.toml`:

```toml
[theme]
primaryColor="#FF4B4B"
backgroundColor="#FFFFFF"
secondaryBackgroundColor="#F0F2F6"
textColor="#262730"
font="sans serif"
```

### 添加密码保护

在 `app.py` 开头添加：

```python
import streamlit as st

# 简单的密码保护
def check_password():
    def password_entered():
        if st.session_state["password"] == "your_password":
            st.session_state["password_correct"] = True
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("密码", type="password", on_change=password_entered, key="password")
        st.error("密码错误")
        return False
    else:
        return True

if not check_password():
    st.stop()
```

## 📝 命令行版本

如果需要在脚本中使用，可以继续用 `model_provider_tester.py`：

```bash
python model_provider_tester.py -k YOUR_KEY -u YOUR_URL -t anthropic
```

## 🐛 常见问题

### Q: 如何在服务器上后台运行？

```bash
# 使用 screen
screen -S provider-tester
streamlit run app.py
# Ctrl+A+D 分离

# 或使用 nohup
nohup streamlit run app.py > app.log 2>&1 &
```

### Q: 如何限制访问？

1. 使用 Streamlit 的内置认证（见上方"添加密码保护"）
2. 在服务器级别配置防火墙
3. 使用 Nginx 反向代理 + Basic Auth

### Q: 可以添加更多 API 格式吗？

可以！编辑 `app.py`，在 `ProviderTester` 类中添加新的 `test_xxx` 方法，并更新 `test()` 方法中的 `test_methods` 字典。

## 📄 许可

MIT License

## 🙏 致谢

- Streamlit - 快速构建数据应用
- Requests - HTTP 请求库
