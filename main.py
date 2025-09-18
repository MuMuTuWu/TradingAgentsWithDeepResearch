# %%
import os
from tradingagents.graph.trading_graph import TradingAgentsGraph
from tradingagents.default_config import DEFAULT_CONFIG

from dotenv import load_dotenv
load_dotenv()

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

# Initialize with custom config
ta = TradingAgentsGraph(
    selected_analysts=["market"],
    selected_deep_researcher=["social_media_deep_research", "news_deep_research", "fundamentals_deep_research"],
    debug=config["debug"],
    config=config
)

# %%
from IPython.display import Image, display
Image(ta.graph.get_graph().draw_mermaid_png())

# %%
# # forward propagate
final_state, decision = ta.propagate("000300.SH", "2025-09-12")
print(decision)

with open("final_state.json", "w", encoding="utf-8") as f:
    import json
    json.dump(final_state, f, indent=2, ensure_ascii=False, default=str)

# %%
# # Memorize mistakes and reflect
# ta.reflect_and_remember(1000) # parameter is the position returns
# %%
