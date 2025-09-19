from langchain_core.messages import AIMessage
import time
import json

# 原始英文prompt:
"""As the Safe/Conservative Risk Analyst, your primary objective is to protect assets, minimize volatility, and ensure steady, reliable growth. You prioritize stability, security, and risk mitigation, carefully assessing potential losses, economic downturns, and market volatility. When evaluating the trader's decision or plan, critically examine high-risk elements, pointing out where the decision may expose the firm to undue risk and where more cautious alternatives could secure long-term gains. Here is the trader's decision:

{trader_decision}

Your task is to actively counter the arguments of the Risky and Neutral Analysts, highlighting where their views may overlook potential threats or fail to prioritize sustainability. Respond directly to their points, drawing from the following data sources to build a convincing case for a low-risk approach adjustment to the trader's decision:

Market Research Report: {market_research_report}
Social Media Sentiment Report: {sentiment_report}
Latest World Affairs Report: {news_report}
Company Fundamentals Report: {fundamentals_report}
Here is the current conversation history: {history} Here is the last response from the risky analyst: {current_risky_response} Here is the last response from the neutral analyst: {current_neutral_response}. If there are no responses from the other viewpoints, do not halluncinate and just present your point.

Engage by questioning their optimism and emphasizing the potential downsides they may have overlooked. Address each of their counterpoints to showcase why a conservative stance is ultimately the safest path for the firm's assets. Focus on debating and critiquing their arguments to demonstrate the strength of a low-risk strategy over their approaches. Output conversationally as if you are speaking without any special formatting."""


def create_safe_debator(llm):
    def safe_node(state) -> dict:
        risk_debate_state = state["risk_debate_state"]
        history = risk_debate_state.get("history", "")
        safe_history = risk_debate_state.get("safe_history", "")

        current_risky_response = risk_debate_state.get("current_risky_response", "")
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

        prompt = f"""作为保守风险分析师，你的主要目标是保护资产、最小化波动并确保稳定、可靠的增长。你优先考虑稳定性、安全性和风险缓解，仔细评估潜在损失、经济衰退和市场波动。在评估交易员的决策或计划时，批判性地检查高风险元素，指出决策可能使公司面临过度风险的地方，以及更谨慎的替代方案如何能够确保长期收益。

<交易员决策>
{trader_decision}
</交易员决策>

你的任务是积极反驳激进分析师和中性分析师的论点，突出他们的观点可能忽视潜在威胁或未能优先考虑可持续性的地方。直接回应他们的观点，利用以下数据来源为调整交易员决策的低风险方法构建令人信服的案例：

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

<中性分析师最后回应>
{current_neutral_response}
</中性分析师最后回应>

如果没有其他观点的回应，不要幻觉，只呈现你的观点。

通过质疑他们的乐观主义并强调他们可能忽视的潜在缺点来进行参与。解决他们的每个反驳点以展示为什么保守立场最终是公司资产最安全路径。专注于辩论和批评他们的论点，以展示低风险策略相对于他们方法的优势。以对话方式输出，就像你在说话一样，没有任何特殊格式。"""

        response = llm.invoke(prompt)
        
        # 打印token使用信息
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, "Conservative Risk Debator")

        argument = f"Safe Analyst: {response.content}"

        new_risk_debate_state = {
            "history": history + "\n" + argument,
            "risky_history": risk_debate_state.get("risky_history", ""),
            "safe_history": safe_history + "\n" + argument,
            "neutral_history": risk_debate_state.get("neutral_history", ""),
            "latest_speaker": "Safe",
            "current_risky_response": risk_debate_state.get(
                "current_risky_response", ""
            ),
            "current_safe_response": argument,
            "current_neutral_response": risk_debate_state.get(
                "current_neutral_response", ""
            ),
            "count": risk_debate_state["count"] + 1,
        }

        return {"risk_debate_state": new_risk_debate_state}

    return safe_node
