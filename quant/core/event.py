#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Dict, List, Union

import logging

logger = logging.getLogger(__name__)

__all__ = ['DataEvent', 'MarketEvent', 'Signal', 'SignalEvent', 'OrderEvent', 'FillEvent']


class Event(object):
    """
    Event is base class providing an interface for all subsequent
    (inherited) events, that will trigger further events in the
    trading infrastructure.
    """
    pass


class DataEvent(Event):
    def __init__(self, timestamp: datetime = None):
        """
        Initialises the DataEvent.
        """
        if timestamp is None:
            timestamp = datetime.today()
        self.timestamp = timestamp


class MarketEvent(Event):
    """
    Handles the event of receiving a new market update with
    corresponding bars.
    """

    def __init__(self, timestamp: datetime = None):
        """
        Initialises the MarketEvent.
        """
        if timestamp is None:
            timestamp = datetime.today()

        self.timestamp: datetime = timestamp


class Signal(object):
    OpenLong = "OpenLong"
    OpenShort = "OpenShort"
    Extend = "Extend"
    Lighten = "Lighten"
    Close = "Close"
    SignalTypes = {
        OpenLong: 0,
        OpenShort: 0,
        Extend: 2,
        Lighten: 2,
        Close: 4
    }

    def __init__(self, symbol: str, signal_type: str, confidence: float, attr: dict = None):
        assert signal_type in Signal.SignalTypes

        self.symbol: str = symbol
        self.signal_type: str = signal_type
        self.confidence: float = confidence
        self.attr = attr

    @classmethod
    def cmp_key(cls, signal) -> float:
        return cls.SignalTypes[signal.signal_type] + signal.confidence


class SignalEvent(Event):
    """
    用于描述股票买卖信号. 做多还是做空, 信号置信度. 由策略发出,
    信号中不包括买卖的数量, 因为数量与lot_size, 仓位, 风险控制相关
    """

    def __init__(self, timestamp: datetime, signals: List[Signal]):
        """
        Initialises the SignalEvent.

        Parameters:
        strategy_id - The unique ID of the strategy sending the signal.
        symbol - The ticker symbol, e.g. 'GOOG'.
        datetime - The timestamp at which the signal was generated.
        signal_type - 做空或做多, 即'LONG' 或 'SHORT'.
        strength - 用于标识信号的强弱, 也可以理解为信号的置信度.
        """
        self.timestamp: datetime = timestamp
        self.signals: List[Signal] = signals


class OrderEvent(Event):
    """
    Handles the event of sending an Order to an execution system.
    The order contains a symbol (e.g. GOOG), a type (market or limit),
    quantity and a direction.
    """
    MKT = 'MKT'
    LMT = 'LMT'
    order_types = {MKT: 0, LMT: 1}

    BUY = 'BUY'
    SELL = 'SELL'
    directions = {BUY: 0, SELL: 1}

    def __init__(self, timestamp: datetime, symbol: str, order_type: str, quantity: int, direction: str,
                 attr: dict = None):
        """
        Initialises the order type, setting whether it is
        a Market order ('MKT') or Limit order ('LMT'), has
        a quantity (integral) and its direction ('BUY' or
        'SELL').

        TODO: Must handle error checking here to obtain
        rational orders (i.e. no negative quantities etc).

        Parameters:
        symbol - The instrument to trade.
        order_type - 'MKT' or 'LMT' for Market or Limit.
        quantity - Non-negative integer for quantity.
        direction - 'BUY' or 'SELL' for long or short.
        """
        self.timestamp = timestamp
        self.symbol: str = symbol
        self.order_type: str = order_type
        self.quantity: int = quantity
        self.direction: str = direction
        self.attr: dict = attr

    def print_order(self):
        """
        Outputs the values within the Order.
        """
        print(
            "Order: Symbol=%s, Type=%s, Quantity=%s, Direction=%s" %
            (self.symbol, self.order_type, self.quantity, self.direction)
        )


class FillEvent(Event):
    """
    Encapsulates the notion of a Filled Order, as returned
    from a brokerage. Stores the quantity of an instrument
    actually filled and at what price. In addition, stores
    the commission of the trade from the brokerage.

    TODO: Currently does not support filling positions at
    different prices. This will be simulated by averaging
    the cost.
    """
    BUY = 'BUY'
    SELL = 'SELL'
    directions = {BUY: 0, SELL: 1}

    def __init__(self, timestamp: datetime, symbol: str, exchange: float, quantity: int,
                 direction: str, fill_cost: float, attr: dict = None, commission: float = None):
        """
        Initialises the FillEvent object. Sets the symbol, exchange,
        quantity, direction, cost of fill and an optional
        commission.

        If commission is not provided, the Fill object will
        calculate it based on the trade size and Interactive
        Brokers fees.

        Parameters:
        timestamp - The bar-resolution when the order was filled.
        symbol - The instrument which was filled.
        exchange - The exchange where the order was filled.
        quantity - The filled quantity.
        direction - The direction of fill ('BUY' or 'SELL')
        fill_cost - The holdings value in dollars.
        commission - An optional commission sent from IB.
        """
        self.timestamp: datetime = timestamp
        self.symbol: str = symbol
        self.exchange: float = exchange
        self.quantity: int = quantity
        self.direction: str = direction
        self.fill_price: float = fill_cost
        self.attr = attr

        # Calculate commission
        if commission is None:
            self.commission: float = self.calculate_ib_commission()
        else:
            self.commission: float = commission

    def calculate_ib_commission(self):
        """
        Calculates the fees of trading based on an Interactive
        Brokers fee structure for API, in USD.

        This does not include exchange or ECN fees.

        Based on "US API Directed Orders":
        https://www.interactivebrokers.com/en/index.php?f=commission&p=stocks2
        """
        full_cost = 1.3
        if self.quantity <= 500:
            full_cost = max(1.3, 0.013 * self.quantity)
        else:  # Greater than 500
            full_cost = max(1.3, 0.008 * self.quantity)
        return full_cost
