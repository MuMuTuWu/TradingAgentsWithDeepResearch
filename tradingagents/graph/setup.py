# TradingAgents/graph/setup.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.default_config import DEFAULT_CONFIG

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """Handles the setup and configuration of the agent graph."""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: Toolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory,
        bear_memory,
        trader_memory,
        invest_judge_memory,
        risk_manager_memory,
        conditional_logic: ConditionalLogic,
        config: Dict[str, Any] = None,
    ):
        """Initialize with required components."""
        self.quick_thinking_llm = quick_thinking_llm
        self.deep_thinking_llm = deep_thinking_llm
        self.toolkit = toolkit
        self.tool_nodes = tool_nodes
        self.bull_memory = bull_memory
        self.bear_memory = bear_memory
        self.trader_memory = trader_memory
        self.invest_judge_memory = invest_judge_memory
        self.risk_manager_memory = risk_manager_memory
        self.conditional_logic = conditional_logic
        self.config = config or DEFAULT_CONFIG

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals"],
        selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research"]
    ):
        """Set up and compile the agent workflow graph.

        Args:
            selected_analysts (list): List of analyst types to include. Options are:
                - "market": Market analyst
                - "social": Social media analyst
                - "news": News analyst
                - "fundamentals": Fundamentals analyst
            selected_deep_researcher (list): List of deep research types to include. Options are:
                - "social_media_deep_research": Social media deep research analyst
                - "news_deep_research": News deep research analyst
                - "fundamentals_deep_research": Fundamentals deep research analyst
        """
        if len(selected_analysts) == 0:
            raise ValueError("Trading Agents Graph Setup Error: no analysts selected!")

        # Create analyst nodes
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}

        if "market" in selected_analysts:
            analyst_nodes["market"] = create_market_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["market"] = create_msg_delete()
            tool_nodes["market"] = self.tool_nodes["market"]

        if "social" in selected_analysts:
            analyst_nodes["social"] = create_social_media_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["social"] = create_msg_delete()
            tool_nodes["social"] = self.tool_nodes["social"]

        if "news" in selected_analysts:
            analyst_nodes["news"] = create_news_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["news"] = create_msg_delete()
            tool_nodes["news"] = self.tool_nodes["news"]

        if "fundamentals" in selected_analysts:
            analyst_nodes["fundamentals"] = create_fundamentals_analyst(
                self.quick_thinking_llm, self.toolkit
            )
            delete_nodes["fundamentals"] = create_msg_delete()
            tool_nodes["fundamentals"] = self.tool_nodes["fundamentals"]

        # Create deep research analyst nodes (no tool nodes or clear nodes needed)
        if "social_media_deep_research" in selected_deep_researcher:
            analyst_nodes["social_media_deep_research"] = create_social_media_deep_research_analyst(
                self.config
            )

        if "news_deep_research" in selected_deep_researcher:
            analyst_nodes["news_deep_research"] = create_news_deep_research_analyst(
                self.config
            )

        if "fundamentals_deep_research" in selected_deep_researcher:
            analyst_nodes["fundamentals_deep_research"] = create_fundamentals_deep_research_analyst(
                self.config
            )

        # Create researcher and manager nodes
        bull_researcher_node = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        bear_researcher_node = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        research_manager_node = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        trader_node = create_trader(self.quick_thinking_llm, self.trader_memory)

        # Create risk analysis nodes
        risky_analyst = create_risky_debator(self.quick_thinking_llm)
        neutral_analyst = create_neutral_debator(self.quick_thinking_llm)
        safe_analyst = create_safe_debator(self.quick_thinking_llm)
        risk_manager_node = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )

        # Create workflow
        workflow = StateGraph(AgentState)

        # Add all analyst nodes to the graph
        all_analysts = list(selected_analysts) + list(selected_deep_researcher)
        for analyst_type, node in analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
            
        # Add tool nodes and delete nodes for regular analysts only
        for analyst_type in selected_analysts:
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # Add other nodes
        workflow.add_node("Bull Researcher", bull_researcher_node)
        workflow.add_node("Bear Researcher", bear_researcher_node)
        workflow.add_node("Research Manager", research_manager_node)
        workflow.add_node("Trader", trader_node)
        workflow.add_node("Risky Analyst", risky_analyst)
        workflow.add_node("Neutral Analyst", neutral_analyst)
        workflow.add_node("Safe Analyst", safe_analyst)
        workflow.add_node("Risk Judge", risk_manager_node)

        # Define edges - Fan-out/Fan-in parallel structure
        # Fan-out: START同时连接到所有analyst（包括深度研究）
        for analyst_type in all_analysts:
            workflow.add_edge(START, f"{analyst_type.capitalize()} Analyst")

        # 配置每个常规analyst的工具循环
        for analyst_type in selected_analysts:
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # Add conditional edges for current analyst
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)
            

        # Fan-in: 常规分析师通过clear节点连接，深度研究分析师直接连接到Bull Researcher
        clear_nodes = [f"Msg Clear {analyst_type.capitalize()}" for analyst_type in selected_analysts]
        deep_research_nodes = [f"{analyst_type.capitalize()} Analyst" for analyst_type in selected_deep_researcher]
        all_final_nodes = clear_nodes + deep_research_nodes
        workflow.add_edge(all_final_nodes, "Bull Researcher")

        # Add remaining edges
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",
                "Research Manager": "Research Manager",
            },
        )
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",
                "Risk Judge": "Risk Judge",
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",
                "Risk Judge": "Risk Judge",
            },
        )

        workflow.add_edge("Risk Judge", END)

        # Compile and return
        return workflow.compile()
