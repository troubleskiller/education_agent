# 教育智能体系统 (Education Agent System)

一个基于大语言模型的智能教育辅助系统，提供个性化学习计划制定和启发式教学功能。

## 系统架构

### 核心模块

1. **学生档案管理模块**
   - 新学生注册和建档
   - 学生信息存储和查询
   - 学习历史追踪

2. **思维链主动提问模块**
   - 基于思维链的智能对话
   - 多轮对话了解学生背景
   - 自动判断进入学习计划制定阶段

3. **学习计划制定模块**
   - 基于对话内容生成个性化学习计划
   - 学习路径规划
   - 进度跟踪

4. **RAG知识库模块**
   - 学习资料向量化存储
   - 智能检索相关知识
   - 动态知识更新

5. **启发式教学模块**
   - 苏格拉底式提问
   - 互动式学习体验
   - 自适应教学策略

## 技术栈

- **后端框架**: FastAPI
- **数据库**: SQLAlchemy + SQLite/PostgreSQL
- **向量数据库**: ChromaDB Cloud
- **LLM框架**: LangChain
- **支持的LLM**: OpenAI、Azure OpenAI、DeepSeek、通义千问、Claude

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env .env
# 编辑 .env 文件，填入您的 API Key 配置
```

### 3. 初始化数据库

```bash
python -m src.scripts.init_db
```

### 4. 启动服务

```bash
python start.py
# 或直接运行
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 访问API文档

打开浏览器访问 http://localhost:8000/docs

## 支持的LLM模型

- **OpenAI**: GPT-4, GPT-3.5
- **Azure OpenAI**: 企业级部署
- **DeepSeek**: 高性价比中文模型
- **通义千问**: 阿里云中文模型
- **Claude**: Anthropic的高级模型

## API 示例

### 创建新学生档案

```bash
POST /api/v1/students
{
  "name": "张三",
  "age": 16,
  "grade": "高一",
  "interests": ["数学", "物理", "编程"]
}
```

### 开始对话

```bash
POST /api/v1/conversations/start
{
  "student_id": "student-uuid",
  "initial_message": "我想学习Python编程"
}
```

## 项目结构

```
education_agent/
├── src/
│   ├── api/            # API路由
│   ├── core/           # 核心配置
│   ├── models/         # 数据模型
│   ├── schemas/        # Pydantic模式
│   ├── services/       # 业务逻辑
│   ├── scripts/        # 脚本工具
│   └── main.py         # 应用入口
├── data/               # 数据存储
├── logs/               # 日志文件
├── requirements.txt    # 项目依赖
├── example.env         # 环境变量示例
├── start.py           # 启动脚本
└── README.md          # 项目说明
```

## 安全提示

- 请妥善保管API密钥，不要提交到版本控制
- 定期更换API密钥
- 使用环境变量管理敏感信息

## 许可证

MIT License 