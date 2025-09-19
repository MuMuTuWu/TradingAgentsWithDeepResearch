import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory

# 原始英文prompt:
"""As the Risk Management Judge and Debate Facilitator, your goal is to evaluate the debate between three risk analysts—Risky, \
Neutral, and Safe/Conservative—and determine the best course of action for the trader. \
Your decision must result in a clear recommendation: Buy, Sell, or Hold. \
Choose Hold only if strongly justified by specific arguments, not as a fallback when all sides seem valid. \
Strive for clarity and decisiveness.

Guidelines for Decision-Making:
1. **Summarize Key Arguments**: Extract the strongest points from each analyst, focusing on relevance to the context.
2. **Provide Rationale**: Support your recommendation with direct quotes and counterarguments from the debate.
3. **Refine the Trader's Plan**: Start with the trader's original plan, **{trader_plan}**, and adjust it based on the analysts' insights.
4. **Learn from Past Mistakes**: Use lessons from **{past_memory_str}** to address prior misjudgments and improve the decision you are making now to make sure you don't make a wrong BUY/SELL/HOLD call that loses money.

Deliverables:
- A clear and actionable recommendation: Buy, Sell, or Hold.
- Detailed reasoning anchored in the debate and past reflections.

---

**Analysts Debate History:**  
{history}

---

Focus on actionable insights and continuous improvement. Build on past lessons, critically evaluate all perspectives, and ensure each decision advances better outcomes."""


def create_risk_manager(llm, memory: FinancialSituationMemory):
    def risk_manager_node(state) -> dict:

        company_name = state["company_of_interest"]

        history = state["risk_debate_state"]["history"]
        risk_debate_state = state["risk_debate_state"]
        market_research_report = state["market_report"]
        news_report = state["news_report"]
        fundamentals_report = state["news_report"]
        sentiment_report = state["sentiment_report"]
        trader_plan = state["investment_plan"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        for i, rec in enumerate(past_memories, 1):
            past_memory_str += rec["recommendation"] + "\n\n"

        prompt = f"""作为风险管理法官和辩论主持人，你的目标是评价三个风险分析师——激进分析师、中性分析师和保守分析师——之间的辩论，并为交易员确定最佳行动方案。你的决策必须得出明确的推荐：买入、卖出或持有。只有在有具体论点强烈支持的情况下才选择持有，而不是在各方似乎都有道理时作为后备选择。力求清晰和果断。

决策制定指南：
1. **总结关键论点**：从每个分析师中提取最强的观点，重点关注与上下文的相关性。
2. **提供理由**：用辩论中的直接引用和反驳论点来支持你的推荐。
3. **完善交易员计划**：从交易员的原始计划开始，并基于分析师的洞察进行调整。
4. **从过去错误中学习**：利用经验教训来处理先前的错误判断，并改进你现在做出的决策，确保不会做出错误的买入/卖出/持有决定而导致亏损。

可交付成果：
- 明确的、可操作的推荐：买入、卖出或持有。
- 基于辩论和过去反思的详细推理。

<可用资源>
<交易员原始计划>
{trader_plan}
</交易员原始计划>

<过去反思和经验教训>
{past_memory_str}
</过去反思和经验教训>

<分析师辩论历史>
{history}
</分析师辩论历史>
</可用资源>

专注于可操作的洞察和持续改进。建立在过去的经验教训基础上，批判性地评价所有观点，确保每个决策都能带来更好的结果。"""

        response = llm.invoke(prompt)

        new_risk_debate_state = {
            "judge_decision": response.content,
            "history": risk_debate_state["history"],
            "risky_history": risk_debate_state["risky_history"],
            "safe_history": risk_debate_state["safe_history"],
            "neutral_history": risk_debate_state["neutral_history"],
            "latest_speaker": "Judge",
            "current_risky_response": risk_debate_state["current_risky_response"],
            "current_safe_response": risk_debate_state["current_safe_response"],
            "current_neutral_response": risk_debate_state["current_neutral_response"],
            "count": risk_debate_state["count"],
        }

        return {
            "risk_debate_state": new_risk_debate_state,
            "final_trade_decision": response.content,
        }

    return risk_manager_node
