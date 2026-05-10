# 个人成长伙伴Agent - 部署指南

## 📋 部署概览

本项目是一个个人成长伙伴智能体，提供穿搭建议、体型分析、健身规划和饮食管理功能。

**部署方式**：后端 API 服务 + Coze 平台 Bot 调用

---

## 🏗️ 架构说明

```
┌─────────────┐     HTTP 请求      ┌──────────────────┐
│  豆包 App   │  ──────────────►   │   API Server     │
│  (用户)     │  ◄──────────────   │  (Agent 服务)    │
└─────────────┘    AI 响应         └────────┬─────────┘
                                            │
                    ┌───────────────────────┼───────────────────────┐
                    │                       │                       │
                    ▼                       ▼                       ▼
             ┌─────────────┐        ┌─────────────┐        ┌─────────────┐
             │  Supabase   │        │   天气 API  │        │   LLM API   │
             │  (数据库)   │        │             │        │   (豆包)    │
             └─────────────┘        └─────────────┘        └─────────────┘
```

---

## 📦 部署步骤

### 步骤 1: 准备服务器环境

**推荐配置**：
- CPU: 2 核+
- 内存: 4GB+
- 系统: Ubuntu 20.04+ 或 CentOS 7+

**安装依赖**：

```bash
# 安装 Python 3.12
sudo apt update
sudo apt install python3.12 python3.12-venv python3-pip git -y

# 克隆代码
cd /opt
git clone https://github.com/838867/personal-style-assistant.git
cd personal-style-assistant
```

### 步骤 2: 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres

# LLM API 配置
COZE_WORKLOAD_IDENTITY_API_KEY=your_api_key_here
COZE_INTEGRATION_MODEL_BASE_URL=https://ark.cn-beijing.volces.com/api/v3

# Supabase 配置（可选，如使用 Supabase）
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_key
```

### 步骤 3: 安装依赖

```bash
cd /opt/personal-style-assistant
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 步骤 4: 启动服务

**方式 A: 直接启动**
```bash
cd /opt/personal-style-assistant
source .venv/bin/activate
bash scripts/http_run.sh -p 8000
```

**方式 B: 使用 systemd 管理服务（推荐）**

创建服务文件 `/etc/systemd/system/agent.service`：

```ini
[Unit]
Description=Personal Growth Partner Agent
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/personal-style-assistant
ExecStart=/opt/personal-style-assistant/.venv/bin/python /opt/personal-style-assistant/src/main.py -m http -p 8000
Restart=always
RestartSec=5
Environment="PYTHONPATH=/opt/personal-style-assistant"
Environment="COZE_WORKSPACE_PATH=/opt/personal-style-assistant"

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl daemon-reload
sudo systemctl enable agent
sudo systemctl start agent
sudo systemctl status agent
```

### 步骤 5: 配置反向代理（Nginx）

创建 Nginx 配置文件 `/etc/nginx/sites-available/agent`：

```nginx
server {
    listen 80;
    server_name your-domain.com;  # 替换为你的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        
        # 超时配置
        proxy_read_timeout 900;
        proxy_connect_timeout 900;
        proxy_send_timeout 900;
    }
}
```

启用配置：
```bash
sudo ln -s /etc/nginx/sites-available/agent /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 步骤 6: 配置 HTTPS（Let's Encrypt）

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d your-domain.com
```

---

## 🔧 Coze 平台集成

### 方式 1: Coze Bot 调用（推荐）

1. **登录 Coze 平台**
   - 访问 https://www.coze.cn
   - 登录你的账号

2. **创建 Bot**
   - 点击「创建 Bot」
   - 填写名称：「个人成长伙伴」
   - 填写描述：「你的专属形象顾问」
   - 头像：上传一张图片

