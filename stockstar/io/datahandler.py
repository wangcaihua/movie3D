#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
from queue import Queue
from abc import ABCMeta, abstractmethod

logger = logging.getLogger(__name__)


class DataHandler(object):

    __metaclass__ = ABCMeta

    def __init__(self, symbol_list, start_date):
        self.events = Queue()
        self.symbol_list = symbol_list
        self.cur_date = start_date

    @abstractmethod
    def cur_bar(self, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def date_bar(self, date, symbol):
        """
        Returns the last bar updated.
        """
        raise NotImplementedError("Should implement get_latest_bar()")

    @abstractmethod
    def cur_bar_value(self, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def date_bar_value(self, date, symbol, val_type):
        """
        Returns one of the Open, High, Low, Close, Volume or OI from the last bar.
        """
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def latest_bars(self, symbol, n=1):
        """
        Returns the last n bars updated.
        """
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def latest_bars_values(self, symbol, val_type, n=1):
        """
        Returns the last n bar values from the
        latest_symbol list, or N-k if less available.
        """
        raise NotImplementedError("Should implement get_latest_bars_values()")

    @abstractmethod
    def update_bars(self, delta):
        """
        Pushes the latest bars to the bars_queue for each symbol
        in a tuple OHLCVI format: (datetime, open, high, low,
        close, volume, open interest).
        """
        raise NotImplementedError("Should implement update_bars()")
