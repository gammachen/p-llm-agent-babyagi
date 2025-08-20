import argparse
import sys
import os
import logging
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.custom_babyagi import CustomBabyAGI
from config import Config

def setup_logging(config):
    """设置日志配置"""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('babyagi.log')
        ]
    )
    
    # 设置第三方库的日志级别，减少噪音
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)

def main():
    parser = argparse.ArgumentParser(description='BabyAGI Agent')
    parser.add_argument('--objective', type=str, help='Objective for the BabyAGI agent')
    parser.add_argument('--initial-task', type=str, help='Initial task to start with')
    parser.add_argument('--mode', type=str, choices=['api', 'web', 'cli'], 
                       default='cli', help='Run mode: api, web, or cli')
    
    args = parser.parse_args()
    
    # 加载配置
    config = Config()
    
    # 设置日志
    setup_logging(config)
    logger = logging.getLogger(__name__)
    logger.info("Starting BabyAGI Agent")
    logger.info(f"LLM Provider: {config.LLM_PROVIDER}")
    logger.info(f"Max iterations: {config.MAX_ITERATIONS}")
    
    if args.mode == 'api':
        # 启动API服务
        logger.info("Starting in API mode")
        from api.app import app
        app.run(host='0.0.0.0', port=5000, debug=False)
        
    elif args.mode == 'web':
        # 启动Web界面
        logger.info("Starting in Web mode")
        from web.interface import iface
        iface.launch(server_name='0.0.0.0', server_port=7860)
        
    else:
        # CLI模式
        objective = args.objective or config.OBJECTIVE
        initial_task = args.initial_task
        
        logger.info("Starting in CLI mode")
        logger.info(f"Objective: {objective}")
        if initial_task:
            logger.info(f"Initial task: {initial_task}")
        
        start_time = time.time()
        try:
            babyagi = CustomBabyAGI(objective, config)
            results = babyagi.run(initial_task)
            
            end_time = time.time()
            
            print("\n" + "="*50)
            print("FINAL RESULTS")
            print("="*50)
            print(f"Total execution time: {end_time - start_time:.2f} seconds")
            
            documents = results.get('documents', [])
            metadatas = results.get('metadatas', [])
            
            for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
                task_name = metadata.get('task', f'Task {i+1}')
                print(f"\nTask {i+1}: {task_name}")
                print(f"Result: {doc}")
                
            logger.info(f"CLI execution completed in {end_time - start_time:.2f} seconds with {len(documents)} tasks")
        except Exception as e:
            logger.error(f"Error during CLI execution: {str(e)}", exc_info=True)
            print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()