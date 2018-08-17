#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np

import logging

from stockstar.event import *
from stockstar.event import Signal
from .strategy import Strategy
from stockstar.portfolio import Portfolio
from stockstar.exceptions import DataNotAvailable

__all__ = ['MACStrategy']

logger = logging.getLogger(__name__)


class MACStrategy(Strategy):    # Moving Average Cross

    def __init__(self, portfolio: Portfolio, short_window: int=10, long_window: int=20):
        super(MACStrategy, self).__init__(portfolio)
        self.short_window = short_window
        self.long_window = long_window
        self.costpos = portfolio.costpos
        self.strategy_id = 1

    def send_signals(self, event: MarketEvent):
        date = event.date

        for symbol in self.bars.symbol_list:
            try:
                latest_bars = self.bars.latest_bars_values(symbol, "close", n=self.long_window)

                assert latest_bars is not None and len(latest_bars) > 0

                short_sma = np.mean(latest_bars[-self.short_window:])
                long_sma = np.mean(latest_bars[-self.long_window:])

                strength = 1.0

                if short_sma > long_sma and self.costpos.isout(symbol):
                    signal = Signal(symbol, SignalType.OPEN_LONG, strength)
                elif short_sma > long_sma and self.costpos.islong(symbol):
                    signal = Signal(symbol, SignalType.LONG_ADDING, strength)
                elif short_sma > long_sma and self.costpos.isshort(symbol):
                    signal = Signal(symbol, SignalType.EXIT, strength)
                elif short_sma < long_sma and self.costpos.isout(symbol):
                    signal = Signal(symbol, SignalType.OPEN_SHORT, strength)
                elif short_sma < long_sma and self.costpos.isshort(symbol):
                    signal = Signal(symbol, SignalType.SHORT_ADDING, strength)
                else:  # short_sma < long_sma and self.costpos.islong(symbol)
                    signal = Signal(symbol, SignalType.EXIT, strength)

                self.events.put(SimpleSignalEvent(self.strategy_id, date, signal))
            except DataNotAvailable as e:
                logger.info(e.msg)
            except AssertionError as _:
                logger.info("The data is available, but it's empty!")

    def place_order(self, event: SimpleSignalEvent):
        symbol, signal_type, mkt_quantity = event.symbol, event.signal_type, 100
        quantity, max_quantity = self.costpos.getposition(symbol), 20 * mkt_quantity
        date, cash = event.date, self.costpos.cash

        order = None
        if signal_type == SignalType.OPEN_LONG and cash > 0:
            order = OrderEvent(date, symbol, OrderType.MKT, mkt_quantity, Direction.OPEN_BUY)
        elif signal_type == SignalType.LONG_ADDING and cash > 0 and 0 < quantity < max_quantity:
            order = OrderEvent(date, symbol, OrderType.MKT, mkt_quantity, Direction.ADDING_BUY)
        elif signal_type == SignalType.OPEN_SHORT and cash > 0:
            order = OrderEvent(date, symbol, OrderType.MKT, mkt_quantity, Direction.OPEN_SELL)
        elif signal_type == SignalType.SHORT_ADDING and cash > 0 and 0 < -quantity < max_quantity:
            order = OrderEvent(date, symbol, OrderType.MKT, mkt_quantity, Direction.ADDING_SEL)
        elif signal_type == SignalType.EXIT and quantity > 0:
            order = OrderEvent(date, symbol, OrderType.MKT, quantity, Direction.EXIT_SEL)
        elif signal_type == SignalType.EXIT and quantity < 0:
            order = OrderEvent(date, symbol, OrderType.MKT, -quantity, Direction.EXIT_BUY)
        else:
            if cash <= 0:
                logger.info("No OrderEvent send, because no cash left !")
            elif cash > 0 and abs(quantity) == max_quantity:
                logger.info("No OrderEvent send, because the quantity is up to max !")
            else:
                logger.info("No OrderEvent send, for nuknown reason !")

        if order is not None:
            self.events.put(order)
