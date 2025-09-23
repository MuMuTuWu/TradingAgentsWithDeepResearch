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
        
        # 构建针对A股指数的一周信息收集型深度研究查询（仅采集与基础筛选）
        research_query = f"""收集 {ticker} 指数一周内的基本面信息

> 时间范围：**{current_date}前一周**（仅纳入该时间窗口内“发生/发布”的信息）"""

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
