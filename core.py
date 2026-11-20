"""
AI Agent 核心框架
实现：Agent = LLM + 规划 + 记忆 + 工具 + 行动
"""

from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class ActionType(Enum):
    """行动类型"""
    THOUGHT = "thought"      # 思考
    ACTION = "action"        # 工具调用
    OBSERVATION = "observation"  # 观察结果
    ANSWER = "answer"        # 最终答案


@dataclass
class Step:
    """ReAct 循环中的单步"""
    step_type: ActionType
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "type": self.step_type.value,
            "content": self.content,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


@dataclass
class Task:
    """任务定义"""
    id: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    subtasks: List['Task'] = field(default_factory=list)
    result: Optional[Any] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "status": self.status,
            "subtasks": [t.to_dict() for t in self.subtasks],
            "result": self.result
        }


class Tool:
    """工具基类"""
    def __init__(self, name: str, description: str, parameters: Dict = None):
        self.name = name
        self.description = description
        self.parameters = parameters or {}
    
    def execute(self, **kwargs) -> Any:
        raise NotImplementedError
    
    def to_schema(self) -> Dict:
        """返回工具 schema，用于 LLM 理解"""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }


class Memory:
    """记忆系统"""
    
    def __init__(self, max_short_term_size: int = 100):
        self.short_term: List[Dict] = []  # 短期记忆（当前会话）
        self.long_term: Dict[str, List[Dict]] = {}  # 长期记忆（分类存储）
        self.max_short_term_size = max_short_term_size
    
    def add_short_term(self, item: Dict):
        """添加短期记忆"""
        self.short_term.append(item)
        self._compress_if_needed()
    
    def add_long_term(self, category: str, item: Dict):
        """添加长期记忆"""
        if category not in self.long_term:
            self.long_term[category] = []
        self.long_term[category].append(item)
    
    def get_short_term(self) -> List[Dict]:
        """获取短期记忆"""
        return self.short_term
    
    def get_long_term(self, category: str) -> List[Dict]:
        """获取某类长期记忆"""
        return self.long_term.get(category, [])
    
    def _compress_if_needed(self):
        """压缩短期记忆（当超过限制时）"""
        if len(self.short_term) <= self.max_short_term_size:
            return
        
        # 保留最近 N 条，压缩之前的
        keep_count = self.max_short_term_size // 2
        recent = self.short_term[-keep_count:]
        old = self.short_term[:-keep_count]
        
        # 简单压缩：将旧的总结为一条
        summary = {
            "type": "summary",
            "content": f"前 {len(old)} 条历史记录已压缩",
            "compressed_count": len(old)
        }
        
        self.short_term = [summary] + recent


class Planner:
    """任务规划器"""
    
    @staticmethod
    def decompose_task(goal: str, available_tools: List[Tool]) -> Task:
        """
        将复杂目标分解为子任务
        这里用规则实现，实际应该用 LLM
        """
        # 简单实现：返回单任务
        return Task(id="1", description=goal, status="pending")
    
    @staticmethod
    def create_plan(task: Task, context: Dict) -> List[str]:
        """
        为任务创建执行计划
        返回步骤列表
        """
        return [
            f"1. 理解任务：{task.description}",
            f"2. 分析可用工具：{len(context.get('tools', []))} 个",
            "3. 选择合适工具执行",
            "4. 验证结果"
        ]


class LLMInterface:
    """LLM 接口（需要实现）"""
    
    def __init__(self, model: str, api_key: str = None, base_url: str = None):
        self.model = model
        self.api_key = api_key
        self.base_url = base_url
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """
        调用 LLM
        返回：{
            "content": str,
            "tool_calls": List[Dict] (可选)
        }
        """
        raise NotImplementedError
    
    def format_system_prompt(self, tools: List[Tool]) -> str:
        """格式化系统提示"""
        tool_descriptions = "\n\n".join([
            f"### {t.name}\n{t.description}\n参数：{t.parameters}"
            for t in tools
        ])
        
        return f"""你是一个 AI Agent，能够自主规划、调用工具、完成任务。

可用工具：
{tool_descriptions}

请按照 ReAct 模式思考：
1. Thought: 分析当前情况，决定下一步行动
2. Action: 如果需要工具，选择并调用
3. Observation: 观察工具返回结果
4. 重复直到可以给出最终答案
5. Answer: 输出最终结果

输出格式：
Thought: <你的思考>
Action: <工具名>
Action Input: <参数 JSON>
--- 或 ---
Answer: <最终答案>
"""


