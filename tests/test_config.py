# -*- coding: utf-8 -*-
"""
配置模块测试

测试配置管理类的功能，包括默认值、环境变量覆盖、验证等。
"""

import unittest
import os
from unittest.mock import patch

# 添加项目根目录到路径
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestConfig(unittest.TestCase):
    """配置类测试"""
    
    def test_default_values(self):
        """测试默认配置值"""
        # 由于 Config 类在导入时就读取了环境变量，我们需要重新导入
        # 清除所有可能影响测试的环境变量
        env_vars_to_clear = {
            'LLM_PROVIDER': None,
            'OPENAI_API_KEY': None,
            'OPENAI_MODEL': None,
            'VECTOR_DB': None,
            'MAX_ITERATIONS': None,
            'LOG_LEVEL': None,
            'API_PORT': None
        }
        with patch.dict(os.environ, env_vars_to_clear, clear=True):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            self.assertEqual(Config.LLM_PROVIDER, "openai")
            self.assertEqual(Config.OPENAI_MODEL, "gpt-3.5-turbo")
            self.assertEqual(Config.VECTOR_DB, "chroma")
            self.assertEqual(Config.MAX_ITERATIONS, 5)
            self.assertEqual(Config.LOG_LEVEL, "INFO")
            self.assertEqual(Config.API_PORT, 5000)
            
    def test_environment_variables(self):
        """测试环境变量覆盖"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'ollama',
            'OPENAI_MODEL': 'gpt-4',
            'VECTOR_DB': 'pinecone',
            'MAX_ITERATIONS': '10',
            'LOG_LEVEL': 'DEBUG',
            'API_PORT': '8080'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            self.assertEqual(Config.LLM_PROVIDER, 'ollama')
            self.assertEqual(Config.OPENAI_MODEL, 'gpt-4')
            self.assertEqual(Config.VECTOR_DB, 'pinecone')
            self.assertEqual(Config.MAX_ITERATIONS, 10)
            self.assertEqual(Config.LOG_LEVEL, 'DEBUG')
            self.assertEqual(Config.API_PORT, 8080)
            
    def test_validate_missing_openai_key(self):
        """测试缺少 OpenAI API 密钥时的验证"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': ''  # 明确设置为空字符串
        }, clear=True):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            with self.assertRaises(ValueError) as context:
                Config.validate()
            self.assertIn("OPENAI_API_KEY", str(context.exception))
                
    def test_validate_openai_with_key(self):
        """测试有 OpenAI API 密钥时的验证"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'test-key'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            # 应该不抛出异常
            self.assertTrue(Config.validate())
            
    def test_validate_pinecone_missing_credentials(self):
        """测试 Pinecone 缺少凭据时的验证"""
        with patch.dict(os.environ, {
            'VECTOR_DB': 'pinecone'
        }, clear=True):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            with self.assertRaises(ValueError) as context:
                Config.validate()
            self.assertIn("PINECONE", str(context.exception))
                
    def test_validate_pinecone_with_credentials(self):
        """测试 Pinecone 有凭据时的验证"""
        with patch.dict(os.environ, {
            'VECTOR_DB': 'pinecone',
            'PINECONE_API_KEY': 'test-key',
            'PINECONE_ENVIRONMENT': 'test-env'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            # 应该不抛出异常
            self.assertTrue(Config.validate())
            
    def test_boolean_conversion(self):
        """测试布尔值转换"""
        with patch.dict(os.environ, {
            'API_DEBUG': 'false'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            self.assertFalse(Config.API_DEBUG, "环境变量 'false' 应该转换为 False")
            
        with patch.dict(os.environ, {
            'API_DEBUG': 'true'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            self.assertTrue(Config.API_DEBUG, "环境变量 'true' 应该转换为 True")
            
    def test_integer_conversion(self):
        """测试整数转换"""
        with patch.dict(os.environ, {
            'MAX_ITERATIONS': '15',
            'API_PORT': '8080'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            self.assertEqual(Config.MAX_ITERATIONS, 15)
            self.assertEqual(Config.API_PORT, 8080)
            self.assertIsInstance(Config.MAX_ITERATIONS, int)
            self.assertIsInstance(Config.API_PORT, int)
            
    def test_llm_provider_validation(self):
        """测试 LLM 提供商验证"""
        valid_providers = ['openai', 'ollama']
        
        for provider in valid_providers:
            with patch.dict(os.environ, {
                'LLM_PROVIDER': provider,
                'OPENAI_API_KEY': 'test-key' if provider == 'openai' else ''
            }):
                # 重新导入配置模块
                if 'config' in sys.modules:
                    del sys.modules['config']
                from config import Config
                self.assertEqual(Config.LLM_PROVIDER, provider)
                
    def test_log_level_validation(self):
        """测试日志级别验证"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR']
        
        for level in valid_levels:
            with patch.dict(os.environ, {'LOG_LEVEL': level}):
                # 重新导入配置模块
                if 'config' in sys.modules:
                    del sys.modules['config']
                from config import Config
                self.assertEqual(Config.LOG_LEVEL, level)
                
    def test_vector_db_validation(self):
        """测试向量数据库类型验证"""
        valid_types = ['chroma', 'pinecone']
        
        for db_type in valid_types:
            env_vars = {'VECTOR_DB': db_type}
            if db_type == 'pinecone':
                env_vars.update({
                    'PINECONE_API_KEY': 'test-key',
                    'PINECONE_ENVIRONMENT': 'test-env'
                })
                
            with patch.dict(os.environ, env_vars):
                # 重新导入配置模块
                if 'config' in sys.modules:
                    del sys.modules['config']
                from config import Config
                self.assertEqual(Config.VECTOR_DB, db_type)
                
    def test_file_path_creation(self):
        """测试文件路径创建"""
        with patch.dict(os.environ, {
            'CHROMA_PERSIST_DIR': '/custom/path',
            'LOG_FILE': '/custom/log.txt'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            self.assertEqual(Config.CHROMA_PERSIST_DIR, '/custom/path')
            self.assertEqual(Config.LOG_FILE, '/custom/log.txt')
            
    def test_get_summary(self):
        """测试获取配置摘要"""
        with patch.dict(os.environ, {
            'LLM_PROVIDER': 'openai',
            'OPENAI_MODEL': 'gpt-4',
            'VECTOR_DB': 'chroma',
            'MAX_ITERATIONS': '10',
            'LOG_LEVEL': 'DEBUG'
        }):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            summary = Config.get_summary()
            
            self.assertIsInstance(summary, dict)
            self.assertIn('llm_provider', summary)
            self.assertIn('vector_db', summary)
            self.assertIn('max_iterations', summary)
            self.assertIn('log_level', summary)
            
            self.assertEqual(summary['llm_provider'], 'openai')
            self.assertEqual(summary['vector_db'], 'chroma')
            self.assertEqual(summary['max_iterations'], 10)
            self.assertEqual(summary['log_level'], 'DEBUG')
            
            # 确保敏感信息不在摘要中
            self.assertNotIn('OPENAI_API_KEY', str(summary))
            self.assertNotIn('PINECONE_API_KEY', str(summary))
            
    def test_complete_configuration(self):
        """测试完整配置"""
        complete_env = {
            'LLM_PROVIDER': 'openai',
            'OPENAI_API_KEY': 'test-key',
            'OPENAI_MODEL': 'gpt-4',
            'VECTOR_DB': 'chroma',
            'CHROMA_PERSIST_DIR': './test_chroma',
            'MAX_ITERATIONS': '20',
            'LOG_LEVEL': 'WARNING',
            'API_PORT': '9000',
            'API_DEBUG': 'false'
        }
        
        with patch.dict(os.environ, complete_env):
            # 重新导入配置模块
            if 'config' in sys.modules:
                del sys.modules['config']
            from config import Config
            
            self.assertEqual(Config.LLM_PROVIDER, 'openai')
            self.assertEqual(Config.OPENAI_API_KEY, 'test-key')
            self.assertEqual(Config.OPENAI_MODEL, 'gpt-4')
            self.assertEqual(Config.VECTOR_DB, 'chroma')
            self.assertEqual(Config.CHROMA_PERSIST_DIR, './test_chroma')
            self.assertEqual(Config.MAX_ITERATIONS, 20)
            self.assertEqual(Config.LOG_LEVEL, 'WARNING')
            self.assertEqual(Config.API_PORT, 9000)
            self.assertFalse(Config.API_DEBUG)
            
            # 验证配置有效
            self.assertTrue(Config.validate())


if __name__ == '__main__':
    unittest.main()