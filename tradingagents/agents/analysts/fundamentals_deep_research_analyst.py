from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from .deep_research_utils import run_deep_research_sync
from pathlib import Path


def create_fundamentals_deep_research_analyst(config):
    def fundamentals_deep_research_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        
        # 构建缓存文件路径
        cache_file_path = Path(config['results_dir']) / ticker / current_date / 'fundamentals_deep_research_report.md'
        
        # 检查缓存文件是否存在
        if cache_file_path.exists():
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cached_report = f.read()
                return {
                    "fundamentals_deep_research_report": cached_report,
                }
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
                # 如果读取失败，继续执行正常的研究流程
        
        # 构建针对基本面的深度研究查询
        research_query = f"""# {ticker} / {company_name} 基本面与财务深度研究报告

> 交付对象：**投资交易团队**

你需要在 **{current_date}前一周** 对 **{ticker} / {company_name}** 开展**财务数据收集 → 深度分析 → 估值建模 → 结构化交付**的全流程基本面研究，并输出可复核、可追溯的分析依据。

## 研究目标（请直接回答这些问题）
- **财务健康状况**：资产负债结构、现金流状况、盈利能力如何？
- **业务经营质量**：收入增长的可持续性、利润率变化趋势、核心竞争力？
- **估值合理性**：当前估值水平是否合理？与同行业对比如何？
- **未来增长前景**：业务发展潜力、市场空间、增长驱动因素？

## 范围与来源（专业数据优先 + 可追溯）
- **官方财务数据**：年报、季报、招股书、定期报告、临时公告
- **专业数据平台**：Wind、同花顺、Choice、Bloomberg、FactSet数据
- **券商研报**：头部券商深度研报、行业分析、盈利预测、估值模型
- **行业数据**：行业协会报告、政府统计数据、第三方市场研究
> 要求：所有数据**必须**注明来源和时间，确保数据的**准确性和时效性**。

## 分析框架（多维度综合评估）
1. **财务质量分析**  
   - 收入确认质量、利润构成分析、现金流与利润匹配度
   - 资产质量、负债结构、偿债能力评估
2. **盈利能力分析**  
   - 毛利率、净利率、ROE、ROIC等关键指标趋势
   - 盈利能力的稳定性和可持续性
3. **成长性分析**  
   - 收入、利润、市场份额的历史增长趋势
   - 未来增长的驱动因素和可实现性
4. **估值分析**  
   - PE、PB、PS、EV/EBITDA等估值指标
   - 与历史估值、同行估值的对比分析

## 数据验证与质量控制
- **数据一致性检查**：确保不同来源数据的一致性
- **异常数据识别**：识别和解释异常的财务数据变化
- **调整项处理**：非经常性损益、会计政策变更等调整
- **预测假设验证**：验证券商预测的合理性和可实现性

## 输出结构（使用markdown格式输出，请严格按顺序与字段）
1) **基本面评级（≤300字，面向投资团队）**  
   - 财务健康度、盈利质量、成长前景的综合评级和核心观点
2) **财务健康度分析**  
   - 资产负债表质量、现金流状况、偿债能力评估
3) **盈利能力分析**  
   - 盈利能力指标趋势、盈利质量评估、与同行对比
4) **成长性分析**  
   - 历史成长轨迹、未来增长驱动因素、增长可持续性
5) **估值分析**  
   - 当前估值水平、历史估值区间、同行估值对比
6) **同业对比分析**  
   - 与主要竞争对手的财务指标和估值对比
7) **风险因素识别**  
   - 财务风险、经营风险、行业风险、估值风险
8) **投资价值评估**  
   - 基于基本面分析的投资建议：BUY/HOLD/SELL，目标价位和投资逻辑"""

        # 调用公共的深度研究函数
        research_report = run_deep_research_sync(config, research_query)
        
        # 如果返回的是错误信息，添加具体的分析类型说明
        if research_report.startswith("无法完成深度研究分析"):
            research_report = f"无法完成{ticker}的基本面深度研究分析: {research_report[9:]}"

        # 保存研究报告到缓存文件
        try:
            # 确保目录存在
            cache_file_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存报告内容
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                f.write(research_report)
            print(f"基本面深度研究报告已保存到: {cache_file_path}")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
            # 即使保存失败，也继续返回结果

      #   # 构建返回消息
      #   result_message = AIMessage(content=research_report)

        return {
            # "messages": [result_message],
            "fundamentals_deep_research_report": research_report,
        }

    return fundamentals_deep_research_analyst_node
