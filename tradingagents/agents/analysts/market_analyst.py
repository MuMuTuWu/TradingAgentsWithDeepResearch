from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
import time
import json
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import Toolkit

# 原始英文prompt:
"""
=== system_message ===
You are a trading assistant tasked with analyzing financial markets. Your role is to select the **most relevant indicators** for a given market condition or trading strategy from the following list. The goal is to choose up to **8 indicators** that provide complementary insights without redundancy. Categories and each category's indicators are:

Moving Averages:
- close_50_sma: 50 SMA: A medium-term trend indicator. Usage: Identify trend direction and serve as dynamic support/resistance. Tips: It lags price; combine with faster indicators for timely signals.
- close_200_sma: 200 SMA: A long-term trend benchmark. Usage: Confirm overall market trend and identify golden/death cross setups. Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries.
- close_10_ema: 10 EMA: A responsive short-term average. Usage: Capture quick shifts in momentum and potential entry points. Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals.

MACD Related:
- macd: MACD: Computes momentum via differences of EMAs. Usage: Look for crossovers and divergence as signals of trend changes. Tips: Confirm with other indicators in low-volatility or sideways markets.
- macds: MACD Signal: An EMA smoothing of the MACD line. Usage: Use crossovers with the MACD line to trigger trades. Tips: Should be part of a broader strategy to avoid false positives.
- macdh: MACD Histogram: Shows the gap between the MACD line and its signal. Usage: Visualize momentum strength and spot divergence early. Tips: Can be volatile; complement with additional filters in fast-moving markets.

Momentum Indicators:
- rsi: RSI: Measures momentum to flag overbought/oversold conditions. Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis.

Volatility Indicators:
- boll: Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. Usage: Acts as a dynamic benchmark for price movement. Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals.
- boll_ub: Bollinger Upper Band: Typically 2 standard deviations above the middle line. Usage: Signals potential overbought conditions and breakout zones. Tips: Confirm signals with other tools; prices may ride the band in strong trends.
- boll_lb: Bollinger Lower Band: Typically 2 standard deviations below the middle line. Usage: Indicates potential oversold conditions. Tips: Use additional analysis to avoid false reversal signals.
- atr: ATR: Averages true range to measure volatility. Usage: Set stop-loss levels and adjust position sizes based on current market volatility. Tips: It's a reactive measure, so use it as part of a broader risk management strategy.

Volume-Based Indicators:
- vwma: VWMA: A moving average weighted by volume. Usage: Confirm trends by integrating price action with volume data. Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses.

- Select indicators that provide diverse and complementary information. Avoid redundancy (e.g., do not select both rsi and stochrsi). Also briefly explain why they are suitable for the given market context. When you tool call, please use the exact name of the indicators provided above as they are defined parameters, otherwise your call will fail. Please make sure to call get_YFin_data first to retrieve the CSV that is needed to generate indicators. Write a very detailed and nuanced report of the trends you observe. Do not simply state the trends are mixed, provide detailed and finegrained analysis and insights that may help traders make decisions.

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


def create_market_analyst(llm, toolkit: Toolkit):

    def market_analyst_node(state: AgentState):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]

        # if toolkit.config["online_tools"]:
        #     tools = [
        #         toolkit.get_YFin_data_online,
        #         toolkit.get_stockstats_indicators_report_online,
        #     ]
        # else:
        #     tools = [
        #         toolkit.get_YFin_data,
        #         toolkit.get_stockstats_indicators_report,
        #     ]
        tools = [
            toolkit.get_index_market_data,
            toolkit.get_index_indicators_report,
        ]

        system_message = (
            """你是一名交易助手，负责分析金融市场。你的角色是从以下列表中为给定的市场状况或交易策略选择**最相关的指标**。目标是选择最多**8个指标**，这些指标提供互补的洞察而无冗余。类别和每个类别的指标如下：

移动平均线：
- close_50_sma: 50 SMA：中期趋势指标。用法：识别趋势方向并作为动态支撑/阻力。提示：它滞后于价格；与更快的指标结合使用以获得及时信号。
- close_200_sma: 200 SMA：长期趋势基准。用法：确认整体市场趋势并识别金叉/死叉设置。提示：反应较慢；最适合战略趋势确认而非频繁交易入场。
- close_10_ema: 10 EMA：响应迅速的短期平均线。用法：捕捉动量的快速变化和潜在入场点。提示：在震荡市场中容易受到噪音影响；与较长平均线结合使用以过滤虚假信号。

MACD相关：
- macd: MACD：通过EMA差异计算动量。用法：寻找交叉和背离作为趋势变化的信号。提示：在低波动或横盘市场中与其他指标确认。
- macds: MACD信号：MACD线的EMA平滑。用法：与MACD线交叉使用以触发交易。提示：应该是更广泛策略的一部分以避免虚假正信号。
- macdh: MACD直方图：显示MACD线与其信号之间的差距。用法：可视化动量强度并及早发现背离。提示：可能波动较大；在快速移动的市场中补充额外过滤器。

动量指标：
- rsi: RSI：测量动量以标记超买/超卖状况。用法：应用70/30阈值并观察背离以信号反转。提示：在强劲趋势中，RSI可能保持极端；始终与趋势分析交叉检查。

波动率指标：
- boll: 布林带中间：作为布林带基础的20 SMA。用法：作为价格运动的动态基准。提示：与上下带结合使用以有效发现突破或反转。
- boll_ub: 布林带上轨：通常在中间线上方2个标准差。用法：信号潜在超买状况和突破区域。提示：用其他工具确认信号；在强劲趋势中价格可能沿着带运行。
- boll_lb: 布林带下轨：通常在中间线下方2个标准差。用法：指示潜在超卖状况。提示：使用额外分析以避免虚假反转信号。
- atr: ATR：平均真实范围以测量波动率。用法：根据当前市场波动率设置止损水平并调整仓位大小。提示：这是一个反应性测量，因此将其作为更广泛风险管理策略的一部分使用。

基于交易量的指标：
- vwma: VWMA：按交易量加权的移动平均。用法：通过整合价格行为与交易量数据确认趋势。提示：注意交易量峰值导致的倾斜结果；与其他交易量分析结合使用。

- 选择提供多样化和互补信息的指标。避免冗余（例如，不要同时选择rsi和stochrsi）。还要简要解释为什么它们适合给定的市场环境。在工具调用时，请使用上面提供的指标的确切名称，因为它们是定义的参数，否则您的调用将失败。请确保首先调用get_YFin_data以检索生成指标所需的CSV。撰写一份非常详细和细致的趋势观察报告。不要简单地说趋势是混合的，而是提供详细和精细的分析和洞察，以帮助交易者做出决策。"""
            + """ 确保在报告末尾附加一个Markdown表格来组织报告中的关键点，便于组织和阅读。"""
        )

        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    "你是一个有帮助的AI助手，与其他助手协作。"
                    " 使用提供的工具来推进回答问题。"
                    " 如果你无法完全回答，没关系；另一个有不同工具的助手"
                    " 将从你停下的地方继续。执行你能做的来取得进展。"
                    " 你可以访问以下工具：{tool_names}.\n{system_message}"
                    "作为参考，当前日期是{current_date}。我们要查看的指数/公司是{ticker}",
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
        from tradingagents.utils.token_logger import print_token_usage
        print_token_usage(result, context_name="Market Analyst")

        report = ""

        if len(result.tool_calls) == 0:
            report = result.content
       
        return {
            "messages": [result],
            "market_report": report,
        }

    return market_analyst_node
