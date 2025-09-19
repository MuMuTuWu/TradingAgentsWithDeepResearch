# %%
from langchain_openai import ChatOpenAI

import os
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(
    model="gpt-5-nano",
    base_url=os.environ.get("BASE_URL"),
    reasoning_effort="minimal",
    # model_kwargs={"reasoning_effort": "minimal"}  # 模型参数={"推理努力": "最小"}
)

# 示例：调用llm进行对话
response = llm.invoke("请简要介绍一下A股市场的主要特点。")
print("LLM回复：", response.content)

# 如果需要打印token用量，可结合utils/token_logger.py中的print_token_usage函数
from tradingagents.utils.token_logger import print_token_usage
print_token_usage(response, context_name="LLM测试")

# %%
