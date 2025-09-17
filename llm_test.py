# %%
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
load_dotenv()

# %%
llm = ChatOpenAI(
    model="gpt-5-nano",
    base_url=os.environ.get("BACKEND_URL"),
    use_responses_api=True,
    model_kwargs={"reasoning": {"effort": "minimal"}}
)

response = llm.invoke("What is 3^3?")
response

# %%
llm = ChatOpenAI(
    model="gpt-5-nano",
    base_url=os.environ.get("BACKEND_URL"),
)

response = llm.invoke("What is 3^3?")
response
# %%
llm = ChatOpenAI(
    model="gpt-5-nano",
    base_url=os.environ.get("BACKEND_URL"),
    model_kwargs={"reasoning_effort": "minimal"}
)

response = llm.invoke("What is 3^3?")
response
# %%
llm = ChatOpenAI(
    model="gpt-5-nano",
    base_url=os.environ.get("BACKEND_URL"),
    reasoning_effort="minimal",
)

response = llm.invoke("What is 3^3?")
response
# %%
