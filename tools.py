import os
import subprocess
import json
import requests
import time
from typing import Dict, Any, List, Optional
from pathlib import Path
from abc import ABC, abstractmethod

from logger import get_logger

logger = get_logger("tools")

class BaseTool(ABC):
    """工具基类"""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        pass
    
    def validate_params(self, params: Dict[str, Any], required_params: List[str]) -> bool:
        """验证参数"""
        for param in required_params:
            if param not in params:
                return False
        return True

class CommandExecutor(BaseTool):
    """命令行执行工具"""
    
    def __init__(self):
        super().__init__(
            name="execute_command",
            description="执行命令行命令，支持 shell 命令执行"
        )
    
    def execute(self, cmd: str, timeout: int = 30, cwd: str = None) -> Dict[str, Any]:
        """执行命令"""
        try:
            logger.info(f"执行命令: {cmd}")
            
            # 安全检查 - 禁止危险命令
            dangerous_commands = ['rm -rf', 'format', 'del /f', 'shutdown', 'reboot']
            if any(dangerous in cmd.lower() for dangerous in dangerous_commands):
                return {
                    "success": False,
                    "error": "禁止执行危险命令",
                    "output": "",
                    "stderr": "安全限制：命令被阻止"
                }
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "output": result.stdout,
                "stderr": result.stderr,
                "command": cmd
            }
            
        except subprocess.TimeoutExpired:
            logger.error(f"命令执行超时: {cmd}")
            return {
                "success": False,
                "error": "命令执行超时",
                "output": "",
                "stderr": f"命令在 {timeout} 秒后超时"
            }
        except Exception as e:
            logger.error(f"命令执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "output": "",
                "stderr": str(e)
            }

