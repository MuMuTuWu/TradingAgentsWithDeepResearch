# 更新后的Deep Research分析师使用指南

## 🎯 重构完成

原有的 `deep_research_analyst` 已被重构为三个专门化的深度研究分析师：

1. **`social_media_deep_research_analyst`** - 社交媒体深度研究
2. **`news_deep_research_analyst`** - 新闻深度研究  
3. **`fundamentals_deep_research_analyst`** - 基本面深度研究

## 📋 新的分析师特性

### Social Media Deep Research Analyst
- **专注领域**：社交媒体情绪、舆论分析、KOL观点
- **Research Query**：保持与原有 `deep_research_analyst` 完全相同
- **输出字段**：`social_media_deep_research_report`

### News Deep Research Analyst  
- **专注领域**：新闻事件、政策动态、媒体报道分析
- **Research Query**：专门针对新闻和事件的深度研究
- **输出字段**：`news_deep_research_report`
- **重点分析**：
  - 重大新闻事件时间线
  - 政策监管动态影响
  - 媒体可信度评估
  - 新闻事件的投资影响

### Fundamentals Deep Research Analyst
- **专注领域**：财务数据、基本面分析、估值建模
- **Research Query**：专门针对基本面和财务的深度研究
- **输出字段**：`fundamentals_deep_research_report`
- **重点分析**：
  - 财务健康度评估
  - 盈利能力和成长性分析
  - 估值合理性分析
  - 同业对比和投资价值评估

## 🚀 使用方法

### 1. 单独使用某个深度研究分析师

```python
from tradingagents.graph import TradingAgentsGraph

# 使用社交媒体深度研究
graph = TradingAgentsGraph(
    selected_analysts=["social_media_deep_research"]
)

# 使用新闻深度研究
graph = TradingAgentsGraph(
    selected_analysts=["news_deep_research"]
)

# 使用基本面深度研究
graph = TradingAgentsGraph(
    selected_analysts=["fundamentals_deep_research"]
)
```

### 2. 组合使用多个深度研究分析师

```python
# 组合新闻和基本面深度研究
graph = TradingAgentsGraph(
    selected_analysts=["news_deep_research", "fundamentals_deep_research"]
)

# 使用全部三个深度研究分析师
graph = TradingAgentsGraph(
    selected_analysts=[
        "social_media_deep_research", 
        "news_deep_research", 
        "fundamentals_deep_research"
    ]
)
```

### 3. 与传统分析师结合

```python
# 结合传统分析师和深度研究分析师
graph = TradingAgentsGraph(
    selected_analysts=[
        "market",  # 传统市场分析师
        "social",  # 传统社交媒体分析师
        "news_deep_research",  # 新闻深度研究
        "fundamentals_deep_research"  # 基本面深度研究
    ]
)
```

### 4. 获取分析结果

```python
final_state, decision = graph.propagate("AAPL", "2024-01-15")

# 获取不同类型的深度研究报告
social_report = final_state.get("social_media_deep_research_report", "")
news_report = final_state.get("news_deep_research_report", "")
fundamentals_report = final_state.get("fundamentals_deep_research_report", "")

print(f"投资决策: {decision}")
print(f"社交媒体深度研究: {social_report[:300]}...")
print(f"新闻深度研究: {news_report[:300]}...")
print(f"基本面深度研究: {fundamentals_report[:300]}...")
```

## 🔧 配置说明

所有深度研究分析师使用相同的配置参数（基于 `open_deep_research/main.py`）：

```python
research_config = {
    "configurable": {
        "thread_id": str(uuid.uuid4()),
        "max_structured_output_retries": 3,
        "allow_clarification": False,
        "max_concurrent_research_units": 5,
        "search_api": "tavily",
        "max_researcher_iterations": 3,
        "max_react_tool_calls": 3,
        "summarization_model": "openai:gpt-5-nano",
        "research_model": "openai:gpt-5-nano",
        "compression_model": "openai:gpt-5-nano",
        "final_report_model": "openai:gpt-5-nano",
        # ... 其他配置参数
    }
}
```

## 📊 变更摘要

### 新增文件
- `tradingagents/agents/analysts/social_media_deep_research_analyst.py`
- `tradingagents/agents/analysts/news_deep_research_analyst.py`
- `tradingagents/agents/analysts/fundamentals_deep_research_analyst.py`

### 删除文件
- `tradingagents/agents/analysts/deep_research_analyst.py`

### 修改文件
- `tradingagents/agents/__init__.py` - 更新导入和导出
- `tradingagents/agents/utils/agent_states.py` - 更新状态字段
- `tradingagents/graph/conditional_logic.py` - 添加新的条件判断方法
- `tradingagents/graph/setup.py` - 支持新的分析师类型
- `tradingagents/graph/trading_graph.py` - 更新工具节点和状态记录
- `example_deep_research_usage.py` - 更新使用示例

### 新增状态字段
- `social_media_deep_research_report`
- `news_deep_research_report` 
- `fundamentals_deep_research_report`

### 移除内容
- 原有的 `deep_research_report` 字段
- 原有的 `deep_research` 分析师类型
- 所有向后兼容性代码

## ✅ 实施完成

重构已完成，现在您可以使用三个专门化的深度研究分析师来进行更精准的投资分析。每个分析师都有其专业领域，可以单独使用或组合使用，为投资决策提供更深入和专业的分析支持。
