"""
工具集
实现文件操作、代码执行、网络请求等工具
"""

import os
import subprocess
import json
from typing import Any, Dict, List, Optional
from .core import Tool


class ReadFileTool(Tool):
    """读取文件"""
    def __init__(self):
        super().__init__(
            name="read_file",
            description="读取文件内容",
            parameters={"path": "string", "offset": "int", "limit": "int"}
        )
    
    def execute(self, path: str, offset: int = 1, limit: int = 500) -> str:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            start = offset - 1
            end = min(start + limit, len(lines))
            
            content = "".join(lines[start:end])
            return f"文件内容 ({end-start} 行):\n{content}"
        except Exception as e:
            return f"读取失败：{e}"


class WriteFileTool(Tool):
    """写入文件"""
    def __init__(self):
        super().__init__(
            name="write_file",
            description="写入文件内容",
            parameters={"path": "string", "content": "string"}
        )
    
    def execute(self, path: str, content: str) -> str:
        try:
            # 创建目录
            os.makedirs(os.path.dirname(path), exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return f"文件已写入：{path} ({len(content)} 字节)"
        except Exception as e:
            return f"写入失败：{e}"


class TerminalTool(Tool):
    """执行终端命令"""
    def __init__(self):
        super().__init__(
            name="terminal",
            description="执行 shell 命令",
            parameters={"command": "string", "workdir": "string"}
        )
    
    def execute(self, command: str, workdir: str = None) -> str:
        try:
            result = subprocess.run(
                command,
                shell=True,
                cwd=workdir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            output = result.stdout
            if result.stderr:
                output += f"\n错误：{result.stderr}"
            
            return f"退出码：{result.return_code}\n{output}"
        except subprocess.TimeoutExpired:
            return "命令超时"
        except Exception as e:
            return f"执行失败：{e}"


class ExecuteCodeTool(Tool):
    """执行 Python 代码"""
    def __init__(self):
        super().__init__(
            name="execute_code",
            description="执行 Python 代码",
            parameters={"code": "string"}
        )
    
    def execute(self, code: str) -> str:
        try:
            # 安全执行（简化版，实际应该用沙箱）
            local_vars = {}
            exec(code, {"__builtins__": {}}, local_vars)
            
            # 获取打印输出
            output = local_vars.get("_output", "代码执行完成")
            return output
        except Exception as e:
            return f"执行错误：{e}"


class WebSearchTool(Tool):
    """网络搜索（示例）"""
    def __init__(self):
        super().__init__(
            name="web_search",
            description="网络搜索",
            parameters={"query": "string", "num_results": "int"}
        )
    
    def execute(self, query: str, num_results: int = 5) -> str:
        # 实际实现应该调用搜索引擎 API
        return f"搜索结果 for '{query}':\n[模拟] 前 {num_results} 条结果"


class BrowserTool(Tool):
    """浏览器控制（示例）"""
    def __init__(self):
        super().__init__(
            name="browser",
            description="浏览器操作",
            parameters={"action": "string", "url": "string"}
        )
    
    def execute(self, action: str, url: str = None) -> str:
        # 实际实现应该控制真实浏览器
        return f"浏览器 {action}: {url}"


class DatabaseTool(Tool):
    """数据库查询（示例）"""
    def __init__(self):
        super().__init__(
            name="database_query",
            description="执行 SQL 查询",
            parameters={"query": "string", "database": "string"}
        )
    
    def execute(self, query: str, database: str = "default") -> str:
        # 实际实现应该连接真实数据库
        return f"SQL 查询结果：{query}"


class APIRequestTool(Tool):
    """HTTP API 请求"""
    def __init__(self):
        super().__init__(
            name="api_request",
            description="发送 HTTP 请求",
            parameters={
                "method": "string",
                "url": "string",
                "headers": "dict",
                "body": "dict"
            }
        )
    
    def execute(
        self, 
        method: str = "GET", 
        url: str = None,
        headers: Dict = None,
        body: Dict = None
    ) -> str:
        try:
            import requests
        except ImportError:
            return "错误：requests 库未安装，请运行：pip install requests"
        
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers or {},
                json=body,
                timeout=30
            )
            
            return f"状态码：{response.status_code}\n{response.text[:500]}"
        except Exception as e:
            return f"请求失败：{e}"


# 工具工厂
def get_all_tools() -> List[Tool]:
    """获取所有可用工具"""
    return [
        ReadFileTool(),
        WriteFileTool(),
        TerminalTool(),
        ExecuteCodeTool(),
        WebSearchTool(),
        BrowserTool(),
        DatabaseTool(),
        APIRequestTool()
    ]


def get_tool_by_name(name: str) -> Optional[Tool]:
    """按名称获取工具"""
    for tool in get_all_tools():
        if tool.name == name:
            return tool
    return None
