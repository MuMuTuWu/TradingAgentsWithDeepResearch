# TradingAgents/graph/setup.py

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.prebuilt import ToolNode

from tradingagents.agents import *
from tradingagents.agents.utils.agent_states import AgentState
from tradingagents.agents.utils.agent_utils import Toolkit
from tradingagents.default_config import DEFAULT_CONFIG
from tradingagents.agents.utils.memory import FinancialSituationMemory

from .conditional_logic import ConditionalLogic


class GraphSetup:
    """处理智能体图的设置和配置。"""

    def __init__(
        self,
        quick_thinking_llm: ChatOpenAI,
        deep_thinking_llm: ChatOpenAI,
        toolkit: Toolkit,
        tool_nodes: Dict[str, ToolNode],
        bull_memory: FinancialSituationMemory,
        bear_memory: FinancialSituationMemory,
        trader_memory: FinancialSituationMemory,
        invest_judge_memory: FinancialSituationMemory,
        risk_manager_memory: FinancialSituationMemory,
        conditional_logic: ConditionalLogic,
        config: Dict[str, Any] = None,
    ):
        """使用必需的组件初始化GraphSetup。
        
        Args:
            quick_thinking_llm: 快速思考模型，用于常规分析师
            deep_thinking_llm: 深度思考模型，用于研究管理和风险管理
            toolkit: 工具包，包含数据获取和分析工具
            tool_nodes: 工具节点字典，按分析师类型组织
            bull_memory: 多头研究员的记忆存储
            bear_memory: 空头研究员的记忆存储
            trader_memory: 交易员的记忆存储
            invest_judge_memory: 投资判断的记忆存储
            risk_manager_memory: 风险管理的记忆存储
            conditional_logic: 条件逻辑处理器
            config: 配置字典，默认使用DEFAULT_CONFIG
        """
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
        selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research", "macro_deep_research"]
    ):
        """设置并编译智能体工作流图。

        这是主要的入口方法，负责协调整个图的构建过程。
        构建过程分为4个步骤：参数验证 → 节点创建 → 图构建 → 边配置 → 编译。

        Args:
            selected_analysts (list): 要包含的常规分析师类型列表。选项包括：
                - "market": 市场分析师（技术分析、价格趋势）
                - "social": 社交媒体分析师（情感分析、舆情监控）
                - "news": 新闻分析师（新闻事件、影响分析）
                - "fundamentals": 基本面分析师（财务数据、公司基本面）
            selected_deep_researcher (list): 要包含的深度研究分析师类型列表。选项包括：
                - "social_media_deep_research": 社交媒体深度研究分析师
                - "news_deep_research": 新闻深度研究分析师
                - "fundamentals_deep_research": 基本面深度研究分析师
                - "macro_deep_research": 宏观深度研究分析师
                
        Returns:
            CompiledGraph: 编译后的工作流图，可直接执行
        """
        # 1. 参数验证
        self._validate_parameters(selected_analysts, selected_deep_researcher)

        # 2. 创建节点
        analyst_nodes, delete_nodes, tool_nodes = self._create_analyst_nodes(selected_analysts)
        deep_research_nodes = self._create_deep_research_nodes(selected_deep_researcher)
        core_nodes = self._create_core_nodes(selected_deep_researcher)

        # 3. 构建工作流
        workflow = StateGraph(AgentState)
        self._setup_workflow_nodes(workflow, analyst_nodes, deep_research_nodes, delete_nodes, tool_nodes, core_nodes, selected_analysts)

        # 4. 设置边连接
        self._setup_deep_research_edges(workflow, selected_deep_researcher, selected_analysts)
        self._setup_analyst_edges(workflow, selected_analysts)
        self._setup_core_edges(workflow)

        return workflow.compile()


    def _validate_parameters(self, selected_analysts, selected_deep_researcher):
        """验证输入参数的有效性。
        
        Args:
            selected_analysts (list): 常规分析师类型列表
            selected_deep_researcher (list): 深度研究分析师类型列表
            
        Raises:
            ValueError: 当没有选择任何分析师时抛出异常
        """
        if len(selected_analysts) == 0 and len(selected_deep_researcher) == 0:
            raise ValueError("交易智能体图设置错误：必须选择至少一个分析师或深度研究员！")

    def _create_analyst_nodes(self, selected_analysts):
        """创建常规分析师节点及其相关的删除节点和工具节点。
        
        Args:
            selected_analysts (list): 要创建的常规分析师类型列表
            
        Returns:
            tuple: (analyst_nodes, delete_nodes, tool_nodes) 三个字典的元组
        """
        analyst_nodes: Dict[str, Any] = {}
        delete_nodes: Dict[str, Any] = {}
        tool_nodes: Dict[str, ToolNode] = {}

        analyst_creators = {
            "market": create_market_analyst,
            "social": create_social_media_analyst,
            "news": create_news_analyst,
            "fundamentals": create_fundamentals_analyst,
        }

        for analyst_type in selected_analysts:
            if analyst_type in analyst_creators:
                analyst_nodes[analyst_type] = analyst_creators[analyst_type](
                    self.quick_thinking_llm, self.toolkit
                )
                delete_nodes[analyst_type] = create_msg_delete()
                tool_nodes[analyst_type] = self.tool_nodes[analyst_type]

        return analyst_nodes, delete_nodes, tool_nodes

    def _create_deep_research_nodes(self, selected_deep_researcher):
        """创建深度研究分析师节点。
        
        Args:
            selected_deep_researcher (list): 要创建的深度研究分析师类型列表
            
        Returns:
            dict: 深度研究节点字典
        """
        deep_research_nodes: Dict[str, Any] = {}
        deep_research_creators = {
            "social_media_deep_research": create_social_media_deep_research_analyst,
            "news_deep_research": create_news_deep_research_analyst,
            "fundamentals_deep_research": create_fundamentals_deep_research_analyst,
            "macro_deep_research": create_macro_deep_research_analyst,
        }

        for research_type in selected_deep_researcher:
            if research_type in deep_research_creators:
                deep_research_nodes[research_type] = deep_research_creators[research_type](
                    self.config
                )

        return deep_research_nodes

    def _create_core_nodes(self, selected_deep_researcher):
        """创建核心节点，包括研究员、管理员、交易员等。
        
        Args:
            selected_deep_researcher (list): 深度研究分析师列表，用于创建同步节点
            
        Returns:
            dict: 核心节点字典
        """
        # 创建同步节点函数
        def create_sync_node(selected_deep_researcher):
            """创建同步节点，等待所有深度研究完成"""
            def sync_node(state: AgentState):
                # 这个节点不修改状态，只是用于同步
                return state
            return sync_node

        core_nodes = {
            "bull_researcher": create_bull_researcher(
                self.quick_thinking_llm, self.bull_memory
            ),
            "bear_researcher": create_bear_researcher(
                self.quick_thinking_llm, self.bear_memory
            ),
            "research_manager": create_research_manager(
                self.deep_thinking_llm, self.invest_judge_memory
            ),
            "trader": create_trader(self.quick_thinking_llm, self.trader_memory),
            "risky_analyst": create_risky_debator(self.quick_thinking_llm),
            "neutral_analyst": create_neutral_debator(self.quick_thinking_llm),
            "safe_analyst": create_safe_debator(self.quick_thinking_llm),
            "risk_manager": create_risk_manager(
                self.deep_thinking_llm, self.risk_manager_memory
            ),
            "report_writer": create_report_writer_analyst(
                self.config, self.deep_thinking_llm
            ),
            "sync_node": create_sync_node(selected_deep_researcher),
        }
        
        return core_nodes

    def _setup_workflow_nodes(self, workflow, analyst_nodes, deep_research_nodes, delete_nodes, tool_nodes, core_nodes, selected_analysts):
        """向工作流添加所有节点。
        
        Args:
            workflow: StateGraph 工作流对象
            analyst_nodes: 常规分析师节点字典
            deep_research_nodes: 深度研究节点字典
            delete_nodes: 删除消息节点字典
            tool_nodes: 工具节点字典
            core_nodes: 核心节点字典
            selected_analysts: 选择的常规分析师列表
        """
        # 添加分析师节点（常规 + 深度研究）
        all_analyst_nodes = {**analyst_nodes, **deep_research_nodes}
        for analyst_type, node in all_analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)

        # 添加常规分析师的辅助节点（删除消息和工具节点）
        for analyst_type in selected_analysts:
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])

        # 添加核心节点
        workflow.add_node("Bull Researcher", core_nodes["bull_researcher"])
        workflow.add_node("Bear Researcher", core_nodes["bear_researcher"])
        workflow.add_node("Research Manager", core_nodes["research_manager"])
        workflow.add_node("Trader", core_nodes["trader"])
        workflow.add_node("Risky Analyst", core_nodes["risky_analyst"])
        workflow.add_node("Neutral Analyst", core_nodes["neutral_analyst"])
        workflow.add_node("Safe Analyst", core_nodes["safe_analyst"])
        workflow.add_node("Risk Judge", core_nodes["risk_manager"])
        workflow.add_node("Report Writer", core_nodes["report_writer"])
        workflow.add_node("Sync Node", core_nodes["sync_node"])

    def _setup_deep_research_edges(self, workflow, selected_deep_researcher, selected_analysts):
        """设置深度研究节点的边连接和同步逻辑。
        
        Args:
            workflow: StateGraph 工作流对象
            selected_deep_researcher: 选择的深度研究分析师列表
            selected_analysts: 选择的常规分析师列表
        """
        # 1. 首先设置深度研究节点的连接（并行启动）
        for analyst_type in selected_deep_researcher:
            workflow.add_edge(START, f"{analyst_type.capitalize()} Analyst")
            # 深度研究完成后都连接到同步节点（深度研究不需要工具循环，直接完成）
            workflow.add_edge(f"{analyst_type.capitalize()} Analyst", "Sync Node")

        # 2. 设置同步节点的条件逻辑（等待所有深度研究完成）
        if selected_deep_researcher:
            # 创建条件逻辑函数，传入selected_deep_researcher参数
            def sync_conditional(state: AgentState):
                return self.conditional_logic.check_deep_research_completion(state, selected_deep_researcher)
            
            if selected_analysts:
                first_analyst = selected_analysts[0]
                workflow.add_conditional_edges(
                    "Sync Node",
                    sync_conditional,
                    {
                        "continue": f"{first_analyst.capitalize()} Analyst",
                        "wait": "Sync Node"  # 继续等待
                    }
                )
            else:
                # 如果没有常规分析师，直接到Bull Researcher
                workflow.add_conditional_edges(
                    "Sync Node",
                    sync_conditional,
                    {
                        "continue": "Bull Researcher",
                        "wait": "Sync Node"
                    }
                )
        else:
            # 如果没有深度研究，直接启动第一个分析师
            if selected_analysts:
                first_analyst = selected_analysts[0]
                workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")

    def _setup_analyst_edges(self, workflow, selected_analysts):
        """设置常规分析师的串行连接逻辑。
        
        Args:
            workflow: StateGraph 工作流对象
            selected_analysts: 选择的常规分析师列表
        """
        # 3. 设置常规分析师的串行连接
        for i, analyst_type in enumerate(selected_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            workflow.add_edge(current_tools, current_analyst)

            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i + 1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                workflow.add_edge(current_clear, "Bull Researcher")

    def _setup_core_edges(self, workflow):
        """设置核心流程的边连接逻辑，包括研究员辩论、风险分析等。
        
        Args:
            workflow: StateGraph 工作流对象
        """
        # 研究员辩论阶段
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
        
        # 研究管理和交易阶段
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")

        # 风险分析辩论阶段
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

        # 最终阶段
        workflow.add_edge("Risk Judge", "Report Writer")
        workflow.add_edge("Report Writer", END)
