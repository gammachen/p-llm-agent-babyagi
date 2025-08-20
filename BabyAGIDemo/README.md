# 任务驱动型：BabyAGI应用简介（基于vllm）

## 一、大语言模型服务安装配置

### 1、建立虚拟环境

```shell
# 创建虚拟环境
conda create -n vllm python=3.10 -y
# 激活虚拟环境
conda activate vllm
# 安装vllm及依赖库
pip install vllm==0.4.3 modelscope==1.15.0 numpy==1.24.2 \
sentence-transformers==3.0.1 \
-i https://pypi.mirrors.ustc.edu.cn/simple
# 验证是否安装成功
python -c "import torch; print(torch.cuda.is_available())"
```

### 2、下载模型

```shell
# 获取模型下载脚本
https://modelscope.cn/models/ZhipuAI/glm-4-9b-chat

modelscope download --model ZhipuAI/glm-4-9b-chat

# 下载向量模型
modelscope download --model BAAI/bge-small-en-v1.5

https://modelscope.cn/models/BAAI/bge-small-en-v1.5
```

### 3、运行API服务

```shell
# 使用vllm改进版的vllm_api_server装载模型
# 支持/v1/embeddings
EMBEDDING_PATH=dataroot/models/BAAI/bge-small-en-v1.5 \
python vllm_api_server.py \
--model dataroot/models/THUDM/glm-4-9b-chat \
--served-model-name glm-4-9b-chat \
--max-model-len 8192 \
--trust-remote-code \
--disable-log-stats
```

## 二、BabyAGI安装

```shell
# 下载源码
git clone https://github.com/git-cloner/babyagi
# 切换到源码目录
cd babyagi
# 建立虚拟环境
conda create -n babyagi python=3.10 -y
# 激活虚拟环境
conda activate babyagi
# 安装依赖库
pip install -r requirements.txt \
-i https://pypi.mirrors.ustc.edu.cn/simple

pip install -r requirements.txt \
-i https://mirrors.aliyun.com/pypi/simple
```

## 三、BabyAGI配置

```shell
# 复制配置文件
cp .env.example .env
# 编辑配置文件
vi .env
# 修改以下三个大模型相关参数
LLM_MODEL=glm-4-9b-chat
OPENAI_API_KEY= EMPTY
OPENAI_API_BASE= http://server-dev:8000/v1

# 目标任务在OBJECTIVE参数中设置
LLM_MODEL=gpt-3.5-turbo
OPENAI_API_KEY=ollama  # EMPTY
OPENAI_API_BASE=http://localhost:11434/v1
# OPENAI_API_BASE=http://192.168.31.116:11434/v1
```

## 四、BabyAGI运行自带的任务

```shell
# 激活虚拟环境
conda activate babyagi
# 运行程序(Linux)
TABLE_NAME=test python babyagi.py
```

