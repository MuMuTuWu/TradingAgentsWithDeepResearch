from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI
from pathlib import Path
from tradingagents.utils.token_logger import print_token_usage


def create_report_writer_analyst(config, llm=None):
    def report_writer_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        
        # 构建缓存文件路径
        cache_file_path = Path(config['results_dir']) / ticker / current_date / 'research_report.md'
        
        # 检查缓存文件是否存在
        if cache_file_path.exists():
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cached_report = f.read()
                return {
                    "research_report": cached_report,
                }
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
                # 如果读取失败，继续执行正常的研报写作流程

        # 收集所有分析师报告
        market_report = state.get("market_report", "")
        sentiment_report = state.get("sentiment_report", "")
        news_report = state.get("news_report", "")
        fundamentals_report = state.get("fundamentals_report", "")
        
        # 收集深度研究报告
        social_media_deep_research_report = state.get("social_media_deep_research_report", "")
        news_deep_research_report = state.get("news_deep_research_report", "")
        fundamentals_deep_research_report = state.get("fundamentals_deep_research_report", "")
        macro_deep_research_report = state.get("macro_deep_research_report", "")
        
        # 获取最终交易决策
        final_trade_decision = state.get("final_trade_decision", "")
        
        # 获取投资计划和辩论历史
        investment_plan = state.get("investment_plan", "")
        investment_debate_history = state.get("investment_debate_state", {}).get("history", "")
        risk_debate_history = state.get("risk_debate_state", {}).get("history", "")
        
        # 构建研报写作提示
        research_report_prompt = f"""# {ticker} / {company_name} 投资研究报告

你是一名专业的证券分析师，需要基于以下分析师团队的研究成果，撰写一份符合中国券商研报书写规范的专业投资研究报告。

## 报告要求
- 严格遵循中国证券业协会发布的证券研究报告规范
- 语言专业、客观、严谨，避免过度主观判断
- 结构完整，逻辑清晰，便于投资者阅读
- 包含必要的风险提示和免责声明
- 报告日期：{current_date}

## 可用研究资料

### 基础分析师报告
**市场技术分析报告：**
{market_report}

**社交媒体情绪分析报告：**
{sentiment_report}

**新闻事件分析报告：**
{news_report}

**基本面分析报告：**
{fundamentals_report}

### 深度研究报告
**社交媒体深度研究报告：**
{social_media_deep_research_report}

**新闻深度研究报告：**
{news_deep_research_report}

**基本面深度研究报告：**
{fundamentals_deep_research_report}

**宏观环境深度研究报告：**
{macro_deep_research_report}

### 投资决策过程
**投资团队讨论记录：**
{investment_debate_history}

**风险管理团队讨论记录：**
{risk_debate_history}

**投资建议：**
{investment_plan}

**最终交易决策：**
{final_trade_decision}

## 研报结构要求（请严格按照以下结构输出）

### 1. 报告摘要（≤500字）
- 投资评级：买入/增持/中性/减持/卖出
- 目标价位（如适用）
- 核心投资逻辑（3-5个要点）
- 主要风险提示

### 2. 投资要点
- **核心观点**：明确的投资观点和理由
- **催化因素**：支持投资观点的关键因素
- **风险因素**：可能影响投资收益的风险点

### 3. 公司基本面分析
- **业务概况**：主营业务和商业模式
- **财务状况**：关键财务指标和变化趋势
- **竞争地位**：行业地位和竞争优势
- **成长性分析**：未来增长驱动因素

### 4. 行业与宏观环境分析
- **行业现状**：所处行业的发展阶段和特征
- **政策环境**：相关政策对公司的影响
- **宏观经济**：宏观经济环境对公司的影响

### 5. 技术面分析
- **价格走势**：近期股价表现和技术指标
- **交易量分析**：成交量变化和市场关注度
- **支撑阻力**：关键技术位点分析

### 6. 市场情绪与舆情分析
- **投资者情绪**：市场对公司的整体情绪
- **媒体关注**：媒体报道的主要观点和影响
- **社交媒体**：社交平台讨论热度和观点分布

### 7. 投资建议
- **评级**：明确的投资评级
- **目标价**：12个月目标价（如适用）
- **投资逻辑**：支撑评级的核心逻辑
- **操作建议**：具体的投资操作建议

### 8. 风险提示
- **主要风险**：可能面临的主要风险
- **风险等级**：风险的可能性和影响程度
- **应对措施**：降低风险的可能措施

### 9. 免责声明
请在报告末尾加入标准的证券研究报告免责声明。

## 写作要求
1. **专业性**：使用专业的金融术语和分析框架
2. **客观性**：基于事实和数据进行分析，避免主观臆断
3. **完整性**：确保信息完整，逻辑链条清晰
4. **可读性**：结构清晰，便于不同层次投资者理解
5. **合规性**：符合监管要求，包含必要的风险提示

请基于以上资料和要求，撰写一份高质量的投资研究报告。"""

        # 如果提供了LLM，使用LLM生成研报
        if llm is not None:
            messages = [
                ("system", "你是一名专业的证券分析师，需要根据提供的研究资料撰写符合中国券商研报规范的专业投资研究报告。"),
                ("human", research_report_prompt)
            ]
            
            response = llm.invoke(messages)
            
            # 打印token使用信息
            print_token_usage(response, f"Report Writer ({ticker})")
            
            research_report = response.content

        return {
            "research_report": research_report,
        }

    return report_writer_analyst_node
