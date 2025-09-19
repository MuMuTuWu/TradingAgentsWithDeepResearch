from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from .deep_research_utils import run_deep_research_sync
from pathlib import Path


def create_macro_deep_research_analyst(config):
    def macro_deep_research_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        
        # 构建缓存文件路径
        cache_file_path = Path(config['results_dir']) / ticker / current_date / 'macro_deep_research_report.md'
        
        # 检查缓存文件是否存在
        if cache_file_path.exists():
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cached_report = f.read()
                return {
                    "macro_deep_research_report": cached_report,
                }
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
                # 如果读取失败，继续执行正常的研究流程
        
        # 构建针对A股宏观经济的深度研究查询
        research_query = f"""# A股市场宏观经济环境与投资机遇深度研究报告

> 交付对象：**投资交易团队**

你需要在 **{current_date}前一周** 对 **A股市场宏观经济背景和投资环境** 开展**宏观数据收集 → 政策分析 → 环境评估 → 结构化交付**的全流程宏观研究，并输出可复核、可追溯的分析依据。

## 研究目标（请直接回答这些问题）
- **宏观经济环境**：当前中国宏观经济运行状况如何？主要经济指标呈现什么趋势？
- **货币财政政策**：央行货币政策取向如何？财政政策有哪些新动向？对市场流动性的影响？
- **监管政策动态**：证监会、银保监会等监管部门有哪些新政策？对A股市场的影响？
- **市场风险机遇**：当前A股市场面临的主要系统性风险和投资机遇是什么？

## 范围与来源（权威机构优先 + 可追溯）
- **官方权威数据**：国家统计局、央行、财政部、发改委、商务部等官方数据和报告
- **监管机构信息**：证监会、银保监会、交易所公告、政策解读、监管动态
- **权威财经媒体**：新华财经、经济参考报、上证报、证券时报、21世纪经济报道、财联社
- **国际权威来源**：IMF、世界银行、OECD对中国经济的评估和预测
- **专业机构研报**：央行货币政策执行报告、各大券商宏观研究报告、智库研究
- **经济数据平台**：Wind、同花顺、Choice等专业数据平台的宏观指标
> 要求：优先采用**官方权威来源**，所有关键结论**必须**提供**可点击链接**或准确出处。

## 分析框架（多维度宏观评估）
1. **宏观经济运行分析**  
   - GDP增长趋势、工业增加值、固定资产投资、消费数据
   - CPI、PPI通胀水平及趋势预判
   - PMI制造业和服务业景气度
2. **货币政策环境分析**  
   - 央行政策利率、准备金率、公开市场操作
   - 社会融资规模、M1/M2货币供应量增速
   - 银行间市场利率走势、流动性环境
3. **财政政策影响分析**  
   - 财政收支状况、减税降费政策
   - 地方政府债务、专项债发行
   - 基建投资、产业政策支持方向
4. **监管政策影响分析**  
   - 资本市场改革进展、注册制推进
   - 金融监管政策变化、风险防控措施
   - 房地产、平台经济等重点领域监管
5. **国际环境影响分析**  
   - 中美关系、地缘政治风险
   - 全球经济形势、主要央行政策
   - 人民币汇率、外资流入流出

## 市场影响评估框架
- **流动性环境**：宽松/中性/紧缩，对股市资金面的影响
- **风险偏好**：政策环境对投资者风险偏好的影响
- **板块轮动**：宏观环境变化对不同行业板块的差异化影响
- **估值水平**：当前A股整体估值水平与历史和国际比较
- **系统性风险**：需要重点关注的宏观风险因素

## 输出结构（使用markdown格式输出，请严格按顺序与字段）
1) **宏观环境评级（≤300字，面向投资团队）**  
   - 当前宏观环境综合评级、主要支撑因素和风险点、对A股市场的总体影响判断
2) **经济基本面分析**  
   - 主要经济指标走势、经济增长动能、结构性变化特征
3) **政策环境分析**  
   - 货币政策取向、财政政策力度、监管政策影响
4) **流动性环境评估**  
   - 市场流动性状况、资金供求关系、对股市资金面的影响
5) **国际环境影响**  
   - 外部环境变化、汇率影响、外资流向分析
6) **系统性风险识别**  
   - 主要宏观风险因素、风险传导路径、影响程度评估
7) **投资机遇分析**  
   - 政策红利、结构性机会、主题投资方向
8) **市场配置建议**  
   - 基于宏观分析的A股投资策略：整体仓位建议、行业配置建议、投资风格建议
9) **投资建议总结**  
   - 基于宏观环境的市场判断：POSITIVE/NEUTRAL/NEGATIVE，并说明理由和风险提示"""

        # 调用公共的深度研究函数
        research_report = run_deep_research_sync(config, research_query)
        
        # 如果返回的是错误信息，添加具体的分析类型说明
        if research_report.startswith("无法完成深度研究分析"):
            research_report = f"无法完成A股宏观环境深度研究分析: {research_report[9:]}"

        # 保存研究报告到缓存文件
        try:
            # 确保目录存在
            cache_file_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存报告内容
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                f.write(research_report)
            print(f"宏观深度研究报告已保存到: {cache_file_path}")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
            # 即使保存失败，也继续返回结果

        return {
            "macro_deep_research_report": research_report,
        }

    return macro_deep_research_analyst_node
