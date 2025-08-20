# -*- coding: utf-8 -*-
"""
工具系统测试

测试各种工具的功能和工具注册系统。
"""

import unittest
import os
import tempfile
import json
from unittest.mock import patch, MagicMock, mock_open

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from tools import (
    BaseTool, CommandExecutor, FileManager, WebSearcher, 
    HTTPClient, CodeAnalyzer, ToolRegistry
)


class TestBaseTool(unittest.TestCase):
    """基础工具类测试"""
    
    def test_base_tool_initialization(self):
        """测试基础工具初始化"""
        tool = BaseTool("test_tool", "测试工具")
        self.assertEqual(tool.name, "test_tool")
        self.assertEqual(tool.description, "测试工具")
        
    def test_base_tool_execute_not_implemented(self):
        """测试基础工具执行方法未实现"""
        tool = BaseTool("test_tool", "测试工具")
        with self.assertRaises(NotImplementedError):
            tool.execute()
            
    def test_base_tool_string_representation(self):
        """测试基础工具字符串表示"""
        tool = BaseTool("test_tool", "测试工具")
        self.assertEqual(str(tool), "test_tool: 测试工具")


class TestCommandExecutor(unittest.TestCase):
    """命令执行器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.executor = CommandExecutor()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.executor.name, "command_executor")
        self.assertIn("执行系统命令", self.executor.description)
        
    @patch('subprocess.run')
    def test_execute_success(self, mock_run):
        """测试命令执行成功"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Hello World",
            stderr=""
        )
        
        result = self.executor.execute(command="echo 'Hello World'")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["output"], "Hello World")
        self.assertEqual(result["return_code"], 0)
        
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run):
        """测试命令执行失败"""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="",
            stderr="Command not found"
        )
        
        result = self.executor.execute(command="invalid_command")
        
        self.assertFalse(result["success"])
        self.assertEqual(result["error"], "Command not found")
        self.assertEqual(result["return_code"], 1)
        
    def test_execute_missing_command(self):
        """测试缺少命令参数"""
        result = self.executor.execute()
        
        self.assertFalse(result["success"])
        self.assertIn("命令参数是必需的", result["error"])
        
    @patch('subprocess.run')
    def test_execute_with_timeout(self, mock_run):
        """测试带超时的命令执行"""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Success",
            stderr=""
        )
        
        result = self.executor.execute(command="sleep 1", timeout=5)
        
        self.assertTrue(result["success"])
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertEqual(kwargs.get('timeout'), 5)


class TestFileManager(unittest.TestCase):
    """文件管理器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.file_manager = FileManager()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.file_manager.name, "file_manager")
        self.assertIn("文件操作", self.file_manager.description)
        
    def test_read_file_success(self):
        """测试读取文件成功"""
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("Test content")
            temp_file = f.name
            
        try:
            result = self.file_manager.execute(action="read", file_path=temp_file)
            
            self.assertTrue(result["success"])
            self.assertEqual(result["content"], "Test content")
        finally:
            os.unlink(temp_file)
            
    def test_read_file_not_found(self):
        """测试读取不存在的文件"""
        result = self.file_manager.execute(action="read", file_path="/nonexistent/file.txt")
        
        self.assertFalse(result["success"])
        self.assertIn("文件不存在", result["error"])
        
    def test_write_file_success(self):
        """测试写入文件成功"""
        with tempfile.NamedTemporaryFile(delete=False) as f:
            temp_file = f.name
            
        try:
            result = self.file_manager.execute(
                action="write", 
                file_path=temp_file, 
                content="New content"
            )
            
            self.assertTrue(result["success"])
            
            # 验证文件内容
            with open(temp_file, 'r') as f:
                content = f.read()
            self.assertEqual(content, "New content")
        finally:
            os.unlink(temp_file)
            
    def test_list_directory_success(self):
        """测试列出目录成功"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试文件
            test_file = os.path.join(temp_dir, "test.txt")
            with open(test_file, 'w') as f:
                f.write("test")
                
            result = self.file_manager.execute(action="list", file_path=temp_dir)
            
            self.assertTrue(result["success"])
            self.assertIn("test.txt", result["files"])
            
    def test_invalid_action(self):
        """测试无效操作"""
        result = self.file_manager.execute(action="invalid_action")
        
        self.assertFalse(result["success"])
        self.assertIn("不支持的操作", result["error"])
        
    def test_missing_parameters(self):
        """测试缺少参数"""
        result = self.file_manager.execute(action="read")
        
        self.assertFalse(result["success"])
        self.assertIn("文件路径是必需的", result["error"])


class TestWebSearcher(unittest.TestCase):
    """网络搜索器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.searcher = WebSearcher()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.searcher.name, "web_searcher")
        self.assertIn("网络搜索", self.searcher.description)
        
    @patch('requests.get')
    def test_search_success(self, mock_get):
        """测试搜索成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "results": [
                {"title": "Test Result", "url": "http://example.com", "snippet": "Test snippet"}
            ]
        }
        mock_get.return_value = mock_response
        
        result = self.searcher.execute(query="test query")
        
        self.assertTrue(result["success"])
        self.assertEqual(len(result["results"]), 1)
        self.assertEqual(result["results"][0]["title"], "Test Result")
        
    def test_search_missing_query(self):
        """测试缺少查询参数"""
        result = self.searcher.execute()
        
        self.assertFalse(result["success"])
        self.assertIn("查询参数是必需的", result["error"])
        
    @patch('requests.get')
    def test_search_request_failure(self, mock_get):
        """测试搜索请求失败"""
        mock_get.side_effect = Exception("Network error")
        
        result = self.searcher.execute(query="test query")
        
        self.assertFalse(result["success"])
        self.assertIn("搜索失败", result["error"])


