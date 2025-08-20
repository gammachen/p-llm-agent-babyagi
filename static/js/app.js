// BabyAGI Web Interface JavaScript
class BabyAGIApp {
    constructor() {
        this.baseURL = '';
        this.agents = new Map();
        this.refreshInterval = null;
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadAgents();
        this.loadSystemStats();
        this.startAutoRefresh();
    }

    bindEvents() {
        // 创建 Agent 表单
        document.getElementById('create-agent-form').addEventListener('submit', (e) => {
            e.preventDefault();
            this.createAgent();
        });

        // 快速执行按钮
        document.getElementById('quick-execute-btn').addEventListener('click', () => {
            this.quickExecute();
        });

        // 刷新 Agents 按钮
        document.getElementById('refresh-agents-btn').addEventListener('click', () => {
            this.loadAgents();
        });
    }

    async createAgent() {
        const name = document.getElementById('agent-name').value.trim();
        const objective = document.getElementById('agent-objective').value.trim();
        const initialTask = document.getElementById('agent-initial-task').value.trim();

        if (!name || !objective || !initialTask) {
            this.showNotification('请填写所有必填字段', 'error');
            return;
        }

        try {
            const response = await fetch('/api/agents', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    objective: objective,
                    initial_task: initialTask
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showNotification(`Agent "${name}" 创建成功`, 'success');
                document.getElementById('create-agent-form').reset();
                this.loadAgents();
            } else {
                this.showNotification(data.error || '创建失败', 'error');
            }
        } catch (error) {
            console.error('创建 Agent 失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }

    async quickExecute() {
        const objective = document.getElementById('quick-objective').value.trim();
        const task = document.getElementById('quick-task').value.trim();

        if (!objective || !task) {
            this.showNotification('请填写目标和任务描述', 'error');
            return;
        }

        try {
            const button = document.getElementById('quick-execute-btn');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>执行中...';

            const response = await fetch('/api/execute', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    objective: objective,
                    initial_task: task
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('任务执行成功', 'success');
                this.displayResults(data.results);
                document.getElementById('quick-objective').value = '';
                document.getElementById('quick-task').value = '';
            } else {
                this.showNotification(data.error || '执行失败', 'error');
            }
        } catch (error) {
            console.error('快速执行失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        } finally {
            const button = document.getElementById('quick-execute-btn');
            button.disabled = false;
            button.innerHTML = '<i class="fas fa-rocket mr-2"></i>立即执行';
        }
    }

    async loadAgents() {
        try {
            const response = await fetch('/api/agents');
            const data = await response.json();
            
            if (response.ok) {
                this.agents.clear();
                data.agents.forEach(agent => {
                    this.agents.set(agent.id, agent);
                });
                this.renderAgentsList();
            } else {
                console.error('加载 Agents 失败:', data.error);
            }
        } catch (error) {
            console.error('加载 Agents 失败:', error);
        }
    }

    renderAgentsList() {
        const container = document.getElementById('agents-list');
        
        if (this.agents.size === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center py-4">暂无 Agent</p>';
            return;
        }

        const agentsHTML = Array.from(this.agents.values()).map(agent => {
            const statusClass = agent.status === 'running' ? 'status-running bg-green-100 text-green-800' : 
                               agent.status === 'stopped' ? 'bg-red-100 text-red-800' : 
                               'bg-gray-100 text-gray-800';
            
            return `
                <div class="border border-gray-200 rounded-md p-3">
                    <div class="flex justify-between items-start mb-2">
                        <h4 class="font-semibold text-gray-800">${agent.name}</h4>
                        <span class="px-2 py-1 text-xs rounded-full ${statusClass}">
                            ${this.getStatusText(agent.status)}
                        </span>
                    </div>
                    <p class="text-sm text-gray-600 mb-2">${agent.objective}</p>
                    <div class="flex space-x-2">
                        ${agent.status === 'stopped' ? 
                            `<button onclick="app.startAgent('${agent.id}')" class="text-xs bg-green-500 hover:bg-green-600 text-white px-2 py-1 rounded">
                                <i class="fas fa-play mr-1"></i>启动
                            </button>` : 
                            `<button onclick="app.stopAgent('${agent.id}')" class="text-xs bg-red-500 hover:bg-red-600 text-white px-2 py-1 rounded">
                                <i class="fas fa-stop mr-1"></i>停止
                            </button>`
                        }
                        <button onclick="app.getAgentResults('${agent.id}')" class="text-xs bg-blue-500 hover:bg-blue-600 text-white px-2 py-1 rounded">
                            <i class="fas fa-eye mr-1"></i>查看结果
                        </button>
                        <button onclick="app.deleteAgent('${agent.id}')" class="text-xs bg-gray-500 hover:bg-gray-600 text-white px-2 py-1 rounded">
                            <i class="fas fa-trash mr-1"></i>删除
                        </button>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = agentsHTML;
    }

    getStatusText(status) {
        const statusMap = {
            'running': '运行中',
            'stopped': '已停止',
            'completed': '已完成',
            'error': '错误'
        };
        return statusMap[status] || status;
    }

    async startAgent(agentId) {
        try {
            const response = await fetch(`/api/agents/${agentId}/start`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Agent 启动成功', 'success');
                this.loadAgents();
            } else {
                this.showNotification(data.error || '启动失败', 'error');
            }
        } catch (error) {
            console.error('启动 Agent 失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }

    async stopAgent(agentId) {
        try {
            const response = await fetch(`/api/agents/${agentId}/stop`, {
                method: 'POST'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Agent 停止成功', 'success');
                this.loadAgents();
            } else {
                this.showNotification(data.error || '停止失败', 'error');
            }
        } catch (error) {
            console.error('停止 Agent 失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }

    async getAgentResults(agentId) {
        try {
            const response = await fetch(`/api/agents/${agentId}/results`);
            const data = await response.json();
            
            if (response.ok) {
                this.displayResults(data.results);
            } else {
                this.showNotification(data.error || '获取结果失败', 'error');
            }
        } catch (error) {
            console.error('获取 Agent 结果失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }

    async deleteAgent(agentId) {
        if (!confirm('确定要删除这个 Agent 吗？')) {
            return;
        }

        try {
            const response = await fetch(`/api/agents/${agentId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (response.ok) {
                this.showNotification('Agent 删除成功', 'success');
                this.loadAgents();
            } else {
                this.showNotification(data.error || '删除失败', 'error');
            }
        } catch (error) {
            console.error('删除 Agent 失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }

    displayResults(results) {
        const container = document.getElementById('results-container');
        
        if (!results || results.length === 0) {
            container.innerHTML = '<p class="text-gray-500 text-center">暂无执行结果</p>';
            return;
        }

        const resultsHTML = results.map((result, index) => {
            return `
                <div class="mb-4 p-4 border border-gray-200 rounded-md">
                    <div class="flex justify-between items-center mb-2">
                        <h4 class="font-semibold text-gray-800">任务 ${index + 1}</h4>
                        <span class="text-xs text-gray-500">${new Date(result.timestamp || Date.now()).toLocaleString()}</span>
                    </div>
                    <p class="text-sm text-gray-600 mb-2"><strong>任务:</strong> ${result.task || '未知任务'}</p>
                    <p class="text-sm text-gray-800"><strong>结果:</strong> ${result.result || '无结果'}</p>
                </div>
            `;
        }).join('');

        container.innerHTML = resultsHTML;
    }

    async loadSystemStats() {
        try {
            const response = await fetch('/api/stats');
            const data = await response.json();
            
            if (response.ok) {
                document.getElementById('active-agents-count').textContent = data.active_agents || 0;
                document.getElementById('completed-tasks-count').textContent = data.completed_tasks || 0;
                document.getElementById('uptime').textContent = this.formatUptime(data.uptime || 0);
                document.getElementById('memory-usage').textContent = `${Math.round(data.memory_usage || 0)}MB`;
            }
        } catch (error) {
            console.error('加载系统统计失败:', error);
        }
    }

    formatUptime(seconds) {
        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        return `${hours}h ${minutes}m`;
    }

    startAutoRefresh() {
        this.refreshInterval = setInterval(() => {
            this.loadAgents();
            this.loadSystemStats();
        }, 5000); // 每5秒刷新一次
    }

    showNotification(message, type = 'success') {
        const notification = document.getElementById('notification');
        const messageElement = document.getElementById('notification-message');
        
        messageElement.textContent = message;
        
        // 设置颜色
        notification.className = `fixed top-4 right-4 px-6 py-3 rounded-md shadow-lg transform transition-transform duration-300 ${
            type === 'success' ? 'bg-green-500 text-white' : 
            type === 'error' ? 'bg-red-500 text-white' : 
            'bg-blue-500 text-white'
        }`;
        
        // 显示通知
        notification.style.transform = 'translateX(0)';
        
        // 3秒后隐藏
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
        }, 3000);
    }
}

// 初始化应用
const app = new BabyAGIApp();

// 页面卸载时清理定时器
window.addEventListener('beforeunload', () => {
    if (app.refreshInterval) {
        clearInterval(app.refreshInterval);
    }
});