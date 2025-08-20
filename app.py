from flask import Flask, request, jsonify, g, render_template, send_from_directory
from flask_cors import CORS
import threading
import time
import uuid
import os
from typing import Dict, Any, Optional
from datetime import datetime

from enhanced_babyagi import EnhancedBabyAGI
from config import config
from logger import get_logger
from tools import tool_registry

logger = get_logger("api")

# 创建 Flask 应用
app = Flask(__name__, 
           template_folder='templates',
           static_folder='static')
CORS(app)  # 启用跨域支持

# 全局变量存储运行中的 Agent 实例
running_agents: Dict[str, Dict[str, Any]] = {}
running_threads: Dict[str, threading.Thread] = {}

class APIResponse:
    """API 响应工具类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        response = {
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat()
        }
        if data is not None:
            response["data"] = data
        return response
    
    @staticmethod
    def error(message: str, code: int = 400, details: Any = None) -> tuple:
        response = {
            "success": False,
            "error": message,
            "timestamp": datetime.now().isoformat()
        }
        if details is not None:
            response["details"] = details
        return jsonify(response), code

@app.before_request
def before_request():
    """请求前处理"""
    g.start_time = time.time()
    logger.info(f"{request.method} {request.path} - 开始处理")

@app.after_request
def after_request(response):
    """请求后处理"""
    duration = time.time() - g.start_time
    logger.info(f"{request.method} {request.path} - 完成 ({duration:.3f}s)")
    return response

@app.errorhandler(404)
def not_found(error):
    return APIResponse.error("API 端点不存在", 404)

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"内部服务器错误: {error}")
    return APIResponse.error("内部服务器错误", 500)

# ==================== 基础信息接口 ====================

# Web 界面路由
@app.route('/')
def index():
    """主页面"""
    return render_template('index.html')

@app.route('/static/<path:filename>')
def static_files(filename):
    """静态文件服务"""
    return send_from_directory(app.static_folder, filename)

@app.route('/api/health', methods=['GET'])
def health_check():
    """健康检查"""
    return jsonify(APIResponse.success({
        "status": "healthy",
        "version": "1.0.0",
        "config": config.get_summary()
    }))

@app.route('/api/info', methods=['GET'])
def get_info():
    """获取系统信息"""
    return jsonify(APIResponse.success({
        "system": "BabyAGI Enhanced Agent",
        "version": "1.0.0",
        "features": [
            "自主任务规划",
            "工具集成",
            "向量数据库存储",
            "多 LLM 支持",
            "RESTful API",
            "Web 界面"
        ],
        "config": config.get_summary(),
        "running_agents": len(running_agents),
        "available_tools": len(tool_registry.tools)
    }))

# ==================== 工具管理接口 ====================

@app.route('/api/tools', methods=['GET'])
def list_tools():
    """获取可用工具列表"""
    tools = tool_registry.list_tools()
    return jsonify(APIResponse.success(tools))

@app.route('/api/tools/<tool_name>/execute', methods=['POST'])
def execute_tool(tool_name: str):
    """执行指定工具"""
    try:
        data = request.get_json() or {}
        result = tool_registry.execute_tool(tool_name, **data)
        
        if result.get("success", False):
            return jsonify(APIResponse.success(result, f"工具 {tool_name} 执行成功"))
        else:
            return APIResponse.error(f"工具执行失败: {result.get('error')}", 400, result)
            
    except Exception as e:
        logger.error(f"工具执行异常: {e}")
        return APIResponse.error(f"工具执行异常: {str(e)}", 500)

# ==================== Agent 管理接口 ====================

@app.route('/api/agents', methods=['GET'])
def list_agents():
    """获取所有 Agent 列表"""
    agents_info = []
    for agent_id, agent_data in running_agents.items():
        agents_info.append({
            "id": agent_id,
            "objective": agent_data["objective"],
            "status": agent_data["status"],
            "created_at": agent_data["created_at"],
            "current_iteration": agent_data.get("current_iteration", 0),
            "completed_tasks": len(agent_data.get("completed_tasks", [])),
            "pending_tasks": len(agent_data.get("pending_tasks", []))
        })
    
    return jsonify(APIResponse.success(agents_info))

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """创建新的 Agent"""
    try:
        data = request.get_json()
        if not data or 'objective' not in data:
            return APIResponse.error("缺少必需参数: objective")
        
        objective = data['objective']
        initial_task = data.get('initial_task')
        agent_id = str(uuid.uuid4())
        
        # 创建 Agent 实例
        agent = EnhancedBabyAGI(objective, initial_task)
        
        # 存储 Agent 信息
        running_agents[agent_id] = {
            "id": agent_id,
            "agent": agent,
            "objective": objective,
            "initial_task": initial_task,
            "status": "created",
            "created_at": datetime.now().isoformat(),
            "results": None,
            "error": None
        }
        
        logger.info(f"创建 Agent: {agent_id}")
        
        return jsonify(APIResponse.success({
            "agent_id": agent_id,
            "objective": objective,
            "initial_task": initial_task,
            "status": "created"
        }, "Agent 创建成功"))
        
    except Exception as e:
        logger.error(f"创建 Agent 失败: {e}")
        return APIResponse.error(f"创建 Agent 失败: {str(e)}", 500)

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id: str):
    """获取指定 Agent 信息"""
    if agent_id not in running_agents:
        return APIResponse.error("Agent 不存在", 404)
    
    agent_data = running_agents[agent_id]
    agent = agent_data["agent"]
    
    # 获取详细状态
    try:
        status = agent.get_enhanced_status()
        agent_data.update({
            "current_iteration": status.get("current_iteration", 0),
            "pending_tasks": status.get("task_list", []),
            "completed_tasks": status.get("recent_completed", [])
        })
    except Exception as e:
        logger.warning(f"获取 Agent 状态失败: {e}")
    
    # 返回信息（不包含 agent 实例）
    response_data = {k: v for k, v in agent_data.items() if k != "agent"}
    return jsonify(APIResponse.success(response_data))

@app.route('/api/agents/<agent_id>/start', methods=['POST'])
def start_agent(agent_id: str):
    """启动 Agent 执行"""
    if agent_id not in running_agents:
        return APIResponse.error("Agent 不存在", 404)
    
    agent_data = running_agents[agent_id]
    
    if agent_data["status"] == "running":
        return APIResponse.error("Agent 已在运行中", 400)
    
    try:
        data = request.get_json() or {}
        max_iterations = data.get('max_iterations', config.MAX_ITERATIONS)
        
        # 在后台线程中运行 Agent
        def run_agent():
            try:
                agent_data["status"] = "running"
                agent = agent_data["agent"]
                
                logger.info(f"开始运行 Agent: {agent_id}")
                results = agent.run(max_iterations)
                
                agent_data["results"] = results
                agent_data["status"] = "completed"
                agent_data["completed_at"] = datetime.now().isoformat()
                
                logger.info(f"Agent 运行完成: {agent_id}")
                
            except Exception as e:
                logger.error(f"Agent 运行失败: {e}")
                agent_data["status"] = "failed"
                agent_data["error"] = str(e)
                agent_data["failed_at"] = datetime.now().isoformat()
        
        # 启动线程
        thread = threading.Thread(target=run_agent, daemon=True)
        thread.start()
        running_threads[agent_id] = thread
        
        return jsonify(APIResponse.success({
            "agent_id": agent_id,
            "status": "running",
            "max_iterations": max_iterations
        }, "Agent 启动成功"))
        
    except Exception as e:
        logger.error(f"启动 Agent 失败: {e}")
        return APIResponse.error(f"启动 Agent 失败: {str(e)}", 500)

@app.route('/api/agents/<agent_id>/stop', methods=['POST'])
def stop_agent(agent_id: str):
    """停止 Agent 执行"""
    if agent_id not in running_agents:
        return APIResponse.error("Agent 不存在", 404)
    
    agent_data = running_agents[agent_id]
    
    if agent_data["status"] != "running":
        return APIResponse.error("Agent 未在运行", 400)
    
    try:
        # 标记为停止状态
        agent_data["status"] = "stopped"
        agent_data["stopped_at"] = datetime.now().isoformat()
        
        # 注意：这里只是标记停止，实际的线程可能需要一些时间才能结束
        logger.info(f"Agent 已标记为停止: {agent_id}")
        
        return jsonify(APIResponse.success({
            "agent_id": agent_id,
            "status": "stopped"
        }, "Agent 停止成功"))
        
    except Exception as e:
        logger.error(f"停止 Agent 失败: {e}")
        return APIResponse.error(f"停止 Agent 失败: {str(e)}", 500)

@app.route('/api/agents/<agent_id>/results', methods=['GET'])
def get_agent_results(agent_id: str):
    """获取 Agent 执行结果"""
    if agent_id not in running_agents:
        return APIResponse.error("Agent 不存在", 404)
    
    agent_data = running_agents[agent_id]
    
    if agent_data["status"] == "running":
        # 返回当前进度
        try:
            agent = agent_data["agent"]
            current_status = agent.get_enhanced_status()
            return jsonify(APIResponse.success({
                "agent_id": agent_id,
                "status": "running",
                "current_progress": current_status
            }))
        except Exception as e:
            logger.warning(f"获取运行状态失败: {e}")
            return jsonify(APIResponse.success({
                "agent_id": agent_id,
                "status": "running",
                "message": "Agent 正在运行中"
            }))
    
    elif agent_data["results"]:
        return jsonify(APIResponse.success({
            "agent_id": agent_id,
            "status": agent_data["status"],
            "results": agent_data["results"]
        }))
    
    else:
        return jsonify(APIResponse.success({
            "agent_id": agent_id,
            "status": agent_data["status"],
            "error": agent_data.get("error"),
            "message": "暂无结果"
        }))

@app.route('/api/agents/<agent_id>', methods=['DELETE'])
def delete_agent(agent_id: str):
    """删除 Agent"""
    if agent_id not in running_agents:
        return APIResponse.error("Agent 不存在", 404)
    
    agent_data = running_agents[agent_id]
    
    if agent_data["status"] == "running":
        return APIResponse.error("无法删除正在运行的 Agent，请先停止", 400)
    
    try:
        # 清理资源
        del running_agents[agent_id]
        if agent_id in running_threads:
            del running_threads[agent_id]
        
        logger.info(f"Agent 已删除: {agent_id}")
        
        return jsonify(APIResponse.success({
            "agent_id": agent_id
        }, "Agent 删除成功"))
        
    except Exception as e:
        logger.error(f"删除 Agent 失败: {e}")
        return APIResponse.error(f"删除 Agent 失败: {str(e)}", 500)

# ==================== 快捷执行接口 ====================

@app.route('/api/execute', methods=['POST'])
def quick_run():
    """快速运行 Agent（一次性执行）"""
    try:
        data = request.get_json()
        if not data or 'objective' not in data:
            return APIResponse.error("缺少必需参数: objective")
        
        objective = data['objective']
        initial_task = data.get('initial_task')
        max_iterations = data.get('max_iterations', config.MAX_ITERATIONS)
        
        logger.info(f"快速执行 Agent，目标: {objective}")
        
        # 创建并运行 Agent
        agent = EnhancedBabyAGI(objective, initial_task)
        results = agent.run(max_iterations)
        
        return jsonify(APIResponse.success({
            "objective": objective,
            "initial_task": initial_task,
            "max_iterations": max_iterations,
            "results": results
        }, "Agent 执行完成"))
        
    except Exception as e:
        logger.error(f"快速执行失败: {e}")
        return APIResponse.error(f"执行失败: {str(e)}", 500)

# ==================== 统计信息接口 ====================

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """获取系统统计信息"""
    try:
        stats = {
            "agents": {
                "total": len(running_agents),
                "running": len([a for a in running_agents.values() if a["status"] == "running"]),
                "completed": len([a for a in running_agents.values() if a["status"] == "completed"]),
                "failed": len([a for a in running_agents.values() if a["status"] == "failed"])
            },
            "tools": {
                "available": len(tool_registry.tools),
                "list": [tool["name"] for tool in tool_registry.list_tools()]
            },
            "system": {
                "config": config.get_summary(),
                "uptime": "运行中"
            }
        }
        
        return jsonify(APIResponse.success(stats))
        
    except Exception as e:
        logger.error(f"获取统计信息失败: {e}")
        return APIResponse.error(f"获取统计信息失败: {str(e)}", 500)

if __name__ == '__main__':
    try:
        # 验证配置
        config.validate()
        
        logger.info(f"启动 BabyAGI API 服务器")
        logger.info(f"配置摘要: {config.get_summary()}")
        
        app.run(
            host=config.API_HOST,
            port=config.API_PORT,
            debug=config.API_DEBUG,
            threaded=True
        )
        
    except Exception as e:
        logger.error(f"启动服务器失败: {e}")
        raise