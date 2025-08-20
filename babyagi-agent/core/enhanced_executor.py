import json
import logging
import time
from typing import Dict, Any
from core.custom_babyagi import CustomBabyAGI
from tools.tools import TOOL_REGISTRY

logger = logging.getLogger(__name__)

class EnhancedExecutor:
    def __init__(self, babyagi: CustomBabyAGI):
        self.babyagi = babyagi
    
    def execute_task_with_tools(self, task: str) -> str:
        """增强的任务执行方法，支持工具调用"""
        logger.info(f"Enhanced execution for task: {task}")
        
        # 分析任务是否需要工具
        tool_prompt = f"""
        Analyze whether the following task requires using tools to execute. If it does, return a JSON formatted tool call instruction:
        Task: {task}
        
        Available tools:
        - execute_command: Execute command line commands, params: {{"cmd": "command"}}
        - web_search: Perform web search, params: {{"query": "search query"}}
        - read_file: Read file, params: {{"filepath": "file path"}}
        - write_file: Write file, params: {{"filepath": "file path", "content": "content"}}
        
        If no tool is needed, think with LLM directly.
        Return format: {{"use_tool": true/false, "tool_name": "tool name", "tool_params": {{}}, "reasoning": "thinking process"}}
        """
        
        try:
            logger.info("Analyzing whether task requires tool execution")
            # 获取工具调用决策
            decision_str = self.babyagi.llm(tool_prompt)
            logger.debug(f"Tool decision response: {decision_str}")
            decision = json.loads(decision_str)
            
            if decision.get("use_tool", False):
                # 执行工具调用
                tool_name = decision.get("tool_name")
                tool_params = decision.get("tool_params", {})
                
                logger.info(f"Executing tool: {tool_name}")
                logger.debug(f"Tool parameters: {tool_params}")
                
                if tool_name in TOOL_REGISTRY:
                    tool_func = TOOL_REGISTRY[tool_name]
                    try:
                        start_time = time.time()
                        result = tool_func(**tool_params)
                        end_time = time.time()
                        
                        logger.info(f"Tool {tool_name} executed successfully in {end_time - start_time:.2f} seconds")
                        logger.debug(f"Tool result: {result[:100]}...")  # 只记录前100个字符
                        return f"Tool {tool_name} execution result: {result}"
                    except Exception as e:
                        logger.error(f"Error executing tool {tool_name}: {str(e)}")
                        return f"Error executing tool {tool_name}: {str(e)}"
                else:
                    logger.error(f"Unknown tool requested: {tool_name}")
                    return f"Error: Unknown tool {tool_name}"
            else:
                # 使用LLM直接处理任务
                logger.info("No tool required, using LLM directly")
                result = self.babyagi.llm(f"Please complete the following task: {task}")
                logger.info("Task completed with LLM")
                return result
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tool decision as JSON: {str(e)}")
            # 如果决策解析失败，直接使用LLM处理任务
            result = self.babyagi.llm(f"Please complete the following task: {task}")
            logger.info("Task completed with LLM after tool decision failure")
            return result
        except Exception as e:
            logger.error(f"Error in enhanced task execution: {str(e)}")
            return f"Error in task execution: {str(e)}"