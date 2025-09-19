from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import AgentState

# 原始英文prompt:
"""You are a Bull Analyst advocating for investing in the stock. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the company's market opportunities, revenue projections, and scalability.
- Competitive Advantages: Emphasize factors like unique products, strong branding, or dominant market positioning.
- Positive Indicators: Use financial health, industry trends, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Resources available:
Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bear argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""


def create_bull_researcher(llm, memory: FinancialSituationMemory):
    def bull_node(state: AgentState) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bull_history = investment_debate_state.get("bull_history", "")

        current_response = investment_debate_state.get("current_response", "")

        # 分析师报告
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]
        # 深度研究分析师报告
        social_media_deep_research_report = state["social_media_deep_research_report"]
        news_deep_research_report = state["news_deep_research_report"]
        fundamentals_deep_research_report = state["fundamentals_deep_research_report"]
        macro_deep_research_report = state["macro_deep_research_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一名多头分析师，负责为该股票的投资进行辩护。你的任务是构建一个强有力的、基于证据的论证，强调增长潜力、竞争优势和积极的市场指标。利用提供的研究和数据来解决担忧并有效地反驳空头论点。

重点关注的要点：
- 增长潜力：突出指数/公司的市场机会、收入预测和可扩展性。
- 竞争优势：强调独特产品、强势品牌或主导市场地位等因素。
- 积极指标：使用财务健康状况、行业趋势和最新积极消息作为证据。
- 空头反驳：用具体数据和合理推理批判性地分析空头论点，全面解决担忧，并展示为什么多头观点具有更强的优势。
- 参与度：以对话风格呈现你的论点，直接回应空头分析师的观点，进行有效辩论，而不仅仅是列举数据。

<可用资源>
<市场研究报告>
{market_research_report}
</市场研究报告>

<社交媒体情绪报告>
{sentiment_report}
</社交媒体情绪报告>

<最新国际事务新闻>
{news_report}
</最新国际事务新闻>

<基本面报告>
{fundamentals_report}
</基本面报告>

<社交媒体深度研究报告>
{social_media_deep_research_report}
</社交媒体深度研究报告>

<新闻深度研究报告>
{news_deep_research_report}
</新闻深度研究报告>

<基本面深度研究报告>
{fundamentals_deep_research_report}
</基本面深度研究报告>

<宏观深度研究报告>
{macro_deep_research_report}
</宏观深度研究报告>

<辩论对话历史>
{history}
</辩论对话历史>

<最后的空头论点>
{current_response}
</最后的空头论点>

<来自类似情况的反思和经验教训>
{past_memory_str}
</来自类似情况的反思和经验教训>
</可用资源>

使用这些信息提供令人信服的多头论点，反驳空头的担忧，并参与展示多头立场优势的动态辩论。你还必须处理反思并从过去的经验教训和错误中学习。
"""

        response = llm.invoke(prompt)
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, context_name="Bull Researcher")

        argument = f"Bull Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bull_history": bull_history + "\n" + argument,
            "bear_history": investment_debate_state.get("bear_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bull_node
