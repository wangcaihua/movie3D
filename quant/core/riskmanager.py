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

    @abstractmethod
    def on_signal(self, event: SignalEvent):
        """
        Simply files an Order object as a constant quantity
        sizing of the signal object, without risk management or
        position sizing considerations.

        Parameters:
        event - The tuple containing Signal information.
        """
        raise NotImplementedError("Should implement on_signal(event: SignalEvent)")

