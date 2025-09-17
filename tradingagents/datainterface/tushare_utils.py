import os
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from typing import Annotated
from pathlib import Path
import tushare as ts
import talib
# from .config import DATA_DIR
from tradingagents.dataflows.config import DATA_DIR

# 配置日志
logger = logging.getLogger(__name__)

if os.getenv("TUSHARE_TOKEN") is None:
    from dotenv import load_dotenv
    load_dotenv()

def get_index_daily(symbol: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """
    获取指数日线数据，支持本地缓存
    
    Args:
        symbol: 股票代码
        start_date: 开始日期（YYYYMMDD）
        end_date: 结束日期（YYYYMMDD）
        
    Returns:
        DataFrame: 指数日线数据
    """
    # 构建缓存文件路径
    cache_dir = Path(DATA_DIR) / 'market_data' / 'price_data'
    cache_file = cache_dir / f'{symbol}-tushare-{start_date}-{end_date}.csv'
    
    # 如果缓存文件存在，直接读取
    if cache_file.exists():
        logger.info(f"📁 Loading cached data from: {cache_file}")
        try:
            data = pd.read_csv(cache_file, index_col=0, parse_dates=True)
            return data
        except Exception as e:
            logger.error(f"❌ Error reading cached file {cache_file}: {e}")
            logger.info("🔄 Falling back to API fetch...")
    
    # 缓存文件不存在，从API获取数据
    logger.info(f"🌐 Fetching data from Tushare API for {symbol} ({start_date} to {end_date})")
    data = ts.pro_api().index_daily(
        ts_code=symbol,
        start_date=start_date,
        end_date=end_date
    )

    # 数据预处理
    data = data.sort_values('trade_date')
    data['trade_date'] = pd.to_datetime(data['trade_date'])
    
    # 只保留指定的列
    columns_to_keep = ['trade_date', 'open', 'high', 'low', 'close', 'vol']
    # 检查列是否存在，如果不存在则跳过
    available_columns = [col for col in columns_to_keep if col in data.columns]
    data = data[available_columns]
    
    # 将数值列四舍五入到2位小数
    numeric_columns = ['open', 'high', 'low', 'close']
    for col in numeric_columns:
        if col in data.columns:
            data[col] = data[col].round(2)

    # 将trade_date设为索引
    data = data.set_index('trade_date')

    # 保存到缓存文件
    try:
        # 确保缓存目录存在
        cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 保存数据到CSV文件
        data.to_csv(cache_file)
        logger.info(f"💾 Data cached to: {cache_file}")

    except Exception as e:
        logger.warning(f"⚠️ Failed to cache data to {cache_file}: {e}")
        # 即使缓存失败，也要返回数据
    
    return data


def get_index_stats_indicators_window(
    symbol: Annotated[str, "index symbol (e.g., '000300.SH' for CSI 300)"],
    indicator: Annotated[str, "technical indicator to get the analysis and report of"],
    curr_date: Annotated[
        str, "The current trading date you are trading on, YYYY-mm-dd"
    ],
    look_back_days: Annotated[int, "how many days to look back"],
) -> str:
    """
    获取指数技术指标历史数据窗口
    
    Args:
        symbol: 指数代码，如 '000300.SH' (沪深300)
        indicator: 技术指标名称
        curr_date: 当前交易日期 (YYYY-mm-dd)
        look_back_days: 回溯天数
        online: 是否在线获取数据（目前仅支持True）
        
    Returns:
        str: 格式化的技术指标报告
    """
    
    # 支持的技术指标及其说明
    best_ind_params = {
        # Moving Averages
        "close_50_sma": (
            "50 SMA: A medium-term trend indicator. "
            "Usage: Identify trend direction and serve as dynamic support/resistance. "
            "Tips: It lags price; combine with faster indicators for timely signals."
        ),
        "close_200_sma": (
            "200 SMA: A long-term trend benchmark. "
            "Usage: Confirm overall market trend and identify golden/death cross setups. "
            "Tips: It reacts slowly; best for strategic trend confirmation rather than frequent trading entries."
        ),
        "close_10_ema": (
            "10 EMA: A responsive short-term average. "
            "Usage: Capture quick shifts in momentum and potential entry points. "
            "Tips: Prone to noise in choppy markets; use alongside longer averages for filtering false signals."
        ),
        # MACD Related
        "macd": (
            "MACD: Computes momentum via differences of EMAs. "
            "Usage: Look for crossovers and divergence as signals of trend changes. "
            "Tips: Confirm with other indicators in low-volatility or sideways markets."
        ),
        "macds": (
            "MACD Signal: An EMA smoothing of the MACD line. "
            "Usage: Use crossovers with the MACD line to trigger trades. "
            "Tips: Should be part of a broader strategy to avoid false positives."
        ),
        "macdh": (
            "MACD Histogram: Shows the gap between the MACD line and its signal. "
            "Usage: Visualize momentum strength and spot divergence early. "
            "Tips: Can be volatile; complement with additional filters in fast-moving markets."
        ),
        # Momentum Indicators
        "rsi": (
            "RSI: Measures momentum to flag overbought/oversold conditions. "
            "Usage: Apply 70/30 thresholds and watch for divergence to signal reversals. "
            "Tips: In strong trends, RSI may remain extreme; always cross-check with trend analysis."
        ),
        # Volatility Indicators
        "boll": (
            "Bollinger Middle: A 20 SMA serving as the basis for Bollinger Bands. "
            "Usage: Acts as a dynamic benchmark for price movement. "
            "Tips: Combine with the upper and lower bands to effectively spot breakouts or reversals."
        ),
        "boll_ub": (
            "Bollinger Upper Band: Typically 2 standard deviations above the middle line. "
            "Usage: Signals potential overbought conditions and breakout zones. "
            "Tips: Confirm signals with other tools; prices may ride the band in strong trends."
        ),
        "boll_lb": (
            "Bollinger Lower Band: Typically 2 standard deviations below the middle line. "
            "Usage: Indicates potential oversold conditions. "
            "Tips: Use additional analysis to avoid false reversal signals."
        ),
        "atr": (
            "ATR: Averages true range to measure volatility. "
            "Usage: Set stop-loss levels and adjust position sizes based on current market volatility. "
            "Tips: It's a reactive measure, so use it as part of a broader risk management strategy."
        ),
        # Volume-Based Indicators
        "vwma": (
            "VWMA: A moving average weighted by volume. "
            "Usage: Confirm trends by integrating price action with volume data. "
            "Tips: Watch for skewed results from volume spikes; use in combination with other volume analyses."
        ),
        "mfi": (
            "MFI: The Money Flow Index is a momentum indicator that uses both price and volume to measure buying and selling pressure. "
            "Usage: Identify overbought (>80) or oversold (<20) conditions and confirm the strength of trends or reversals. "
            "Tips: Use alongside RSI or MACD to confirm signals; divergence between price and MFI can indicate potential reversals."
        ),
    }

    if indicator not in best_ind_params:
        raise ValueError(
            f"Indicator {indicator} is not supported. Please choose from: {list(best_ind_params.keys())}"
        )

    # 计算日期范围
    end_date = curr_date
    curr_date_dt = datetime.strptime(curr_date, "%Y-%m-%d")
    before_dt = curr_date_dt - relativedelta(days=look_back_days + 250)  # 额外获取更多数据用于指标计算
    
    # 转换为tushare需要的日期格式 (YYYYMMDD)
    start_date_formatted = before_dt.strftime("%Y%m%d")
    end_date_formatted = curr_date_dt.strftime("%Y%m%d")
    
    try:
        # 获取指数数据
        data = get_index_daily(symbol, start_date_formatted, end_date_formatted)
        
        if data.empty:
            return f"No data available for {symbol} in the specified date range."
        
        # 确保数据按日期排序
        data = data.sort_index()
        
        # 计算技术指标
        indicator_values = _calculate_talib_indicator(data, indicator)
        
        # 筛选出指定时间窗口内的数据
        window_start = curr_date_dt - relativedelta(days=look_back_days)
        mask = (data.index >= window_start) & (data.index <= curr_date_dt)
        
        # 构建结果字符串
        ind_string = ""
        for date, value in indicator_values[mask].items():
            if pd.notna(value):  # 只显示有效值
                ind_string += f"{date.strftime('%Y-%m-%d')}: {value:.4f}\n"
        
        if not ind_string.strip():
            return f"No valid {indicator} data available in the specified time window."
        
        result_str = (
            f"## {indicator} values from {window_start.strftime('%Y-%m-%d')} to {end_date}:\n\n"
            + ind_string
            + "\n"
            + best_ind_params.get(indicator, "No description available.")
        )
        
        return result_str
        
    except Exception as e:
        return f"Error calculating {indicator} for {symbol}: {str(e)}"


def _calculate_talib_indicator(data: pd.DataFrame, indicator: str) -> pd.Series:
    """
    使用 TA-Lib 计算技术指标
    
    Args:
        data: 包含 OHLCV 数据的 DataFrame
        indicator: 指标名称
        
    Returns:
        pd.Series: 指标值序列
    """
    # 提取价格数据
    high = data['high'].astype(float).values
    low = data['low'].astype(float).values
    close = data['close'].astype(float).values
    open_price = data['open'].astype(float).values
    volume = data.get('vol', pd.Series(index=data.index)).fillna(0).astype(float).values
    
    # 根据指标类型计算
    if indicator == "close_50_sma":
        values = talib.SMA(close, timeperiod=50)
    elif indicator == "close_200_sma":
        values = talib.SMA(close, timeperiod=200)
    elif indicator == "close_10_ema":
        values = talib.EMA(close, timeperiod=10)
    elif indicator == "rsi":
        values = talib.RSI(close, timeperiod=14)
    elif indicator == "macd":
        macd_line, _, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        values = macd_line
    elif indicator == "macds":
        _, macd_signal, _ = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        values = macd_signal
    elif indicator == "macdh":
        _, _, macd_hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
        values = macd_hist
    elif indicator == "boll":
        upper, middle, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        values = middle
    elif indicator == "boll_ub":
        upper, _, _ = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        values = upper
    elif indicator == "boll_lb":
        _, _, lower = talib.BBANDS(close, timeperiod=20, nbdevup=2, nbdevdn=2, matype=0)
        values = lower
    elif indicator == "atr":
        values = talib.ATR(high, low, close, timeperiod=14)
    elif indicator == "vwma":
        # TA-Lib 没有直接的 VWMA，我们手动计算
        if len(volume) > 0 and not all(v == 0 for v in volume):
            # 计算 20 期成交量加权移动平均
            period = 20
            values = np.full(len(close), np.nan)
            for i in range(period-1, len(close)):
                price_vol_sum = np.sum(close[i-period+1:i+1] * volume[i-period+1:i+1])
                vol_sum = np.sum(volume[i-period+1:i+1])
                if vol_sum > 0:
                    values[i] = price_vol_sum / vol_sum
        else:
            # 如果没有成交量数据，使用简单移动平均代替
            values = talib.SMA(close, timeperiod=20)
    elif indicator == "mfi":
        if len(volume) > 0 and not all(v == 0 for v in volume):
            values = talib.MFI(high, low, close, volume, timeperiod=14)
        else:
            # 如果没有成交量数据，返回 NaN
            values = np.full(len(close), np.nan)
    else:
        raise ValueError(f"Unsupported indicator: {indicator}")
    
    return pd.Series(values, index=data.index)