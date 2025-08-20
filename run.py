#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
BabyAGI Agent 系统启动脚本

这个脚本用于启动 BabyAGI Agent 系统的 Web 服务器。
它会自动加载配置、初始化日志系统，并启动 Flask 应用。

使用方法:
    python run.py
    
环境变量:
    - 可以通过 .env 文件配置系统参数
    - 详见 .env.example 文件
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from app import app
    from config import config
    from logger import get_logger
    
    logger = get_logger("startup")
    
    def main():
        """主函数"""
        try:
            # 验证配置
            config.validate()
            
            logger.info("="*50)
            logger.info("启动 BabyAGI Agent 系统")
            logger.info("="*50)
            logger.info(f"配置摘要: {config.get_summary()}")
            logger.info(f"Web 界面: http://{config.API_HOST}:{config.API_PORT}")
            logger.info(f"API 文档: http://{config.API_HOST}:{config.API_PORT}/api/info")
            logger.info("="*50)
            
            # 启动 Flask 应用
            app.run(
                host=config.API_HOST,
                port=config.API_PORT,
                debug=config.API_DEBUG,
                threaded=True
            )
            
        except KeyboardInterrupt:
            logger.info("收到中断信号，正在关闭服务器...")
        except Exception as e:
            logger.error(f"启动服务器失败: {e}")
            sys.exit(1)
        finally:
            logger.info("BabyAGI Agent 系统已关闭")
    
    if __name__ == '__main__':
        main()
        
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖包: pip install -r requirements.txt")
    sys.exit(1)
except Exception as e:
    print(f"启动失败: {e}")
    sys.exit(1)