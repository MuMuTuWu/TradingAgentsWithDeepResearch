# %%
import os
import time
from pathlib import Path
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv
load_dotenv()

# forward propagate
ticker = "000300.SH"
current_date = "2025-09-19"

# Create a custom config
config = DEFAULT_CONFIG.copy()
config["llm_provider"] = "openai"
config["deep_think_llm"] = "gpt-5-mini"
config["quick_think_llm"] = "gpt-5-nano"
config["backend_url"] = os.environ.get("BASE_URL")
config["max_debate_rounds"] = 1
config["max_risk_discuss_rounds"] = 1
config["max_recur_limit"] = 100
config["online_tools"] = True
config["debug"] = False

# 创建 results_dir 目录
results_dir = Path(config['results_dir']) / ticker / current_date
results_dir.mkdir(parents=True, exist_ok=True)

# Initialize with custom config, and create trading_graph
ta = TradingAgentsGraph(
    # selected_analysts=["market", "social", "news", "fundamentals"],
    selected_analysts=["market"],
    selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research", "macro_deep_research"],
    debug=config["debug"],
    config=config
)

# %%
# 输出 mermaid 代码到文件，并保存到 results_dir 目录
mermaid_file_path = results_dir / 'trading_graph.mmd'
with open(mermaid_file_path, 'w', encoding='utf-8') as f:
    f.write(ta.graph.get_graph().draw_mermaid())

print(f"Mermaid 代码已保存到: {mermaid_file_path}")
print(f"你可以将此文件内容复制到 mermaid 编辑器中查看图表")

# %%
# 开始计时
start_time = time.time()
final_state, decision = ta.propagate(ticker, current_date)
# 结束计时并打印用时
end_time = time.time()
execution_time = end_time - start_time
print(f"ta.propagate() 执行完成 - 时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(end_time))}")
print(f"总执行用时: {execution_time:.2f} 秒 ({execution_time/60:.2f} 分钟)")
print(f"决策结果: {decision}")

# 保存 market_report
if 'market_report' in final_state:
    market_report_path = results_dir / 'market_report.md'
    with open(market_report_path, 'w', encoding='utf-8') as f:
        f.write(final_state['market_report'])
    print(f"Market report saved to: {market_report_path}")

# 保存 final_trade_decision
if 'final_trade_decision' in final_state:
    final_decision_path = results_dir / 'final_trade_decision.md'
    with open(final_decision_path, 'w', encoding='utf-8') as f:
        f.write(final_state['final_trade_decision'])
    print(f"Final trade decision saved to: {final_decision_path}")

# 保存 research_report
if 'research_report' in final_state:
    research_report_path = results_dir / 'research_report.md'
    with open(research_report_path, 'w', encoding='utf-8') as f:
        f.write(final_state['research_report'])
    print(f"Research report saved to: {research_report_path}")

# 保存 final_state 到指定路径
with open(results_dir / "final_state.json", "w", encoding="utf-8") as f:
    import json
    json.dump(final_state, f, indent=2, ensure_ascii=False, default=str)

# # Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns

# %%
