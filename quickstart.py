#!/usr/bin/env python3
"""
MyAgent 快速启动脚本
"""

import sys
from pathlib import Path

# 添加项目路径（父目录）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from myagent import Agent, LocalLLM
from myagent.core import EchoTool, CalculatorTool, SearchTool


def quick_demo():
    """快速演示"""
    print("\n" + "="*50)
    print("MyAgent 快速演示")
    print("="*50 + "\n")
    
    # 创建 Agent
    llm = LocalLLM(model="demo")
    tools = [EchoTool(), CalculatorTool(), SearchTool()]
    agent = Agent(llm=llm, tools=tools, max_iterations=5)
    
    # 测试 1: 简单对话
    print("🤖 测试 1: 简单对话")
    result = agent.think("你好，AI Agent")
    print(f"   回复：{result[:80]}...\n")
    
    # 测试 2: 工具调用
    print("🤖 测试 2: 计算任务")
    agent.reset()
    result = agent.think("计算 25 * 4 + 10")
    print(f"   结果：{result}\n")
    
    # 查看执行历史
    print("📜 执行历史:")
    for i, step in enumerate(agent.get_history()[:3], 1):
        print(f"   {i}. {step['type']}: {step['content'][:50]}...")
    
    print("\n" + "="*50)
    print("演示完成！")
    print("="*50 + "\n")


def interactive_mode():
    """交互模式"""
    print("\n" + "="*50)
    print("MyAgent 交互模式（输入 'quit' 退出）")
    print("="*50 + "\n")
    
    llm = LocalLLM(model="interactive")
    tools = [EchoTool(), CalculatorTool(), SearchTool()]
    agent = Agent(llm=llm, tools=tools, max_iterations=5)
    
    while True:
        user_input = input("你：").strip()
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("再见！👋")
            break
        
        if not user_input:
            continue
        
        # 执行
        result = agent.think(user_input)
        print(f"Agent: {result}\n")


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="MyAgent 快速启动")
    parser.add_argument(
        "--demo", "-d",
        action="store_true",
        help="运行快速演示"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="进入交互模式"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        quick_demo()
    elif args.interactive:
        interactive_mode()
    else:
        # 默认运行演示
        print("\n欢迎使用 MyAgent! 🚀\n")
        print("用法:")
        print("  python3 quickstart.py --demo        # 运行演示")
        print("  python3 quickstart.py --interactive # 交互模式")
        print("\n直接运行将显示快速演示...\n")
        quick_demo()


if __name__ == "__main__":
    main()
