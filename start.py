"""
教育智能体系统启动脚本
"""
import os
import sys
import subprocess


def check_requirements():
    """检查必要的依赖"""
    print("检查系统依赖...")
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误：需要Python 3.8或更高版本")
        return False
    
    print(f"✓ Python {sys.version.split()[0]}")
    
    # 检查环境变量文件
    if not os.path.exists(".env"):
        print("\n警告：未找到.env文件")
        print("请创建.env文件并配置以下内容：")
        print("""
# OpenAI API配置
OPENAI_API_KEY=your-openai-api-key-here
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4

# 数据库配置
DATABASE_URL=sqlite:///./education_agent.db

# 其他配置...
        """)
        return False
    
    print("✓ 环境配置文件")
    return True


def install_dependencies():
    """安装依赖"""
    print("\n安装项目依赖...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ 依赖安装完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 依赖安装失败")
        return False


def init_database():
    """初始化数据库"""
    print("\n初始化数据库...")
    try:
        subprocess.check_call([sys.executable, "-m", "src.scripts.init_db"])
        print("✓ 数据库初始化完成")
        return True
    except subprocess.CalledProcessError:
        print("✗ 数据库初始化失败")
        return False


def start_server():
    """启动服务器"""
    print("\n启动教育智能体系统...")
    print("=" * 50)
    print("系统启动成功！")
    print(f"访问地址: http://localhost:8000")
    print(f"API文档: http://localhost:8000/docs")
    print("=" * 50)
    
    try:
        subprocess.call([sys.executable, "-m", "uvicorn", "src.main:app", "--reload", "--host", "0.0.0.0", "--port", "8000"])
    except KeyboardInterrupt:
        print("\n系统已停止")


def main():
    """主函数"""
    print("教育智能体系统启动器")
    print("=" * 50)
    
    # 检查依赖
    if not check_requirements():
        return
    
    # 询问是否安装依赖
    if input("\n是否安装/更新依赖？(y/n): ").lower() == 'y':
        if not install_dependencies():
            return
    
    # 询问是否初始化数据库
    if input("\n是否初始化/重置数据库？(y/n): ").lower() == 'y':
        if not init_database():
            return
    
    # 启动服务器
    start_server()


if __name__ == "__main__":
    main() 