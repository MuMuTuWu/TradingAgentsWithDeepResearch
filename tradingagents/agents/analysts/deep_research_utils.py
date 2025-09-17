import asyncio
import uuid
from langgraph.checkpoint.memory import MemorySaver
from open_deep_research import deep_researcher_builder


async def run_deep_research(config, research_query):
    """
    运行深度研究分析的公共函数
    
    Args:
        config: 配置字典，需要包含 'debug' 键
        research_query: 研究查询字符串
        
    Returns:
        str: 研究报告内容或错误信息
    """
    # 配置deep research，参考main.py中的配置
    graph = deep_researcher_builder.compile(checkpointer=MemorySaver(), debug=config['debug'])
    research_config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "max_structured_output_retries": 3,
            "allow_clarification": False,
            "max_concurrent_research_units": 5,
            "search_api": "tavily",
            "max_researcher_iterations": 6,
            "max_researcher_iterations": 3,
            # "max_react_tool_calls": 10,
            "max_react_tool_calls": 3,
            "summarization_model": "openai:gpt-5-nano",
            "summarization_model_max_tokens": 8192,
            "max_content_length": 50000,
            "research_model": "openai:gpt-5-nano",
            "research_model_max_tokens": 10000,
            "compression_model": "openai:gpt-5-nano",
            "compression_model_max_tokens": 8192,
            "final_report_model": "openai:gpt-5-nano",
            "final_report_model_max_tokens": 10000,
            "mcp_config": None,
            "mcp_prompt": None,
        }
    }
    
    inputs = {
        "messages": [
            {"role": "user", "content": research_query}
        ]
    }

    try:
        result_state = await graph.ainvoke(inputs, research_config)
        return result_state.get("final_report", "深度研究报告生成失败")
    except Exception as e:
        return f"深度研究分析过程中出现错误: {str(e)}"


def run_deep_research_sync(config, research_query, timeout=300):
    """
    同步调用深度研究分析的辅助函数
    
    Args:
        config: 配置字典，需要包含 'debug' 键
        research_query: 研究查询字符串
        timeout: 超时时间（秒），默认5分钟
        
    Returns:
        str: 研究报告内容或错误信息
    """
    try:
        # 尝试获取当前事件循环
        try:
            loop = asyncio.get_running_loop()
            # 如果已经有运行中的事件循环，创建任务
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(asyncio.run, run_deep_research(config, research_query))
                return future.result(timeout=timeout)
        except RuntimeError:
            # 没有运行中的事件循环，直接运行
            return asyncio.run(run_deep_research(config, research_query))
    except Exception as e:
        # 如果异步调用失败，返回错误信息
        return f"无法完成深度研究分析: {str(e)}\n请检查网络连接、API配置和环境依赖。"
