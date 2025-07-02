# 教育智能体系统使用指南

## 快速开始

### 1. 环境准备

首先，确保您已经安装了 Python 3.8 或更高版本。

### 2. 创建环境变量文件

在项目根目录创建 `.env` 文件，内容如下：

```bash
# 选择LLM提供商 (openai/azure/deepseek/qwen/claude)
LLM_PROVIDER=openai

# OpenAI配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# Azure OpenAI配置（使用Azure时需要）
AZURE_API_KEY=your-azure-api-key-here
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_API_VERSION=2024-05-01-preview
AZURE_DEPLOYMENT_NAME=your-deployment-name

# DeepSeek配置（使用DeepSeek时需要）
DEEPSEEK_API_KEY=your-deepseek-api-key-here
DEEPSEEK_API_BASE=https://api.deepseek.com/v1
DEEPSEEK_MODEL=deepseek-chat

# 通义千问配置（使用Qwen时需要）
QWEN_API_KEY=your-qwen-api-key-here
QWEN_API_BASE=https://dashscope.aliyuncs.com/api/v1
QWEN_MODEL=qwen-turbo

# Claude配置（使用Claude时需要）
CLAUDE_API_KEY=your-claude-api-key-here
CLAUDE_MODEL=claude-3-opus-20240229

# ChromaDB云配置（已预设，无需修改）
CHROMA_API_KEY=ck-APjQHA3VvJ8NpehfqWV6uzJKu456oduAMHo2jGPEZJQe
CHROMA_TENANT=4568293d-4b29-434d-9e2b-f0972d5c0c52
CHROMA_DATABASE=education_agent

# 数据库配置
DATABASE_URL=sqlite:///./education_agent.db

# 其他配置
LOG_LEVEL=INFO
DEBUG=True
```

### 配置示例

#### 使用OpenAI
```bash
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

#### 使用Azure OpenAI
```bash
LLM_PROVIDER=azure
AZURE_API_KEY=your-azure-key
AZURE_API_BASE=https://your-resource.openai.azure.com/
AZURE_DEPLOYMENT_NAME=gpt-4o
```

#### 使用DeepSeek
```bash
LLM_PROVIDER=deepseek
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

#### 使用通义千问
```bash
LLM_PROVIDER=qwen
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx
```

#### 使用Claude
```bash
LLM_PROVIDER=claude
CLAUDE_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxxx
```

### 3. 启动系统

运行启动脚本：

```bash
python start.py
```

按照提示选择：
- 输入 `y` 安装依赖
- 输入 `y` 初始化数据库
- 系统将自动启动

### 4. 访问系统

- 主页：http://localhost:8000
- API文档：http://localhost:8000/docs

## 使用流程

### 第一步：创建学生档案

```bash
POST /api/v1/students
{
  "name": "张三",
  "age": 16,
  "grade": "高一",
  "interests": ["数学", "物理", "编程"],
  "learning_goals": "想要学习Python编程，为将来的AI研究打基础",
  "learning_style": "视觉型"
}
```

响应示例：
```json
{
  "id": "abc123...",
  "name": "张三",
  "age": 16,
  "grade": "高一",
  "interests": ["数学", "物理", "编程"],
  "learning_goals": "想要学习Python编程，为将来的AI研究打基础",
  "learning_style": "视觉型",
  "created_at": "2024-01-01T00:00:00"
}
```

### 第二步：开始评估对话

```bash
POST /api/v1/conversations/start
{
  "student_id": "abc123...",
  "initial_message": "我想学习Python编程"
}
```

系统会通过多轮对话了解学生的：
- 学习背景
- 具体目标
- 可用时间
- 学习偏好

### 第三步：继续对话

```bash
POST /api/v1/conversations/{conversation_id}/continue
{
  "message": "我之前学过一点C语言，但是不太熟练"
}
```

系统会根据学生的回答继续深入了解，并在合适的时机提议制定学习计划。

### 第四步：学习计划生成

当系统判断已经收集足够信息后，会询问是否制定学习计划。学生确认后，系统会自动生成个性化学习计划并存储到RAG知识库。

### 第五步：开始学习

```bash
POST /api/v1/teaching/start
{
  "student_id": "abc123...",
  "topic": "Python基础语法",
  "learning_plan_id": "plan123..."  // 可选
}
```

### 第六步：互动教学

```bash
POST /api/v1/teaching/continue
{
  "session_id": "teach_abc123_Python基础语法",
  "student_response": "我不太理解什么是变量",
  "conversation_history": [...]
}
```

系统会采用启发式教学方法，通过提问和引导帮助学生理解概念。

## 高级功能

### 查找相似学生

```bash
GET /api/v1/students/{student_id}/similar?k=3
```

### 获取学习建议

```bash
GET /api/v1/teaching/{student_id}/recommendations
```

### 查看对话历史

```bash
GET /api/v1/conversations/{conversation_id}/history
```

## API 完整文档

访问 http://localhost:8000/docs 查看交互式API文档。

## 注意事项

1. **API Key安全**：
   - 请妥善保管您的API Key，不要提交到版本控制系统
   - 不要在公开场合分享真实的API Key
   - 定期更换API Key以确保安全

2. **数据隐私**：学生数据存储在本地数据库，请确保数据安全。

3. **费用控制**：
   - 不同的LLM提供商收费标准不同
   - OpenAI和Claude通常较贵
   - DeepSeek和Qwen相对便宜
   - 请根据预算选择合适的模型

4. **模型选择建议**：
   - **OpenAI GPT-4**：效果最好，但成本较高
   - **Azure OpenAI**：适合企业用户，需要Azure订阅
   - **DeepSeek**：中文效果好，性价比高
   - **通义千问**：阿里云的模型，中文支持好
   - **Claude**：擅长长文本和复杂推理

## 故障排除

### 常见问题

1. **ImportError**: 请确保已安装所有依赖：
   ```bash
   pip install -r requirements.txt
   ```

2. **数据库错误**: 重新初始化数据库：
   ```bash
   python -m src.scripts.init_db
   ```

3. **API调用失败**: 
   - 检查.env文件中的API Key是否正确
   - 确认选择的LLM_PROVIDER与配置的API Key匹配
   - 检查网络连接是否正常

4. **ChromaDB连接错误**:
   - 确保ChromaDB云服务正常
   - 检查API Key和租户ID是否正确

## 扩展开发

### 添加新的教学材料

可以通过RAG服务添加教学材料：

```python
from src.services.rag_service import RAGService

rag = RAGService()
rag.store_teaching_material(
    material_id="mat001",
    content="Python中的列表是一种有序的集合...",
    metadata={
        "subject": "Python",
        "level": "初级",
        "topic": "数据结构"
    }
)
```

### 自定义教学策略

修改 `src/services/teaching_service.py` 中的教学策略提示词，可以调整教学风格。

### 添加新的LLM提供商

如需添加新的LLM提供商：
1. 在 `src/core/config.py` 中添加配置
2. 在 `src/services/llm_service.py` 中添加初始化逻辑
3. 实现相应的API调用接口 