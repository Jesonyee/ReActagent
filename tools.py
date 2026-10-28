import os
import http.client
import json
from ToolExecutor import ToolExecutor
from dotenv import load_dotenv


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
            'Content_Type': 'application/json'
        }
        conn.request("POST","/search", payload, headers)
        res = conn.getresponse()
        data = res.read()
        results = json.loads(data.decode("utf-8"))
   
        # 智能解析：寻找直接答案
        if "knowledgeGraph" in results and "description" in results["knowledgeGraph"]:
            return results["knowledgeGraph"]["description"]
        if "organic" in results and results["organic"]:
            # 如果没有直接答案，返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic"][:3])
            ]
            return "\n\n".join(snippets)

        return f"没有找到关于 '{query}' 的信息。"
        
    except Exception as e:
        return f"搜索时发生错误：{e}"


if __name__ == '__main__':
    # 1.初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2.注册搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事，事实以及在你的知识库找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)

    # 3.打印可用工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4.智能体的Action调用，这次我们回答一个实时性问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察(Observation) ---")
        print(observation)
    else:
        print(f"错误：未找到 '{tool_name}' 工具")

