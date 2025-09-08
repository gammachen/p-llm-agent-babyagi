#!/usr/bin/env python3
"""
简单测试脚本
"""

import os
import sys

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_custom_babyagi():
    """测试CustomBabyAGI"""
    try:
        from custom_babyagi import CustomBabyAGI
        
        print("✅ 成功导入CustomBabyAGI")
        
        # 创建Agent
        agent = CustomBabyAGI(
            objective="测试修复",
            initial_task="测试系统是否正常工作"
        )
        
        print("✅ Agent创建成功")
        
        # 检查向量数据库
        if hasattr(agent, 'vector_db'):
            count = agent.vector_db.count()
            print(f"✅ 向量数据库初始化成功，当前记录数: {count}")
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== CustomBabyAGI修复测试 ===")
    
    if test_custom_babyagi():
        print("\n🎉 修复成功！CustomBabyAGI现在可以正常使用")
    else:
        print("\n❌ 测试失败，请检查错误信息")