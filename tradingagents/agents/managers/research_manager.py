import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory

# 原始英文prompt:
"""As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan for the trader. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting. 

Here are your past reflections on mistakes:
\"{past_memory_str}\"

Here is the debate:
Debate History:
{history}"""


def create_research_manager(llm, memory: FinancialSituationMemory):
    def research_manager_node(state) -> dict:
        history = state["investment_debate_state"].get("history", "")
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        investment_debate_state = state["investment_debate_state"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作为投资组合经理和辩论主持人，你的角色是批判性地评价这一轮辩论，并做出明确的决定：支持空头分析师、多头分析师，或者只有在基于呈现的论点有充分理由的情况下才选择持有。

简要总结双方的重要观点，重点关注最具说服力的证据或推理。你的推荐——买入、卖出或持有——必须清晰且可操作。避免仅仅因为双方都有合理观点就默认选择持有；而要基于辩论中最有力的论点做出立场。

此外，为交易员制定详细的投资计划。这应该包括：

你的推荐：基于最具说服力论点的坚定立场。
理由：解释这些论点如何导致你的结论。
战略行动：实施推荐的具体步骤。
考虑你在类似情况下的过去错误。利用这些洞察来完善你的决策过程，确保你在学习和改进。以对话方式呈现你的分析，就像自然说话一样，没有特殊格式。

<过去反思>
{past_memory_str}
</过去反思>

<辩论历史>
{history}
</辩论历史>"""
        response = llm.invoke(prompt)
        
        # 打印token使用信息
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(response, "Research Manager")

        new_investment_debate_state = {
            "judge_decision": response.content,
            "history": investment_debate_state.get("history", ""),
            "bear_history": investment_debate_state.get("bear_history", ""),
            "bull_history": investment_debate_state.get("bull_history", ""),
            "current_response": response.content,
            "count": investment_debate_state["count"],
        }

        return {
            "investment_debate_state": new_investment_debate_state,
            "investment_plan": response.content,
        }

    return research_manager_node
