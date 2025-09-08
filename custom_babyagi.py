import json
import time
import uuid
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction, DefaultEmbeddingFunction
import openai
import requests

from config import config
from logger import get_logger

logger = get_logger("babyagi")

@dataclass
class Task:
    """任务数据类"""
    id: str
    content: str
    priority: int = 1
    status: str = "pending"  # pending, in_progress, completed, failed
    created_at: float = None
    completed_at: float = None
    result: str = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "priority": self.priority,
            "status": self.status,
            "created_at": self.created_at,
            "completed_at": self.completed_at,
            "result": self.result
        }

class CustomBabyAGI:
    """自定义 BabyAGI 实现"""
    
    def __init__(self, objective: str, initial_task: str = None):
        self.objective = objective
        self.initial_task = initial_task or f"制定实现以下目标的任务列表: {objective}"
        
        # 初始化组件
        self.vector_db = self._init_vector_db()
        self.llm = self._init_llm()
        
        # 任务管理
        self.task_list: List[Task] = []
        self.completed_tasks: List[Task] = []
        self.current_iteration = 0
        
        logger.info(f"BabyAGI 初始化完成，目标: {objective}")
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        try:
            if config.VECTOR_DB == "chroma":
                from chromadb.config import Settings
                
                # 选择嵌入函数
                if config.LLM_PROVIDER == "openai" and config.OPENAI_API_KEY:
                    embedding_function = OpenAIEmbeddingFunction(
                        api_key=config.OPENAI_API_KEY,
                        api_base=config.OPENAI_BASE_URL,
                        model_name="text-embedding-ada-002"
                    )
                else:
                    embedding_function = DefaultEmbeddingFunction()
                
                # 创建 Chroma 客户端，使用一致的设置
                client = chromadb.PersistentClient(
                    path=config.CHROMA_PERSIST_DIR,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                
                # 获取或创建集合
                collection = client.get_or_create_collection(
                    name="babyagi_tasks",
                    embedding_function=embedding_function,
                    metadata={"hnsw:space": "cosine"}
                )
                
                logger.info(f"ChromaDB 初始化成功，存储路径: {config.CHROMA_PERSIST_DIR}")
                return collection
            
            else:
                raise ValueError(f"不支持的向量数据库: {config.VECTOR_DB}")
                
        except Exception as e:
            logger.error(f"向量数据库初始化失败: {e}")
            raise
    
    def _init_llm(self):
        """初始化 LLM 客户端"""
        try:
            if config.LLM_PROVIDER == "openai":
                if not config.OPENAI_API_KEY:
                    raise ValueError("使用 OpenAI 时必须设置 OPENAI_API_KEY")
                
                openai.api_key = config.OPENAI_API_KEY
                openai.base_url = config.OPENAI_BASE_URL
                
                def openai_llm(prompt: str, max_tokens: int = 1000) -> str:
                    try:
                        response = openai.ChatCompletion.create(
                            model=config.OPENAI_MODEL,
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=max_tokens,
                            temperature=0.7
                        )
                        return response.choices[0].message.content.strip()
                    except Exception as e:
                        logger.error(f"OpenAI API 调用失败: {e}")
                        return f"LLM 调用失败: {str(e)}"
                
                logger.info(f"OpenAI LLM 初始化成功，模型: {config.OPENAI_MODEL}")
                return openai_llm
            
            elif config.LLM_PROVIDER == "ollama":
                def ollama_llm(prompt: str, max_tokens: int = 1000) -> str:
                    try:
                        response = requests.post(
                            f"{config.OLLAMA_BASE_URL}/api/generate",
                            json={
                                "model": config.OLLAMA_MODEL,
                                "prompt": prompt,
                                "stream": False,
                                "options": {
                                    "num_predict": max_tokens,
                                    "temperature": 0.7
                                }
                            },
                            timeout=60
                        )
                        response.raise_for_status()
                        return response.json()["response"].strip()
                    except Exception as e:
                        logger.error(f"Ollama API 调用失败: {e}")
                        return f"LLM 调用失败: {str(e)}"
                
                logger.info(f"Ollama LLM 初始化成功，模型: {config.OLLAMA_MODEL}")
                return ollama_llm
            
            else:
                raise ValueError(f"不支持的 LLM 提供商: {config.LLM_PROVIDER}")
                
        except Exception as e:
            logger.error(f"LLM 初始化失败: {e}")
            raise
    
    def execute_task(self, task: Task) -> str:
        """执行单个任务"""
        logger.info(f"开始执行任务: {task.content}")
        task.status = "in_progress"
        
        try:
            # 获取相关上下文
            context = self._get_relevant_context(task.content)
            
            # 构建执行提示
            prompt = f"""
你是一个高效的任务执行助手。请根据以下信息执行任务：

目标: {self.objective}

当前任务: {task.content}

相关上下文:
{context}

请提供详细的执行结果，包括：
1. 具体的执行步骤
2. 遇到的问题和解决方案
3. 最终结果
4. 对实现总体目标的贡献

执行结果:
"""
            
            # 调用 LLM 执行任务
            result = self.llm(prompt, max_tokens=1500)
            
            # 更新任务状态
            task.result = result
            task.status = "completed"
            task.completed_at = time.time()
            
            # 存储到向量数据库
            self._store_task_result(task)
            
            logger.info(f"任务执行完成: {task.id}")
            return result
            
        except Exception as e:
            logger.error(f"任务执行失败: {e}")
            task.status = "failed"
            task.result = f"执行失败: {str(e)}"
            return task.result
    
    def create_new_tasks(self, completed_task: Task) -> List[Task]:
        """基于已完成任务创建新任务"""
        prompt = f"""
基于以下已完成的任务，创建新的任务来推进总体目标的实现。

总体目标: {self.objective}

已完成任务: {completed_task.content}
任务结果: {completed_task.result}

现有任务列表:
{self._format_task_list()}

请分析当前进展，并创建 1-3 个新任务来继续推进目标实现。
每个任务应该：
1. 具体可执行
2. 与总体目标相关
3. 基于已完成任务的结果
4. 避免重复现有任务

请以 JSON 格式返回新任务列表：
[
  {{"content": "任务描述1", "priority": 优先级数字}},
  {{"content": "任务描述2", "priority": 优先级数字}}
]

如果不需要创建新任务，返回空数组 []。
"""
        
        try:
            response = self.llm(prompt, max_tokens=800)
            
            # 尝试解析 JSON
            try:
                new_tasks_data = json.loads(response.strip())
                if not isinstance(new_tasks_data, list):
                    logger.warning("LLM 返回的不是列表格式，尝试提取任务")
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
                
                logger.info(f"创建了 {len(new_tasks)} 个新任务")
                return new_tasks
                
            except json.JSONDecodeError:
                logger.warning(f"无法解析 LLM 返回的 JSON: {response}")
                return []
                
        except Exception as e:
            logger.error(f"创建新任务失败: {e}")
            return []
    
    def prioritize_tasks(self) -> None:
        """重新排序任务优先级"""
        if len(self.task_list) <= 1:
            return
        
        prompt = f"""
请为以下任务列表重新分配优先级，以最有效地实现总体目标。

总体目标: {self.objective}

当前任务列表:
{self._format_task_list()}

已完成任务摘要:
{self._format_completed_tasks()}

请分析每个任务的重要性和紧急性，然后返回重新排序的任务列表。
优先级数字越小表示优先级越高（1 = 最高优先级）。

请以 JSON 格式返回：
[
  {{"id": "任务ID", "priority": 新优先级数字}}
]
"""
        
        try:
            response = self.llm(prompt, max_tokens=600)
            priority_data = json.loads(response.strip())
            
            # 更新任务优先级
            priority_map = {item["id"]: item["priority"] for item in priority_data}
            for task in self.task_list:
                if task.id in priority_map:
                    task.priority = priority_map[task.id]
            
            # 按优先级排序
            self.task_list.sort(key=lambda t: t.priority)
            logger.info("任务优先级重新排序完成")
            
        except Exception as e:
            logger.warning(f"任务优先级排序失败，使用默认排序: {e}")
            self.task_list.sort(key=lambda t: t.priority)
    
    def _get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """获取相关上下文"""
        try:
            if self.vector_db.count() == 0:
                return "暂无相关历史信息。"
            
            results = self.vector_db.query(
                query_texts=[query],
                n_results=min(n_results, self.vector_db.count())
            )
            
            if not results["documents"] or not results["documents"][0]:
                return "暂无相关历史信息。"
            
            context_parts = []
            for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                context_parts.append(f"- {metadata.get('task', '未知任务')}: {doc[:200]}...")
            
            return "\n".join(context_parts)
            
        except Exception as e:
            logger.warning(f"获取相关上下文失败: {e}")
            return "获取历史信息时出现错误。"
    
    def _store_task_result(self, task: Task) -> None:
        """存储任务结果到向量数据库"""
        try:
            self.vector_db.add(
                documents=[task.result],
                metadatas=[{
                    "task_id": task.id,
                    "task": task.content,
                    "status": task.status,
                    "completed_at": task.completed_at or time.time()
                }],
                ids=[task.id]
            )
        except Exception as e:
            logger.error(f"存储任务结果失败: {e}")
    
    def _format_task_list(self) -> str:
        """格式化任务列表为字符串"""
        if not self.task_list:
            return "无待执行任务"
        
        formatted = []
        for i, task in enumerate(self.task_list, 1):
            formatted.append(f"{i}. [{task.priority}] {task.content} (ID: {task.id})")
        return "\n".join(formatted)
    
    def _format_completed_tasks(self) -> str:
        """格式化已完成任务摘要"""
        if not self.completed_tasks:
            return "暂无已完成任务"
        
        formatted = []
        for task in self.completed_tasks[-3:]:  # 只显示最近3个
            result_preview = task.result[:100] + "..." if len(task.result) > 100 else task.result
            formatted.append(f"- {task.content}: {result_preview}")
        return "\n".join(formatted)
    
    def run(self, max_iterations: int = None) -> Dict[str, Any]:
        """运行 BabyAGI 主循环"""
        max_iterations = max_iterations or config.MAX_ITERATIONS
        
        # 添加初始任务
        initial_task = Task(
            id=str(uuid.uuid4()),
            content=self.initial_task,
            priority=1
        )
        self.task_list.append(initial_task)
        
        logger.info(f"开始运行 BabyAGI，最大迭代次数: {max_iterations}")
        
        results = {
            "objective": self.objective,
            "initial_task": self.initial_task,
            "iterations": [],
            "completed_tasks": [],
            "status": "running"
        }
        
        try:
            for iteration in range(max_iterations):
                self.current_iteration = iteration + 1
                logger.info(f"开始第 {self.current_iteration} 次迭代")
                
                if not self.task_list:
                    logger.info("任务列表为空，停止执行")
                    results["status"] = "completed_no_tasks"
                    break
                
                # 执行优先级最高的任务
                current_task = self.task_list.pop(0)
                
                iteration_result = {
                    "iteration": self.current_iteration,
                    "task": current_task.to_dict(),
                    "timestamp": time.time()
                }
                
                # 执行任务
                task_result = self.execute_task(current_task)
                iteration_result["result"] = task_result
                
                # 移动到已完成列表
                self.completed_tasks.append(current_task)
                
                # 创建新任务
                if current_task.status == "completed":
                    new_tasks = self.create_new_tasks(current_task)
                    self.task_list.extend(new_tasks)
                    iteration_result["new_tasks"] = [task.to_dict() for task in new_tasks]
                    
                    # 重新排序任务
                    self.prioritize_tasks()
                
                iteration_result["remaining_tasks"] = len(self.task_list)
                results["iterations"].append(iteration_result)
                
                logger.info(f"第 {self.current_iteration} 次迭代完成，剩余任务: {len(self.task_list)}")
            
            results["completed_tasks"] = [task.to_dict() for task in self.completed_tasks]
            results["status"] = "completed" if self.current_iteration < max_iterations else "max_iterations_reached"
            
            logger.info(f"BabyAGI 运行完成，状态: {results['status']}")
            return results
            
        except Exception as e:
            logger.error(f"BabyAGI 运行出错: {e}")
            results["status"] = "error"
            results["error"] = str(e)
            return results
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "objective": self.objective,
            "current_iteration": self.current_iteration,
            "pending_tasks": len(self.task_list),
            "completed_tasks": len(self.completed_tasks),
            "task_list": [task.to_dict() for task in self.task_list],
            "recent_completed": [task.to_dict() for task in self.completed_tasks[-3:]]
        }