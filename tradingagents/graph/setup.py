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

    def _validate_parameters(self, selected_analysts, selected_deep_researcher):
        """验证输入参数的有效性。"""
        if len(selected_analysts) == 0:
            raise ValueError("交易智能体图设置错误：未选择任何分析师！")
    
    def _create_regular_analyst_nodes(self, selected_analysts):
        """创建常规分析师节点及其关联的工具节点和消息清理节点。
        
        常规分析师需要工具支持来获取数据，因此每个分析师都有对应的：
        - 分析师节点：执行分析逻辑
        - 工具节点：调用外部API获取数据
        - 清理节点：清理消息历史以节省token
        """
        analyst_nodes = {}
        delete_nodes = {}
        tool_nodes = {}
        
        # 分析师创建函数映射表
        analyst_creators = {
            "market": create_market_analyst,        # 市场分析师
            "social": create_social_media_analyst,  # 社交媒体分析师
            "news": create_news_analyst,           # 新闻分析师
            "fundamentals": create_fundamentals_analyst,  # 基本面分析师
        }
        
        for analyst_type in selected_analysts:
            if analyst_type in analyst_creators:
                # 创建分析师节点
                analyst_nodes[analyst_type] = analyst_creators[analyst_type](
                    self.quick_thinking_llm, self.toolkit
                )
                # 创建消息清理节点
                delete_nodes[analyst_type] = create_msg_delete()
                # 获取预配置的工具节点
                tool_nodes[analyst_type] = self.tool_nodes[analyst_type]
        
        return analyst_nodes, delete_nodes, tool_nodes
    
    def _create_deep_research_analyst_nodes(self, selected_deep_researcher):
        """创建深度研究分析师节点。
        
        深度研究分析师使用开放深度研究框架，不需要外部工具，
        因此只需要创建分析师节点本身，无需工具节点和清理节点。
        """
        deep_research_nodes = {}
        
        # 深度研究分析师创建函数映射表
        deep_research_creators = {
            "social_media_deep_research": create_social_media_deep_research_analyst,  # 社交媒体深度研究
            "news_deep_research": create_news_deep_research_analyst,                 # 新闻深度研究
            "fundamentals_deep_research": create_fundamentals_deep_research_analyst, # 基本面深度研究
            "macro_deep_research": create_macro_deep_research_analyst,               # 宏观深度研究
        }
        
        for research_type in selected_deep_researcher:
            if research_type in deep_research_creators:
                # 创建深度研究分析师节点（使用配置而非LLM和工具包）
                deep_research_nodes[research_type] = deep_research_creators[research_type](
                    self.config
                )
        
        return deep_research_nodes
    
    def _create_core_nodes(self):
        """创建核心节点：研究员、管理员、交易员和风险分析节点。
        
        核心节点构成了交易决策的主要流程：
        1. 研究阶段：多头研究员 ↔ 空头研究员 (辩论)
        2. 管理阶段：研究管理员 (综合决策)
        3. 交易阶段：交易员 (制定交易策略)
        4. 风险阶段：风险分析师们 (风险评估和辩论)
        """
        core_nodes = {}
        
        # 创建研究员和管理员节点
        core_nodes["bull_researcher"] = create_bull_researcher(
            self.quick_thinking_llm, self.bull_memory
        )
        core_nodes["bear_researcher"] = create_bear_researcher(
            self.quick_thinking_llm, self.bear_memory
        )
        core_nodes["research_manager"] = create_research_manager(
            self.deep_thinking_llm, self.invest_judge_memory
        )
        core_nodes["trader"] = create_trader(self.quick_thinking_llm, self.trader_memory)
        
        # 创建风险分析节点
        core_nodes["risky_analyst"] = create_risky_debator(self.quick_thinking_llm)    # 激进风险分析师
        core_nodes["neutral_analyst"] = create_neutral_debator(self.quick_thinking_llm) # 中性风险分析师
        core_nodes["safe_analyst"] = create_safe_debator(self.quick_thinking_llm)      # 保守风险分析师
        core_nodes["risk_manager"] = create_risk_manager(
            self.deep_thinking_llm, self.risk_manager_memory
        )
        
        # 创建研报写作节点
        core_nodes["report_writer"] = create_report_writer_analyst(self.config, self.deep_thinking_llm)
        
        return core_nodes
    
    def _add_nodes_to_workflow(self, workflow, analyst_nodes, deep_research_nodes, 
                              core_nodes, selected_analysts, delete_nodes, tool_nodes):
        """将所有节点添加到工作流图中。
        
        节点添加顺序：
        1. 所有分析师节点（常规 + 深度研究）
        2. 常规分析师的工具节点和清理节点
        3. 核心流程节点（研究员、管理员、交易员、风险分析师）
        """
        # 添加所有分析师节点到图中
        all_analyst_nodes = {**analyst_nodes, **deep_research_nodes}
        for analyst_type, node in all_analyst_nodes.items():
            workflow.add_node(f"{analyst_type.capitalize()} Analyst", node)
        
        # 仅为常规分析师添加工具节点和清理节点
        for analyst_type in selected_analysts:
            workflow.add_node(
                f"Msg Clear {analyst_type.capitalize()}", delete_nodes[analyst_type]
            )
            workflow.add_node(f"tools_{analyst_type}", tool_nodes[analyst_type])
        
        # 添加核心节点
        workflow.add_node("Bull Researcher", core_nodes["bull_researcher"])        # 多头研究员
        workflow.add_node("Bear Researcher", core_nodes["bear_researcher"])        # 空头研究员
        workflow.add_node("Research Manager", core_nodes["research_manager"])      # 研究管理员
        workflow.add_node("Trader", core_nodes["trader"])                         # 交易员
        workflow.add_node("Risky Analyst", core_nodes["risky_analyst"])           # 激进风险分析师
        workflow.add_node("Neutral Analyst", core_nodes["neutral_analyst"])       # 中性风险分析师
        workflow.add_node("Safe Analyst", core_nodes["safe_analyst"])             # 保守风险分析师
        workflow.add_node("Risk Judge", core_nodes["risk_manager"])               # 风险判断员
        workflow.add_node("Report Writer", core_nodes["report_writer"])           # 研报写作分析师
    
    def _configure_start_edges(self, workflow, selected_analysts, selected_deep_researcher):
        """配置START边，实现并行执行。
        
        并行启动策略：
        - 所有深度研究分析师并行启动（无需工具，可立即开始）
        - 第一个常规分析师并行启动（与深度研究分析师同时开始）
        """
        # 扇出：START并行连接到所有深度研究分析师
        for analyst_type in selected_deep_researcher:
            workflow.add_edge(START, f"{analyst_type.capitalize()} Analyst")
        
        if selected_analysts:
            # 第一个常规分析师也并行启动
            first_analyst = selected_analysts[0]
            workflow.add_edge(START, f"{first_analyst.capitalize()} Analyst")
    
    def _configure_analyst_tool_loops(self, workflow, selected_analysts):
        """配置常规分析师的工具循环和串行连接。
        
        每个常规分析师的执行模式：
        1. 分析师节点 → 条件判断 → 工具节点 或 清理节点
        2. 工具节点 → 分析师节点 (形成循环，直到分析完成)
        3. 清理节点 → 下一个分析师 或 Bull Researcher (串行连接)
        """
        for i, analyst_type in enumerate(selected_analysts):
            current_analyst = f"{analyst_type.capitalize()} Analyst"
            current_tools = f"tools_{analyst_type}"
            current_clear = f"Msg Clear {analyst_type.capitalize()}"

            # 添加当前分析师的条件边（决定是否需要调用工具）
            workflow.add_conditional_edges(
                current_analyst,
                getattr(self.conditional_logic, f"should_continue_{analyst_type}"),
                [current_tools, current_clear],
            )
            # 工具节点执行完毕后回到分析师节点（形成工具调用循环）
            workflow.add_edge(current_tools, current_analyst)
            
            # 串行连接：连接到下一个分析师或到Bull Researcher（如果是最后一个）
            if i < len(selected_analysts) - 1:
                next_analyst = f"{selected_analysts[i+1].capitalize()} Analyst"
                workflow.add_edge(current_clear, next_analyst)
            else:
                # 最后一个分析师连接到Bull Researcher，开始研究辩论阶段
                workflow.add_edge(current_clear, "Bull Researcher")
    
    def _configure_fan_in_edges(self, workflow, selected_deep_researcher):
        """配置从深度研究分析师到Bull Researcher的汇聚边。
        
        扇入策略：所有深度研究分析师完成后直接汇聚到Bull Researcher，
        与常规分析师的结果一起进入研究辩论阶段。
        """
        # 扇入：所有深度研究分析师直接连接到Bull Researcher
        for analyst_type in selected_deep_researcher:
            workflow.add_edge(f"{analyst_type.capitalize()} Analyst", "Bull Researcher")
    
    def _configure_core_workflow_edges(self, workflow):
        """配置核心工作流的边（研究、交易、风险管理）。
        
        核心工作流包含三个阶段：
        1. 研究阶段：Bull Researcher ↔ Bear Researcher 辩论，直到达成共识或超时
        2. 交易阶段：Research Manager 综合决策 → Trader 制定交易策略
        3. 风险阶段：三个风险分析师循环辩论 → Risk Judge 最终决策
        """
        # 研究阶段边：多头空头研究员辩论
        workflow.add_conditional_edges(
            "Bull Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bear Researcher": "Bear Researcher",      # 继续辩论
                "Research Manager": "Research Manager",    # 结束辩论，进入管理阶段
            },
        )
        workflow.add_conditional_edges(
            "Bear Researcher",
            self.conditional_logic.should_continue_debate,
            {
                "Bull Researcher": "Bull Researcher",      # 继续辩论
                "Research Manager": "Research Manager",    # 结束辩论，进入管理阶段
            },
        )
        
        # 交易阶段边：管理员决策 → 交易员策略
        workflow.add_edge("Research Manager", "Trader")
        workflow.add_edge("Trader", "Risky Analyst")
        
        # 风险管理阶段边：三个风险分析师循环辩论
        workflow.add_conditional_edges(
            "Risky Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Safe Analyst": "Safe Analyst",    # 激进 → 保守
                "Risk Judge": "Risk Judge",        # 结束风险分析
            },
        )
        workflow.add_conditional_edges(
            "Safe Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Neutral Analyst": "Neutral Analyst",  # 保守 → 中性
                "Risk Judge": "Risk Judge",            # 结束风险分析
            },
        )
        workflow.add_conditional_edges(
            "Neutral Analyst",
            self.conditional_logic.should_continue_risk_analysis,
            {
                "Risky Analyst": "Risky Analyst",  # 中性 → 激进（循环）
                "Risk Judge": "Risk Judge",        # 结束风险分析
            },
        )
        
        # 最终边：风险判断完成后进入研报写作，研报写作完成后结束整个流程
        workflow.add_edge("Risk Judge", "Report Writer")
        workflow.add_edge("Report Writer", END)

    def setup_graph(
        self, selected_analysts=["market", "social", "news", "fundamentals"],
        selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research", "macro_deep_research"]
    ):
        """设置并编译智能体工作流图。
        
        这是主要的入口方法，负责协调整个图的构建过程。
        构建过程分为5个步骤：参数验证 → 节点创建 → 图构建 → 边配置 → 编译。

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
        # 1. 验证参数
        self._validate_parameters(selected_analysts, selected_deep_researcher)
        
        # 2. 创建各类型节点
        analyst_nodes, delete_nodes, tool_nodes = self._create_regular_analyst_nodes(selected_analysts)
        deep_research_nodes = self._create_deep_research_analyst_nodes(selected_deep_researcher)
        core_nodes = self._create_core_nodes()
        
        # 3. 创建工作流并添加节点
        workflow = StateGraph(AgentState)
        self._add_nodes_to_workflow(
            workflow, analyst_nodes, deep_research_nodes, core_nodes,
            selected_analysts, delete_nodes, tool_nodes
        )
        
        # 4. 配置边连接
        self._configure_start_edges(workflow, selected_analysts, selected_deep_researcher)
        self._configure_analyst_tool_loops(workflow, selected_analysts)
        self._configure_fan_in_edges(workflow, selected_deep_researcher)
        self._configure_core_workflow_edges(workflow)
        
        # 5. 编译并返回工作流图
        return workflow.compile()