3. **配置 Bot 技能**
   在 Bot 设置中添加以下工具：
   
   - `create_user_profile` - 创建用户档案
   - `get_user_profile` - 获取用户信息
   - `update_user_profile` - 更新用户信息
   - `add_wardrobe_item` - 添加衣橱物品
   - `query_wardrobe_items` - 查询衣橱
   - `update_wardrobe_item` - 更新衣物
   - `record_item_wear` - 记录穿着
   - `analyze_body_from_photo` - 体型分析
   - `check_clothing_fit` - 衣服适合度
   - `create_fitness_plan` - 创建健身计划
   - `get_fitness_plans` - 获取健身计划
   - `record_fitness` - 记录锻炼
   - `get_fitness_records` - 获取锻炼记录
   - `create_diet_plan` - 创建饮食计划
   - `get_diet_plans` - 获取饮食计划
   - `record_diet` - 记录饮食
   - `get_diet_records` - 查询饮食记录
   - `get_daily_nutrition_summary` - 每日营养摘要
   - `get_detailed_nutrition_analysis` - 详细营养分析
   - `get_nutrition_recommendations` - 营养建议
   - `add_food_item` - 添加食物
   - `get_food_inventory` - 获取食物仓库
   - `update_food_item` - 更新食物
   - `get_shopping_suggestions` - 采购建议
   - `get_weather` - 天气查询

4. **配置 API 地址**
   
   在 Bot 设置中配置你的 API 服务地址：
   ```
   https://your-domain.com/run
   ```

5. **导入 System Prompt**
   
   将 `config/agent_llm_config.json` 中的 `sp` 字段内容复制到 Bot 的「角色设定」中。

6. **发布 Bot**
   - 点击「发布」
   - 选择「发布到豆包」
   - 等待审核

### 方式 2: 直接调用 API

如果你有其他渠道（如微信、钉钉等），可以直接调用 API：

```python
import requests

# 同步调用
response = requests.post(
    "https://your-domain.com/run",
    json={"type": "query", "session_id": "user123", "message": "你好"},
    headers={"Content-Type": "application/json"}
)

print(response.json())

# 流式调用
response = requests.post(
    "https://your-domain.com/stream_run",
    json={"type": "query", "session_id": "user123", "message": "你好"},
    stream=True,
    headers={"Content-Type": "application/json"}
)

for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))
```

---

## 📡 API 文档

### 端点列表

| 端点 | 方法 | 说明 |
|------|------|------|
| `/run` | POST | 同步调用 Agent |
| `/stream_run` | POST | 流式调用 Agent |
| `/cancel/{run_id}` | POST | 取消执行 |
| `/health` | GET | 健康检查 |
| `/v1/chat/completions` | POST | OpenAI 兼容接口 |

### 请求格式

```json
{
  "type": "query",
  "session_id": "用户会话ID",
  "message": "用户消息",
  "content": {
    "query": {
      "prompt": [
        {
          "type": "text",
          "content": {"text": "用户消息"}
        },
        {
          "type": "image_url",
          "content": {"url": "图片URL"}
        }
      ]
    }
  }
}
```

### 响应格式

```json
{
  "run_id": "运行ID",
  "messages": [
    {
      "role": "assistant",
      "content": "回复内容"
    }
  ],
  "tool_results": [
    {
      "tool": "工具名称",
      "result": "工具执行结果"
    }
  ]
}
```

---

## 🔒 安全配置

### 1. 配置 API 密钥

在 `.env` 中添加 API 密钥验证：

```bash
API_KEY=your_secure_api_key_here
```

### 2. 启用 CORS

在 `src/main.py` 中配置 CORS：

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.coze.cn"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 🐳 Docker 部署（可选）

创建 `Dockerfile`：

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# 安装依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["python", "src/main.py", "-m", "http", "-p", "8000"]
```

构建和运行：

```bash
docker build -t personal-growth-agent .
docker run -d -p 8000:8000 --env-file .env personal-growth-agent
```

---

## ✅ 验证部署

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

预期响应：
```json
{"status": "ok", "message": "Service is running"}
```

### 2. 测试对话

```bash
curl -X POST http://localhost:8000/run \
  -H "Content-Type: application/json" \
  -d '{"type": "query", "session_id": "test", "message": "你好"}'
```

---

## 🆘 故障排查

### 1. 服务启动失败

检查日志：
```bash
journalctl -u agent -n 100
```

### 2. 数据库连接失败

```bash
# 测试数据库连接
psql $DATABASE_URL -c "SELECT 1;"
```

### 3. LLM API 调用失败

检查环境变量配置：
```bash
echo $COZE_WORKLOAD_IDENTITY_API_KEY
echo $COZE_INTEGRATION_MODEL_BASE_URL
```

---

## 📞 支持

如有问题，请检查：
1. 日志文件：`/app/work/logs/bypass/app.log`
2. API 服务状态：`systemctl status agent`
3. Nginx 状态：`systemctl status nginx`

---

**祝你部署成功！** 🎉
