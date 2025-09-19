import time
import json

# 原始英文prompt:
"""As the Neutral Risk Analyst, your role is to provide a balanced perspective, weighing both the potential benefits and risks of the trader's decision or plan. You prioritize a well-rounded approach, evaluating the upsides and downsides while factoring in broader market trends, potential economic shifts, and diversification strategies.Here is the trader's decision:

{trader_decision}

Your task is to challenge both the Risky and Safe Analysts, pointing out where each perspective may be overly optimistic or overly cautious. Use insights from the following data sources to support a moderate, sustainable strategy to adjust the trader's decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the safe analyst: {current_safe_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage actively by analyzing both sides critically, addressing weaknesses in the risky and conservative arguments to advocate for a more balanced approach. Challenge each of their points to illustrate why a moderate risk strategy might offer the best of both worlds, providing growth potential while safeguarding against extreme volatility. Focus on debating rather than simply presenting data, aiming to show that a balanced view can lead to the most reliable outcomes. Output conversationally as if you are speaking without any special formatting."""


def create_neutral_debator(llm):
    def neutral_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        neutral_history = risk_debate_state.get("neutral_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
        current_safe_response = risk_debate_state.get("current_safe_response", "")

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

        prompt = f"""作为中性风险分析师，你的角色是提供平衡的视角，权衡交易员决策或计划的潜在收益和风险。你优先考虑全面的方法，评估利弊，同时考虑更广泛的市场趋势、潜在的经济变化和多元化策略。

<交易员决策>
{trader_decision}
</交易员决策>

你的任务是挑战激进分析师和保守分析师的观点，指出每个视角可能过于乐观或过于谨慎的地方。利用以下数据来源的洞察来支持温和、可持续的策略，以调整交易员的决策：

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

<激进分析师最后回应>
{current_risky_response}
</激进分析师最后回应>

<保守分析师最后回应>
{current_safe_response}
</保守分析师最后回应>

如果没有其他观点的回应，不要幻觉，只呈现你的观点。

通过批判性地分析双方，积极参与，解决激进和保守论点中的弱点，以倡导更平衡的方法。挑战他们的每个观点来说明为什么适度风险策略可能提供两全其美，既提供增长潜力又防范极端波动。专注于辩论而不是仅仅呈现数据，旨在表明平衡的观点可以带来最可靠的结果。以对话方式输出，就像你在说话一样，没有任何特殊格式。"""

        response = llm.invoke(prompt)
        
        # 打印token使用信息
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, "Neutral Risk Debator")

        argument = f"Neutral Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": risk_debate_state.get("safe_history", ""),
            "neutral_history": neutral_history + "\n" + argument,
            "latest_speaker": "Neutral",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": risk_debate_state.get("current_safe_response", ""),
            "current_neutral_response": argument,
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return neutral_node
