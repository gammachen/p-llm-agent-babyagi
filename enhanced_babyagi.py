import json
import re
from typing import Dict, Any, List, Optional

from custom_babyagi import CustomBabyAGI, Task
from tools import tool_registry
from logger import get_logger

logger = get_logger("enhanced_babyagi")

class EnhancedBabyAGI(CustomBabyAGI):
    """增强版 BabyAGI，集成工具系统"""
    
    def __init__(self, objective: str, initial_task: str = None):
        super().__init__(objective, initial_task)
        self.tool_registry = tool_registry
        logger.info("增强版 BabyAGI 初始化完成，已集成工具系统")
    
    def execute_task(self, task: Task) -> str:
        """增强的任务执行方法，支持工具调用"""
        logger.info(f"开始执行增强任务: {task.content}")
        task.status = "in_progress"
        
        try:
            # 获取相关上下文
            context = self._get_relevant_context(task.content)
            
            # 分析任务是否需要工具
            tool_decision = self._analyze_tool_requirement(task, context)
            
            if tool_decision["use_tool"]:
                # 使用工具执行任务
                result = self._execute_task_with_tools(task, tool_decision, context)
            else:
                # 使用 LLM 直接处理任务
                result = self._execute_task_with_llm(task, context)
            
            # 更新任务状态
            task.result = result
            task.status = "completed"
            task.completed_at = time.time()
            
            # 存储到向量数据库
            self._store_task_result(task)
            
            logger.info(f"增强任务执行完成: {task.id}")
            return result
            
        except Exception as e:
            logger.error(f"增强任务执行失败: {e}")
            task.status = "failed"
            task.result = f"执行失败: {str(e)}"
            return task.result
    
    def _analyze_tool_requirement(self, task: Task, context: str) -> Dict[str, Any]:
        """分析任务是否需要使用工具"""
        available_tools = self.tool_registry.list_tools()
        tools_description = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in available_tools
        ])
        
        prompt = f"""
你是一个任务分析专家。请分析以下任务是否需要使用工具来执行，如果需要，请指定使用哪个工具和相应参数。

总体目标: {self.objective}

当前任务: {task.content}

相关上下文:
{context}

可用工具:
{tools_description}

请分析任务并返回 JSON 格式的决策：
{{
  "use_tool": true/false,
  "tool_name": "工具名称（如果需要工具）",
  "tool_params": {{"参数名": "参数值"}},
  "reasoning": "分析推理过程",
  "fallback_to_llm": true/false
}}

分析要点：
1. 如果任务需要执行命令、操作文件、网络搜索等实际操作，应使用相应工具
2. 如果任务是纯思考、分析、规划类工作，可以直接使用 LLM
3. 如果不确定，优先选择使用工具
4. 参数应该具体明确，避免模糊描述

决策结果:
"""
        
        try:
            response = self.llm(prompt, max_tokens=800)
            
            # 尝试提取 JSON
            json_match = re.search(r'\{[^{}]*(?:\{[^{}]*\}[^{}]*)*\}', response)
            if json_match:
                decision_json = json_match.group()
                decision = json.loads(decision_json)
                
                # 验证决策格式
                if "use_tool" not in decision:
                    decision["use_tool"] = False
                
                logger.info(f"工具决策: {decision['reasoning']}")
                return decision
            else:
                logger.warning("无法解析工具决策 JSON，默认不使用工具")
                return {"use_tool": False, "reasoning": "JSON 解析失败"}
                
        except Exception as e:
            logger.error(f"工具需求分析失败: {e}")
            return {"use_tool": False, "reasoning": f"分析失败: {str(e)}"}
    
    def _execute_task_with_tools(self, task: Task, tool_decision: Dict[str, Any], context: str) -> str:
        """使用工具执行任务"""
        tool_name = tool_decision.get("tool_name")
        tool_params = tool_decision.get("tool_params", {})
        
        logger.info(f"使用工具 {tool_name} 执行任务")
        
        # 执行工具
        tool_result = self.tool_registry.execute_tool(tool_name, **tool_params)
        
        # 如果工具执行失败，尝试回退到 LLM
        if not tool_result.get("success", False):
            logger.warning(f"工具执行失败: {tool_result.get('error')}")
            if tool_decision.get("fallback_to_llm", True):
                logger.info("回退到 LLM 执行")
                return self._execute_task_with_llm(task, context, tool_error=tool_result.get('error'))
            else:
                return f"工具执行失败: {tool_result.get('error')}"
        
        # 使用 LLM 解释和总结工具结果
        interpretation_prompt = f"""
你刚刚使用工具 {tool_name} 执行了以下任务：

任务: {task.content}
总体目标: {self.objective}

工具执行结果:
{json.dumps(tool_result, ensure_ascii=False, indent=2)}

请基于工具执行结果，提供一个清晰、有用的任务完成报告，包括：
1. 任务执行摘要
2. 关键发现或结果
3. 对实现总体目标的贡献
4. 后续建议（如果有）

任务完成报告:
"""
        
        try:
            interpretation = self.llm(interpretation_prompt, max_tokens=1000)
            
            # 组合最终结果
            final_result = f"""
【任务执行方式】: 使用工具 {tool_name}
【工具执行状态】: 成功

【任务完成报告】:
{interpretation}

【详细工具结果】:
{json.dumps(tool_result, ensure_ascii=False, indent=2)}
"""
            
            return final_result
            
        except Exception as e:
            logger.error(f"工具结果解释失败: {e}")
            return f"""
【任务执行方式】: 使用工具 {tool_name}
【工具执行状态】: 成功
【原始结果】: {json.dumps(tool_result, ensure_ascii=False, indent=2)}
【注意】: 结果解释失败，显示原始数据
"""
    
    def _execute_task_with_llm(self, task: Task, context: str, tool_error: str = None) -> str:
        """使用 LLM 直接执行任务"""
        error_context = f"\n\n注意：工具执行失败 - {tool_error}" if tool_error else ""
        
        prompt = f"""
你是一个高效的任务执行助手。请根据以下信息执行任务：

目标: {self.objective}

当前任务: {task.content}

相关上下文:
{context}{error_context}

请提供详细的执行结果，包括：
1. 具体的执行步骤或分析过程
2. 遇到的问题和解决方案
3. 最终结果或结论
4. 对实现总体目标的贡献
5. 后续建议

执行结果:
"""
        
        try:
            result = self.llm(prompt, max_tokens=1500)
            return f"【任务执行方式】: LLM 直接处理\n\n{result}"
        except Exception as e:
            logger.error(f"LLM 任务执行失败: {e}")
            return f"LLM 执行失败: {str(e)}"
    
    def create_new_tasks(self, completed_task: Task) -> List[Task]:
        """基于已完成任务创建新任务（增强版）"""
        # 获取工具使用历史
        tool_usage_summary = self._get_tool_usage_summary()
        
        prompt = f"""
基于以下已完成的任务，创建新的任务来推进总体目标的实现。

总体目标: {self.objective}

已完成任务: {completed_task.content}
任务结果: {completed_task.result}

现有任务列表:
{self._format_task_list()}

工具使用情况:
{tool_usage_summary}

可用工具:
{self._format_available_tools()}

请分析当前进展，并创建 1-3 个新任务来继续推进目标实现。
每个任务应该：
1. 具体可执行
2. 与总体目标相关
3. 基于已完成任务的结果
4. 避免重复现有任务
5. 考虑是否需要使用特定工具

请以 JSON 格式返回新任务列表：
[
  {{
    "content": "任务描述1", 
    "priority": 优先级数字,
    "suggested_tool": "建议使用的工具名称（可选）",
    "reasoning": "创建此任务的原因"
  }}
]

如果不需要创建新任务，返回空数组 []。
"""
        
        try:
            response = self.llm(prompt, max_tokens=1000)
            
            # 尝试解析 JSON
            json_match = re.search(r'\[[^\[\]]*(?:\[[^\[\]]*\][^\[\]]*)*\]', response)
            if json_match:
                tasks_json = json_match.group()
                new_tasks_data = json.loads(tasks_json)
                
                if not isinstance(new_tasks_data, list):
                    logger.warning("LLM 返回的不是列表格式")
                    return []
                
                new_tasks = []
                for task_data in new_tasks_data:
                    if isinstance(task_data, dict) and "content" in task_data:
                        task = Task(
                            id=str(uuid.uuid4()),
                            content=task_data["content"],
                            priority=task_data.get("priority", 1)
                        )
                        new_tasks.append(task)
                        
                        # 记录建议的工具
                        if "suggested_tool" in task_data:
                            logger.info(f"新任务 {task.id} 建议使用工具: {task_data['suggested_tool']}")
                
                logger.info(f"创建了 {len(new_tasks)} 个新任务")
                return new_tasks
            else:
                logger.warning("无法找到 JSON 数组")
                return []
                
        except Exception as e:
            logger.error(f"创建新任务失败: {e}")
            return []
    
    def _get_tool_usage_summary(self) -> str:
        """获取工具使用摘要"""
        # 这里可以实现工具使用统计
        # 目前返回简单的可用工具列表
        return "工具系统已就绪，可根据任务需要调用相应工具。"
    
    def _format_available_tools(self) -> str:
        """格式化可用工具列表"""
        tools = self.tool_registry.list_tools()
        formatted = []
        for tool in tools:
            formatted.append(f"- {tool['name']}: {tool['description']}")
        return "\n".join(formatted)
    
    def get_enhanced_status(self) -> Dict[str, Any]:
        """获取增强状态信息"""
        base_status = self.get_status()
        
        # 添加工具相关信息
        base_status.update({
            "available_tools": self.tool_registry.list_tools(),
            "tool_count": len(self.tool_registry.tools),
            "enhanced_features": [
                "工具集成",
                "智能工具选择",
                "工具执行回退",
                "结果解释"
            ]
        })
        
        return base_status

# 导入必要的模块
import time
import uuid