# -*- coding: utf-8 -*-
"""
BabyAGI 核心类测试

测试自定义 BabyAGI 类的任务管理、执行和优先级排序功能。
"""

import unittest
import tempfile
import os
from unittest.mock import patch, MagicMock, Mock
from datetime import datetime

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from custom_babyagi import CustomBabyAGI, Task


class TestTask(unittest.TestCase):
    """任务数据类测试"""
    
    def test_task_creation(self):
        """测试任务创建"""
        task = Task(
            id="test-1",
            description="测试任务",
            priority=1
        )
        
        self.assertEqual(task.id, "test-1")
        self.assertEqual(task.description, "测试任务")
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.status, "pending")
        self.assertIsInstance(task.created_at, datetime)
        
    def test_task_string_representation(self):
        """测试任务字符串表示"""
        task = Task(
            id="test-1",
            description="测试任务",
            priority=1
        )
        
        task_str = str(task)
        self.assertIn("test-1", task_str)
        self.assertIn("测试任务", task_str)
        self.assertIn("priority=1", task_str)
        
    def test_task_to_dict(self):
        """测试任务转换为字典"""
        task = Task(
            id="test-1",
            description="测试任务",
            priority=1,
            result="任务结果"
        )
        
        task_dict = task.to_dict()
        
        self.assertEqual(task_dict["id"], "test-1")
        self.assertEqual(task_dict["description"], "测试任务")
        self.assertEqual(task_dict["priority"], 1)
        self.assertEqual(task_dict["result"], "任务结果")
        self.assertIn("created_at", task_dict)
        
    def test_task_from_dict(self):
        """测试从字典创建任务"""
        task_data = {
            "id": "test-1",
            "description": "测试任务",
            "priority": 1,
            "status": "completed",
            "result": "任务结果",
            "created_at": "2024-01-01T00:00:00"
        }
        
        task = Task.from_dict(task_data)
        
        self.assertEqual(task.id, "test-1")
        self.assertEqual(task.description, "测试任务")
        self.assertEqual(task.priority, 1)
        self.assertEqual(task.status, "completed")
        self.assertEqual(task.result, "任务结果")


