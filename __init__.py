"""
MyAgent - AI Agent 框架
实现：Agent = LLM + 规划 + 记忆 + 工具 + 行动
"""

from .core import (
    Agent,
    Task,
    Step,
    ActionType,
    Tool,
    Memory,
    Planner,
    LLMInterface
)

from .llm import (
    OpenAILLM,
    AnthropicLLM,
    LocalLLM
)

from .tools import (
    ReadFileTool,
    WriteFileTool,
    TerminalTool,
    ExecuteCodeTool,
    WebSearchTool,
    BrowserTool,
    DatabaseTool,
    APIRequestTool,
    get_all_tools,
    get_tool_by_name
)

from .multi_agent import (
    MultiAgentOrchestrator,
    AgentConversation,
    KanbanWorkflow,
    AgentRole
)

from .skills import (
    Skill,
    SkillLibrary,
    SkillExecutor
)

__version__ = "0.1.0"
__all__ = [
    # Core
    "Agent",
    "Task",
    "Step",
    "ActionType",
    "Tool",
    "Memory",
    "Planner",
    "LLMInterface",
    # LLM
    "OpenAILLM",
    "AnthropicLLM",
    "LocalLLM",
    # Tools
    "ReadFileTool",
    "WriteFileTool",
    "TerminalTool",
    "ExecuteCodeTool",
    "WebSearchTool",
    "BrowserTool",
    "DatabaseTool",
    "APIRequestTool",
    "get_all_tools",
    "get_tool_by_name",
    # Multi-Agent
    "MultiAgentOrchestrator",
    "AgentConversation",
    "KanbanWorkflow",
    "AgentRole",
    # Skills
    "Skill",
    "SkillLibrary",
    "SkillExecutor"
]
