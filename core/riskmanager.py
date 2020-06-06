#!/usr/bin/python
# -*- coding: utf-8 -*-


import queue
import datetime
import numpy as np
import pandas as pd
from typing import Union, List
from abc import ABCMeta, abstractmethod

from quant.core.portfolio import Portfolio
from quant.core.datahandler import DataHandler
from quant.core.event import SignalEvent, OrderEvent


class RiskManager(object, metaclass=ABCMeta):
    def __init__(self, portfolio: Portfolio):
        self.portfolio: Portfolio = portfolio
        self.events: queue.Queue = portfolio.events
        self.symbol_list: List[str] = portfolio.symbol_list
        self.data_handler: DataHandler = portfolio.data_handler

    def on_signal(self, event: SignalEvent):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        signal - The tuple containing Signal information.
        """
        order = None

        symbol = event.symbol
        direction = event.signal_type
        strength = event.strength

        mkt_quantity = 100
        cur_quantity = self.portfolio.current_positions[symbol]
        order_type = 'MKT'

        if direction == 'LONG' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'BUY')
        if direction == 'SHORT' and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, 'SELL')

        if direction == 'EXIT' and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'SELL')
        if direction == 'EXIT' and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), 'BUY')
        return order
