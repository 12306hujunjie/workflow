#!/usr/bin/env python3
"""验证测试代码的脚本"""

import subprocess
import sys
import os

def check_imports():
    """检查导入是否正确"""
    print("=== 检查导入 ===")
    
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    test_files = [
        "tests/unit/test_user_entity.py",
        "tests/unit/test_user_repository.py", 
        "tests/unit/test_user_application_service.py",
        "tests/unit/test_auth_services.py",
        "tests/conftest.py"
    ]
    
    for file in test_files:
        print(f"\n检查 {file}...")
        if not os.path.exists(file):
            print(f"✗ 文件不存在: {file}")
            continue
            
        try:
            # 尝试导入文件中的模块
            cmd = [sys.executable, "-m", "py_compile", file]
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=script_dir)
            if result.returncode == 0:
                print(f"✓ {file} 语法正确")
            else:
                print(f"✗ {file} 有语法错误:")
                print(result.stderr)
        except Exception as e:
            print(f"✗ 错误: {e}")

def run_simple_test():
    """运行简单的测试验证"""
    print("\n\n=== 运行简单测试 ===")
    
    # 创建一个简单的测试文件
    test_code = '''
import sys
sys.path.insert(0, '.')

# 测试值对象
try:
    from shared_kernel.domain.value_objects import Username, Email, HashedPassword
    print("✓ 值对象导入成功")
    
    # 测试创建值对象
    username = Username(value="testuser")
    email = Email(value="test@example.com")
    hashed = HashedPassword(value="hashed_password")
    print("✓ 值对象创建成功")
except Exception as e:
    print(f"✗ 值对象测试失败: {e}")

# 测试用户实体
try:
    from bounded_contexts.user_management.domain.entities.user import User
    print("✓ User实体导入成功")
    
    # 测试创建用户
    user = User.create(
        username="testuser",
        email="test@example.com",
        hashed_password="hashed_password_123"
    )
    print("✓ User实体创建成功")
except Exception as e:
    print(f"✗ User实体测试失败: {e}")

# 测试密码服务
try:
    from bounded_contexts.user_management.infrastructure.auth.password_service import PasswordService
    service = PasswordService()
    hashed = service.hash_password("test123")
    verified = service.verify_password("test123", hashed)
    assert verified == True
    print("✓ 密码服务测试成功")
except Exception as e:
    print(f"✗ 密码服务测试失败: {e}")
'''
    
    with open("_test_verify.py", "w") as f:
        f.write(test_code)
    
    # 运行测试
    result = subprocess.run([sys.executable, "_test_verify.py"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("错误输出:")
        print(result.stderr)
    
    # 清理
    os.remove("_test_verify.py")

def main():
    """主函数"""
    print("验证测试代码...\n")
    
    check_imports()
    run_simple_test()
    
    print("\n\n=== 验证完成 ===")
    print("\n建议:")
    print("1. 如果有导入错误，请检查文件路径和模块名称")
    print("2. 确保所有依赖都已安装: pip install -r requirements.txt")
    print("3. 运行测试前确保在项目根目录")

if __name__ == "__main__":
    main()