class FileManager(BaseTool):
    """文件管理工具"""
    
    def __init__(self):
        super().__init__(
            name="file_manager",
            description="文件和目录操作工具，支持读取、写入、创建、删除等操作"
        )
    
    def execute(self, action: str, **kwargs) -> Dict[str, Any]:
        """执行文件操作"""
        try:
            if action == "read":
                return self._read_file(kwargs.get("filepath"))
            elif action == "write":
                return self._write_file(kwargs.get("filepath"), kwargs.get("content"))
            elif action == "append":
                return self._append_file(kwargs.get("filepath"), kwargs.get("content"))
            elif action == "delete":
                return self._delete_file(kwargs.get("filepath"))
            elif action == "list":
                return self._list_directory(kwargs.get("dirpath"))
            elif action == "create_dir":
                return self._create_directory(kwargs.get("dirpath"))
            elif action == "exists":
                return self._check_exists(kwargs.get("path"))
            else:
                return {
                    "success": False,
                    "error": f"不支持的操作: {action}"
                }
        except Exception as e:
            logger.error(f"文件操作失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _read_file(self, filepath: str) -> Dict[str, Any]:
        """读取文件"""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"success": False, "error": "文件不存在"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "size": len(content),
                "filepath": str(path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _write_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """写入文件"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"文件写入成功: {filepath}",
                "size": len(content),
                "filepath": str(path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _append_file(self, filepath: str, content: str) -> Dict[str, Any]:
        """追加文件内容"""
        try:
            path = Path(filepath)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "message": f"内容追加成功: {filepath}",
                "filepath": str(path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _delete_file(self, filepath: str) -> Dict[str, Any]:
        """删除文件"""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"success": False, "error": "文件不存在"}
            
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                path.rmdir()  # 只删除空目录
            
            return {
                "success": True,
                "message": f"删除成功: {filepath}"
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _list_directory(self, dirpath: str) -> Dict[str, Any]:
        """列出目录内容"""
        try:
            path = Path(dirpath)
            if not path.exists() or not path.is_dir():
                return {"success": False, "error": "目录不存在"}
            
            items = []
            for item in path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None,
                    "path": str(item.absolute())
                })
            
            return {
                "success": True,
                "items": items,
                "count": len(items),
                "dirpath": str(path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_directory(self, dirpath: str) -> Dict[str, Any]:
        """创建目录"""
        try:
            path = Path(dirpath)
            path.mkdir(parents=True, exist_ok=True)
            
            return {
                "success": True,
                "message": f"目录创建成功: {dirpath}",
                "dirpath": str(path.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _check_exists(self, path: str) -> Dict[str, Any]:
        """检查路径是否存在"""
        try:
            p = Path(path)
            return {
                "success": True,
                "exists": p.exists(),
                "type": "directory" if p.is_dir() else "file" if p.is_file() else "unknown",
                "path": str(p.absolute())
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

class WebSearcher(BaseTool):
    """网络搜索工具"""
    
    def __init__(self):
        super().__init__(
            name="web_search",
            description="执行网络搜索，获取相关信息"
        )
    
    def execute(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """执行网络搜索"""
        try:
            # 这里使用一个简单的搜索模拟
            # 在实际应用中，可以集成 SerperAPI、SerpAPI 等服务
            logger.info(f"执行网络搜索: {query}")
            
            # 模拟搜索结果
            results = [
                {
                    "title": f"搜索结果 {i+1} - {query}",
                    "url": f"https://example.com/result{i+1}",
                    "snippet": f"这是关于 '{query}' 的搜索结果 {i+1}。包含相关信息和详细描述。"
                }
                for i in range(min(num_results, 3))
            ]
            
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"网络搜索失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }

class HTTPClient(BaseTool):
    """HTTP 客户端工具"""
    
    def __init__(self):
        super().__init__(
            name="http_client",
            description="发送 HTTP 请求，支持 GET、POST 等方法"
        )
    
    def execute(self, method: str, url: str, **kwargs) -> Dict[str, Any]:
        """发送 HTTP 请求"""
        try:
            method = method.upper()
            headers = kwargs.get("headers", {})
            data = kwargs.get("data")
            json_data = kwargs.get("json")
            params = kwargs.get("params")
            timeout = kwargs.get("timeout", 10)
            
            logger.info(f"发送 {method} 请求到: {url}")
            
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                json=json_data,
                params=params,
                timeout=timeout
            )
            
            # 尝试解析 JSON 响应
            try:
                response_json = response.json()
            except:
                response_json = None
            
            return {
                "success": response.status_code < 400,
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "text": response.text,
                "json": response_json,
                "url": url,
                "method": method
            }
            
        except requests.exceptions.Timeout:
            return {
                "success": False,
                "error": "请求超时",
                "url": url,
                "method": method
            }
        except Exception as e:
            logger.error(f"HTTP 请求失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "url": url,
                "method": method
            }

class CodeAnalyzer(BaseTool):
    """代码分析工具"""
    
    def __init__(self):
        super().__init__(
            name="code_analyzer",
            description="分析代码文件，提取函数、类等信息"
        )
    
    def execute(self, filepath: str, language: str = "python") -> Dict[str, Any]:
        """分析代码文件"""
        try:
            path = Path(filepath)
            if not path.exists():
                return {"success": False, "error": "文件不存在"}
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                "filepath": str(path.absolute()),
                "language": language,
                "lines": len(content.splitlines()),
                "characters": len(content),
                "functions": [],
                "classes": [],
                "imports": []
            }
            
            if language.lower() == "python":
                analysis.update(self._analyze_python_code(content))
            
            return {
                "success": True,
                "analysis": analysis
            }
            
        except Exception as e:
            logger.error(f"代码分析失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _analyze_python_code(self, content: str) -> Dict[str, Any]:
        """分析 Python 代码"""
        lines = content.splitlines()
        functions = []
        classes = []
        imports = []
        
        for i, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 查找函数定义
            if stripped.startswith('def '):
                func_name = stripped.split('(')[0].replace('def ', '')
                functions.append({
                    "name": func_name,
                    "line": i,
                    "signature": stripped
                })
            
            # 查找类定义
            elif stripped.startswith('class '):
                class_name = stripped.split('(')[0].split(':')[0].replace('class ', '')
                classes.append({
                    "name": class_name,
                    "line": i,
                    "signature": stripped
                })
            
            # 查找导入语句
            elif stripped.startswith(('import ', 'from ')):
                imports.append({
                    "statement": stripped,
                    "line": i
                })
        
        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }

class ToolRegistry:
    """工具注册表"""
    
    def __init__(self):
        self.tools: Dict[str, BaseTool] = {}
        self._register_default_tools()
    
    def _register_default_tools(self):
        """注册默认工具"""
        default_tools = [
            CommandExecutor(),
            FileManager(),
            WebSearcher(),
            HTTPClient(),
            CodeAnalyzer()
        ]
        
        for tool in default_tools:
            self.register_tool(tool)
    
    def register_tool(self, tool: BaseTool):
        """注册工具"""
        self.tools[tool.name] = tool
        logger.info(f"工具已注册: {tool.name}")
    
    def get_tool(self, name: str) -> Optional[BaseTool]:
        """获取工具"""
        return self.tools.get(name)
    
    def list_tools(self) -> List[Dict[str, str]]:
        """列出所有工具"""
        return [
            {
                "name": tool.name,
                "description": tool.description
            }
            for tool in self.tools.values()
        ]
    
    def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """执行工具"""
        tool = self.get_tool(tool_name)
        if not tool:
            return {
                "success": False,
                "error": f"工具不存在: {tool_name}"
            }
        
        try:
            result = tool.execute(**kwargs)
            logger.info(f"工具 {tool_name} 执行完成")
            return result
        except Exception as e:
            logger.error(f"工具 {tool_name} 执行失败: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool": tool_name
            }

# 全局工具注册表实例
tool_registry = ToolRegistry()

# 便捷函数
def execute_command(cmd: str, **kwargs) -> Dict[str, Any]:
    """执行命令的便捷函数"""
    return tool_registry.execute_tool("execute_command", cmd=cmd, **kwargs)

def read_file(filepath: str) -> Dict[str, Any]:
    """读取文件的便捷函数"""
    return tool_registry.execute_tool("file_manager", action="read", filepath=filepath)

def write_file(filepath: str, content: str) -> Dict[str, Any]:
    """写入文件的便捷函数"""
    return tool_registry.execute_tool("file_manager", action="write", filepath=filepath, content=content)

def web_search(query: str, num_results: int = 5) -> Dict[str, Any]:
    """网络搜索的便捷函数"""
    return tool_registry.execute_tool("web_search", query=query, num_results=num_results)

def http_get(url: str, **kwargs) -> Dict[str, Any]:
    """HTTP GET 请求的便捷函数"""
    return tool_registry.execute_tool("http_client", method="GET", url=url, **kwargs)

def analyze_code(filepath: str, language: str = "python") -> Dict[str, Any]:
    """代码分析的便捷函数"""
    return tool_registry.execute_tool("code_analyzer", filepath=filepath, language=language)