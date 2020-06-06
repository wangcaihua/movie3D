import datetime
import numpy as np
import pandas as pd

from quant.core.event import SignalEvent
from quant.core.strategy import Strategy


class MovingAverageCrossStrategy(Strategy):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    def __init__(self, data_handler, events, short_window=100, long_window=400):
        """
        Initialises the buy and hold strategy.

        Parameters:
        data_handler - The DataHandler object that provides bar information
        events - The Event Queue object.
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        self.data_handler = data_handler
        self.symbol_list = self.data_handler.symbol_list
        self.events = events
        self.short_window = short_window
        self.long_window = long_window

        # Set to True if a symbol is in the market
        self.bought = {symbol:'OUT'  for symbol in self.symbol_list}


    def on_signal(self, event):
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.    

        Parameters
        event - A MarketEvent object. 
        """
        if event.type == 'MARKET':
            for symbol in self.symbol_list:
                data_handler = self.data_handler.get_latest_data_handler_values(symbol, "close", N=self.long_window)               

                if data_handler is not None and data_handler != []:
                    short_sma = np.mean(data_handler[-self.short_window:])
                    long_sma = np.mean(data_handler[-self.long_window:])

                    dt = self.data_handler.get_latest_bar_datetime(symbol)
                    sig_dir = ""
                    strength = 1.0
                    strategy_id = 1

                    if short_sma > long_sma and self.bought[symbol] == "OUT":
                        sig_dir = 'LONG'
                        signal = SignalEvent(strategy_id, symbol, dt, sig_dir, strength)
                        self.events.put(signal)
                        self.bought[symbol] = 'LONG'

                    elif short_sma < long_sma and self.bought[symbol] == "LONG":
                        sig_dir = 'EXIT'
                        signal = SignalEvent(strategy_id, symbol, dt, sig_dir, strength)
                        self.events.put(signal)
                        self.bought[symbol] = 'OUT'
