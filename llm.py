"""
OpenAI 兼容的 LLM 实现
支持：OpenAI, DeepSeek, Qwen 等 API
"""

import os
import json
from typing import List, Dict, Optional
from .core import LLMInterface

# 延迟导入 requests
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


class OpenAILLM(LLMInterface):
    """OpenAI 兼容的 LLM 实现"""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        super().__init__(model, api_key, base_url)
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 从环境变量读取
        if not self.api_key:
            self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.base_url:
            self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """调用 LLM API"""
        if not REQUESTS_AVAILABLE:
            return {"content": "错误：requests 库未安装，请运行：pip install requests", "error": True}
        
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if tools:
            payload["tools"] = [
                {
                    "type": "function",
                    "function": {
                        "name": t["name"],
                        "description": t["description"],
                        "parameters": self._convert_params(t.get("parameters", {}))
                    }
                }
                for t in tools
            ]
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            choice = result["choices"][0]
            message = choice["message"]
            
            # 检查工具调用
            if "tool_calls" in message and message["tool_calls"]:
                tool_call = message["tool_calls"][0]
                return {
                    "content": message.get("content", ""),
                    "tool_calls": [
                        {
                            "name": tc["function"]["name"],
                            "arguments": json.loads(tc["function"]["arguments"])
                        }
                        for tc in message["tool_calls"]
                    ]
                }
            
            return {"content": message["content"]}
            
        except requests.RequestException as e:
            return {"content": f"API 调用失败：{str(e)}", "error": True}
        except Exception as e:
            return {"content": f"错误：{str(e)}", "error": True}
    
    def _convert_params(self, params: Dict) -> Dict:
        """转换参数格式为 OpenAI schema"""
        if not params:
            return {"type": "object", "properties": {}}
        
        properties = {}
        required = []
        
        for param_name, param_type in params.items():
            properties[param_name] = {"type": self._map_type(param_type)}
            required.append(param_name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required
        }
    
    def _map_type(self, type_str: str) -> str:
        """映射类型"""
        type_map = {
            "string": "string",
            "int": "integer",
            "float": "number",
            "bool": "boolean",
            "list": "array",
            "dict": "object"
        }
        return type_map.get(type_str, "string")


class AnthropicLLM(LLMInterface):
    """Anthropic Claude LLM 实现"""
    
    def __init__(
        self,
        model: str = "claude-3-sonnet",
        api_key: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        max_tokens: int = 2000
    ):
        super().__init__(model, api_key, base_url)
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        if not self.api_key:
            self.api_key = os.getenv("ANTHROPIC_API_KEY")
        if not self.base_url:
            self.base_url = os.getenv("ANTHROPIC_BASE_URL", "https://api.anthropic.com/v1")
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """调用 Claude API"""
        if not REQUESTS_AVAILABLE:
            return {"content": "错误：requests 库未安装，请运行：pip install requests", "error": True}
        
        url = f"{self.base_url}/messages"
        
        # 转换消息格式
        anthropic_messages = []
        system_prompt = ""
        
        for msg in messages:
            if msg["role"] == "system":
                system_prompt = msg["content"]
            else:
                anthropic_messages.append({
                    "role": "user" if msg["role"] == "user" else "assistant",
                    "content": msg["content"]
                })
        
        payload = {
            "model": self.model,
            "messages": anthropic_messages,
            "system": system_prompt,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens
        }
        
        if tools:
            payload["tools"] = [
                {
                    "name": t["name"],
                    "description": t["description"],
                    "input_schema": self._convert_params(t.get("parameters", {}))
                }
                for t in tools
            ]
        
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            content = result["content"][0]["text"]
            
            # 检查工具调用
            if "tool_use" in result:
                return {
                    "content": content,
                    "tool_calls": result["tool_use"]
                }
            
            return {"content": content}
            
        except Exception as e:
            return {"content": f"API 调用失败：{str(e)}", "error": True}


class LocalLLM(LLMInterface):
    """本地 LLM 实现（用于测试）"""
    
    def __init__(self, model: str = "local"):
        super().__init__(model)
    
    def chat(self, messages: List[Dict], tools: List[Dict] = None) -> Dict:
        """模拟 LLM 响应（测试用）"""
        # 简单规则响应
        last_user_msg = ""
        for msg in reversed(messages):
            if msg["role"] == "user":
                last_user_msg = msg["content"]
                break
        
        # 模拟 ReAct 响应
        if "计算" in last_user_msg or "calculate" in last_user_msg.lower():
            return {
                "content": """Thought: 用户需要计算，我应该使用 calculator 工具
Action: calculator
Action Input: {"expression": "25 * 4 + 10"}"""
            }
        elif "Echo:" in last_user_msg or "历史步骤" in last_user_msg:
            return {
                "content": """Thought: 已获得计算结果，可以给出答案
Answer: 计算结果是 110 (25 * 4 = 100, 100 + 10 = 110)"""
            }
        else:
            return {
                "content": """Thought: 我需要理解用户的请求
Answer: 我理解您的需求，请告诉我具体要做什么？"""
            }