class Agent:
    """AI Agent 主类"""
    
    def __init__(
        self,
        llm: LLMInterface,
        tools: List[Tool] = None,
        max_iterations: int = 10
    ):
        self.llm = llm
        self.tools = {t.name: t for t in tools or []}
        self.memory = Memory()
        self.planner = Planner()
        self.max_iterations = max_iterations
        self.steps: List[Step] = []
    
    def think(self, user_input: str, context: Dict = None) -> str:
        """
        思考并执行任务
        返回最终答案
        """
        # 创建任务
        task = self.planner.decompose_task(user_input, list(self.tools.values()))
        
        # 准备消息
        system_prompt = self.llm.format_system_prompt(list(self.tools.values()))
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # ReAct 循环
        for iteration in range(self.max_iterations):
            # 添加历史步骤到上下文
            if self.steps:
                history = "\n".join([
                    f"{s.step_type.value}: {s.content}"
                    for s in self.steps[-5:]  # 最近 5 步
                ])
                messages.append({
                    "role": "user",
                    "content": f"历史步骤:\n{history}\n\n请继续"
                })
            
            # 调用 LLM
            response = self.llm.chat(
                messages=messages,
                tools=[t.to_schema() for t in self.tools.values()]
            )
            
            content = response.get("content", "")
            
            # 解析响应
            if "Action:" in content:
                # 需要调用工具
                thought = self._extract_field(content, "Thought:")
                action_name = self._extract_field(content, "Action:")
                action_input = self._extract_field(content, "Action Input:")
                
                # 记录思考
                self.steps.append(Step(ActionType.THOUGHT, thought))
                self.memory.add_short_term({"type": "thought", "content": thought})
                
                # 执行工具
                if action_name in self.tools and action_input:
                    try:
                        params = json.loads(action_input)
                        result = self.tools[action_name].execute(**params)
                        
                        # 记录行动和观察
                        self.steps.append(Step(ActionType.ACTION, f"{action_name}({action_input})"))
                        self.steps.append(Step(ActionType.OBSERVATION, str(result)))
                        
                        self.memory.add_short_term({
                            "type": "action",
                            "tool": action_name,
                            "result": str(result)
                        })
                        
                        # 继续循环
                        continue
                        
                    except Exception as e:
                        error_msg = f"工具调用失败：{e}"
                        self.steps.append(Step(ActionType.OBSERVATION, error_msg))
                        messages.append({"role": "user", "content": error_msg})
            else:
                # 最终答案
                answer = self._extract_field(content, "Answer:") or content
                self.steps.append(Step(ActionType.ANSWER, answer))
                self.memory.add_short_term({"type": "answer", "content": answer})
                task.status = "completed"
                task.result = answer
                
                return answer
        
        # 超过最大迭代次数
        task.status = "failed"
        return f"任务未完成（超过 {self.max_iterations} 次迭代）"
    
    def _extract_field(self, text: str, field_name: str) -> str:
        """从文本中提取字段值"""
        try:
            start = text.index(field_name) + len(field_name)
            end = text.index("\n", start)
            return text[start:end].strip()
        except ValueError:
            return ""
    
    def get_history(self) -> List[Dict]:
        """获取执行历史"""
        return [s.to_dict() for s in self.steps]
    
    def reset(self):
        """重置 Agent 状态"""
        self.steps = []
        self.memory = Memory()


# ============ 示例工具实现 ============

class EchoTool(Tool):
    """回声工具（测试用）"""
    def __init__(self):
        super().__init__(
            name="echo",
            description="回声工具，返回输入的内容",
            parameters={"message": "string"}
        )
    
    def execute(self, message: str) -> str:
        return f"Echo: {message}"


class CalculatorTool(Tool):
    """计算器工具"""
    def __init__(self):
        super().__init__(
            name="calculator",
            description="执行数学计算，支持 + - * /",
            parameters={"expression": "string"}
        )
    
    def execute(self, expression: str) -> str:
        try:
            # 安全计算
            result = eval(expression, {"__builtins__": {}}, {})
            return str(result)
        except Exception as e:
            return f"计算错误：{e}"


class SearchTool(Tool):
    """搜索工具（示例）"""
    def __init__(self):
        super().__init__(
            name="search",
            description="搜索信息",
            parameters={"query": "string"}
        )
    
    def execute(self, query: str) -> str:
        # 实际实现应该调用搜索引擎 API
        return f"搜索结果 for '{query}': [模拟结果]"


# ============ 使用示例 ============

if __name__ == "__main__":
    # 创建 LLM 接口（需要实现具体调用）
    # llm = OpenAILLM(model="gpt-4", api_key="your-key")
    
    # 创建工具
    tools = [EchoTool(), CalculatorTool(), SearchTool()]
    
    # 创建 Agent
    # agent = Agent(llm=llm, tools=tools)
    
    # 执行任务
    # result = agent.think("计算 25 * 4 + 10")
    # print(result)
    
    print("AI Agent 框架已加载")
    print(f"可用工具：{[t.name for t in tools]}")
