REACT_PROMPT_TEMPLATE = """
请注意，你是⼀个有能⼒调⽤外部⼯具的智能助⼿。

可⽤⼯具如下:
{tools}

请严格按照以下格式进⾏回应:

Thought: 你的思考过程，⽤于分析问题、拆解任务和规划下⼀步⾏动。
Action: 你决定采取的⾏动，必须是以下格式之⼀:
- `{{tool_name}}[{{tool_input}}]`:调⽤⼀个可⽤⼯具。
- `Finish[最终答案]`:当你认为已经获得最终答案时。
- 当你收集到⾜够的信息，能够回答⽤户的最终问题时，你必须在Action:字段后使⽤ Finish[最终答案] 来输出最终答案。

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""