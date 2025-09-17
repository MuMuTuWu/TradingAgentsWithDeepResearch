from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from .deep_research_utils import run_deep_research_sync


def create_news_deep_research_analyst(config):
    def news_deep_research_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        
        # 构建针对新闻的深度研究查询
        research_query = f"""# {ticker} / {company_name} 新闻与市场事件深度研究报告

> 交付对象：**投资交易团队**

你需要在 **{current_date}前一周** 对 **{ticker} / {company_name}** 开展**新闻事件收集 → 事实核查 → 影响分析 → 结构化交付**的全流程新闻研究，并输出可复核、可追溯的证据链。

## 研究目标（请直接回答这些问题）
- 过去一周与该股票/指数相关的**重大新闻事件**有哪些？
- **政策变化、监管动态、行业事件**对公司的具体影响是什么？
- **媒体报道的真实性和可信度**如何？是否存在误导性信息？
- **新闻事件的时序关系**和**市场反应的逻辑链条**是什么？

## 范围与来源（权威媒体优先 + 可追溯）
- **权威财经媒体**：上证报、证券时报、21世纪经济报道、财联社、第一财经、央视财经、澎湃财经
- **国际权威媒体**：彭博、路透、华尔街日报、金融时报、CNBC、MarketWatch
- **官方权威来源**：交易所公告、证监会发布、央行政策、部委通知、公司官方公告
- **券商研报**：头部券商的研究报告、分析师观点、投资建议
- **行业专业媒体**：相关行业的专业媒体和权威报告
> 要求：优先采用**A级来源**（官方、头部媒体），所有关键信息**必须**提供**可点击链接**或准确出处。

## 搜索与收集流程（权威性优先，显式记录）
1. **事件识别与分类**  
   - 按重要性分级：重大事件、一般事件、传闻信息
   - 按类型分类：政策监管、业务经营、财务数据、行业动态、突发事件
2. **多源验证**  
   - 交叉验证不同媒体的报道内容
   - 区分**已确认事实**、**官方表态**、**市场传言**
3. **时间线构建**  
   - 精确记录事件发生时间、报道时间、市场反应时间
   - 构建完整的因果关系链

## 信息质量分级（严格标准）
- **来源分级**：  
  - **A+**：监管机构、交易所、上市公司官方
  - **A**：权威财经媒体、国际主流媒体
  - **B**：券商研报、行业专业媒体、知名财经记者
  - **C**：一般媒体、网络传言、未验证消息
- **可信度评估**：`官方确认 / 多源验证 / 单源可信 / 传言待证 / 存疑信息`

## 影响分析框架
- **直接影响**：对公司业务、财务、估值的直接影响
- **行业影响**：对整个行业或相关产业链的影响  
- **政策影响**：监管政策变化对公司合规和经营的影响
- **市场情绪影响**：新闻对投资者信心和市场预期的影响
- **时间维度**：短期（1-3个月）、中期（3-12个月）、长期（1年以上）影响

## 输出结构（使用markdown格式输出，请严格按顺序与字段）
1) **新闻摘要（≤300字，面向投资团队）**  
   - 本周最重要的3-5个新闻事件及其投资影响
2) **重大事件时间线**  
   - `YYYY-MM-DD HH:MM`：事件描述、来源级别、市场反应、影响评估
3) **政策监管动态**  
   - 相关政策变化、监管表态、合规要求变化及其影响
4) **业务经营新闻**  
   - 公司业务进展、合作协议、重大合同、人事变动等
5) **财务与业绩相关**  
   - 业绩预告、财务数据、分红派息、股权变动等
6) **行业与竞争动态**  
   - 行业政策、竞争对手动向、市场格局变化
7) **媒体可信度分析**  
   - 各媒体报道的一致性、准确性、可能的偏向性分析
8) **投资影响评估**  
   - 基于新闻事件的投资建议：BUY/HOLD/SELL，风险提示和机会识别"""

        # 调用公共的深度研究函数
        research_report = run_deep_research_sync(config, research_query)
        
        # 如果返回的是错误信息，添加具体的分析类型说明
        if research_report.startswith("无法完成深度研究分析"):
            research_report = f"无法完成{ticker}的新闻深度研究分析: {research_report[9:]}"

        # 构建返回消息
        result_message = AIMessage(content=research_report)

        return {
            "messages": [result_message],
            "news_deep_research_report": research_report,
        }

    return news_deep_research_analyst_node
