#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from abc import ABCMeta, abstractmethod


class DataHandler(object, metaclass=ABCMeta):
    """
    DataHandler is an abstract base class providing an interface for
    all subsequent (inherited) data handlers (both live and historic).

    The goal of a (derived) DataHandler object is to output a generated
    set of bars (OHLCVI) for each symbol requested. 

    This will replicate how a live strategy would function as current
    market data would be sent "down the pipe". Thus a historic and live
    system will be treated identically by the rest of the backtesting suite.
    """

    def __init__(self, symbol_list, events, start_date):
        self.events = events
        self.start_date = start_date
        self.symbol_list = symbol_list
        self.snapshot: pd.DataFrame = None
        self.hist_snapshots = []

        self.tfmt = '%Y-%m-%d'
        self.cur_datetime: str = start_date
        self.continue_backtest: bool = True

    @abstractmethod
    def get_mkt_snapshot(self):
        """
        Returns the snapshot for the market
        """
        raise NotImplementedError("Should implement get_mkt_snapshot()")

    def get_latest_bar(self, symbol) -> pd.Series:
        return self.snapshot.loc[symbol]

    def get_latest_datetime(self):
        """
        Returns a Python datetime object for the last bar.
        """
        return self.cur_datetime

    def get_latest_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        assert val_type in self.snapshot.columns
        return self.snapshot.loc[symbol, val_type]

    @abstractmethod
    def get_latest_bars(self, symbol, n=1) -> pd.DataFrame:
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bars_values(self, symbol, val_type, n=1):
        """
        Returns the last N bar values from the 
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low, 
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")
