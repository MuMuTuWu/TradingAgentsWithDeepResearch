# %%
"""
现在 main.py 支持命令行参数 --stream, 可选择是否流式输出

直接用 uv 运行:
不流式: uv run python -m main
流式:   uv run python -m main --stream
"""
import argparse
import asyncio, uuid
from dotenv import load_dotenv
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research.deep_researcher import deep_researcher_builder

load_dotenv()  # 确保已填写模型/Search API 等密钥

query = """# 指数舆情与新闻周度盘点

> 交付对象：**投研团队**

你需要在 **2025-09-08 ～ 2025-09-15（过去7天，时区：Asia/Shanghai）** 对 **沪深300 / 000300** 开展**广域信息收集 → 初步筛选 → 情绪与主题分析 → 结构化交付**的全流程研究，并输出可复核、可追溯的证据链。

## 研究目标（请直接回答这些问题）
- 过去一周与该指数相关的**公众讨论与情绪**如何变化？
- **关键事件 / 催化 / 风险**分别是什么？时间点与触发机制如何？
- **媒体报道与社媒观点**是否一致？如不一致，谁先谁后、背离原因？

## 范围与来源（尽可能广 + 可追溯）
- **社交/社区**：微博、雪球、知乎、贴吧、抖音/快手评论区、B站、X（Twitter）、Reddit（涉海外/ETF）、各大论坛与评论区。
- **新闻与研报**：上证报、证券时报、21世纪、财联社、第一财经、央视财经、澎湃、券商晨报/快评（标注机构与要点）、彭博、路透、FT、WSJ。
- **官方与数据**：上交所/深交所/中证指数公司/指数编制方公告，监管与部委发布，上市公司公告（与成分权重相关），指数方法学/事实表；如可用可引用 Wind/同花顺/Choice 指示性数据。
- **关键词扩展**：主码/简称/英文缩写/口语别称/常见错拼；覆盖**成分股龙头/权重行业**与相关主题（如“再平衡”“纳入/剔除”“权重调整”“北向资金”“ETF申赎”“两融”）。
- **多语言**：必要时纳入英文/繁体来源并**简要翻译为中文**。
> 要求：所有关键结论**必须**提供**可点击链接**或可定位出处（媒体名+日期+标题）；标注时间戳与抓取时间。

## 搜索与收集流程（先广后精，显式记录）
1. **检索策略与记录**  
   - 迭代关键词；记录每轮**检索词**、平台与收获要点。
2. **代表性样本采集**  
   - 覆盖不同账号类型（官方/媒体/KOL/普通用户）、不同互动层级（高赞/中量/低量）、不同观点立场（看多/中性/看空）。  
   - 对高度传播的相似帖/转发链保留**首发源 + 1~2条最具代表性二传**；其余去重。
3. **时间与证据链**  
   - 每条样本保留：平台、账号类型、时间、互动量（如可得）、原文要点、链接、初判情绪。

## 初步筛选与质量分级（降噪/可信度）
- **去重与降噪**：过滤明显营销号、机器人刷量、复读帖、标题党；将“低证据/夸张”单独归类。
- **来源分级**：  
  - **A**：官方/头部权威媒体/监管/指数方/交易所  
  - **B**：专业创作者/行业KOL/券商机构内容  
  - **C**：普通用户/匿名账号/不明来源  
  > 结论优先采用 A，B/C 作为佐证或线索。
- **可信度标签**：`已证实 / 多源一致 / 单源线索 / 传闻待证实`（传闻必须显著标注）。

## 情绪与主题分析（-2..+2 刻度）
- **情绪刻度**：-2 强空；-1 偏空；0 中性；+1 偏多；+2 强多。  
- **每日指标**：`提及量`、`看多/看空比`、`净情绪 = 看多 - 看空`；标注**异常波动点**与对应事件链接。  
- **主题框架**：`宏观/政策` ｜ `资金面（北向/两融/ETF申赎）` ｜ `编制与成分变动` ｜ `行业催化` ｜ `海外相关性` ｜ `监管与舆情风险`。  
- **一致性校验**：将**社媒净情绪**与**主流媒体基调**、**指数当日涨跌幅/成交额（如可得）**对比，指出**最大背离日**与可能原因（信息时滞/话题错配/事件误读等）。

## 输出结构（使用markdown格式输出，请严格按顺序与字段）
1) **基本结论（≤360字，面向投研团队）**  
   - 本周情绪方向；最重要**3个催化/风险**；与行情一致性结论。  
2) **逐日时间线**  
   - `YYYY-MM-DD`：净情绪、看多/看空比、提及量、**关键事件 2-4**（含**链接**、来源分级、可信度标签）。  
3) **情绪区间综述**  
   - 平均/中位净情绪、最高/最低日、**最大“情绪-行情”背离日**及解释。  
1) **主题洞察**
   - 每主题 3-6 条要点，附代表言论链接、情绪评分、来源分级。  
1) **Top 帖子/讨论 （8条）**  
   - 平台、时间、互动量、要点摘要、链接、情绪、是否疑似机器人。  
1) **Top 新闻 （8条）**  
   - 媒体、时间、标题/要点、链接、与社媒关系（吻合/背离/分歧）。  
7) **方法与样本**  
   - 平台覆盖、样本量、去重策略、情绪口径、已知偏差与盲点、主要检索词。"""


async def main():
    graph = deep_researcher_builder.compile(checkpointer=MemorySaver(), debug=True)
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "max_structured_output_retries": 3,
            "allow_clarification": False,
            "max_concurrent_research_units": 5,
            "search_api": "tavily",
            "max_researcher_iterations": 6,
            "max_react_tool_calls": 10,
            "summarization_model": "openai:gpt-5-mini",
            # "summarization_model": "openai:gpt-4.1-mini",
            "summarization_model_max_tokens": 8192,
            "max_content_length": 50000,
            "research_model": "openai:gpt-5-mini",
            # "research_model": "openai:gpt-4.1-mini",
            "research_model_max_tokens": 10000,
            "compression_model": "openai:gpt-5-mini",
            # "compression_model": "openai:gpt-4.1-mini",
            "compression_model_max_tokens": 8192,
            "final_report_model": "openai:gpt-5-mini",
            # "final_report_model": "openai:gpt-4.1-mini",
            "final_report_model_max_tokens": 10000,
            "mcp_config": None,
            "mcp_prompt": None,
        }
    }
    inputs = {"messages": [{"role": "user", "content": query}]}

    state = await graph.ainvoke(inputs, config)
    print(state["final_report"])
    with open("final_state.json", "w", encoding="utf-8") as f:
        import json

        json.dump(state, f, indent=2, ensure_ascii=False, default=str)


if __name__ == "__main__":
    asyncio.run(main())
# %%
