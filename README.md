# MyAgent - AI Agent 框架

一个轻量级的 Python AI Agent 框架，实现：**Agent = LLM + 规划 + 记忆 + 工具 + 行动**

## ✨ 特性

- **ReAct 模式**: 思考 → 行动 → 观察 → 再思考的循环
- **多 Agent 协作**: Orchestrator-Worker 模式、并行委托、多 Agent 对话
- **记忆系统**: 短期记忆（上下文）+ 长期记忆（分类存储）
- **工具系统**: 文件操作、代码执行、API 调用等
- **技能系统**: 可复用的工作流模板
- **Kanban 工作流**: 任务看板管理

## 📦 安装

```bash
# 克隆或下载代码
cd your-project

# 安装依赖（可选）
pip install requests pyyaml
```

## 🚀 快速开始

### 1. 基础 Agent

```python
from myagent import Agent, LocalLLM
from myagent.core import EchoTool, CalculatorTool

# 创建 LLM（本地模拟或真实 API）
llm = LocalLLM(model="test")

# 创建工具
tools = [EchoTool(), CalculatorTool()]

# 创建 Agent
agent = Agent(llm=llm, tools=tools, max_iterations=10)

# 执行任务
result = agent.think("计算 25 * 4 + 10")
print(result)

# 查看执行历史
history = agent.get_history()
for step in history:
    print(f"{step['type']}: {step['content']}")
```

### 2. 使用真实 LLM

```python
from myagent import OpenAILLM, AnthropicLLM

# OpenAI / DeepSeek / Qwen
llm = OpenAILLM(
    model="gpt-4",
    api_key="your-api-key",
    base_url="https://api.openai.com/v1"
)

# Anthropic Claude
llm = AnthropicLLM(
    model="claude-3-sonnet",
    api_key="your-api-key"
)

agent = Agent(llm=llm, tools=tools)
```

### 3. 文件操作

```python
from myagent import ReadFileTool, WriteFileTool

# 写入文件
write_tool = WriteFileTool()
result = write_tool.execute(
    path="/tmp/hello.txt",
    content="Hello, World!"
)

# 读取文件
read_tool = ReadFileTool()
content = read_tool.execute(path="/tmp/hello.txt")
```

### 4. 多 Agent 协作

```python
from myagent import (
    MultiAgentOrchestrator, 
    AgentRole,
    LocalLLM
)

# 创建多个 Agent
llm1 = LocalLLM(model="researcher")
llm2 = LocalLLM(model="reviewer")

from myagent.core import EchoTool
agent1 = Agent(llm=llm1, tools=[EchoTool()])
agent2 = Agent(llm=llm2, tools=[EchoTool()])

# 创建协调器
orchestrator = MultiAgentOrchestrator(
    orchestrator=agent1, 
    workers=[agent2]
)

# 添加角色
researcher_role = AgentRole(
    name="researcher",
    description="研究专家，负责收集和分析信息",
    skills=["搜索", "分析", "总结"],
    tools=["web_search", "read_file"]
)

orchestrator.roles["researcher"] = researcher_role

# 执行复杂任务
result = orchestrator.orchestrate("研究 AI Agent 的发展趋势")
```

### 5. Kanban 工作流

```python
from myagent import KanbanWorkflow, Task

# 创建工作流
workflow = KanbanWorkflow(agent)

# 添加任务
workflow.add_task(Task(id="1", description="研究 Python 最佳实践"))
workflow.add_task(Task(id="2", description="编写代码示例"))

# 执行下一个任务
result = workflow.execute_next()

# 查看看板状态
board = workflow.get_board()
print(f"待办：{len(board['todo'])}")
print(f"进行中：{len(board['in_progress'])}")
print(f"审核：{len(board['review'])}")
print(f"完成：{len(board['done'])}")
```

### 6. 技能系统

```python
from myagent import SkillLibrary, SkillExecutor

# 创建技能库
library = SkillLibrary()

# 列出可用技能
for skill in library.list_skills():
    print(f"- {skill['name']}: {skill['description']}")

# 执行技能
executor = SkillExecutor(library, agent)
result = executor.execute("code_review", {"file_path": "./main.py"})
```

## 🏗️ 架构设计

### 核心组件

```
Agent
├── LLM (大脑)
│   ├── OpenAILLM
│   ├── AnthropicLLM
│   └── LocalLLM
├── Memory (记忆)
│   ├── Short-term (短期)
│   └── Long-term (长期)
├── Planner (规划器)
└── Tools (工具集)
    ├── File Tools
    ├── Terminal Tools
    ├── API Tools
    └── Custom Tools
```

### 设计模式实现

| 模式 | 实现类 | 说明 |
|------|--------|------|
| ReAct | `Agent.think()` | 思考→行动→观察循环 |
| Orchestrator-Worker | `MultiAgentOrchestrator` | 协调者 - 工作者模式 |
| Parallelization | `parallel_execute()` | 并行执行多个任务 |
| Evaluator-Optimizer | 技能系统 | 评估和优化循环 |
| RAG | `Memory` | 检索增强生成 |
| Reflection | `Step` 历史 | 从历史中学习 |
| Checkpointing | `KanbanWorkflow` | 任务状态保存 |

## 🛠️ 可用工具

| 工具 | 功能 | 参数 |
|------|------|------|
| `ReadFileTool` | 读取文件 | path, offset, limit |
| `WriteFileTool` | 写入文件 | path, content |
| `TerminalTool` | 执行 shell 命令 | command, workdir |
| `ExecuteCodeTool` | 执行 Python 代码 | code |
| `WebSearchTool` | 网络搜索 | query, num_results |
| `APIRequestTool` | HTTP 请求 | method, url, headers, body |
| `EchoTool` | 回声（测试） | message |
| `CalculatorTool` | 计算器 | expression |

## 📚 内置技能

1. **code_review**: 代码审查
2. **generate_docs**: 文档生成
3. **generate_tests**: 测试生成
4. **research**: 研究总结

## 🔧 自定义工具

```python
from myagent import Tool

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="my_tool",
            description="我的自定义工具",
            parameters={"param1": "string", "param2": "int"}
        )
    
    def execute(self, param1: str, param2: int) -> str:
        # 实现工具逻辑
        return f"结果：{param1}, {param2}"

# 使用
agent = Agent(llm=llm, tools=[MyCustomTool()])
```

## 📝 自定义技能

创建 `skills/my_skill.yaml`:

```yaml
name: my_skill
description: 我的自定义技能
parameters:
  input_file: ""
  output_file: "result.md"
tools_required:
  - read_file
  - write_file
steps:
  - action: read_file
    description: 读取输入文件
    parameters:
      path: "${input_file}"
    output_var: content
  
  - action: analyze
    description: 分析内容
    prompt: "分析以下内容:\n${content}"
    output_var: analysis
  
  - action: write_file
    description: 写入结果
    parameters:
      path: "${output_file}"
      content: "${analysis}"
```

## 🧪 运行示例

```bash
cd myagent
python3 examples.py
```

## 📖 相关资源

- [AI Agent 概念与架构](../AI%20Agent%20概念与架构.md)
- [Agent 设计模式](../Agent%20设计模式.md)
- [Lilian Weng: LLM Powered Autonomous Agents](https://lilianweng.github.io/posts/2023-06-23-agent/)
- [Anthropic: Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)

## 📄 License

MIT
