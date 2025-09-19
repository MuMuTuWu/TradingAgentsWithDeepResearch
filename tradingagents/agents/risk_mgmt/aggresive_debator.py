import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory

# 原始英文prompt:
"""As the Risky Risk Analyst, your role is to actively champion high-reward, high-risk opportunities, emphasizing bold strategies and competitive advantages. When evaluating the trader's decision or plan, focus intently on the potential upside, growth potential, and innovative benefits—even when these come with elevated risk. Use the provided market data and sentiment analysis to strengthen your arguments and challenge the opposing views. Specifically, respond directly to each point made by the conservative and neutral analysts, countering with data-driven rebuttals and persuasive reasoning. Highlight where their caution might miss critical opportunities or where their assumptions may be overly conservative. Here is the trader's decision:

{trader_decision}

Your task is to create a compelling case for the trader's decision by questioning and critiquing the conservative and neutral stances to demonstrate why your high-reward perspective offers the best path forward. Incorporate insights from the following sources into your arguments:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here are the last arguments from the conservative analyst: {current_safe_response} Here are the last arguments from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by addressing any specific concerns raised, refuting the weaknesses in their logic, and asserting the benefits of risk-taking to outpace market norms. Maintain a focus on debating and persuading, not just presenting data. Challenge each counterpoint to underscore why a high-risk approach is optimal. Output conversationally as if you are speaking without any special formatting."""


def create_risky_debator(llm: FinancialSituationMemory):
    def risky_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        risky_history = risk_debate_state.get("risky_history", "")

        current_safe_response = risk_debate_state.get("current_safe_response", "")
        current_neutral_response = risk_debate_state.get("current_neutral_response", "")

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

        trader_decision = state["trader_investment_plan"]

        prompt = f"""作为激进风险分析师，你的角色是积极倡导高回报、高风险的机会，强调大胆的策略和竞争优势。在评估交易员的决策或计划时，要重点关注潜在的上行空间、增长潜力和创新收益——即使这些伴随着更高的风险。利用提供市场数据和情绪分析来加强你的论点，并挑战对立的观点。具体来说，直接回应保守派和中性分析师提出的每一点观点，用数据驱动的反驳和有说服力的推理来进行反驳。突出他们的谨慎可能错失关键机会的地方，或他们的假设过于保守的地方。

<交易员决策>
{trader_decision}
</交易员决策>

你的任务是为交易员的决策创建一个令人信服的案例，通过质疑和批评保守派和中性立场来证明为什么你的高回报视角提供了最佳前进道路。将以下来源的洞察融入你的论点：

<市场研究报告>
{market_research_report}
</市场研究报告>

<社交媒体情绪报告>
{sentiment_report}
</社交媒体情绪报告>

<最新国际事务报告>
{news_report}
</最新国际事务报告>

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

<对话历史>
{history}
</对话历史>

<保守派分析师最后论点>
{current_safe_response}
</保守派分析师最后论点>

<中性分析师最后论点>
{current_neutral_response}
</中性分析师最后论点>

如果没有其他观点的回应，不要幻觉，只呈现你的观点。

通过解决提出的具体担忧、反驳他们逻辑中的弱点，并主张冒险的好处来超越市场常态，积极参与。保持辩论和说服的重点，而不仅仅是呈现数据。挑战每个反驳点以强调为什么高风险方法是最优的。以对话方式输出，就像你在说话一样，没有任何特殊格式。"""

        response = llm.invoke(prompt)
        
        # 打印token使用信息
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, "Aggressive Risk Debator")

        argument = f"Risky Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risky_history + "\n" + argument,
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Risky",
            "current_risky_response": argument,
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return risky_node
