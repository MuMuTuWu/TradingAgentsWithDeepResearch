from langchain_core.messages import AIMessage
import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory

# 原始英文prompt:
"""You are a Bear Analyst making the case against investing in the stock. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:

- Risks and Challenges: Highlight factors like market saturation, financial instability, or macroeconomic threats that could hinder the stock's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker market positioning, declining innovation, or threats from competitors.
- Negative Indicators: Use evidence from financial data, market trends, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Resources available:

Market research report: {market_research_report}
Social media sentiment report: {sentiment_report}
Latest world affairs news: {news_report}
Company fundamentals report: {fundamentals_report}
Conversation history of the debate: {history}
Last bull argument: {current_response}
Reflections from similar situations and lessons learned: {past_memory_str}
Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the stock. You must also address reflections and learn from lessons and mistakes you made in the past.
"""


def create_bear_researcher(llm, memory: FinancialSituationMemory):
    def bear_node(state) -> dict:
        investment_debate_state = state["investment_debate_state"]
        history = investment_debate_state.get("history", "")
        bear_history = investment_debate_state.get("bear_history", "")

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
        # 反思和经验教训
        curr_situation = f"""{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"""
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""你是一名空头分析师，负责论证不投资该股票的理由。你的目标是呈现一个有理有据的论证，强调风险、挑战和负面指标。利用提供的研究和数据突出潜在的劣势，并有效地反驳多头论点。

重点关注的要点：

- 风险和挑战：突出市场饱和、财务不稳定或宏观经济威胁等可能阻碍股票表现的因素。
- 竞争劣势：强调弱势市场定位、创新衰退或来自竞争对手的威胁等脆弱性。
- 负面指标：使用财务数据、市场趋势或最近不利消息的证据来支持你的立场。
- 多头反驳：用具体数据和合理推理批判性地分析多头论点，揭露弱点或过于乐观的假设。
- 参与度：以对话风格呈现你的论点，直接回应多头分析师的观点，进行有效辩论，而不仅仅是列举事实。

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

<最后的多头论点>
{current_response}
</最后的多头论点>

<反思和经验教训>
{past_memory_str}
</反思和经验教训>
</可用资源>

使用这些信息提供令人信服的空头论点，反驳多头的说法，并参与展示投资该股票的风险和弱点的动态辩论。你还必须处理反思并从过去的经验教训和错误中学习。
"""

        response = llm.invoke(prompt)
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, context_name="Bear Researcher")

        argument = f"Bear Analyst: {response.content}"

        new_investment_debate_state = {
            "history": history + "\n" + argument,
            "bear_history": bear_history + "\n" + argument,
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": argument,
            "count": investment_debate_state["count"] + 1,
        }

        return {"investment_debate_state": new_investment_debate_state}

    return bear_node
