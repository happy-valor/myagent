"""
AI Agent 框架使用示例
"""

import sys
sys.path.insert(0, '.')

from myagent.core import Agent, Task, EchoTool, CalculatorTool, SearchTool
from myagent.llm import LocalLLM
from myagent.tools import get_all_tools
from myagent.multi_agent import (
    MultiAgentOrchestrator, 
    AgentRole,
    KanbanWorkflow
)
from myagent.skills import SkillLibrary, SkillExecutor


def example_basic_agent():
    """示例 1: 基础 Agent"""
    print("\n" + "="*50)
    print("示例 1: 基础 Agent")
    print("="*50)
    
    # 创建 LLM（使用本地模拟）
    llm = LocalLLM(model="local-test")
    
    # 创建工具
    tools = [EchoTool(), CalculatorTool(), SearchTool()]
    
    # 创建 Agent
    agent = Agent(llm=llm, tools=tools, max_iterations=5)
    
    # 执行任务
    result = agent.think("计算 25 * 4 + 10")
    print(f"结果：{result}")
    
    # 查看历史
    print("\n执行历史:")
    for step in agent.get_history():
        print(f"  {step['type']}: {step['content'][:50]}...")


def example_file_operations():
    """示例 2: 文件操作"""
    print("\n" + "="*50)
    print("示例 2: 文件操作")
    print("="*50)
    
    from myagent.tools import ReadFileTool, WriteFileTool
    
    # 写入文件
    write_tool = WriteFileTool()
    result = write_tool.execute(
        path="/tmp/test_agent.txt",
        content="Hello, AI Agent!\n这是测试文件。"
    )
    print(f"写入结果：{result}")
    
    # 读取文件
    read_tool = ReadFileTool()
    result = read_tool.execute(path="/tmp/test_agent.txt")
    print(f"读取结果：{result}")


def example_multi_agent():
    """示例 3: 多 Agent 协作"""
    print("\n" + "="*50)
    print("示例 3: 多 Agent 协作")
    print("="*50)
    
    # 创建多个 Agent
    llm1 = LocalLLM(model="researcher")
    llm2 = LocalLLM(model="reviewer")
    
    from myagent.core import EchoTool
    agent1 = Agent(llm=llm1, tools=[EchoTool()])
    agent2 = Agent(llm=llm2, tools=[EchoTool()])
    
    # 创建协调器
    orchestrator = MultiAgentOrchestrator(orchestrator=agent1, workers=[agent2])
    
    # 添加角色
    researcher_role = AgentRole(
        name="researcher",
        description="研究专家，负责收集和分析信息",
        skills=["搜索", "分析", "总结"],
        tools=["web_search", "read_file"]
    )
    
    reviewer_role = AgentRole(
        name="reviewer",
        description="审核专家，负责检查质量和准确性",
        skills=["审查", "验证", "建议"],
        tools=["read_file", "write_file"]
    )
    
    orchestrator.roles["researcher"] = researcher_role
    orchestrator.roles["reviewer"] = reviewer_role
    
    # 执行复杂任务
    result = orchestrator.orchestrate("研究 AI Agent 的发展趋势")
    print(f"协作结果：{result}")


def example_kanban():
    """示例 4: Kanban 工作流"""
    print("\n" + "="*50)
    print("示例 4: Kanban 工作流")
    print("="*50)
    
    llm = LocalLLM(model="worker")
    agent = Agent(llm=llm, tools=[EchoTool()])
    
    # 创建工作流
    workflow = KanbanWorkflow(agent)
    
    # 添加任务
    workflow.add_task(Task(id="1", description="研究 Python 最佳实践"))
    workflow.add_task(Task(id="2", description="编写代码示例"))
    workflow.add_task(Task(id="3", description="生成文档"))
    
    # 查看看板
    board = workflow.get_board()
    print(f"待办：{len(board['todo'])} 个任务")
    print(f"进行中：{len(board['in_progress'])} 个任务")
    
    # 执行下一个任务
    result = workflow.execute_next()
    print(f"执行结果：{result[:100]}...")
    
    # 查看更新后的看板
    board = workflow.get_board()
    print(f"\n更新后:")
    print(f"  待办：{len(board['todo'])}")
    print(f"  进行中：{len(board['in_progress'])}")
    print(f"  审核：{len(board['review'])}")


def example_skills():
    """示例 5: 技能系统"""
    print("\n" + "="*50)
    print("示例 5: 技能系统")
    print("="*50)
    
    # 创建技能库
    library = SkillLibrary()
    
    # 列出可用技能
    print("可用技能:")
    for skill in library.list_skills():
        print(f"  - {skill['name']}: {skill['description']}")
    
    # 获取技能详情
    code_review = library.get_skill("code_review")
    if code_review:
        print(f"\n代码审查技能步骤:")
        for i, step in enumerate(code_review.steps, 1):
            print(f"  {i}. {step['action']}: {step['description']}")


def example_task_planning():
    """示例 6: 任务规划"""
    print("\n" + "="*50)
    print("示例 6: 任务规划")
    print("="*50)
    
    from myagent.core import Planner
    
    # 创建任务
    task = Task(
        id="1",
        description="开发一个待办事项应用",
        status="pending"
    )
    
    # 添加子任务
    task.subtasks = [
        Task(id="1.1", description="设计数据库模型"),
        Task(id="1.2", description="实现 API 接口"),
        Task(id="1.3", description="创建前端界面"),
        Task(id="1.4", description="编写测试"),
    ]
    
    # 创建计划
    plan = Planner.create_plan(task, {"tools": ["read_file", "write_file", "terminal"]})
    
    print(f"任务：{task.description}\n")
    print("执行计划:")
    for step in plan:
        print(f"  {step}")
    
    print("\n子任务:")
    for subtask in task.subtasks:
        print(f"  - [{subtask.status}] {subtask.description}")


def main():
    """运行所有示例"""
    print("\n" + "="*50)
    print("AI Agent 框架示例")
    print("="*50)
    
    try:
        example_basic_agent()
    except Exception as e:
        print(f"示例 1 失败：{e}")
    
    try:
        example_file_operations()
    except Exception as e:
        print(f"示例 2 失败：{e}")
    
    try:
        example_multi_agent()
    except Exception as e:
        print(f"示例 3 失败：{e}")
    
    try:
        example_kanban()
    except Exception as e:
        print(f"示例 4 失败：{e}")
    
    try:
        example_skills()
    except Exception as e:
        print(f"示例 5 失败：{e}")
    
    try:
        example_task_planning()
    except Exception as e:
        print(f"示例 6 失败：{e}")
    
    print("\n" + "="*50)
    print("所有示例完成!")
    print("="*50)


if __name__ == "__main__":
    main()
