#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

from stockstar.portfolio import Portfolio
from ..event import FillEvent, OrderEvent
from .execution import ExecutionHandler

__all__ = ["SimulatedExecHandler"]

logger = logging.getLogger(__name__)


class SimulatedExecHandler(ExecutionHandler):

    def __init__(self, portfolio: Portfolio):
        super(SimulatedExecHandler, self).__init__(portfolio)

    def execute_order(self, event: OrderEvent):
        fill_event = FillEvent(event.date, event.symbol, 1.0,
                               event.quantity, event.direction)
        self.events.put(fill_event)
