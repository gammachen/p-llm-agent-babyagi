from flask import Flask, request, jsonify
import logging
import sys
import os
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.custom_babyagi import CustomBabyAGI
from config import Config

app = Flask(__name__)
config = Config()

# 设置日志
logging.basicConfig(level=getattr(logging, config.LOG_LEVEL.upper()))
logger = logging.getLogger(__name__)

@app.before_request
def log_request_info():
    logger.info(f"Incoming request: {request.method} {request.url}")
    logger.debug(f"Request headers: {dict(request.headers)}")
    if request.is_json:
        logger.debug(f"Request data: {request.get_json()}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response status: {response.status}")
    logger.debug(f"Response data: {response.get_data()}")
    return response

@app.route('/api/run', methods=['POST'])
def run_babyagi():
    start_time = time.time()
    data = request.json
    objective = data.get('objective', config.OBJECTIVE)
    initial_task = data.get('initial_task')
    
    logger.info(f"Starting BabyAGI run with objective: {objective}")
    if initial_task:
        logger.info(f"Initial task: {initial_task}")
    
    try:
        babyagi = CustomBabyAGI(objective, config)
        results = babyagi.run(initial_task)
        
        end_time = time.time()
        logger.info(f"BabyAGI run completed in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            "status": "success",
            "objective": objective,
            "execution_time": end_time - start_time,
            "results": results
        })
    except Exception as e:
        logger.error(f"Error running BabyAGI: {str(e)}", exc_info=True)
        end_time = time.time()
        return jsonify({
            "status": "error",
            "message": str(e),
            "execution_time": end_time - start_time
        }), 500

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    logger.info("Fetching task history")
    start_time = time.time()
    
    # 获取存储的任务历史
    try:
        babyagi = CustomBabyAGI("", config)
        results = babyagi.vector_db.get() if hasattr(babyagi.vector_db, 'get') else babyagi.vector_db
        
        end_time = time.time()
        logger.info(f"Task history fetched in {end_time - start_time:.2f} seconds")
        
        return jsonify({
            "tasks": results.get('documents', []),
            "metadatas": results.get('metadatas', []),
            "fetch_time": end_time - start_time
        })
    except Exception as e:
        logger.error(f"Error getting tasks: {str(e)}", exc_info=True)
        end_time = time.time()
        return jsonify({
            "status": "error",
            "message": str(e),
            "fetch_time": end_time - start_time
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    logger.debug("Health check requested")
    return jsonify({"status": "healthy"})

if __name__ == '__main__':
    logger.info("Starting BabyAGI API server")
    app.run(debug=True, host='0.0.0.0', port=5000)