# Deep Research集成方案实现文档

## 概述

本文档描述了如何将`open_deep_research`作为`tradingagents`的一个分析师节点使用。集成后，您可以在交易分析工作流中使用强大的深度研究能力。

## 实现内容

### 1. 新增文件

#### `tradingagents/agents/analysts/deep_research_analyst.py`
- 实现了`create_deep_research_analyst`函数
- 基于`open_deep_research/main.py`的配置和prompt结构
- 支持异步执行和错误处理
- 针对投资交易场景优化了研究query

### 2. 修改的文件

#### `tradingagents/agents/__init__.py`
- 添加了`create_deep_research_analyst`的导入和导出

#### `tradingagents/agents/utils/agent_states.py`
- 在`AgentState`中添加了`deep_research_report`字段

#### `tradingagents/graph/conditional_logic.py`
- 添加了`should_continue_deep_research`方法

#### `tradingagents/graph/setup.py`
- 在`setup_graph`方法中添加了对`deep_research`分析师的支持
- 更新了文档字符串

#### `tradingagents/graph/trading_graph.py`
- 在`_create_tool_nodes`中添加了`deep_research`工具节点（空节点）
- 在状态日志记录中添加了`deep_research_report`字段

## 使用方法

### 1. 基本使用

```python
from tradingagents.graph import TradingAgentsGraph

# 只使用深度研究分析师
graph = TradingAgentsGraph(
    selected_analysts=["deep_research"],
    debug=False
)

# 执行分析
final_state, decision = graph.propagate("AAPL", "2024-01-15")
print(f"投资决策: {decision}")
print(f"深度研究报告: {final_state['deep_research_report']}")
```

### 2. 与其他分析师结合使用

```python
# 结合多种分析师
graph = TradingAgentsGraph(
    selected_analysts=["market", "news", "deep_research"],
    debug=False
)

final_state, decision = graph.propagate("TSLA", "2024-01-15")
```

### 3. 分析中国股票/指数

```python
# 分析沪深300指数
graph = TradingAgentsGraph(
    selected_analysts=["deep_research"],
    debug=False
)

final_state, decision = graph.propagate("000300.SH", "2024-01-15")
```

## 配置说明

### Deep Research配置

deep_research_analyst使用以下配置（基于`open_deep_research/main.py`）：

```python
config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
        "max_structured_output_retries": 3,
        "allow_clarification": False,
        "max_concurrent_research_units": 5,
        "search_api": "tavily",
        "max_researcher_iterations": 6,
        "max_react_tool_calls": 10,
        "summarization_model": "openai:gpt-5-mini",
        "summarization_model_max_tokens": 8192,
        "max_content_length": 50000,
        "research_model": "openai:gpt-5-mini",
        "research_model_max_tokens": 10000,
        "compression_model": "openai:gpt-5-mini",
        "compression_model_max_tokens": 8192,
        "final_report_model": "openai:gpt-5-mini",
        "final_report_model_max_tokens": 10000,
        "mcp_config": None,
        "mcp_prompt": None,
    }
}
```

### 研究Query结构

针对投资交易优化的研究query包含以下部分：

1. **研究目标**：公众讨论、情绪变化、关键事件、催化因素等
2. **信息来源**：社交媒体、新闻、官方数据、多语言来源
3. **搜索流程**：检索策略、样本采集、证据链构建
4. **质量分级**：来源分级（A/B/C）、可信度标签
5. **情绪分析**：-2到+2的情绪刻度、主题框架
6. **输出结构**：投资结论、时间线、情绪综述、投资建议等

## 技术特性

### 1. 异步执行
- 支持在现有事件循环中运行
- 包含超时机制（5分钟）
- 完整的错误处理

### 2. 错误处理
- 网络连接错误处理
- API配置错误处理
- 异步执行错误处理

### 3. 集成特性
- 遵循tradingagents的分析师模式
- 无缝集成到现有工作流
- 支持与其他分析师组合使用

## 依赖要求

### 必需依赖
- `open_deep_research` 模块
- `asyncio`
- `uuid`
- `concurrent.futures`（用于异步执行）

### API要求
- Tavily搜索API（或其他配置的搜索API）
- OpenAI API（用于GPT-5-mini模型）

## 环境设置

### 1. 环境变量
确保设置了以下环境变量：
```bash
export OPENAI_API_KEY="your_openai_api_key"
export TAVILY_API_KEY="your_tavily_api_key"
```

### 2. 依赖安装
确保安装了所有必需的依赖包。

## 示例文件

参考 `example_deep_research_usage.py` 文件，其中包含：

1. **配置测试**：验证环境设置是否正确
2. **基本使用示例**：只使用深度研究分析师
3. **组合使用示例**：结合传统分析师
4. **中国市场示例**：分析中国股票/指数

## 运行示例

```bash
# 运行示例
python example_deep_research_usage.py

# 或使用uv
uv run python example_deep_research_usage.py
```

## 注意事项

### 1. 性能考虑
- deep_research执行时间较长（通常2-5分钟）
- 建议在需要深度分析时使用
- 可以通过调整配置参数优化性能

### 2. 成本考虑
- 使用多个LLM调用和搜索API
- 建议合理设置token限制
- 监控API使用量

### 3. 错误处理
- 网络不稳定时可能失败
- 建议实施重试机制
- 检查API配额和限制

## 故障排除

### 常见问题

1. **导入错误**
   - 确保`open_deep_research`模块在Python路径中
   - 检查所有依赖是否正确安装

2. **API错误**
   - 验证API密钥是否正确设置
   - 检查API配额是否充足

3. **异步执行错误**
   - 确保Python版本支持asyncio
   - 检查事件循环配置

4. **超时错误**
   - 调整超时设置
   - 检查网络连接稳定性

### 调试建议

1. 启用debug模式：`debug=True`
2. 检查日志输出
3. 逐步测试各个组件
4. 使用配置测试功能

## 总结

通过这个集成方案，您可以：

- 在tradingagents中使用open_deep_research的强大功能
- 获得更深入的市场研究和分析
- 保持与现有工作流的兼容性
- 灵活配置和使用不同的分析师组合

这个实现遵循了tradingagents的架构模式，确保了良好的可维护性和扩展性。
