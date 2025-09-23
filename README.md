# TradingAgents with Deep Research Integration

## 项目概述

本项目是基于两个开源项目的深度整合：
- [TauricResearch/TradingAgents](https://github.com/TauricResearch/TradingAgents): 多智能体金融交易框架
- [langchain-ai/open_deep_research](https://github.com/langchain-ai/open_deep_research): 深度研究分析系统

通过将深度研究能力集成到投研智能体中，本项目构建了一个更加全面和深入的金融分析与交易决策系统。该系统不仅具备传统的技术分析、基本面分析、情绪分析和新闻分析能力，还引入了深度研究机制，能够对特定主题进行更加深入和全面的调研。

## 快速开始

### 环境配置

在运行项目之前，需要先配置环境变量。创建 `.env` 文件并添加必要的API密钥：

```bash
# 创建环境变量文件
touch .env

# 编辑 .env 文件，添加以下API密钥：
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here        # 用于深度研究搜索
BASE_URL=https://api.openai.com/v1             # API基础URL，可自定义
```

### 安装依赖

使用 `uv` 包管理器安装项目依赖：

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 安装项目依赖
uv sync
```

### 运行项目

项目的主要运行入口是 `main.py`：

```bash
# 使用 uv 运行主程序
uv run main.py
```

### 当前配置

当前版本的 `selected_analysts` 仅支持 **market analyst**，这是为了专注于技术分析能力的优化。未来版本将逐步支持更多分析师类型。

```python
# main.py 中的配置示例
ta = TradingAgentsGraph(
    selected_analysts=["market"],  # 当前仅支持市场分析师
    selected_deep_researcher=[
        "social_media_deep_research", 
        "news_deep_research", 
        "fundamentals_deep_research", 
        "macro_deep_research"
    ],
    debug=False,
    config=config
)
```

## 系统架构

<p align="center">
  <img src="assets/agent_graph.png" alt="Multi-Agent Architecture" style="width: 100%; height: auto;">
</p>

本系统采用多智能体协作架构，通过专业化分工和动态协作来实现全面的投资研究和交易决策。整个架构可以分为以下几个层次：

### 1. 数据采集与分析层 (Analyst Team)

#### 常规分析师 (Regular Analysts)
这些分析师负责基础的市场数据收集和初步分析：

- **Market Analyst (市场分析师)** [当前支持]
  - **功能**: 技术指标分析和市场趋势研究
  - **工具**: 移动平均线(SMA/EMA)、MACD、RSI、布林带、ATR、成交量加权移动平均(VWMA)等
  - **输出**: 详细的技术分析报告，包含趋势判断和关键指标分析
  - **特点**: 选择最相关的8个指标进行互补性分析，避免冗余

- **Social Media Analyst (社交媒体分析师)** [待支持]
  - **功能**: 社交媒体情绪分析和公司特定新闻研究
  - **数据源**: Reddit、Twitter等社交平台的股票讨论
  - **输出**: 公众情绪报告和社交媒体趋势分析

- **News Analyst (新闻分析师)** [待支持]
  - **功能**: 全球新闻和宏观经济指标分析
  - **数据源**: 主流财经媒体、政策发布、行业新闻
  - **输出**: 新闻事件对市场影响的综合分析报告

- **Fundamentals Analyst (基本面分析师)** [待支持]
  - **功能**: 公司财务数据和基本面信息分析
  - **数据源**: 财务报表、内部人士交易、公司公告
  - **输出**: 公司基本面健康度和价值评估报告

#### 深度研究分析师 (Deep Research Analysts)
这些分析师利用深度研究系统进行更加全面和深入的专题分析：

- **Social Media Deep Research Analyst (社交媒体深度研究分析师)**
  - **功能**: 广域社交媒体信息收集与深度情绪分析
  - **研究范围**: 微博、雪球、知乎、Reddit、Twitter等多平台
  - **分析维度**: 
    - 公众讨论与情绪变化趋势
    - 关键事件催化剂识别
    - 媒体报道与社媒观点一致性分析
    - 情绪刻度量化(-2到+2)
  - **输出**: 结构化的深度社交媒体研究报告，包含逐日时间线、情绪区间综述、主题洞察等

- **News Deep Research Analyst (新闻深度研究分析师)**
  - **功能**: 权威新闻事件的深度收集与影响分析
  - **数据源**: 权威财经媒体、国际主流媒体、官方公告、券商研报
  - **分析框架**:
    - 重大新闻事件识别与分类
    - 多源验证与事实核查
    - 政策监管动态分析
    - 业务经营新闻跟踪
  - **输出**: 新闻事件时间线、政策影响评估、媒体可信度分析

- **Fundamentals Deep Research Analyst (基本面深度研究分析师)**
  - **功能**: 财务数据的深度挖掘与估值建模
  - **数据源**: 官方财务数据、专业数据平台、券商研报、行业数据
  - **分析维度**:
    - 财务质量深度分析
    - 盈利能力可持续性评估
    - 成长性驱动因素识别
    - 估值合理性多维度对比
  - **输出**: 基本面评级、财务健康度分析、同业对比、投资价值评估

- **Macro Deep Research Analyst (宏观深度研究分析师)**
  - **功能**: 宏观经济环境与政策影响的深度分析
  - **数据源**: 央行政策、经济数据、国际市场动态
  - **分析维度**:
    - 货币政策影响评估
    - 经济周期位置判断
    - 国际市场联动性分析
    - 行业政策影响评估
  - **输出**: 宏观环境报告、政策影响评估、市场风险预警

### 2. 研究辩论层 (Research Team)

- **Bull Researcher (多头研究员)**
  - **功能**: 构建看涨论证，强调增长潜力和竞争优势
  - **策略**: 利用正面指标和市场机会，反驳空头观点
  - **记忆机制**: 从历史决策中学习，避免重复错误

- **Bear Researcher (空头研究员)**
  - **功能**: 构建看跌论证，强调风险和挑战
  - **策略**: 识别潜在威胁和竞争劣势，质疑乐观假设
  - **记忆机制**: 基于过往经验优化风险识别能力

- **Research Manager (研究总监)**
  - **功能**: 主持多空辩论，做出最终投资建议
  - **决策过程**: 综合评估辩论双方论点，形成明确的BUY/HOLD/SELL建议
  - **输出**: 详细的投资计划和实施策略

### 3. 交易执行层 (Trading Team)

- **Trader (交易员)**
  - **功能**: 基于研究团队的投资计划制定具体交易方案
  - **输入**: 所有分析师报告和研究团队的投资建议
  - **输出**: 明确的交易提案(BUY/HOLD/SELL)
  - **学习能力**: 从历史交易结果中总结经验教训

### 4. 风险管理层 (Risk Management Team)

- **Risky Analyst (激进风险分析师)**
  - **功能**: 倡导高风险高收益策略
  - **观点**: 强调增长潜力和竞争优势，质疑过度保守的策略
  - **辩论策略**: 用数据驱动的反驳来挑战保守观点

- **Safe Analyst (保守风险分析师)**
  - **功能**: 优先考虑资产保护和稳定增长
  - **观点**: 强调风险缓解和长期可持续性
  - **辩论策略**: 识别高风险因素，提出谨慎替代方案

- **Neutral Analyst (中性风险分析师)**
  - **功能**: 提供平衡视角，权衡收益与风险
  - **观点**: 倡导适度风险策略，避免极端立场
  - **辩论策略**: 挑战激进和保守观点，寻求最佳平衡点

- **Risk Judge (风险总监)**
  - **功能**: 主持风险辩论，对交易员提案进行最终风险评估
  - **决策权**: 批准或拒绝交易提案
  - **输出**: 最终的交易决策和风险调整建议

## 工作流程

系统的工作流程经过精心设计，确保高效协作和全面分析：

1. **并行分析阶段**: 
   - 深度研究分析师并行启动，进行专题深度调研
   - 常规分析师等待深度研究完成后开始工作
   - 同步节点协调不同阶段的衔接

2. **常规分析阶段**: 
   - 常规分析师串行执行，确保数据一致性
   - 每个分析师可调用工具进行数据收集和分析
   - 生成专业分析报告

3. **研究辩论阶段**: 
   - Bull和Bear研究员基于所有分析师的报告进行辩论
   - 多轮动态辩论，直到达到设定轮数或Research Manager介入
   - Research Manager综合评估并形成投资建议

4. **交易决策阶段**: 
   - Trader基于投资建议制定交易方案

5. **风险评估阶段**: 
   - 三类风险分析师对交易方案进行多角度评估
   - 多轮风险辩论，全面评估潜在风险
   - Risk Judge做出最终批准或拒绝决定

6. **报告生成阶段**:
   - Report Writer整合所有分析结果
   - 生成最终的综合研究报告

## 技术特性

### 核心架构
- **LangGraph架构**: 基于LangGraph构建的模块化智能体系统
- **模块化设计**: 重构后的图设置系统，功能清晰分离
- **并行处理**: 深度研究分析师并行工作，提高效率
- **同步机制**: 智能同步节点确保工作流程的协调

### 智能体能力
- **记忆机制**: 各个智能体具备学习和记忆能力，能够从历史决策中改进
- **深度研究集成**: 结合open_deep_research的深度调研能力
- **动态辩论**: 支持多轮动态辩论机制
- **工具调用**: 支持丰富的数据获取和分析工具

### 配置灵活性
- **可配置性**: 支持灵活的分析师组合和参数配置
- **多LLM支持**: 支持OpenAI、Anthropic、Google等多种LLM提供商
- **在线/离线模式**: 支持在线工具和离线缓存数据两种模式

## 配置说明

### 系统配置

系统通过 `DEFAULT_CONFIG` 进行配置，主要参数包括：

```python
DEFAULT_CONFIG = {
    # 路径配置
    "project_dir": PROJECT_ROOT,
    "results_dir": PROJECT_ROOT / "results",
    "data_dir": PROJECT_ROOT / "tradingagents" / "datainterface" / "data",
    "data_cache_dir": PROJECT_ROOT / "tradingagents" / "datainterface" / "data_cache",
    
    # LLM设置
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5-mini",      # 深度思考模型
    "quick_think_llm": "gpt-5-nano",     # 快速思考模型
    "backend_url": "https://api.openai.com/v1",
    
    # 辩论设置
    "max_debate_rounds": 1,              # 投资辩论最大轮数
    "max_risk_discuss_rounds": 1,        # 风险辩论最大轮数
    "max_recur_limit": 100,              # 递归限制
    
    # 工具设置
    "online_tools": True,                # 是否使用在线工具
    
    # 调试设置
    "debug": True,                       # 是否输出调试信息
}
```

### 自定义配置

在 `main.py` 中可以自定义配置：

```python
# 创建自定义配置
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5-mini"
config["quick_think_llm"] = "gpt-5-nano"
config["backend_url"] = os.environ.get("BASE_URL")
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
config["online_tools"] = True
config["debug"] = False

# 目标股票和日期
ticker = "000300.SH"  # 沪深300指数
current_date = "2025-09-23"
```

## 输出结果

系统运行后会在 `results/{ticker}/{date}/` 目录下生成以下文件：

- `trading_graph.mmd`: Mermaid格式的工作流图
- `market_report.md`: 市场分析报告
- `research_report.md`: 综合研究报告
- `final_trade_decision.md`: 最终交易决策
- `final_state.json`: 完整的系统状态数据
- `*_deep_research_report.md`: 各类深度研究报告

## CLI工具

项目还提供了命令行交互工具：

```bash
# 运行CLI工具
uv run python -m cli.main
```

CLI工具提供了交互式的分析师选择和配置界面，方便用户快速设置和运行分析。

## 开发指南

### 项目结构

```
TradingAgents/
├── main.py                    # 主运行入口
├── cli/                       # CLI工具
├── tradingagents/            # 核心代码
│   ├── agents/               # 智能体定义
│   ├── graph/                # 图结构和工作流
│   ├── dataflows/            # 数据流处理
│   ├── datainterface/        # 数据接口
│   └── utils/                # 工具函数
├── open_deep_research/       # 深度研究模块
├── results/                  # 输出结果
└── assets/                   # 资源文件
```

### 扩展开发

1. **添加新分析师**: 在 `tradingagents/agents/analysts/` 目录下创建新的分析师类
2. **修改工作流**: 在 `tradingagents/graph/setup.py` 中调整图结构
3. **添加数据源**: 在 `tradingagents/dataflows/` 中添加新的数据接口
4. **自定义工具**: 在 `tradingagents/agents/utils/` 中添加新的工具函数

## 注意事项

1. **API配额**: 深度研究功能会消耗大量API调用，请注意配额限制
2. **数据缓存**: 系统支持数据缓存，可以减少重复的API调用
3. **调试模式**: 开启调试模式可以查看详细的执行过程，但会增加输出量
4. **网络要求**: 在线工具模式需要稳定的网络连接

## 许可证

本项目基于原开源项目的许可证进行开发和分发。

## 贡献

欢迎提交Issue和Pull Request来改进项目。在贡献代码前，请确保：

1. 代码符合项目的编码规范
2. 添加必要的测试和文档
3. 确保所有测试通过

## 支持

如果在使用过程中遇到问题，请：

1. 检查环境变量配置是否正确
2. 确认API密钥是否有效
3. 查看调试输出信息
4. 提交Issue描述具体问题