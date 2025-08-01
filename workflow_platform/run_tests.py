#!/usr/bin/env python3
"""运行测试脚本"""

import subprocess
import sys
import os

def run_tests():
    """运行测试"""
    # 确保在正确的目录
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("=== 运行用户管理模块单元测试 ===\n")
    
    # 运行pytest
    result = subprocess.run([
        sys.executable, "-m", "pytest", 
        "tests/unit/", 
        "-v", 
        "--tb=short"
    ])
    
    return result.returncode

if __name__ == "__main__":
    exit_code = run_tests()
    sys.exit(exit_code)