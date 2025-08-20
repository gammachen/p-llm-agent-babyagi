import logging
import json
import os
import time
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class CustomBabyAGI:
    def __init__(self, objective, config):
        self.config = config
        self.objective = objective
        
        # 初始化向量数据库
        self.vector_db = self._init_vector_db()
        
        # 初始化 LLM
        self.llm = self._init_llm()
    
    def _init_vector_db(self):
        """初始化向量数据库"""
        if self.config.VECTOR_DB == "chroma":
            try:
                # 禁用遥测以避免版本兼容性问题
                os.environ["ANONYMIZED_TELEMETRY"] = "False"
                
                from chromadb import PersistentClient
                from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction, OllamaEmbeddingFunction
                
                # 根据配置选择嵌入函数
                if self.config.LLM_PROVIDER == "ollama":
                    embedding_function = OllamaEmbeddingFunction(
                        model_name=self.config.OLLAMA_MODEL,
                        url=self.config.OLLAMA_BASE_URL
                    )
                else:
                    embedding_function = OpenAIEmbeddingFunction(
                        api_key=self.config.OPENAI_API_KEY,
                        api_base_url=self.config.OPENAI_BASE_URL,
                        model_name="text-embedding-ada-002"
                    )
                
                # 创建 Chroma 客户端
                client = PersistentClient(path=self.config.CHROMA_PERSIST_DIR)
                collection = client.get_or_create_collection(
                    name="babyagi_tasks",
                    embedding_function=embedding_function
                )
                return collection
            
            except ImportError:
                logger.warning("ChromaDB not installed. Using in-memory storage.")
                return {"documents": [], "metadatas": [], "ids": []}
        
        # 可以添加其他向量数据库支持
        raise ValueError(f"Unsupported vector database: {self.config.VECTOR_DB}")
    
    def _init_llm(self):
        """初始化 LLM 客户端"""
        if self.config.LLM_PROVIDER == "openai":
            try:
                import openai
                openai.api_key = self.config.OPENAI_API_KEY
                openai.base_url = self.config.OPENAI_BASE_URL
                
                def openai_llm(prompt):
                    logger.info(f"Calling OpenAI API with model: {self.config.OPENAI_MODEL}")
                    logger.debug(f"Prompt: {prompt[:100]}...")  # 只记录前100个字符
                    
                    start_time = time.time()
                    try:
                        response = openai.ChatCompletion.create(
                            model=self.config.OPENAI_MODEL,
                            messages=[{"role": "user", "content": prompt}]
                        )
                        end_time = time.time()
                        
                        content = response.choices[0].message.content
                        logger.info(f"OpenAI API call completed in {end_time - start_time:.2f} seconds")
                        logger.debug(f"Response: {content[:100]}...")  # 只记录前100个字符
                        
                        return content
                    except Exception as e:
                        logger.error(f"OpenAI API call failed: {str(e)}")
                        raise e
                
                return openai_llm
            except ImportError:
                logger.warning("OpenAI library not installed. Using mock LLM.")
                return lambda prompt: f"Mock response for: {prompt}"
        
        elif self.config.LLM_PROVIDER == "ollama":
            try:
                import requests
                
                def ollama_llm(prompt):
                    logger.info(f"Calling Ollama API with model: {self.config.OLLAMA_MODEL}")
                    logger.debug(f"Prompt: {prompt[:100]}...")  # 只记录前100个字符
                    
                    start_time = time.time()
                    try:
                        response = requests.post(
                            f"{self.config.OLLAMA_BASE_URL}/api/generate",
                            json={
                                "model": self.config.OLLAMA_MODEL,
                                "prompt": prompt,
                                "stream": False
                            },
                            timeout=120  # 增加超时时间
                        )
                        end_time = time.time()
                        
                        if response.status_code == 200:
                            content = response.json()["response"]
                            logger.info(f"Ollama API call completed in {end_time - start_time:.2f} seconds")
                            logger.debug(f"Response: {content[:100]}...")  # 只记录前100个字符
                            return content
                        else:
                            logger.error(f"Ollama API call failed with status {response.status_code}: {response.text}")
                            raise Exception(f"Ollama API error: {response.status_code}")
                    except Exception as e:
                        logger.error(f"Ollama API call failed: {str(e)}")
                        raise e
                
                return ollama_llm
            except ImportError:
                logger.warning("Requests library not installed. Using mock LLM.")
                return lambda prompt: f"Mock response for: {prompt}"
        
        raise ValueError(f"Unsupported LLM provider: {self.config.LLM_PROVIDER}")
    
    def execute_task(self, task: str) -> str:
        """执行单个任务"""
        logger.info(f"Executing task: {task}")
        # 使用LLM直接处理任务
        result = self.llm(f"Please complete the following task: {task}")
        logger.info(f"Task completed with result length: {len(result)} characters")
        return result
    
    def create_tasks(self, current_task: str, result: str) -> List[str]:
        """基于当前任务和结果创建新任务"""
        prompt = f"""
        Based on the objective: {self.objective}
        Current task: {current_task}
        Result: {result}
        
        Please create a list of new tasks that should be done next.
        Return ONLY a JSON array of strings, like: ["task1", "task2", "task3"]
        """
        
        logger.info("Creating new tasks based on current task and result")
        try:
            response = self.llm(prompt)
            # 尝试解析为JSON
            tasks = json.loads(response)
            if isinstance(tasks, list):
                logger.info(f"Created {len(tasks)} new tasks")
                return tasks
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse tasks as JSON: {str(e)}")
            logger.debug(f"Response received: {response}")
        except Exception as e:
            logger.error(f"Error while creating tasks: {str(e)}")
        
        # 如果解析失败，返回空列表
        logger.info("No new tasks created")
        return []
    
    def prioritize_tasks(self, task_list: List[str]) -> List[str]:
        """对任务列表进行优先级排序"""
        if len(task_list) <= 1:
            logger.info("Task list has 1 or fewer tasks, no prioritization needed")
            return task_list
            
        prompt = f"""
        Objective: {self.objective}
        
        Tasks to prioritize:
        {json.dumps(task_list, indent=2)}
        
        Please reorder these tasks based on their importance and priority for achieving the objective.
        Return ONLY a JSON array of strings in the desired order.
        """
        
        logger.info(f"Prioritizing {len(task_list)} tasks")
        try:
            response = self.llm(prompt)
            # 尝试解析为JSON
            tasks = json.loads(response)
            if isinstance(tasks, list):
                logger.info("Task prioritization completed")
                return tasks
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse prioritized tasks as JSON: {str(e)}")
            logger.debug(f"Response received: {response}")
        except Exception as e:
            logger.error(f"Error while prioritizing tasks: {str(e)}")
        
        # 如果解析失败，返回原始列表
        logger.info("Returning original task order due to prioritization failure")
        return task_list
    
    def run(self, initial_task=None):
        """运行 BabyAGI"""
        if initial_task is None:
            initial_task = f"Develop a task list to achieve: {self.objective}"
        
        logger.info(f"Starting BabyAGI with objective: {self.objective}")
        
        # 运行核心逻辑
        task_list = [initial_task]
        
        for i in range(self.config.MAX_ITERATIONS):
            if not task_list:
                logger.info("Task list is empty. Stopping.")
                break
                
            task = task_list.pop(0)
            logger.info(f"Executing task: {task}")
            
            # 执行任务
            result = self.execute_task(task)
            logger.info(f"Task result: {result}")
            
            # 存储结果（如果使用ChromaDB）
            if hasattr(self.vector_db, 'add'):
                self.vector_db.add(
                    documents=[result],
                    metadatas=[{"task": task}],
                    ids=[f"task_{i}"]
                )
            else:
                # 内存存储
                self.vector_db["documents"].append(result)
                self.vector_db["metadatas"].append({"task": task})
                self.vector_db["ids"].append(f"task_{i}")
            
            # 创建新任务
            new_tasks = self.create_tasks(task, result)
            task_list.extend(new_tasks)
            
            # 重新排序任务
            task_list = self.prioritize_tasks(task_list)
            
            logger.info(f"Updated task list: {task_list}")
        
        # 返回结果
        if hasattr(self.vector_db, 'get'):
            return self.vector_db.get()
        else:
            return self.vector_db