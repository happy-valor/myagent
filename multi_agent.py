"""
多 Agent 协作模块
支持：Orchestrator-Worker, 并行委托，多 Agent 对话
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from .core import Agent, Task, Step, ActionType


@dataclass
class AgentRole:
    """Agent 角色定义"""
    name: str
    description: str
    skills: List[str] = field(default_factory=list)
    tools: List[str] = field(default_factory=list)
    
    def to_prompt(self) -> str:
        return f"""你是 {self.name}，{self.description}

你的技能：
{chr(10).join(f'- {skill}' for skill in self.skills)}

可用工具：
{chr(10).join(f'- {tool}' for tool in self.tools)}
"""


class MultiAgentOrchestrator:
    """
    多 Agent 协调器
    实现 Orchestrator-Worker 模式
    """
    
    def __init__(self, orchestrator: Agent, workers: List[Agent] = None):
        self.orchestrator = orchestrator
        self.workers = {w.llm.model: w for w in workers or []}
        self.roles: Dict[str, AgentRole] = {}
    
    def add_role(self, role: AgentRole, agent: Agent):
        """添加角色和对应的 Agent"""
        self.roles[role.name] = role
        self.workers[agent.llm.model] = agent
    
    def delegate(self, task: str, role_name: str) -> Any:
        """
        将任务委托给特定角色的 Agent
        """
        if role_name not in self.roles:
            raise ValueError(f"未知角色：{role_name}")
        
        role = self.roles[role_name]
        
        # 获取对应 Agent
        agent = list(self.workers.values())[0]  # 简化：使用第一个 worker
        
        # 添加角色上下文
        role_prompt = role.to_prompt()
        full_task = f"{role_prompt}\n\n任务：{task}"
        
        # 执行任务
        result = agent.think(full_task)
        return result
    
    def parallel_execute(self, tasks: List[Dict[str, str]]) -> List[Any]:
        """
        并行执行多个任务
        tasks: [{"task": "任务描述", "role": "角色名"}, ...]
        """
        results = []
        for task_info in tasks:
            try:
                result = self.delegate(task_info["task"], task_info["role"])
                results.append({
                    "task": task_info["task"],
                    "role": task_info["role"],
                    "result": result,
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "task": task_info["task"],
                    "role": task_info["role"],
                    "error": str(e),
                    "status": "failed"
                })
        return results
    
    def orchestrate(self, complex_task: str) -> str:
        """
        协调复杂任务
        1. 分析任务
        2. 分解子任务
        3. 分配给合适角色
        4. 汇总结果
        """
        # 使用协调者分析任务
        analysis_prompt = f"""分析以下任务，分解为子任务并分配角色：

任务：{complex_task}

可用角色：
{chr(10).join(f'- {name}: {role.description}' for name, role in self.roles.items())}

请输出 JSON 格式：
{{
  "subtasks": [
    {{
      "task": "子任务描述",
      "role": "负责角色",
      "dependencies": []  // 依赖的其他任务 ID
    }}
  ]
}}"""
        
        # 这里简化处理，实际应该调用 LLM
        # 模拟任务分解
        subtasks = [
            {"task": f"分析 {complex_task}", "role": list(self.roles.keys())[0] if self.roles else "default"}
        ]
        
        # 执行子任务
        results = self.parallel_execute(subtasks)
        
        # 汇总结果
        summary = "任务执行结果：\n"
        for r in results:
            status = "✓" if r["status"] == "success" else "✗"
            summary += f"{status} [{r['role']}] {r['task']}: {r.get('result', r.get('error', ''))}\n"
        
        return summary


class AgentConversation:
    """
    多 Agent 对话
    实现 Multi-Agent Conversation 模式
    """
    
    def __init__(self, agents: List[Agent], max_rounds: int = 5):
        self.agents = agents
        self.max_rounds = max_rounds
        self.conversation_history: List[Dict] = []
    
    def discuss(self, topic: str) -> str:
        """
        让多个 Agent 讨论一个话题
        """
        self.conversation_history = []
        
        for round_num in range(self.max_rounds):
            if round_num >= len(self.agents):
                break
            
            agent = self.agents[round_num % len(self.agents)]
            
            # 构建上下文
            context = f"讨论话题：{topic}\n\n历史对话：\n"
            for msg in self.conversation_history[-3:]:
                context += f"{msg['agent']}: {msg['content']}\n"
            
            # Agent 发言
            response = agent.think(context)
            
            # 记录
            self.conversation_history.append({
                "agent": agent.llm.model,
                "content": response,
                "round": round_num
            })
            
            # 检查是否达成共识
            if "结论" in response or "同意" in response:
                break
        
        # 返回对话总结
        return self._summarize()
    
    def _summarize(self) -> str:
        """总结对话"""
        summary = "对话总结：\n"
        for msg in self.conversation_history:
            summary += f"[{msg['agent']}] {msg['content'][:100]}...\n"
        return summary


class KanbanWorkflow:
    """
    Kanban 工作流
    实现任务看板管理
    """
    
    def __init__(self, agent: Agent):
        self.agent = agent
        self.columns = {
            "todo": [],
            "in_progress": [],
            "review": [],
            "done": []
        }
    
    def add_task(self, task: Task):
        """添加任务到待办"""
        task.status = "pending"
        self.columns["todo"].append(task)
    
    def move_to_progress(self, task_id: str) -> Optional[Task]:
        """移动任务到进行中"""
        for i, task in enumerate(self.columns["todo"]):
            if task.id == task_id:
                task.status = "in_progress"
                return self.columns["todo"].pop(i)
        return None
    
    def move_to_review(self, task: Task) -> bool:
        """移动任务到审核"""
        # 移除进行中的任务
        self.columns["in_progress"] = [t for t in self.columns["in_progress"] if t.id != task.id]
        task.status = "review"
        self.columns["review"].append(task)
        return True
    
    def move_to_done(self, task_id: str) -> Optional[Task]:
        """移动任务到完成"""
        for i, task in enumerate(self.columns["review"]):
            if task.id == task_id:
                task.status = "completed"
                return self.columns["review"].pop(i)
        return None
    
    def execute_next(self) -> Optional[str]:
        """执行下一个任务"""
        if not self.columns["todo"]:
            return None
        
        # 获取下一个任务
        task = self.move_to_progress(self.columns["todo"][0].id)
        if not task:
            return None
        
        # 执行任务
        result = self.agent.think(task.description)
        task.result = result
        
        # 移动到审核
        self.move_to_review(task)
        
        return result
    
    def get_board(self) -> Dict:
        """获取看板状态"""
        return {
            col: [t.to_dict() for t in tasks]
            for col, tasks in self.columns.items()
        }
