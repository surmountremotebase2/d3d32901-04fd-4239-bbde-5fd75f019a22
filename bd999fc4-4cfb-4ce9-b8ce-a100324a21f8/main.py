from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import RSI, MACD, EMA
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL"]

    @property
    def assets(self):
        return self.tickers

    @property
    def interval(self):
        # Using daily data for analysis
        return "1day"

    def run(self, data):
        # Initial allocation with no stake
        allocation_dict = {"AAPL": 0}  

        # Extracting the needed historical data
        ohlcv = data["ohlcv"]
        rsi_values = RSI("AAPL", ohlcv, length=14)
        macd_dict = MACD("AAPL", ohlcv, fast=12, slow=26)
        short_ema = EMA("AAPL", ohlcv, length=12)  # Short-term EMA
        long_ema = EMA("AAPL", ohlcv, length=26)  # Long-term EMA

        # Ensure we have enough data for all indicators
        if rsi_values is None or macd_dict is None or short_ema is None or long_ema is None:
            log("Not enough data for indicators")
            return TargetAllocation(allocation_dict)

        # Latest indicator values
        latest_rsi = rsi_values[-1]
        latest_macd = macd_dict['MACD'][-1]
        latest_signal = macd_dict['signal'][-1]
        trend = short_ema[-1] > long_ema[-1]  # Identify the trend

        # Buy condition: Oversold RSI and MACD crossover in an uptrend
        if latest_rsi < 30 and latest_macd > latest_signal and trend:
            allocation_dict["AAPL"] = 1  # Increasing stake in AAPL

        # Sell condition: Overbought RSI or MACD crossunder indicating downward momentum
        elif latest_rsi > 70 or (latest_macd < latest_signal and not trend):
            allocation_dict["AAPL"] = 0  # No stake in AAPL

        # Update the log with our decision
        log(f"Allocation for AAPL: {allocation_dict['AAPL']}")

        return TargetAllocation(allocation_dict)