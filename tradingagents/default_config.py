import os
from pathlib import Path

# 获取当前文件所在目录作为项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

DEFAULT_CONFIG = {
    "project_dir": PROJECT_ROOT,
    "results_dir": PROJECT_ROOT / "results",
    "data_dir": PROJECT_ROOT / "tradingagents" / "datainterface" / "data",
    "data_cache_dir": PROJECT_ROOT / "tradingagents" / "datainterface" / "data_cache",
    # LLM settings
    "llm_provider": "openai",
    "deep_think_llm": "gpt-5-mini",
    "quick_think_llm": "gpt-5-nano",
    "backend_url": "https://api.openai.com/v1",
    # Debate and discussion settings
    "max_debate_rounds": 1,
    "max_risk_discuss_rounds": 1,
    "max_recur_limit": 100,
    # Tool settings
    "online_tools": True,
    # Output Debug Messages
    "debug": True,
}
