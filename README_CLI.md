# Model Provider Tester

一个用于测试自定义模型 Provider 连通性的 Python 工具。

## 功能特性

✅ 支持三种主流 API 格式：
- **Anthropic Messages API**
- **OpenAI Chat Completions API**
- **Google Gemini API**

✅ 测试功能：
- 验证 API Key 有效性
- 检查 Provider 地址连通性
- 测量响应时间
- 显示详细错误信息

## 安装依赖

```bash
pip install requests
```

## 使用方法

### 基本用法

```bash
python model_provider_tester.py -k YOUR_API_KEY -u PROVIDER_URL -t API_TYPE
```

### 参数说明

- `-k, --api-key`: API Key（必填）
- `-u, --url`: Provider 地址/base URL（必填）
- `-t, --type`: API 类型，可选值：`anthropic`、`openai`、`google`（必填）
- `-m, --model`: 模型名称（可选，默认使用测试模型）
- `--json`: 以 JSON 格式输出结果（可选）

### 使用示例

#### 1. 测试 Anthropic 格式

```bash
python model_provider_tester.py \
  -k sk-ant-xxxxx \
  -u https://api.anthropic.com \
  -t anthropic
```

#### 2. 测试 OpenAI 格式（指定模型）

```bash
python model_provider_tester.py \
  -k sk-xxxxx \
  -u https://api.openai.com \
  -t openai \
  -m gpt-4
```

#### 3. 测试 Google Gemini

```bash
python model_provider_tester.py \
  -k AIzaSyxxxxx \
  -u https://generativelanguage.googleapis.com \
  -t google
```

#### 4. 测试自定义 Provider（兼容 OpenAI 格式）

```bash
python model_provider_tester.py \
  -k sk-xxxxx \
  -u https://api.taijiaicloud.com \
  -t openai \
  -m gpt-3.5-turbo
```

#### 5. JSON 输出（用于脚本集成）

```bash
python model_provider_tester.py \
  -k YOUR_KEY \
  -u YOUR_URL \
  -t anthropic \
  --json
```

## 输出示例

### 成功输出

```
🔍 测试中...
  类型: anthropic
  地址: https://api.anthropic.com
  模型: claude-3-haiku-20240307

============================================================
✅ 连通成功！
============================================================
状态码: 200
响应时间: 1.234s
请求地址: https://api.anthropic.com/v1/messages

✅ Provider 配置正确，可以正常使用！

响应预览:
{
  "id": "msg_xxxxx",
  "type": "message",
  "role": "assistant",
  ...
}
```

### 失败输出

```
🔍 测试中...
  类型: openai
  地址: https://api.openai.com
  模型: gpt-3.5-turbo

============================================================
❌ 连接失败
============================================================
状态码: 401
响应时间: 0.523s
请求地址: https://api.openai.com/v1/chat/completions

❌ 连接失败，请检查配置

错误信息:
{
  "error": {
    "message": "Incorrect API key provided",
    "type": "invalid_request_error"
  }
}
```

## 默认测试模型

工具会自动为每种 API 类型选择合适的测试模型：

- **Anthropic**: `claude-3-haiku-20240307`
- **OpenAI**: `gpt-3.5-turbo`
- **Google**: `gemini-pro`

你也可以通过 `-m` 参数指定其他模型。

## 常见问题

### Q: 支持其他 API 格式吗？

A: 目前支持三种主流格式。如果你的 Provider 兼容 OpenAI 或 Anthropic 格式，可以选择对应类型测试。

### Q: 如何测试需要特殊 header 的 Provider？

A: 目前版本使用标准 header。如需自定义，可以修改代码中的 `test_xxx` 方法。

### Q: 连接超时时间是多少？

A: 默认 30 秒。可以在代码中修改 `timeout` 参数。

## 在 OpenClaw 中使用

如果你想测试 OpenClaw 配置中的 Provider，可以从 `~/.openclaw/openclaw.json` 中提取配置：

```json
{
  "models": {
    "providers": {
      "your-provider": {
        "baseUrl": "https://api.example.com",
        "apiKey": "sk-xxxxx",
        "api": "anthropic-messages"  // 或 "openai"
      }
    }
  }
}
```

然后运行：

```bash
python model_provider_tester.py \
  -k sk-xxxxx \
  -u https://api.example.com \
  -t anthropic  # 或 openai
```

## 技术实现

- 使用 `requests` 库处理 HTTP 请求
- 支持标准 Anthropic / OpenAI / Google API 格式
- 自动处理不同 Provider 的认证方式
- 详细的错误诊断和响应时间测量

## 许可

MIT License
