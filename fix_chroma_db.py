#!/usr/bin/env python3
"""
ChromaDB 数据库修复脚本
修复 "no such column: collections.topic" 错误
"""

import os
import shutil
import sqlite3
import logging
from pathlib import Path

def backup_chroma_db(chroma_dir: str) -> str:
    """备份现有的ChromaDB数据"""
    if not os.path.exists(chroma_dir):
        return None
    
    backup_dir = f"{chroma_dir}_backup_{int(time.time())}"
    shutil.copytree(chroma_dir, backup_dir)
    print(f"已备份ChromaDB到: {backup_dir}")
    return backup_dir

def fix_chroma_schema(db_path: str) -> bool:
    """修复ChromaDB数据库结构"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查collections表的结构
        cursor.execute("PRAGMA table_info(collections)")
        columns = cursor.fetchall()
        
        column_names = [col[1] for col in columns]
        print(f"现有列: {column_names}")
        
        # 如果缺少topic列，添加它
        if 'topic' not in column_names:
            print("添加缺失的topic列...")
            cursor.execute("ALTER TABLE collections ADD COLUMN topic TEXT")
            conn.commit()
            print("topic列添加成功")
        
        # 检查其他可能的缺失列
        missing_columns = [
            ("topic", "TEXT"),
            ("dimension", "INTEGER"),
            ("metadata", "TEXT")
        ]
        
        for col_name, col_type in missing_columns:
            if col_name not in column_names:
                try:
                    cursor.execute(f"ALTER TABLE collections ADD COLUMN {col_name} {col_type}")
                    print(f"添加缺失的列: {col_name}")
                except sqlite3.OperationalError as e:
                    if "duplicate column name" not in str(e).lower():
                        print(f"添加列{col_name}时出错: {e}")
        
        conn.commit()
        conn.close()
        return True
        
    except Exception as e:
        print(f"修复数据库结构失败: {e}")
        return False

def recreate_chroma_db(chroma_dir: str) -> bool:
    """重新创建ChromaDB"""
    try:
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir)
            print(f"已删除旧的ChromaDB目录: {chroma_dir}")
        
        # 创建新的空目录
        os.makedirs(chroma_dir, exist_ok=True)
        print(f"已创建新的ChromaDB目录: {chroma_dir}")
        return True
        
    except Exception as e:
        print(f"重新创建ChromaDB失败: {e}")
        return False

def check_and_fix_chromadb():
    """检查和修复ChromaDB"""
    chroma_dir = "./chroma_db"
    db_path = os.path.join(chroma_dir, "chroma.sqlite3")
    
    print("=== ChromaDB 修复检查 ===")
    
    if not os.path.exists(chroma_dir):
        print("ChromaDB目录不存在，将创建新的")
        os.makedirs(chroma_dir, exist_ok=True)
        return True
    
    if not os.path.exists(db_path):
        print("ChromaDB数据库文件不存在，将创建新的")
        return True
    
    # 备份现有数据
    backup_dir = backup_chroma_db(chroma_dir)
    
    try:
        # 尝试修复现有数据库
        if fix_chroma_schema(db_path):
            print("数据库结构修复成功")
            return True
        else:
            print("数据库结构修复失败，将重新创建")
            return recreate_chroma_db(chroma_dir)
            
    except Exception as e:
        print(f"修复过程中出现错误: {e}")
        print("将重新创建ChromaDB")
        return recreate_chroma_db(chroma_dir)

def test_chromadb_connection():
    """测试ChromaDB连接"""
    try:
        import chromadb
        from chromadb.config import Settings
        
        # 使用临时客户端测试
        client = chromadb.PersistentClient(
            path="./chroma_db",
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 测试创建集合
        collection = client.get_or_create_collection(
            name="test_collection",
            metadata={"hnsw:space": "cosine"}
        )
        
        # 测试添加数据
        collection.add(
            documents=["测试文档"],
            metadatas=[{"test": True}],
            ids=["test_1"]
        )
        
        # 测试查询
        results = collection.query(
            query_texts=["测试"],
            n_results=1
        )
        
        print("ChromaDB连接测试成功")
        client.delete_collection("test_collection")
        return True
        
    except Exception as e:
        print(f"ChromaDB连接测试失败: {e}")
        return False

if __name__ == "__main__":
    import time
    
    print("开始修复ChromaDB...")
    
    # 检查ChromaDB安装
    try:
        import chromadb
        print(f"ChromaDB版本: {chromadb.__version__}")
    except ImportError:
        print("未安装ChromaDB，请先安装: pip install chromadb")
        exit(1)
    
    # 执行修复
    success = check_and_fix_chromadb()
    
    if success:
        print("ChromaDB修复完成，正在测试连接...")
        if test_chromadb_connection():
            print("✅ ChromaDB修复和测试全部完成")
        else:
            print("⚠️ ChromaDB修复完成，但连接测试失败")
    else:
        print("❌ ChromaDB修复失败")
        exit(1)