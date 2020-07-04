#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from typing import Optional
from enum import Enum
from abc import ABCMeta, abstractmethod

SField = Enum('SField', ('name', 'lot_size', 'stock_type', 'listing_date', 'plate_name', 'plate_id'))
KField = Enum('KField', ("code", "time_key", "open", "close", "high", "low", "pe_ratio", "atr",
                         "turnover_rate", "volume", "turnover", "change_rate", "last_close"))


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
        self.snapshot: Optional[pd.DataFrame] = None

        self.tfmt = '%Y-%m-%d'
        self.cur_datetime: str = start_date
        self.continue_backtest: bool = True

    @abstractmethod
    def update_snapshot(self):
        """
        Returns the snapshot for the market
        """
        raise NotImplementedError("Should implement get_mkt_snapshot()")

    def get_curr_bar(self, symbol) -> pd.Series:
        return self.snapshot.loc[symbol]

    def get_curr_bar_value(self, symbol, field: KField):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        return self.snapshot.loc[symbol, field.name]

    @abstractmethod
    def get_hist_bars(self, symbol: str, n: int) -> pd.DataFrame:
        """
        Returns the last N bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_hist_bars_values(self, symbol: str, val_type: KField, n: int) -> pd.Series:
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
