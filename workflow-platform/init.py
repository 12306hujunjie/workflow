"""项目初始化脚本"""

import os
import secrets
import shutil
from pathlib import Path


def generate_secret_key():
    """生成安全的密钥"""
    return secrets.token_urlsafe(32)


def init_env_file():
    """初始化.env文件"""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return
    
    if not os.path.exists('.env.example'):
        print("✗ .env.example not found")
        return
    
    # 复制.env.example到.env
    shutil.copy('.env.example', '.env')
    
    # 读取.env文件
    with open('.env', 'r') as f:
        content = f.read()
    
    # 替换JWT密钥
    new_secret = generate_secret_key()
    content = content.replace('your-secret-key-here-please-change-this', new_secret)
    
    # 写回文件
    with open('.env', 'w') as f:
        f.write(content)
    
    print("✓ Created .env file with secure JWT secret key")


def create_directories():
    """创建必要的目录"""
    directories = [
        'logs',
        'uploads',
        'exports',
        'temp'
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")
    
    # 创建.gitignore文件
    gitignore_content = """
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.env
*.egg-info/
dist/
build/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Project specific
logs/
uploads/
exports/
temp/
*.log
.coverage
htmlcov/
.pytest_cache/
"""
    
    with open('.gitignore', 'w') as f:
        f.write(gitignore_content.strip())
    
    print("✓ Created .gitignore file")


def check_requirements():
    """检查Python版本和依赖"""
    import sys
    
    # 检查Python版本
    if sys.version_info < (3, 10):
        print(f"✗ Python 3.10+ required, you have {sys.version}")
        return False
    
    print(f"✓ Python {sys.version.split()[0]} detected")
    return True


def main():
    """主函数"""
    print("Workflow Platform - Project Initialization")
    print("=" * 50)
    
    # 检查Python版本
    if not check_requirements():
        return
    
    # 初始化.env文件
    init_env_file()
    
    # 创建必要的目录
    create_directories()
    
    print("\n" + "=" * 50)
    print("✓ Initialization completed!")
    print("\nNext steps:")
    print("1. Review and update .env file with your configurations")
    print("2. Install dependencies: pip install -r requirements.txt")
    print("3. Start services: docker-compose up -d postgres redis")
    print("4. Run migrations: psql -h localhost -U postgres -d workflow_platform -f migrations/user_management.sql")
    print("5. Start application: uvicorn api_gateway.main:app --reload")
    print("\nOr use the convenience script: ./scripts/start-dev.sh")


if __name__ == "__main__":
    main()