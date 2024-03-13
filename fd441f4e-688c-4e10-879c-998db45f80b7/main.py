from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import MACD
from surmount.logging import log

class TradingStrategy(Strategy):
    """
    A momentum-based trading strategy using the Moving Average Convergence Divergence (MACD).
    The strategy buys an asset when the MACD line crosses above the signal line, indicating an uptrend,
    and sells when the MACD line crosses below the signal line, indicating a downtrend.
    """
    
    def __init__(self):
        self.tickers = ["SPY"]
    
    @property
    def assets(self):
        """
        Specifies the assets to be traded.
        """
        return self.tickers

    @property
    def interval(self):
        """
        The data interval to be used for the strategy. Using '1day' for daily trend analysis.
        """
        return "1day"

    def run(self, data):
        """
        Executes the trading strategy.

        :param data: The market data needed to compute the MACD.
        """
        allocation_dict = {}
        for ticker in self.tickers:
            # Calculate the MACD and its signal for the given ticker
            macd_data = MACD(ticker, data["ohlcv"], fast=12, slow=26)
            macd_line = macd_data["MACD"]
            signal_line = macd_data["signal"]
            
            # Check if data available
            if len(macd_line) == 0 or len(signal_line) == 0:
                log(f"No sufficient data for {ticker}. Skipping.")
                continue

            # Trading signals based on MACD crossover
            if macd_line[-1] > signal_line[-1] and macd_line[-2] < signal_line[-2]:  # Golden cross detected
                log(f"Buying {ticker} based on MACD crossover.")
                allocation_dict[ticker] = 1.0  # Full allocation to this ticker
            elif macd_line[-1] < signal_line[-1] and macd_line[-2] > signal_line[-2]:  # Death cross detected
                log(f"Selling {ticker} based on MACD crossover.")
                allocation_dict[ticker] = 0.0  # No allocation to this ticker
            else:
                log(f"No trade signal for {ticker}. Holding position.")
                # Allocate based on existing position to hold or no allocation if no position exists
                allocation_dict[ticker] = data["holdings"].get(ticker, 0.0)

        return TargetAllocation(allocation_dict)