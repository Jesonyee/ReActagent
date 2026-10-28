from llm_client import HelloAgentsLLM
from prompt import REACT_PROMPT_TEMPLATE
from openai.types.chat import ChatCompletionMessageParam
from typing import List
import re
from datetime import date
from tools import ToolExecutor, search

class ReActagent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []

    def run(self, question: str):
        # 运行ReAct智能体回答一个问题
        # 每次运行重置历史记录
        self.history = []
        current_step = 0

        while current_step < self.max_steps:
            current_step += 1
            print(f"--- 第 {current_step} 步 ---")

            # 1. 格式化提示词
            tools_desc = self.tool_executor.getAvailableTools()
            history_str = "\n".join(self.history)
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools = tools_desc,
                question = question,
                history = history_str,
                current_date = date.today().isoformat()
            )

            # 2. 调用LLM进行思考
            messages: List[ChatCompletionMessageParam] = [{"role": "user", "content": prompt}]
            response_text = self.llm_client.think(messages=messages)

            if not response_text:
                print("错误：LLM未能返回有效响应。")
                break

            # 3. 解析LLM响应
            thought, action = self._parse_output(response_text)

            if thought:
                print(f"思考: {thought} ")
            if not action:
                print("警告：未能解析到有效Action, 结束运行。")
                break

            # 4. 执行Action
            # 它⾸先检查是否为 Finish 指令，如果是，则流程结束。否则，它会通过 tool_executor 获取对应的⼯具函数并执⾏，得到 observation
            if action.startswith("Finish"):
                # 如果Action是Finish，表示任务完成
                # re.match 匹配失败时返回 None，必须先判空再取 group(1)
                finish_match = re.match(r"Finish\((.*)\)", action)
                # 若格式不符合 Finish(...)，退而把整个 Action 当作答案返回
                final_answer = finish_match.group(1) if finish_match else action
                print(f"最终答案：{final_answer} ")
                return final_answer

            tool_name, tool_input = self._parse_action(action)
            if not tool_name or not tool_input:
                # 处理无效Action
                continue

            print(f"行动：{tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误：未找到名为 '{tool_name}' 的工具。"
            else:
                # 调用真实工具
                observation = tool_function(tool_input)

            print(f"观察:\n{observation}")

            # 将本轮的 Action 和 observation 添加到历史记录
            # 智能体在下⼀轮⽣成提示词时，就能“看到”上⼀步⾏动的结果，并据此进⾏新⼀轮的思考和规划。
            self.history.append(f"Action: {action}")
            self.history.append(f"Observation: {observation}")

        # 循环结束
        print("已达到最大步数,流程终止.")
        return None

    def _parse_output(self, text: str):
        # 解析LLM的输出，分别提取 Thought 和 Action 。
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        # Action: 匹配到文本末尾
        action_match = re.search(r"Action:\s*(.*?)$", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        # 解析 Action 字符串,提取工具名称和输入.
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None
    
if __name__ == '__main__':
    llm = HelloAgentsLLM()
    toolExecutor = ToolExecutor()

    search_desc = "一个网页搜索引擎。当你需要回答关于时事，事实以及在你的知识库找不到的信息时，应使用此工具。"
    toolExecutor.registerTool('Search', search_desc, search)
    agent = ReActagent(llm, toolExecutor)
    question = '苹果最新的手机是哪一款？它的主要卖点是什么？'
    agent.run(question)

