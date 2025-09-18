from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import AIMessage
from .deep_research_utils import run_deep_research_sync
from pathlib import Path


def create_social_media_deep_research_analyst(config):
    def deep_research_analyst_node(state):
        current_date = state["trade_date"]
        ticker = state["company_of_interest"]
        company_name = state["company_of_interest"]
        
        # 构建缓存文件路径
        cache_file_path = Path(config['results_dir']) / ticker / current_date / 'social_media_deep_research_report.md'
        
        # 检查缓存文件是否存在
        if cache_file_path.exists():
            try:
                with open(cache_file_path, 'r', encoding='utf-8') as f:
                    cached_report = f.read()
                return {
                    "social_media_deep_research_report": cached_report,
                }
            except Exception as e:
                print(f"读取缓存文件失败: {e}")
                # 如果读取失败，继续执行正常的研究流程
        
        # 构建针对交易的深度研究查询，参考main.py中的query结构
        research_query = f"""# {ticker} / {company_name} 深度投资研究报告

> 交付对象：**投资交易团队**

你需要在 **{current_date}前一周** 对 **{ticker} / {company_name}** 开展**广域信息收集 → 初步筛选 → 情绪与主题分析 → 结构化交付**的全流程投资研究，并输出可复核、可追溯的证据链。

## 研究目标（请直接回答这些问题）
- 过去一周与该股票/指数相关的**公众讨论与情绪**如何变化？
- **关键事件 / 催化 / 风险**分别是什么？时间点与触发机制如何？
- **媒体报道与社媒观点**是否一致？如不一致，谁先谁后、背离原因？
- **基本面和技术面**呈现什么特征和趋势？

## 范围与来源（尽可能广 + 可追溯）
- **社交/社区**：微博、雪球、知乎、贴吧、抖音/快手评论区、B站、X（Twitter）、Reddit、各大论坛与评论区。
- **新闻与研报**：上证报、证券时报、21世纪、财联社、第一财经、央视财经、澎湃、券商晨报/快评（标注机构与要点）、彭博、路透、FT、WSJ。
- **官方与数据**：交易所公告，监管与部委发布，上市公司公告，财务报告；如可用可引用 Wind/同花顺/Choice 指示性数据。
- **关键词扩展**：股票代码/简称/英文缩写/口语别称/常见错拼；覆盖相关主题（如"业绩""分红""重组""增发""回购"）。
- **多语言**：必要时纳入英文来源并**简要翻译为中文**。
> 要求：所有关键结论**必须**提供**可点击链接**或可定位出处（媒体名+日期+标题）；标注时间戳与抓取时间。

## 搜索与收集流程（先广后精，显式记录）
1. **检索策略与记录**  
   - 迭代关键词；记录每轮**检索词**、平台与收获要点。
2. **代表性样本采集**  
   - 覆盖不同账号类型（官方/媒体/KOL/普通用户）、不同互动层级（高赞/中量/低量）、不同观点立场（看多/中性/看空）。  
   - 对高度传播的相似帖/转发链保留**首发源 + 1~2条最具代表性二传**；其余去重。
3. **时间与证据链**  
   - 每条样本保留：平台、账号类型、时间、互动量（如可得）、原文要点、链接、初判情绪。

## 初步筛选与质量分级（降噪/可信度）
- **去重与降噪**：过滤明显营销号、机器人刷量、复读帖、标题党；将"低证据/夸张"单独归类。
- **来源分级**：  
  - **A**：官方/头部权威媒体/监管/交易所/上市公司  
  - **B**：专业创作者/行业KOL/券商机构内容  
  - **C**：普通用户/匿名账号/不明来源  
  > 结论优先采用 A，B/C 作为佐证或线索。
- **可信度标签**：`已证实 / 多源一致 / 单源线索 / 传闻待证实`（传闻必须显著标注）。

## 情绪与主题分析（-2..+2 刻度）
- **情绪刻度**：-2 强空；-1 偏空；0 中性；+1 偏多；+2 强多。  
- **每日指标**：`提及量`、`看多/看空比`、`净情绪 = 看多 - 看空`；标注**异常波动点**与对应事件链接。  
- **主题框架**：`基本面变化` ｜ `技术面信号` ｜ `资金面动向` ｜ `政策影响` ｜ `行业催化` ｜ `市场情绪` ｜ `风险因素`。  
- **一致性校验**：将**社媒净情绪**与**主流媒体基调**、**股价当日涨跌幅/成交量（如可得）**对比，指出**最大背离日**与可能原因。

## 输出结构（使用markdown格式输出，请严格按顺序与字段）
1) **投资结论（≤360字，面向投资团队）**  
   - 本周情绪方向；最重要**3个催化/风险**；投资建议和理由。  
2) **逐日时间线**  
   - `YYYY-MM-DD`：净情绪、看多/看空比、提及量、**关键事件 2-4**（含**链接**、来源分级、可信度标签）。  
3) **情绪区间综述**  
   - 平均/中位净情绪、最高/最低日、**最大"情绪-行情"背离日**及解释。  
4) **主题洞察**
   - 每主题 3-6 条要点，附代表言论链接、情绪评分、来源分级。  
5) **Top 帖子/讨论 （8条）**  
   - 平台、时间、互动量、要点摘要、链接、情绪、是否疑似机器人。  
6) **Top 新闻 （8条）**  
   - 媒体、时间、标题/要点、链接、与社媒关系（吻合/背离/分歧）。  
7) **方法与样本**  
   - 平台覆盖、样本量、去重策略、情绪口径、已知偏差与盲点、主要检索词。
8) **投资建议总结**
   - 基于以上分析的具体投资建议：BUY/HOLD/SELL，并说明理由和风险提示。"""

        # 调用公共的深度研究函数
        research_report = run_deep_research_sync(config, research_query)
        
        # 如果返回的是错误信息，添加具体的分析类型说明
        if research_report.startswith("无法完成深度研究分析"):
            research_report = f"无法完成{ticker}的社交媒体深度研究分析: {research_report[9:]}"

        # 保存研究报告到缓存文件
        try:
            # 确保目录存在
            cache_file_path.parent.mkdir(parents=True, exist_ok=True)
            # 保存报告内容
            with open(cache_file_path, 'w', encoding='utf-8') as f:
                f.write(research_report)
            print(f"社交媒体深度研究报告已保存到: {cache_file_path}")
        except Exception as e:
            print(f"保存缓存文件失败: {e}")
            # 即使保存失败，也继续返回结果

        return {
            "social_media_deep_research_report": research_report,
        }

    return deep_research_analyst_node
