import os
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv
from typing import Iterable, List, Optional

# 加载 .env 文件的环境变量
load_dotenv()

class HelloAgentsLLM:
    def __init__(self, model: Optional[str] = None, apiKey: Optional[str] = None, baseUrl: Optional[str] = None, timeout: Optional[int] = None):
        #初始化客户端。优先使用传入参数，未提供则从环境变量加载。
        resolved_model = model or os.getenv("LLM_MODEL_ID")
        resolved_api_key = apiKey or os.getenv("LLM_API_KEY")
        resolved_base_url = baseUrl or os.getenv("LLM_BASE_URL")
        resolved_timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        # 逐项判空而非 all([...])：这样写检查工具才能在这行之后确定三个值都是非空 str
        if not resolved_model or not resolved_api_key or not resolved_base_url:
            raise ValueError("模型、API密钥和地址必须被提供或在 .env 文件定义")

        self.model: str = resolved_model
        self.client = OpenAI(api_key=resolved_api_key, base_url=resolved_base_url, timeout=resolved_timeout)

    def think(self, messages: Iterable[ChatCompletionMessageParam], temperature: float = 0.2) -> Optional[str]:
        # 调用大语言模型进行思考，并返回响应。
        print(f"正在调用 {self.model} 模型。。。")
        try:
            response = self.client.chat.completions.create(
                model = self.model,
                messages = messages,
                temperature = temperature,
                stream = True,
            )

            # 处理流式响应
            print("大语言模型响应：")
            collected_content = []
            in_reasoning = False   # 是否正在打印思考过程
            answer_started = False  # 是否已打印"正式回答"分隔标记
            for chunk in response:
                if not chunk.choices:
                    continue
                delta = chunk.choices[0].delta
                # 推理模型先输出 reasoning_content（思考），再输出 content（答案）
                reasoning_delta = getattr(delta, "reasoning_content", None)
                if reasoning_delta:
                    if not in_reasoning:
                        print("--- 思考过程 ---")
                        in_reasoning = True
                    print(reasoning_delta, end="", flush=True)
                content_delta = delta.content or ""
                if content_delta:
                    if in_reasoning and not answer_started:
                        print("\n--- 正式回答 ---")
                        answer_started = True
                    print(content_delta, end="", flush=True)
                    collected_content.append(content_delta)
            # 换行
            print()
            # 空流保护：正常模型不可能一个文本块都不返回，多半是接口地址/配额/模型名问题
            if not in_reasoning and not collected_content:
                print("警告：未从服务端收到任何文本内容，请检查 LLM_BASE_URL 是否为 API 接口地址、模型名与配额是否正确。")
            return "".join(collected_content)
        
        except Exception as e:
            print(f"调用LLM API时发生错误: {e}")
            return None

# 客服端使用示例
# if __name__ == '__main__':
#     try:
#         llmClient = HelloAgentsLLM()
#         exampleMessages: List[ChatCompletionMessageParam] = [
#             {"role": "system", "content": "You are a helpful assistant that writes Python code."},
#             {"role": "user", "content": "写一个快速排序算法"}
#         ]
#         print("--- 调用LLM ---")
#         responseText = llmClient.think(exampleMessages)
#         if responseText:
#             print("\n\n--- 完整模型响应 ---")
#             print(responseText)
#     except ValueError as e:
#         print(e)
                