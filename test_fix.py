#!/usr/bin/env python3
"""
测试ChromaDB修复结果的脚本
"""

import os
import sys
import logging
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_chromadb_basic():
    """测试ChromaDB基本功能"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        print("✅ ChromaDB 导入成功")
        
        # 测试客户端创建
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        print("✅ ChromaDB 客户端创建成功")
        
        # 测试集合创建
        collection = client.get_or_create_collection(
            name="babyagi_tasks",
            metadata={"hnsw:space": "cosine"}
        )
        print("✅ ChromaDB 集合创建成功")
        
        # 测试数据添加
        collection.add(
            documents=["测试任务1：这是一个测试任务"],
            metadatas=[{"task_id": "test_1", "task": "测试任务"}],
            ids=["test_1"]
        )
        print("✅ ChromaDB 数据添加成功")
        
        # 测试数据查询
        results = collection.query(
            query_texts=["测试"],
            n_results=1
        )
        
        if results["documents"] and len(results["documents"][0]) > 0:
            print("✅ ChromaDB 查询成功")
        else:
            print("❌ ChromaDB 查询失败")
            return False
            
        # 清理测试数据
        client.delete_collection("babyagi_tasks")
        print("✅ ChromaDB 测试清理完成")
        
        return True
        
    except Exception as e:
        print(f"❌ ChromaDB 基本测试失败: {e}")
        return False

def test_custom_babyagi_import():
    """测试CustomBabyAGI导入"""
    try:
        from custom_babyagi import CustomBabyAGI, Task
        print("✅ CustomBabyAGI 导入成功")
        return True
    except Exception as e:
        print(f"❌ CustomBabyAGI 导入失败: {e}")
        return False

def test_config():
    """测试配置"""
    try:
        from config import config
        print("✅ 配置模块导入成功")
        
        # 检查必要配置
        required_configs = [
            "VECTOR_DB", "CHROMA_PERSIST_DIR", 
            "LLM_PROVIDER", "OPENAI_MODEL"
        ]
        
        for cfg in required_configs:
            value = getattr(config, cfg, None)
            print(f"  {cfg}: {value}")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        return False

def test_agent_creation():
    """测试Agent创建"""
    try:
        from custom_babyagi import CustomBabyAGI
        
        # 创建测试Agent
        agent = CustomBabyAGI(
            objective="测试ChromaDB修复",
            initial_task="测试系统是否正常工作"
        )
        
        print("✅ Agent 创建成功")
        
        # 检查向量数据库
        if hasattr(agent, 'vector_db') and agent.vector_db:
            print("✅ 向量数据库初始化成功")
            
            # 测试向量数据库连接
            count = agent.vector_db.count()
            print(f"✅ 向量数据库当前有 {count} 条记录")
            
            return True
        else:
            print("❌ 向量数据库初始化失败")
            return False
            
    except Exception as e:
        print(f"❌ Agent 创建失败: {e}")
        return False

def main():
    """主测试函数"""
    print("=== ChromaDB 修复测试 ===\n")
    
    tests = [
        ("ChromaDB 基本功能", test_chromadb_basic),
        ("配置模块", test_config),
        ("CustomBabyAGI 导入", test_custom_babyagi_import),
        ("Agent 创建", test_agent_creation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"正在测试: {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} 通过\n")
        else:
            print(f"❌ {test_name} 失败\n")
    
    print(f"=== 测试结果: {passed}/{total} 测试通过 ===")
    
    if passed == total:
        print("🎉 所有测试通过！ChromaDB修复成功")
        return True
    else:
        print("⚠️ 部分测试失败，请检查日志")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)