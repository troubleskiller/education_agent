# Python 版本和安装要求

## 推荐的 Python 版本

**强烈推荐使用 Python 3.9 或 3.10**

- Python 3.9.x（推荐）
- Python 3.10.x（推荐）
- Python 3.8.x（最低要求，但可能遇到某些包的兼容性问题）

## 安装步骤

### 1. 创建虚拟环境

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux/Mac
python -m venv .venv
source .venv/bin/activate
```

### 2. 升级 pip

```bash
python -m pip install --upgrade pip
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

## 常见问题解决

### ChromaDB 安装失败

如果遇到 ChromaDB 安装问题，尝试以下方法：

1. **单独安装 ChromaDB**：
```bash
pip install chromadb==0.4.24 --no-deps
pip install -r requirements.txt
```

2. **使用国内镜像源**（如果在中国）：
```bash
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### tokenizers 安装失败

如果遇到 tokenizers 相关错误：

1. **安装 Microsoft C++ Build Tools**（Windows）：
   - 下载并安装 [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/)
   - 选择 "Desktop development with C++" 工作负载

2. **使用预编译的wheel**：
```bash
pip install tokenizers --prefer-binary
```

### numpy 版本冲突

如果遇到 numpy 版本冲突：

```bash
pip uninstall numpy
pip install numpy==1.24.3
```

## 版本兼容性矩阵

| Package | Python 3.8 | Python 3.9 | Python 3.10 | Python 3.11 |
|---------|------------|------------|-------------|-------------|
| chromadb 0.4.24 | ⚠️ | ✅ | ✅ | ⚠️ |
| numpy 1.24.3 | ✅ | ✅ | ✅ | ❌ |
| langchain 0.1.6 | ✅ | ✅ | ✅ | ✅ |
| fastapi 0.110.0 | ✅ | ✅ | ✅ | ✅ |

- ✅ 完全兼容
- ⚠️ 可能有小问题
- ❌ 不兼容

## 最小化安装（如果完整安装失败）

创建 `requirements-minimal.txt`：

```txt
fastapi==0.110.0
uvicorn[standard]==0.27.0
pydantic==2.5.3
pydantic-settings==2.1.0
sqlalchemy==2.0.25
langchain==0.1.6
langchain-openai==0.0.5
openai==1.12.0
python-dotenv==1.0.1
chromadb==0.4.24
```

然后逐步安装其他包。 