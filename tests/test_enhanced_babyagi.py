# -*- coding: utf-8 -*-
"""
增强版 BabyAGI 测试

测试集成工具系统的增强版 BabyAGI 类功能。
"""

import unittest
import tempfile
from unittest.mock import patch, MagicMock, Mock

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from enhanced_babyagi import EnhancedBabyAGI
from custom_babyagi import Task
from tools import BaseTool, ToolRegistry


class MockTool(BaseTool):
    """测试用的模拟工具"""
    
    def __init__(self):
        super().__init__()
        self.name = "mock_tool"
        self.description = "模拟工具用于测试"
        
    def execute(self, **kwargs):
        """执行模拟操作"""
        action = kwargs.get('action', 'default')
        if action == 'error':
            raise Exception("模拟错误")
        return f"模拟工具执行结果: {action}"


class TestEnhancedBabyAGI(unittest.TestCase):
    """增强版 BabyAGI 类测试"""
    
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
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_initialization(self, mock_openai, mock_chromadb):
        """测试初始化"""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        self.assertEqual(enhanced_babyagi.objective, "测试目标")
        self.assertIsInstance(enhanced_babyagi.tool_registry, ToolRegistry)
        self.assertGreater(len(enhanced_babyagi.tool_registry.tools), 0)
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_select_tool_for_task(self, mock_openai, mock_chromadb):
        """测试为任务选择工具"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "mock_tool"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        task = Task(id="test-1", description="需要使用工具的任务", priority=1)
        selected_tool = enhanced_babyagi.select_tool_for_task(task)
        
        self.assertEqual(selected_tool, "mock_tool")
        mock_client.chat.completions.create.assert_called_once()
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_select_tool_for_task_no_tool(self, mock_openai, mock_chromadb):
        """测试任务不需要工具的情况"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "none"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="简单的思考任务", priority=1)
        selected_tool = enhanced_babyagi.select_tool_for_task(task)
        
        self.assertIsNone(selected_tool)
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_generate_tool_parameters(self, mock_openai, mock_chromadb):
        """测试生成工具参数"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = '{"action": "test", "data": "测试数据"}'
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="需要参数的任务", priority=1)
        mock_tool = MockTool()
        
        params = enhanced_babyagi.generate_tool_parameters(task, mock_tool)
        
        self.assertIsInstance(params, dict)
        self.assertEqual(params["action"], "test")
        self.assertEqual(params["data"], "测试数据")
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_generate_tool_parameters_invalid_json(self, mock_openai, mock_chromadb):
        """测试生成无效 JSON 参数的情况"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "无效的 JSON"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="需要参数的任务", priority=1)
        mock_tool = MockTool()
        
        params = enhanced_babyagi.generate_tool_parameters(task, mock_tool)
        
        self.assertEqual(params, {})
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_interpret_tool_result(self, mock_openai, mock_chromadb):
        """测试解释工具结果"""
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "工具执行成功，结果已处理"
        mock_client.chat.completions.create.return_value = mock_response
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="测试任务", priority=1)
        tool_result = "模拟工具执行结果"
        
        interpretation = enhanced_babyagi.interpret_tool_result(task, tool_result)
        
        self.assertEqual(interpretation, "工具执行成功，结果已处理")
        mock_client.chat.completions.create.assert_called_once()
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_execute_task_with_tool(self, mock_openai, mock_chromadb):
        """测试使用工具执行任务"""
        mock_client = MagicMock()
        
        # Mock 工具选择响应
        tool_selection_response = MagicMock()
        tool_selection_response.choices = [MagicMock()]
        tool_selection_response.choices[0].message.content = "mock_tool"
        
        # Mock 参数生成响应
        param_generation_response = MagicMock()
        param_generation_response.choices = [MagicMock()]
        param_generation_response.choices[0].message.content = '{"action": "test"}'
        
        # Mock 结果解释响应
        interpretation_response = MagicMock()
        interpretation_response.choices = [MagicMock()]
        interpretation_response.choices[0].message.content = "任务完成，工具执行成功"
        
        mock_client.chat.completions.create.side_effect = [
            tool_selection_response,
            param_generation_response,
            interpretation_response
        ]
        mock_openai.return_value = mock_client
        
        mock_chroma_client = MagicMock()
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        task = Task(id="test-1", description="需要工具的任务", priority=1)
        result = enhanced_babyagi.execute_task(task)
        
        self.assertEqual(result, "任务完成，工具执行成功")
        self.assertEqual(mock_client.chat.completions.create.call_count, 3)
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_execute_task_tool_error(self, mock_openai, mock_chromadb):
        """测试工具执行错误的情况"""
        mock_client = MagicMock()
        
        # Mock 工具选择响应
        tool_selection_response = MagicMock()
        tool_selection_response.choices = [MagicMock()]
        tool_selection_response.choices[0].message.content = "mock_tool"
        
        # Mock 参数生成响应（会导致工具错误）
        param_generation_response = MagicMock()
        param_generation_response.choices = [MagicMock()]
        param_generation_response.choices[0].message.content = '{"action": "error"}'
        
        # Mock LLM 执行响应（作为后备）
        llm_response = MagicMock()
        llm_response.choices = [MagicMock()]
        llm_response.choices[0].message.content = "LLM 处理结果"
        
        mock_client.chat.completions.create.side_effect = [
            tool_selection_response,
            param_generation_response,
            llm_response
        ]
        mock_openai.return_value = mock_client
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        task = Task(id="test-1", description="会导致工具错误的任务", priority=1)
        result = enhanced_babyagi.execute_task(task)
        
        # 应该回退到 LLM 处理
        self.assertEqual(result, "LLM 处理结果")
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_execute_task_no_tool_needed(self, mock_openai, mock_chromadb):
        """测试不需要工具的任务执行"""
        mock_client = MagicMock()
        
        # Mock 工具选择响应（不需要工具）
        tool_selection_response = MagicMock()
        tool_selection_response.choices = [MagicMock()]
        tool_selection_response.choices[0].message.content = "none"
        
        # Mock LLM 执行响应
        llm_response = MagicMock()
        llm_response.choices = [MagicMock()]
        llm_response.choices[0].message.content = "LLM 直接处理结果"
        
        mock_client.chat.completions.create.side_effect = [
            tool_selection_response,
            llm_response
        ]
        mock_openai.return_value = mock_client
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        task = Task(id="test-1", description="简单的思考任务", priority=1)
        result = enhanced_babyagi.execute_task(task)
        
        self.assertEqual(result, "LLM 直接处理结果")
        self.assertEqual(mock_client.chat.completions.create.call_count, 2)
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_get_available_tools(self, mock_openai, mock_chromadb):
        """测试获取可用工具列表"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        tools = enhanced_babyagi.get_available_tools()
        
        self.assertIsInstance(tools, list)
        self.assertGreater(len(tools), 0)
        
        # 检查是否包含模拟工具
        tool_names = [tool["name"] for tool in tools]
        self.assertIn("mock_tool", tool_names)
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_execute_tool_directly(self, mock_openai, mock_chromadb):
        """测试直接执行工具"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        result = enhanced_babyagi.execute_tool("mock_tool", action="test")
        
        self.assertEqual(result, "模拟工具执行结果: test")
        
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_execute_tool_not_found(self, mock_openai, mock_chromadb):
        """测试执行不存在的工具"""
        mock_openai.return_value = MagicMock()
        mock_chromadb.PersistentClient.return_value = MagicMock()
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        with self.assertRaises(ValueError):
            enhanced_babyagi.execute_tool("nonexistent_tool")
            
    @patch('enhanced_babyagi.chromadb')
    @patch('enhanced_babyagi.OpenAI')
    def test_run_single_iteration_with_tools(self, mock_openai, mock_chromadb):
        """测试使用工具的单次迭代运行"""
        mock_client = MagicMock()
        
        # Mock 工具选择响应
        tool_selection_response = MagicMock()
        tool_selection_response.choices = [MagicMock()]
        tool_selection_response.choices[0].message.content = "mock_tool"
        
        # Mock 参数生成响应
        param_generation_response = MagicMock()
        param_generation_response.choices = [MagicMock()]
        param_generation_response.choices[0].message.content = '{"action": "test"}'
        
        # Mock 结果解释响应
        interpretation_response = MagicMock()
        interpretation_response.choices = [MagicMock()]
        interpretation_response.choices[0].message.content = "任务完成"
        
        mock_client.chat.completions.create.side_effect = [
            tool_selection_response,
            param_generation_response,
            interpretation_response
        ]
        mock_openai.return_value = mock_client
        
        mock_collection = MagicMock()
        mock_collection.query.return_value = {"documents": [[]], "metadatas": [[]]}
        mock_chroma_client = MagicMock()
        mock_chroma_client.get_or_create_collection.return_value = mock_collection
        mock_chromadb.PersistentClient.return_value = mock_chroma_client
        
        enhanced_babyagi = EnhancedBabyAGI(
            objective="测试目标",
            initial_task="初始任务",
            config=self.mock_config
        )
        
        # 添加模拟工具
        mock_tool = MockTool()
        enhanced_babyagi.tool_registry.register_tool(mock_tool)
        
        result = enhanced_babyagi.run_single_iteration()
        
        self.assertIsNotNone(result)
        self.assertIn("task", result)
        self.assertIn("result", result)
        self.assertEqual(result["result"], "任务完成")


if __name__ == '__main__':
    unittest.main()