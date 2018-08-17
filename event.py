#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function
from enum import Enum, unique

__all__ = ["OrderType", "SignalType", "Direction", "Signal", "BatchSignalEvent",
           "Event", "MarketEvent", "SimpleSignalEvent", "OrderEvent", "FillEvent"]


@unique
class OrderType(Enum):
    MKT = 1
    SIMU = 2


@unique
class SignalType(Enum):
    OPEN_LONG = 1
    OPEN_SHORT = 2
    LONG_ADDING = 3
    SHORT_ADDING = 4
    LONG_LIGHTEN = 5
    SHORT_LIGHTEN = 6
    EXIT = 7


@unique
class Direction(Enum):
    OPEN_SELL = 1
    OPEN_BUY = 2
    ADDING_BUY = 3
    ADDING_SEL = 4
    LIGHTEN_BUY = 5
    LIGHTEN_SEL = 6
    EXIT_BUY = 7
    EXIT_SEL = 8


class Signal(object):
    def __init__(self, symbol, signal_type, strength):
        self.symbol = symbol
        self.signal_type = signal_type
        self.strength = strength


class Event(object):
    def __init__(self, date: str):
        self.date = date

    @classmethod
    def ismarket(cls, event) -> bool:
        return isinstance(event, MarketEvent)

    @classmethod
    def issignal(cls, event) -> bool:
        simple = isinstance(event, SimpleSignalEvent)
        batch = isinstance(event, BatchSignalEvent)
        return simple or batch

    @classmethod
    def isorder(cls, event) -> bool:
        return isinstance(event, OrderEvent)

    @classmethod
    def isfill(cls, event) -> bool:
        return isinstance(event, FillEvent)


class MarketEvent(Event):
    def __init__(self, date: str):
        super(MarketEvent, self).__init__(date)


class SimpleSignalEvent(Event):
    def __init__(self, strategy_id: int, date: str, signal: Signal):
        super(SimpleSignalEvent, self).__init__(date)
        self.symbol = signal.symbol
        self.strategy_id = strategy_id
        self.signal_type = signal.signal_type
        self.strength = signal.strength


class BatchSignalEvent(Event):
    def __init__(self, strategy_id: int, date: str, signal_list: list):
        super(BatchSignalEvent, self).__init__(date)
        self.strategy_id = strategy_id
        self.signal_list = signal_list


class OrderEvent(Event):
    def __init__(self, date: str, symbol: str, order_type: OrderType,
                 quantity: float, direction: Direction):
        super(OrderEvent, self).__init__(date)
        self.symbol = symbol
        self.order_type = order_type
        self.quantity = quantity
        self.direction = direction

    def print_order(self):
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
            (self.symbol, self.order_type, self.quantity, self.direction)
        )


class FillEvent(Event):
    def __init__(self, date: str, symbol: str, exchange: float, quantity: float,
                 direction: Direction):
        super(FillEvent, self).__init__(date)
        self.symbol = symbol
        self.exchange = exchange
        self.quantity = quantity
        self.direction = direction

    @property
    def fee(self) -> float:
        full_cost = 1.3
        if self.quantity <= 500:
            return max(full_cost, 0.013 * self.quantity)
        else:  # Greater than 500
            return max(full_cost, 0.008 * self.quantity)
