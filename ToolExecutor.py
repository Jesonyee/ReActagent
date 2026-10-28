from typing import Dict, Any, Callable, Optional

class ToolExecutor:
    # 根据执行器，负责管理和执行工具。
    def __init__(self):
        # 初始化一个用于存放工具的空字典
        self.tools:Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: Callable):
        # 注册新工具
        if name in self.tools:
            print(f"警告：工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {
            "description": description,
            "function": func
        }
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> Optional[Callable]:
        # 根据名称获取工具执行函数
        return self.tools.get(name, {}).get("function")

    def getAvailableTools(self) -> str:
        # 获取所有可用工具的格式化描述字符串
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])