class TestCustomBabyAGI(unittest.TestCase):
    """自定义 BabyAGI 类测试"""
    
    def setUp(self):
        """测试前准备"""
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            
        # Mock 配置
        self.mock_config = MagicMock()
        self.mock_config.LLM_PROVIDER = "openai"
        self.mock_config.OPENAI_API_KEY = "test-key"
        self.mock_config.LLM_MODEL = "gpt-3.5-turbo"
        self.mock_config.VECTOR_DB_TYPE = "chromadb"
        self.mock_config.CHROMA_PERSIST_DIRECTORY = self.temp_dir
        self.mock_config.MAX_ITERATIONS = 5
        self.mock_config.TASK_MAX_LENGTH = 1000
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_initialization_openai(self, mock_openai, mock_chromadb):
        """测试使用 OpenAI 初始化"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        self.assertEqual(babyagi.objective, "测试目标")
        self.assertEqual(babyagi.llm_provider, "openai")
        self.assertEqual(babyagi.llm_client, mock_client)
        self.assertEqual(len(babyagi.task_list), 1)
        self.assertEqual(babyagi.task_list[0].description, "初始任务")
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.requests')
    def test_initialization_ollama(self, mock_requests, mock_chromadb):
        """测试使用 Ollama 初始化"""
        self.mock_config.LLM_PROVIDER = "ollama"
        self.mock_config.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        self.assertEqual(babyagi.llm_provider, "ollama")
        self.assertIsNotNone(babyagi.ollama_base_url)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_add_task(self, mock_openai, mock_chromadb):
        """测试添加任务"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        initial_count = len(babyagi.task_list)
        babyagi.add_task("新任务", 2)
        
        self.assertEqual(len(babyagi.task_list), initial_count + 1)
        new_task = babyagi.task_list[-1]
        self.assertEqual(new_task.description, "新任务")
        self.assertEqual(new_task.priority, 2)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_get_next_task(self, mock_openai, mock_chromadb):
        """测试获取下一个任务"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加不同优先级的任务
        babyagi.add_task("低优先级任务", 3)
        babyagi.add_task("高优先级任务", 1)
        
        next_task = babyagi.get_next_task()
        
        # 应该返回优先级最高（数字最小）的任务
        self.assertEqual(next_task.priority, 1)
        self.assertEqual(next_task.description, "高优先级任务")
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_get_next_task_empty_list(self, mock_openai, mock_chromadb):
        """测试空任务列表获取下一个任务"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 清空任务列表
        babyagi.task_list = []
        
        next_task = babyagi.get_next_task()
        self.assertIsNone(next_task)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_execute_task_openai(self, mock_openai, mock_chromadb):
        """测试使用 OpenAI 执行任务"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "任务执行结果"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="测试任务", priority=1)
        result = babyagi.execute_task(task)
        
        self.assertEqual(result, "任务执行结果")
        mock_client.chat.completions.create.assert_called_once()
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.requests')
    def test_execute_task_ollama(self, mock_requests, mock_chromadb):
        """测试使用 Ollama 执行任务"""
        self.mock_config.LLM_PROVIDER = "ollama"
        self.mock_config.OLLAMA_BASE_URL = "http://localhost:11434"
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "response": "任务执行结果"
        }
        mock_requests.post.return_value = mock_response
        
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="测试任务", priority=1)
        result = babyagi.execute_task(task)
        
        self.assertEqual(result, "任务执行结果")
        mock_requests.post.assert_called_once()
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_create_new_tasks(self, mock_openai, mock_chromadb):
        """测试创建新任务"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1. 新任务1\n2. 新任务2\n3. 新任务3"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        initial_count = len(babyagi.task_list)
        babyagi.create_new_tasks("任务结果", "任务描述")
        
        # 应该添加了新任务
        self.assertGreater(len(babyagi.task_list), initial_count)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_prioritize_tasks(self, mock_openai, mock_chromadb):
        """测试任务优先级排序"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "1. 高优先级任务\n2. 中优先级任务\n3. 低优先级任务"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加一些任务
        babyagi.add_task("任务1", 3)
        babyagi.add_task("任务2", 1)
        babyagi.add_task("任务3", 2)
        
        babyagi.prioritize_tasks()
        
        # 验证任务已按优先级排序
        priorities = [task.priority for task in babyagi.task_list]
        self.assertEqual(priorities, sorted(priorities))
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_get_context(self, mock_openai, mock_chromadb):
        """测试获取上下文"""
        mock_openai.return_value = MagicMock()
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {
            "documents": [["相关文档1", "相关文档2"]],
            "metadatas": [[{"task": "任务1"}, {"task": "任务2"}]]
        }
        
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        context = babyagi.get_context("查询文本")
        
        self.assertIn("相关文档1", context)
        self.assertIn("相关文档2", context)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_store_result(self, mock_openai, mock_chromadb):
        """测试存储结果"""
        mock_openai.return_value = MagicMock()
        
        mock_collection = MagicMock()
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="测试任务", priority=1)
        babyagi.store_result(task, "任务结果")
        
        # 验证结果已存储到向量数据库
        mock_collection.add.assert_called_once()
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_run_single_iteration(self, mock_openai, mock_chromadb):
        """测试运行单次迭代"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "任务执行结果"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        initial_count = len(babyagi.task_list)
        result = babyagi.run_single_iteration()
        
        self.assertIsNotNone(result)
        self.assertIn("task", result)
        self.assertIn("result", result)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_run_with_max_iterations(self, mock_openai, mock_chromadb):
        """测试运行最大迭代次数"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "任务执行结果"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        self.mock_config.MAX_ITERATIONS = 2
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        results = babyagi.run()
        
        # 应该执行指定次数的迭代
        self.assertEqual(len(results), 2)
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_get_task_list(self, mock_openai, mock_chromadb):
        """测试获取任务列表"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        babyagi.add_task("任务1", 1)
        babyagi.add_task("任务2", 2)
        
        task_list = babyagi.get_task_list()
        
        self.assertEqual(len(task_list), 3)  # 包括初始任务
        self.assertIsInstance(task_list[0], dict)
        self.assertIn("id", task_list[0])
        self.assertIn("description", task_list[0])
        self.assertIn("priority", task_list[0])
        
    @patch('custom_babyagi.chromadb')
    @patch('custom_babyagi.OpenAI')
    def test_get_results(self, mock_openai, mock_chromadb):
        """测试获取结果"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        babyagi = CustomBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加一些结果
        babyagi.results.append({"task": "任务1", "result": "结果1"})
        babyagi.results.append({"task": "任务2", "result": "结果2"})
        
        results = babyagi.get_results()
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["task"], "任务1")
        self.assertEqual(results[1]["result"], "结果2")


if __name__ == '__main__':
    unittest.main()