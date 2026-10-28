import os
import http.client
import json
from dotenv import load_dotenv
from typing import Dict, Any, Callable, Optional


# 加载 .env 文件的环境变量
load_dotenv()
def search(query: str) -> str:
    # 基于SerperApi的网页搜索引擎工具
    # 智能分析搜索结果，优先返回直接答案或知识图谱信息
    print(f" 正在执行 [SerperApi] 网页搜索：{query}")

    try:
        conn = http.client.HTTPSConnection("google.serper.dev")
        api_key = os.getenv("SERPER_API_KEY")
        if not api_key:
            return "错误：未配置SERPER_API_KEY"

        payload= json.dumps({
            "q": query,
            "gl": "cn",
            "hl": "zh-cn"
        })
        headers = {
            'X-API-KEY': api_key,
            'Content-Type': 'application/json'
        }
        conn.request("POST","/search", payload, headers)
        res = conn.getresponse()
        data = res.read()

        # 先检查状态码：非 200 时响应体是错误信息而非搜索结果，不能当作"没找到"
        if res.status != 200:
            return f"搜索接口返回错误（HTTP {res.status}）：{data.decode('utf-8', 'replace')[:200]}"

        results = json.loads(data.decode("utf-8"))

        # 智能解析：寻找直接答案
        if "knowledgeGraph" in results and "description" in results["knowledgeGraph"]:
            return results["knowledgeGraph"]["description"]
        if "organic" in results and results["organic"]:
            # 如果没有直接答案，返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {item.get('title', '')}\n{item.get('snippet', '')}"
                for i, item in enumerate(results["organic"][:3])
            ]
            return "\n\n".join(snippets)

        return f"没有找到关于 '{query}' 的信息。"
        
    except Exception as e:
        return f"搜索时发生错误：{e}"

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


# 工具使用实例
# if __name__ == '__main__':
#     # 1.初始化工具执行器
#     toolExecutor = ToolExecutor()

#     # 2.注册搜索工具
#     search_description = "一个网页搜索引擎。当你需要回答关于时事，事实以及在你的知识库找不到的信息时，应使用此工具。"
#     toolExecutor.registerTool("Search", search_description, search)

#     # 3.打印可用工具
#     print("\n--- 可用的工具(tools) ---")
#     print(toolExecutor.getAvailableTools())

#     # 4.智能体的Action调用，这次我们回答一个实时性问题
#     print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
#     tool_name = "Search"
#     tool_input = "英伟达最新的GPU型号是什么"

#     tool_function = toolExecutor.getTool(tool_name)
#     if tool_function:
#         observation = tool_function(tool_input)
#         print("--- 观察(Observation) ---")
#         print(observation)
#     else:
#         print(f"错误：未找到 '{tool_name}' 工具")

