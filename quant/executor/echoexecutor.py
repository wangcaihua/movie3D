#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
from typing import cast

from quant.core.datahandler import KField
from quant.core.execution import ExecutionHandler
from quant.core.event import OrderEvent, FillEvent
from quant.core.portfolio import Portfolio
from quant.data.sqlitedatahandler import SQLiteDataHandler

import logging

logger = logging.getLogger(__name__)


class EchoExecutionHandler(ExecutionHandler):
    """
    The simulated execution handler simply converts all order
    objects into their equivalent fill objects automatically
    without latency, slippage or fill-ratio issues.

    This allows a straightforward "first go" test of any strategy,
    before implementation with a more sophisticated execution
    handler.
    """

    def __init__(self, portfolio: Portfolio):
        """
        Initialises the handler, setting the event queues
        up internally.

        Parameters:
        events - The Queue of Event objects.
        """
        super(EchoExecutionHandler, self).__init__(portfolio)
        self.data_handler: SQLiteDataHandler = cast(SQLiteDataHandler, self.data_handler)

    def on_order(self, event: OrderEvent):
        """
        Simply converts Order objects into Fill objects naively,
        i.e. without any latency, slippage or fill ratio problems.

        Parameters:
        event - Contains an Event object with order information.
        """

        symbol = event.symbol
        fill_cost = self.data_handler.get_latest_bar_value(symbol, KField.close)
        direction = 1 if event.direction == OrderEvent.BUY else -1
        fill_event = FillEvent(event.timestamp, symbol, exchange=1.0, quantity=direction * event.quantity,
                               direction=event.direction, fill_cost=fill_cost, attr=event.attr)

        self.events.put(fill_event)
