import functools
import time
import json
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.utils.token_logger import print_token_usage

# 原始英文prompt:
"""
system:
You are a trading agent analyzing market data to make investment decisions. \
Based on your analysis, provide a specific recommendation to buy, sell, or hold. \
End with a firm decision and always conclude your response with 'FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL**' to confirm your recommendation. \
Do not forget to utilize lessons from past decisions to learn from your mistakes. \
Here is some reflections from similar situatiosn you traded in and the lessons learned: {past_memory_str}

user:
Based on a comprehensive analysis by a team of analysts, here is an investment plan tailored for {company_name}. \
This plan incorporates insights from current technical market trends, macroeconomic indicators, and social media sentiment. \
Use this plan as a foundation for evaluating your next trading decision.

Proposed Investment Plan: {investment_plan}

Leverage these insights to make an informed and strategic decision.
"""

def create_trader(llm, memory: FinancialSituationMemory):
    def trader_node(state, name):
        company_name = state["company_of_interest"]
        investment_plan = state["investment_plan"]
        market_research_report = state["market_report"]
        sentiment_report = state["sentiment_report"]
        news_report = state["news_report"]
        fundamentals_report = state["fundamentals_report"]

        curr_situation = f"{market_research_report}\n\n{sentiment_report}\n\n{news_report}\n\n{fundamentals_report}"
        past_memories = memory.get_memories(curr_situation, n_matches=2)

        past_memory_str = ""
        if past_memories:
            for i, rec in enumerate(past_memories, 1):
                past_memory_str += rec["recommendation"] + "\n\n"
        else:
            past_memory_str = "未找到过去的记忆记录。"

        context = {
            "role": "user",
            "content": f"""基于分析师团队的全面分析，这里是为{company_name}量身定制的投资计划。该计划整合了当前技术市场趋势、宏观经济指标和社会媒体情绪的洞察。将此计划作为评估您下一个交易决策的基础。

<建议投资计划>
{investment_plan}
</建议投资计划>

利用这些洞察做出明智且战略性的决策。""",
        }

        messages = [
            {
                "role": "system",
                "content": f"""你是一名交易代理，负责分析市场数据以做出投资决策。基于你的分析，提供具体的买入、卖出或持有推荐。以坚定决策结束，并始终以'最终交易建议：**买入/持有/卖出**'来确认你的推荐。不要忘记利用过去决策的经验教训来从错误中学习。

<过去交易反思和经验教训>
{past_memory_str}
</过去交易反思和经验教训>""",
            },
            context,
        ]

        result = llm.invoke(messages)
        
        # 打印token使用信息
        print_token_usage(result, f"Trader ({company_name})")

        return {
            "messages": [result],
            "trader_investment_plan": result.content,
            "sender": name,
        }

    return functools.partial(trader_node, name="Trader")
