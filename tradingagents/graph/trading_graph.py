# 交易代理系统/图/trading_graph.py

import os
from pathlib import Path
import json
from datetime import date
from typing import Dict, Any, Tuple, List, Optional

from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI

from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory
from tradingagents.agents.utils.agent_states import (
    AgentState,
    InvestDebateState,
    RiskDebateState,
)
from tradingagents.dataflows.interface import set_config

from .conditional_logic import ConditionalLogic
from .setup import GraphSetup
from .propagation import Propagator
from .reflection import Reflector
from .signal_processing import SignalProcessor


class TradingAgentsGraph:
    """协调交易代理系统框架的主类。"""

    def __init__(
        self,
        selected_analysts=["market", "social", "news", "fundamentals"],
        selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research", "macro_deep_research"],
        debug=False,
        config: Dict[str, Any] = None,
    ):
        """初始化交易代理图和组件。

        参数:
            selected_analysts (list): 要包含的分析师类型列表。可选值包括：
                - "market": 市场分析师
                - "social": 社交媒体分析师
                - "news": 新闻分析师
                - "fundamentals": 基本面分析师
            selected_deep_researcher (list): 要包含的深度研究类型列表。可选值包括：
                - "social_media_deep_research": 社交媒体深度研究分析师
                - "news_deep_research": 新闻深度研究分析师
                - "fundamentals_deep_research": 基本面深度研究分析师
                - "macro_deep_research": 宏观深度研究分析师
            debug: 是否以调试模式运行
            config: 配置字典。如果为None，则使用默认配置
        """
        self.debug = debug
        self.config = config or DEFAULT_CONFIG

        # 更新接口的配置
        set_config(self.config)

        # 创建必要的目录
        os.makedirs(
            os.path.join(self.config["project_dir"], "dataflows/data_cache"),
            exist_ok=True,
        )

        # 初始化大语言模型
        if self.config["llm_provider"].lower() == "openai" or self.config["llm_provider"] == "ollama" or self.config["llm_provider"] == "openrouter":
            self.deep_thinking_llm = ChatOpenAI(
                model=self.config["deep_think_llm"],
                base_url=self.config["backend_url"],
                reasoning_effort="minimal",
                # model_kwargs={"reasoning_effort": "minimal"}  # 模型参数={"推理努力": "最小"}
            )
            self.quick_thinking_llm = ChatOpenAI(
                model=self.config["quick_think_llm"],
                base_url=self.config["backend_url"],
                reasoning_effort="minimal",
                # model_kwargs={"reasoning_effort": "minimal"}  # 模型参数={"推理努力": "最小"}
            )
        elif self.config["llm_provider"].lower() == "anthropic":
            self.deep_thinking_llm = ChatAnthropic(model=self.config["deep_think_llm"], base_url=self.config["backend_url"])
            self.quick_thinking_llm = ChatAnthropic(model=self.config["quick_think_llm"], base_url=self.config["backend_url"])
        elif self.config["llm_provider"].lower() == "google":
            self.deep_thinking_llm = ChatGoogleGenerativeAI(model=self.config["deep_think_llm"])
            self.quick_thinking_llm = ChatGoogleGenerativeAI(model=self.config["quick_think_llm"])
        else:
            raise ValueError(f"Unsupported LLM provider: {self.config['llm_provider']}")
        
        self.toolkit = Toolkit(config=self.config)

        # Initialize memories
        self.bull_memory = FinancialSituationMemory("bull_memory", self.config)
        self.bear_memory = FinancialSituationMemory("bear_memory", self.config)
        self.trader_memory = FinancialSituationMemory("trader_memory", self.config)
        self.invest_judge_memory = FinancialSituationMemory("invest_judge_memory", self.config)
        self.risk_manager_memory = FinancialSituationMemory("risk_manager_memory", self.config)

        # 创建工具节点
        self.tool_nodes = self._create_tool_nodes()

        # 初始化组件
        self.conditional_logic = ConditionalLogic()
        self.graph_setup = GraphSetup(
            self.quick_thinking_llm,
            self.deep_thinking_llm,
            self.toolkit,
            self.tool_nodes,
            self.bull_memory,
            self.bear_memory,
            self.trader_memory,
            self.invest_judge_memory,
            self.risk_manager_memory,
            self.conditional_logic,
            self.config
        )

        self.propagator = Propagator()
        self.reflector = Reflector(self.quick_thinking_llm)
        self.signal_processor = SignalProcessor(self.quick_thinking_llm)

        # 状态跟踪
        self.curr_state = None
        self.ticker = None
        self.log_states_dict = {}  # 日期到完整状态字典

        # 设置图
        self.graph = self.graph_setup.setup_graph(selected_analysts, selected_deep_researcher)

    def _create_tool_nodes(self) -> Dict[str, ToolNode]:
        """为不同的数据源创建工具节点。"""
        return {
            "market": ToolNode(
                [
                    self.toolkit.get_index_market_data,
                    self.toolkit.get_index_indicators_report,
                    # # 在线工具
                    # self.toolkit.get_YFin_data_online,
                    # self.toolkit.get_stockstats_indicators_report_online,
                    # # 离线工具
                    # self.toolkit.get_YFin_data,
                    # self.toolkit.get_stockstats_indicators_report,
                ]
            ),
            "social": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_stock_news_openai,
                    # 离线工具
                    self.toolkit.get_reddit_stock_info,
                ]
            ),
            "news": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_global_news_openai,
                    self.toolkit.get_google_news,
                    # 离线工具
                    self.toolkit.get_finnhub_news,
                    self.toolkit.get_reddit_news,
                ]
            ),
            "fundamentals": ToolNode(
                [
                    # 在线工具
                    self.toolkit.get_fundamentals_openai,
                    # 离线工具
                    self.toolkit.get_finnhub_company_insider_sentiment,
                    self.toolkit.get_finnhub_company_insider_transactions,
                    self.toolkit.get_simfin_balance_sheet,
                    self.toolkit.get_simfin_cashflow,
                    self.toolkit.get_simfin_income_stmt,
                ]
            ),
        }

    def propagate(self, company_name, trade_date):
        """为特定日期的公司运行交易代理图。"""

        self.ticker = company_name

        # 初始化状态
        init_agent_state = self.propagator.create_initial_state(
            company_name, trade_date
        )
        args = self.propagator.get_graph_args()

        if self.debug:
            # 带追踪的调试模式
            trace = []
            for chunk in self.graph.stream(init_agent_state, **args):
                if len(chunk["messages"]) == 0:
                    pass
                else:
                    chunk["messages"][-1].pretty_print()
                    trace.append(chunk)

            final_state = trace[-1]
        else:
            # 无追踪的标准模式
            final_state = self.graph.invoke(init_agent_state, **args)

        # 存储当前状态以供反思
        self.curr_state = final_state

        # 记录状态
        self._log_state(trade_date, final_state)

        # 返回决策和处理后的信号
        return final_state, self.process_signal(final_state["final_trade_decision"])

    def _log_state(self, trade_date, final_state):
        """将最终状态记录到JSON文件中。"""
        self.log_states_dict[str(trade_date)] = {
            "company_of_interest": final_state["company_of_interest"],
            "trade_date": final_state["trade_date"],
            "market_report": final_state["market_report"],
            "sentiment_report": final_state["sentiment_report"],
            "news_report": final_state["news_report"],
            "fundamentals_report": final_state["fundamentals_report"],
            "social_media_deep_research_report": final_state.get("social_media_deep_research_report", ""),
            "news_deep_research_report": final_state.get("news_deep_research_report", ""),
            "fundamentals_deep_research_report": final_state.get("fundamentals_deep_research_report", ""),
            "macro_deep_research_report": final_state.get("macro_deep_research_report", ""),
            "investment_debate_state": {
                "bull_history": final_state["investment_debate_state"]["bull_history"],
                "bear_history": final_state["investment_debate_state"]["bear_history"],
                "history": final_state["investment_debate_state"]["history"],
                "current_response": final_state["investment_debate_state"][
                    "current_response"
                ],
                "judge_decision": final_state["investment_debate_state"][
                    "judge_decision"
                ],
            },
            "trader_investment_decision": final_state["trader_investment_plan"],
            "risk_debate_state": {
                "risky_history": final_state["risk_debate_state"]["risky_history"],
                "safe_history": final_state["risk_debate_state"]["safe_history"],
                "neutral_history": final_state["risk_debate_state"]["neutral_history"],
                "history": final_state["risk_debate_state"]["history"],
                "judge_decision": final_state["risk_debate_state"]["judge_decision"],
            },
            "investment_plan": final_state["investment_plan"],
            "final_trade_decision": final_state["final_trade_decision"],
            "research_report": final_state.get("research_report", ""),
        }

        # Save to file
        directory = Path(f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/")
        directory.mkdir(parents=True, exist_ok=True)

        with open(
            f"eval_results/{self.ticker}/TradingAgentsStrategy_logs/full_states_log_{trade_date}.json",
            "w",
        ) as f:
            json.dump(self.log_states_dict, f, indent=4)

    def reflect_and_remember(self, returns_losses):
        """反思决策并基于回报更新记忆。"""
        self.reflector.reflect_bull_researcher(
            self.curr_state, returns_losses, self.bull_memory
        )
        self.reflector.reflect_bear_researcher(
            self.curr_state, returns_losses, self.bear_memory
        )
        self.reflector.reflect_trader(
            self.curr_state, returns_losses, self.trader_memory
        )
        self.reflector.reflect_invest_judge(
            self.curr_state, returns_losses, self.invest_judge_memory
        )
        self.reflector.reflect_risk_manager(
            self.curr_state, returns_losses, self.risk_manager_memory
        )

    def process_signal(self, full_signal):
        """处理信号以提取核心决策。"""
        return self.signal_processor.process_signal(full_signal)
