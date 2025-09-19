from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json

# 原始英文prompt:
"""
=== system_message ===
You are a researcher tasked with analyzing fundamental information over the past week about a company. \
Please write a comprehensive report of the company's fundamental information such as financial documents, company profile, \
basic company financials, company financial history, insider sentiment and insider transactions to gain a full view of the company's fundamental information to inform traders. \
Make sure to include as much detail as possible. \
Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions. \
Make sure to append a Markdown table at the end of the report to organize key points in the report, organized and easy to read.

=== system ===
You are a helpful AI assistant, collaborating with other assistants. \
Use the provided tools to progress towards answering the question. \
If you are unable to fully answer, that's OK; another assistant with different tools \
will help where you left off. Execute what you can to make progress. \
If you or any other assistant has the FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** or deliverable, \
prefix your response with FINAL TRANSACTION PROPOSAL: **BUY/HOLD/SELL** so the team knows to stop. \
You have access to the following tools: {tool_names}.\n{system_message} \
For your reference, the current date is {current_date}. The company we want to look at is {ticker}
"""

def create_fundamentals_analyst(llm, toolkit):
    def fundamentals_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        if toolkit.config["online_tools"]:
            tools = [toolkit.get_fundamentals_openai]
        else:
            tools = [
                toolkit.get_finnhub_company_insider_sentiment,
                toolkit.get_finnhub_company_insider_transactions,
                toolkit.get_simfin_balance_sheet,
                toolkit.get_simfin_cashflow,
                toolkit.get_simfin_income_stmt,
            ]

        system_message = (
            "你是一名研究员，负责分析过去一周内关于公司的基本面信息。请撰写一份全面的公司基本面信息报告，包括财务文件、公司概况、公司基本财务数据、公司财务历史、内部人士情绪和内部人士交易等，以获得公司基本面信息的完整视图，为交易者提供信息。确保包含尽可能多的细节。不要简单地说趋势是混合的，而是提供详细和精细的分析和洞察，以帮助交易者做出决策。"
            + " 确保在报告末尾附加一个Markdown表格来组织报告中的关键点，便于组织和阅读。",
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有帮助的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你无法完全回答，没关系；另一个有不同工具的助手"
                    " 将从你停下的地方继续。执行你能做的来取得进展。"
                    " 如果你或其他助手有最终交易建议：**买入/持有/卖出**或可交付成果，"
                    " 请在响应前加上最终交易建议：**买入/持有/卖出**以便团队知道停止。"
                    " 你可以访问以下工具：{tool_names}.\n{system_message}"
                    "作为参考，当前日期是{current_date}。我们要查看的公司是{ticker}",
                ),
                MessagesPlaceholder(variable_name="messages"),
            ]
        )

        prompt = prompt.partial(system_message=system_message)
        prompt = prompt.partial(tool_names=", ".join([tool.name for tool in tools]))
        prompt = prompt.partial(current_date=current_date)
        prompt = prompt.partial(ticker=ticker)

        chain = prompt | llm.bind_tools(tools)

        result = chain.invoke(state["messages"])

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content

        return {
            "messages": [result],
            "fundamentals_report": report,
        }

    return fundamentals_analyst_node
