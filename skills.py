"""
技能系统
实现可复用的工作流模板
"""

import os
import json
import subprocess
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field

# 延迟导入 yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


@dataclass
class Skill:
    """技能定义"""
    name: str
    description: str
    steps: List[Dict]  # 执行步骤
    parameters: Dict[str, Any] = field(default_factory=dict)
    tools_required: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "description": self.description,
            "steps": self.steps,
            "parameters": self.parameters,
            "tools_required": self.tools_required
        }


class SkillLibrary:
    """技能库"""
    
    def __init__(self, skills_dir: str = None):
        self.skills: Dict[str, Skill] = {}
        self.skills_dir = skills_dir or "./skills"
        
        # 加载内置技能
        self._load_builtin_skills()
        
        # 从目录加载
        if os.path.exists(self.skills_dir):
            self._load_from_directory()
    
    def add_skill(self, skill: Skill):
        """添加技能"""
        self.skills[skill.name] = skill
    
    def get_skill(self, name: str) -> Optional[Skill]:
        """获取技能"""
        return self.skills.get(name)
    
    def list_skills(self) -> List[Dict]:
        """列出所有技能"""
        return [s.to_dict() for s in self.skills.values()]
    
    def _load_builtin_skills(self):
        """加载内置技能"""
        # 代码审查技能
        self.skills["code_review"] = Skill(
            name="code_review",
            description="代码审查：检查代码质量、安全问题、最佳实践",
            steps=[
                {
                    "action": "read_file",
                    "description": "读取代码文件",
                    "parameters": {"path": "${file_path}"}
                },
                {
                    "action": "analyze",
                    "description": "分析代码结构和潜在问题",
                    "prompt": "审查以下代码，指出问题和建议:\n${code_content}"
                },
                {
                    "action": "generate_report",
                    "description": "生成审查报告",
                    "template": """
## 代码审查报告

### 问题
{issues}

### 建议
{suggestions}
"""
                }
            ],
            tools_required=["read_file", "write_file"],
            parameters={"file_path": ""}
        )
        
        # 文档生成技能
        self.skills["generate_docs"] = Skill(
            name="generate_docs",
            description="从代码生成文档",
            steps=[
                {
                    "action": "read_file",
                    "description": "读取源代码",
                    "parameters": {"path": "${source_file}"}
                },
                {
                    "action": "analyze",
                    "description": "分析函数和类",
                    "prompt": "分析以下代码的 API 接口:\n${code_content}"
                },
                {
                    "action": "write_file",
                    "description": "写入文档",
                    "parameters": {
                        "path": "${output_file}",
                        "content": "${docs}"
                    }
                }
            ],
            tools_required=["read_file", "write_file"],
            parameters={"source_file": "", "output_file": "README.md"}
        )
        
        # 测试生成技能
        self.skills["generate_tests"] = Skill(
            name="generate_tests",
            description="为代码生成单元测试",
            steps=[
                {
                    "action": "read_file",
                    "description": "读取源代码",
                    "parameters": {"path": "${source_file}"}
                },
                {
                    "action": "analyze",
                    "description": "识别测试场景",
                    "prompt": "为以下代码生成测试用例:\n${code_content}"
                },
                {
                    "action": "write_file",
                    "description": "写入测试文件",
                    "parameters": {
                        "path": "${test_file}",
                        "content": "${tests}"
                    }
                },
                {
                    "action": "terminal",
                    "description": "运行测试",
                    "parameters": {"command": "pytest ${test_file}"}
                }
            ],
            tools_required=["read_file", "write_file", "terminal"],
            parameters={"source_file": "", "test_file": "test_generated.py"}
        )
        
        # 研究技能
        self.skills["research"] = Skill(
            name="research",
            description="研究某个主题，收集信息并总结",
            steps=[
                {
                    "action": "web_search",
                    "description": "搜索相关信息",
                    "parameters": {"query": "${topic}", "num_results": 10}
                },
                {
                    "action": "analyze",
                    "description": "分析搜索结果",
                    "prompt": "总结以下信息:\n${search_results}"
                },
                {
                    "action": "write_file",
                    "description": "保存研究报告",
                    "parameters": {
                        "path": "${output_file}",
                        "content": "${summary}"
                    }
                }
            ],
            tools_required=["web_search", "write_file"],
            parameters={"topic": "", "output_file": "research_report.md"}
        )
    
    def _load_from_directory(self):
        """从目录加载技能"""
        for filename in os.listdir(self.skills_dir):
            if filename.endswith(('.yaml', '.yml', '.json')):
                filepath = os.path.join(self.skills_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        if filename.endswith('.json'):
                            data = json.load(f)
                        elif YAML_AVAILABLE:
                            data = yaml.safe_load(f)
                        else:
                            print(f"跳过 {filename}: yaml 库未安装")
                            continue
                    
                    skill = Skill(
                        name=data["name"],
                        description=data["description"],
                        steps=data["steps"],
                        parameters=data.get("parameters", {}),
                        tools_required=data.get("tools_required", [])
                    )
                    self.skills[skill.name] = skill
                    
                except Exception as e:
                    print(f"加载技能失败 {filename}: {e}")


class SkillExecutor:
    """技能执行器"""
    
    def __init__(self, skill_library: SkillLibrary, agent):
        self.library = skill_library
        self.agent = agent
        self.context: Dict[str, Any] = {}
    
    def execute(self, skill_name: str, parameters: Dict = None) -> Any:
        """执行技能"""
        skill = self.library.get_skill(skill_name)
        if not skill:
            raise ValueError(f"未知技能：{skill_name}")
        
        # 合并参数
        params = {**skill.parameters, **(parameters or {})}
        self.context = params
        
        # 执行步骤
        results = []
        for i, step in enumerate(skill.steps):
            result = self._execute_step(step, params)
            results.append(result)
            
            # 更新上下文
            if "output_var" in step:
                self.context[step["output_var"]] = result
        
        return {
            "skill": skill_name,
            "steps_executed": len(results),
            "results": results
        }
    
    def _execute_step(self, step: Dict, context: Dict) -> Any:
        """执行单步"""
        action = step["action"]
        
        if action == "read_file":
            return self._read_file(step["parameters"])
        
        elif action == "write_file":
            return self._write_file(step["parameters"])
        
        elif action == "terminal":
            return self._run_terminal(step["parameters"])
        
        elif action == "analyze":
            return self._analyze(step["prompt"], context)
        
        elif action == "generate_report":
            return self._generate_report(step["template"], context)
        
        else:
            return f"未知动作：{action}"
    
    def _read_file(self, params: Dict) -> str:
        """读取文件"""
        path = self._resolve_var(params["path"])
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def _write_file(self, params: Dict) -> str:
        """写入文件"""
        path = self._resolve_var(params["path"])
        content = self._resolve_var(params["content"])
        
        os.makedirs(os.path.dirname(path) or '.', exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return f"已写入：{path}"
    
    def _run_terminal(self, params: Dict) -> str:
        """运行终端命令"""
        command = self._resolve_var(params["command"])
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout
    
    def _analyze(self, prompt_template: str, context: Dict) -> str:
        """分析（调用 LLM）"""
        prompt = self._resolve_var(prompt_template, context)
        # 实际应该调用 LLM
        return f"分析结果：{prompt[:200]}..."
    
    def _generate_report(self, template: str, context: Dict) -> str:
        """生成报告"""
        return template.format(**context)
    
    def _resolve_var(self, value: str, context: Dict = None) -> str:
        """解析变量 ${var_name}"""
        if context is None:
            context = self.context
        
        import re
        def replace_var(match):
            var_name = match.group(1)
            return str(context.get(var_name, match.group(0)))
        
        return re.sub(r'\$\{(\w+)\}', replace_var, value)