class TestHTTPClient(unittest.TestCase):
    """HTTP 客户端测试"""
    
    def setUp(self):
        """测试前准备"""
        self.client = HTTPClient()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.client.name, "http_client")
        self.assertIn("HTTP 请求", self.client.description)
        
    @patch('requests.request')
    def test_get_request_success(self, mock_request):
        """测试 GET 请求成功"""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "Success"
        mock_response.headers = {"Content-Type": "text/plain"}
        mock_request.return_value = mock_response
        
        result = self.client.execute(method="GET", url="http://example.com")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["status_code"], 200)
        self.assertEqual(result["content"], "Success")
        
    def test_missing_url(self):
        """测试缺少 URL 参数"""
        result = self.client.execute(method="GET")
        
        self.assertFalse(result["success"])
        self.assertIn("URL 是必需的", result["error"])
        
    @patch('requests.request')
    def test_request_failure(self, mock_request):
        """测试请求失败"""
        mock_request.side_effect = Exception("Connection error")
        
        result = self.client.execute(method="GET", url="http://example.com")
        
        self.assertFalse(result["success"])
        self.assertIn("HTTP 请求失败", result["error"])


class TestCodeAnalyzer(unittest.TestCase):
    """代码分析器测试"""
    
    def setUp(self):
        """测试前准备"""
        self.analyzer = CodeAnalyzer()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertEqual(self.analyzer.name, "code_analyzer")
        self.assertIn("代码分析", self.analyzer.description)
        
    def test_analyze_python_code(self):
        """测试分析 Python 代码"""
        python_code = """
def hello_world():
    print("Hello, World!")
    return "success"

class TestClass:
    def __init__(self):
        self.value = 42
"""
        
        result = self.analyzer.execute(code=python_code, language="python")
        
        self.assertTrue(result["success"])
        self.assertIn("functions", result["analysis"])
        self.assertIn("classes", result["analysis"])
        self.assertEqual(len(result["analysis"]["functions"]), 1)
        self.assertEqual(len(result["analysis"]["classes"]), 1)
        
    def test_analyze_javascript_code(self):
        """测试分析 JavaScript 代码"""
        js_code = """
function greet(name) {
    return `Hello, ${name}!`;
}

const add = (a, b) => a + b;

class Calculator {
    constructor() {
        this.result = 0;
    }
}
"""
        
        result = self.analyzer.execute(code=js_code, language="javascript")
        
        self.assertTrue(result["success"])
        self.assertIn("functions", result["analysis"])
        self.assertIn("classes", result["analysis"])
        
    def test_analyze_unsupported_language(self):
        """测试分析不支持的语言"""
        result = self.analyzer.execute(code="some code", language="unsupported")
        
        self.assertFalse(result["success"])
        self.assertIn("不支持的语言", result["error"])
        
    def test_missing_code_parameter(self):
        """测试缺少代码参数"""
        result = self.analyzer.execute(language="python")
        
        self.assertFalse(result["success"])
        self.assertIn("代码参数是必需的", result["error"])


class TestToolRegistry(unittest.TestCase):
    """工具注册表测试"""
    
    def setUp(self):
        """测试前准备"""
        self.registry = ToolRegistry()
        
    def test_initialization(self):
        """测试初始化"""
        self.assertIsInstance(self.registry.tools, dict)
        
    def test_register_tool(self):
        """测试注册工具"""
        tool = BaseTool("test_tool", "测试工具")
        tool.execute = lambda **kwargs: {"success": True}
        
        self.registry.register(tool)
        
        self.assertIn("test_tool", self.registry.tools)
        self.assertEqual(self.registry.tools["test_tool"], tool)
        
    def test_get_tool_success(self):
        """测试获取工具成功"""
        tool = BaseTool("test_tool", "测试工具")
        tool.execute = lambda **kwargs: {"success": True}
        
        self.registry.register(tool)
        retrieved_tool = self.registry.get_tool("test_tool")
        
        self.assertEqual(retrieved_tool, tool)
        
    def test_get_tool_not_found(self):
        """测试获取不存在的工具"""
        retrieved_tool = self.registry.get_tool("nonexistent_tool")
        
        self.assertIsNone(retrieved_tool)
        
    def test_list_tools(self):
        """测试列出工具"""
        tool1 = BaseTool("tool1", "工具1")
        tool2 = BaseTool("tool2", "工具2")
        
        self.registry.register(tool1)
        self.registry.register(tool2)
        
        tools_list = self.registry.list_tools()
        
        self.assertEqual(len(tools_list), 2)
        self.assertIn({"name": "tool1", "description": "工具1"}, tools_list)
        self.assertIn({"name": "tool2", "description": "工具2"}, tools_list)
        
    def test_execute_tool_success(self):
        """测试执行工具成功"""
        tool = BaseTool("test_tool", "测试工具")
        tool.execute = lambda **kwargs: {"success": True, "result": "test result"}
        
        self.registry.register(tool)
        result = self.registry.execute_tool("test_tool", param1="value1")
        
        self.assertTrue(result["success"])
        self.assertEqual(result["result"], "test result")
        
    def test_execute_tool_not_found(self):
        """测试执行不存在的工具"""
        result = self.registry.execute_tool("nonexistent_tool")
        
        self.assertFalse(result["success"])
        self.assertIn("工具不存在", result["error"])
        
    def test_execute_tool_exception(self):
        """测试工具执行异常"""
        tool = BaseTool("test_tool", "测试工具")
        tool.execute = lambda **kwargs: exec('raise Exception("Test error")')
        
        self.registry.register(tool)
        result = self.registry.execute_tool("test_tool")
        
        self.assertFalse(result["success"])
        self.assertIn("工具执行失败", result["error"])


if __name__ == '__main__':
    unittest.main()