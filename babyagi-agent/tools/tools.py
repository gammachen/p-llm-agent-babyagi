import subprocess
import json
import logging
import time
from typing import Dict, Callable, Any

logger = logging.getLogger(__name__)

class ToolKit:
    @staticmethod
    def execute_command(cmd: str) -> str:
        """执行命令行命令"""
        logger.info(f"Executing command: {cmd}")
        start_time = time.time()
        
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            end_time = time.time()
            
            logger.info(f"Command executed in {end_time - start_time:.2f} seconds")
            if result.returncode == 0:
                logger.debug(f"Command stdout: {result.stdout[:100]}...")  # 只记录前100个字符
                return result.stdout
            else:
                logger.warning(f"Command failed with return code {result.returncode}")
                logger.debug(f"Command stderr: {result.stderr[:100]}...")  # 只记录前100个字符
                return result.stderr
        except subprocess.TimeoutExpired:
            logger.error("Command timed out after 30 seconds")
            return "Error: Command timed out"
        except Exception as e:
            logger.error(f"Error executing command: {str(e)}")
            return f"Error executing command: {str(e)}"
    
    @staticmethod
    def web_search(query: str) -> str:
        """执行网络搜索（示例）"""
        logger.info(f"Performing web search for query: {query}")
        # 这里可以集成 SerperAPI、SerpAPI 或其他搜索API
        result = f"Web search results for: {query}"
        logger.debug(f"Web search result: {result}")
        return result
    
    @staticmethod
    def read_file(filepath: str) -> str:
        """读取文件内容"""
        logger.info(f"Reading file: {filepath}")
        start_time = time.time()
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                end_time = time.time()
                
                logger.info(f"File read completed in {end_time - start_time:.2f} seconds")
                logger.debug(f"File size: {len(content)} characters")
                return content
        except Exception as e:
            logger.error(f"Error reading file {filepath}: {str(e)}")
            return f"Error reading file: {str(e)}"
    
    @staticmethod
    def write_file(filepath: str, content: str) -> str:
        """写入文件内容"""
        logger.info(f"Writing file: {filepath}")
        logger.debug(f"Content size: {len(content)} characters")
        start_time = time.time()
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
                end_time = time.time()
                
                logger.info(f"File write completed in {end_time - start_time:.2f} seconds")
                return f"Successfully wrote to {filepath}"
        except Exception as e:
            logger.error(f"Error writing file {filepath}: {str(e)}")
            return f"Error writing file: {str(e)}"

# 工具注册表
TOOL_REGISTRY: Dict[str, Callable[..., str]] = {
    "execute_command": ToolKit.execute_command,
    "web_search": ToolKit.web_search,
    "read_file": ToolKit.read_file,
    "write_file": ToolKit.write_file
}