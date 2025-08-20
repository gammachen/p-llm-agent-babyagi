# -*- coding: utf-8 -*-
"""
Flask API 应用测试

测试 BabyAGI Web API 接口的功能。
"""

import unittest
import json
import tempfile
from unittest.mock import patch, MagicMock

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app import app, running_agents, APIResponse


class TestFlaskApp(unittest.TestCase):
    """Flask 应用测试"""
    
    def setUp(self):
        """测试前准备"""
        self.app = app
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
        
        # 清空运行中的代理
        running_agents.clear()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            self.temp_dir = temp_dir
            
    def test_health_check(self):
        """测试健康检查接口"""
        response = self.client.get('/api/health')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        
    def test_system_info(self):
        """测试系统信息接口"""
        response = self.client.get('/api/info')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('version', data)
        self.assertIn('description', data)
        self.assertIn('features', data)
        
    def test_list_tools(self):
        """测试工具列表接口"""
        with patch('app.EnhancedBabyAGI') as mock_babyagi:
            mock_instance = MagicMock()
            mock_instance.get_available_tools.return_value = [
                {"name": "command_executor", "description": "执行命令"},
                {"name": "file_manager", "description": "文件管理"}
            ]
            mock_babyagi.return_value = mock_instance
            
            response = self.client.get('/api/tools')
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertIn('tools', data)
            self.assertEqual(len(data['tools']), 2)
            
    def test_execute_tool(self):
        """测试工具执行接口"""
        with patch('app.EnhancedBabyAGI') as mock_babyagi:
            mock_instance = MagicMock()
            mock_instance.execute_tool.return_value = "工具执行结果"
            mock_babyagi.return_value = mock_instance
            
            payload = {
                "tool_name": "command_executor",
                "parameters": {"command": "ls"}
            }
            
            response = self.client.post(
                '/api/tools/execute',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 200)
            data = json.loads(response.data)
            self.assertEqual(data['result'], "工具执行结果")
            
    def test_execute_tool_missing_parameters(self):
        """测试工具执行缺少参数"""
        payload = {"tool_name": "command_executor"}
        
        response = self.client.post(
            '/api/tools/execute',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_execute_tool_error(self):
        """测试工具执行错误"""
        with patch('app.EnhancedBabyAGI') as mock_babyagi:
            mock_instance = MagicMock()
            mock_instance.execute_tool.side_effect = Exception("工具执行失败")
            mock_babyagi.return_value = mock_instance
            
            payload = {
                "tool_name": "command_executor",
                "parameters": {"command": "invalid_command"}
            }
            
            response = self.client.post(
                '/api/tools/execute',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
            self.assertEqual(response.status_code, 500)
            data = json.loads(response.data)
            self.assertIn('error', data)
            
    def test_create_agent(self):
        """测试创建代理接口"""
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        data = json.loads(response.data)
        self.assertIn('agent_id', data)
        self.assertIn('objective', data)
        self.assertIn('initial_task', data)
        
        # 验证代理已添加到运行列表
        agent_id = data['agent_id']
        self.assertIn(agent_id, running_agents)
        
    def test_create_agent_missing_parameters(self):
        """测试创建代理缺少参数"""
        payload = {"objective": "测试目标"}
        
        response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_list_agents(self):
        """测试代理列表接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        # 获取代理列表
        response = self.client.get('/api/agents')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('agents', data)
        self.assertEqual(len(data['agents']), 1)
        
    def test_get_agent(self):
        """测试获取单个代理接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 获取代理信息
        response = self.client.get(f'/api/agents/{agent_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['agent_id'], agent_id)
        self.assertEqual(data['objective'], "测试目标")
        
    def test_get_agent_not_found(self):
        """测试获取不存在的代理"""
        response = self.client.get('/api/agents/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    @patch('app.threading.Thread')
    def test_start_agent(self, mock_thread):
        """测试启动代理接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 启动代理
        response = self.client.post(f'/api/agents/{agent_id}/start')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # 验证线程已启动
        mock_thread.assert_called_once()
        
    def test_start_agent_not_found(self):
        """测试启动不存在的代理"""
        response = self.client.post('/api/agents/nonexistent/start')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_start_agent_already_running(self):
        """测试启动已运行的代理"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 设置代理为运行状态
        running_agents[agent_id]['status'] = 'running'
        
        # 尝试再次启动
        response = self.client.post(f'/api/agents/{agent_id}/start')
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_stop_agent(self):
        """测试停止代理接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 设置代理为运行状态
        running_agents[agent_id]['status'] = 'running'
        
        # 停止代理
        response = self.client.post(f'/api/agents/{agent_id}/stop')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # 验证代理状态已更新
        self.assertEqual(running_agents[agent_id]['status'], 'stopped')
        
    def test_stop_agent_not_found(self):
        """测试停止不存在的代理"""
        response = self.client.post('/api/agents/nonexistent/stop')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_get_agent_results(self):
        """测试获取代理结果接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 添加一些模拟结果
        running_agents[agent_id]['instance'].results = [
            {"task": "任务1", "result": "结果1"},
            {"task": "任务2", "result": "结果2"}
        ]
        
        # 获取结果
        response = self.client.get(f'/api/agents/{agent_id}/results')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('results', data)
        self.assertEqual(len(data['results']), 2)
        
    def test_delete_agent(self):
        """测试删除代理接口"""
        # 先创建一个代理
        payload = {
            "objective": "测试目标",
            "initial_task": "初始任务"
        }
        
        create_response = self.client.post(
            '/api/agents',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        agent_id = json.loads(create_response.data)['agent_id']
        
        # 删除代理
        response = self.client.delete(f'/api/agents/{agent_id}')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)
        
        # 验证代理已从列表中移除
        self.assertNotIn(agent_id, running_agents)
        
    def test_delete_agent_not_found(self):
        """测试删除不存在的代理"""
        response = self.client.delete('/api/agents/nonexistent')
        
        self.assertEqual(response.status_code, 404)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    @patch('app.EnhancedBabyAGI')
    def test_quick_execute(self, mock_babyagi):
        """测试快速执行接口"""
        mock_instance = MagicMock()
        mock_instance.run_single_iteration.return_value = {
            "task": "测试任务",
            "result": "执行结果"
        }
        mock_babyagi.return_value = mock_instance
        
        payload = {
            "objective": "测试目标",
            "task": "执行任务"
        }
        
        response = self.client.post(
            '/api/execute',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('result', data)
        self.assertEqual(data['result']['task'], "测试任务")
        
    def test_quick_execute_missing_parameters(self):
        """测试快速执行缺少参数"""
        payload = {"objective": "测试目标"}
        
        response = self.client.post(
            '/api/execute',
            data=json.dumps(payload),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_get_stats(self):
        """测试统计信息接口"""
        # 创建几个代理
        for i in range(3):
            payload = {
                "objective": f"测试目标{i}",
                "initial_task": f"初始任务{i}"
            }
            
            self.client.post(
                '/api/agents',
                data=json.dumps(payload),
                content_type='application/json'
            )
            
        response = self.client.get('/api/stats')
        
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('total_agents', data)
        self.assertIn('running_agents', data)
        self.assertIn('completed_tasks', data)
        self.assertEqual(data['total_agents'], 3)
        
    def test_api_response_helper(self):
        """测试 API 响应辅助类"""
        # 测试成功响应
        success_response = APIResponse.success({"key": "value"})
        self.assertEqual(success_response[1], 200)
        
        success_data = json.loads(success_response[0].data)
        self.assertTrue(success_data['success'])
        self.assertEqual(success_data['data']['key'], "value")
        
        # 测试错误响应
        error_response = APIResponse.error("测试错误", 400)
        self.assertEqual(error_response[1], 400)
        
        error_data = json.loads(error_response[0].data)
        self.assertFalse(error_data['success'])
        self.assertEqual(error_data['error'], "测试错误")
        
    def test_web_interface_routes(self):
        """测试 Web 界面路由"""
        # 测试主页
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        
        # 测试静态文件路由（模拟）
        with patch('app.send_from_directory') as mock_send:
            mock_send.return_value = "static file content"
            response = self.client.get('/static/css/style.css')
            mock_send.assert_called_once()
            
    def test_cors_headers(self):
        """测试 CORS 头部"""
        response = self.client.get('/api/health')
        
        # 检查 CORS 头部是否存在
        self.assertIn('Access-Control-Allow-Origin', response.headers)
        
    def test_json_error_handling(self):
        """测试 JSON 错误处理"""
        # 发送无效的 JSON
        response = self.client.post(
            '/api/agents',
            data="invalid json",
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)
        
    def test_content_type_validation(self):
        """测试内容类型验证"""
        # 发送非 JSON 内容类型
        response = self.client.post(
            '/api/agents',
            data="objective=test&initial_task=test",
            content_type='application/x-www-form-urlencoded'
        )
        
        # 应该仍然能处理，但可能返回错误
        self.assertIn(response.status_code, [400, 415])


if __name__ == '__main__':
    unittest.main()