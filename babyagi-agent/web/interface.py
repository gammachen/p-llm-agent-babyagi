import gradio as gr
import sys
import os
import logging
import time

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.custom_babyagi import CustomBabyAGI
from config import Config

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = Config()

def run_babyagi_interface(objective, initial_task):
    logger.info(f"Starting BabyAGI run from web interface")
    logger.info(f"Objective: {objective}")
    if initial_task:
        logger.info(f"Initial task: {initial_task}")
    
    start_time = time.time()
    try:
        babyagi = CustomBabyAGI(objective, config)
        results = babyagi.run(initial_task or None)
        
        end_time = time.time()
        logger.info(f"BabyAGI run completed in {end_time - start_time:.2f} seconds")
        
        # 格式化结果
        output = f"目标: {objective}\n"
        output += f"执行时间: {end_time - start_time:.2f} 秒\n\n"
        
        documents = results.get('documents', [])
        metadatas = results.get('metadatas', [])
        
        for i, (doc, metadata) in enumerate(zip(documents, metadatas)):
            task_name = metadata.get('task', f'任务 {i+1}')
            output += f"任务 {i+1}: {task_name}\n"
            output += f"结果: {doc}\n\n"
        
        if not documents:
            output += "没有生成任务结果。\n"
        
        logger.info(f"Returning results with {len(documents)} tasks")
        return output
    except Exception as e:
        logger.error(f"Error in BabyAGI execution: {str(e)}", exc_info=True)
        end_time = time.time()
        return f"执行出错: {str(e)}\n执行时间: {end_time - start_time:.2f} 秒"

# 创建 Gradio 界面
with gr.Blocks(title="BabyAGI Agent") as iface:
    gr.Markdown("# BabyAGI Agent")
    gr.Markdown("基于 BabyAGI 的自主 Agent 系统")
    
    with gr.Row():
        with gr.Column():
            objective = gr.Textbox(
                label="目标", 
                value="Solve world hunger",
                max_lines=3
            )
            initial_task = gr.Textbox(
                label="初始任务（可选）",
                max_lines=3
            )
            run_btn = gr.Button("运行 BabyAGI")
        
        with gr.Column():
            output = gr.Textbox(
                label="执行结果",
                interactive=False,
                lines=20
            )
    
    run_btn.click(
        fn=run_babyagi_interface,
        inputs=[objective, initial_task],
        outputs=output
    )

if __name__ == '__main__':
    logger.info("Starting BabyAGI web interface")
    iface.launch(server_name="0.0.0.0", server_port=7860)