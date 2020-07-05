#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import queue
from queue import Queue

from quant.core.event import *
from quant.core.strategy import Strategy
from quant.core.datahandler import DataHandler
from quant.data.sqlitedatahandler import SQLiteDataHandler
from quant.core.riskmanager import RiskManager
from quant.core.execution import ExecutionHandler
from quant.core.portfolio import Portfolio

from typing import cast

import logging

logger = logging.getLogger(__name__)


class Backtest(object):
    """
    Enscapsulates the settings and components for carrying out
    an event-driven backtest.
    """

    def __init__(self, events: Queue, heartbeat: float,
                 data_handler: DataHandler,
                 strategy: Strategy,
                 risk_mgr: RiskManager,
                 execution_handler: ExecutionHandler,
                 portfolio: Portfolio):
        """
        Initialises the backtest.

        Parameters:
        heartbeat - Backtest "heartbeat" in seconds
        data_handler - Handles the market data feed.
        execution_handler - Handles the orders/fills for trades.
        portfolio - Keeps track of portfolio current and prior positions.
        strategy - Generates signals based on market data.
        """

        self.heartbeat: float = heartbeat
        self.events: Queue = events
        self.data_handler: SQLiteDataHandler = cast(SQLiteDataHandler, data_handler)
        self.strategy: Strategy = strategy
        self.risk_mgr = risk_mgr
        self.portfolio: Portfolio = portfolio
        self.execution_handler: ExecutionHandler = execution_handler

        self.signals = 0
        self.orders = 0
        self.fills = 0
        self.num_strats = 1

    def _run_backtest(self):
        """
        Executes the backtest.
        """
        while True:
            if self.data_handler.continue_backtest:
                logger.info('{datetime}-update_timeindex'.format(datetime=self.data_handler.cur_datetime))
                self.portfolio.update_timeindex(self.data_handler.cur_datetime)
                self.data_handler.update_bars()
            else:
                break

            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if isinstance(event, DataEvent):
                            self.strategy.on_data(event)

                        elif isinstance(event, SignalEvent):
                            self.signals += 1
                            self.risk_mgr.on_signal(event)

                        elif isinstance(event, OrderEvent):
                            self.orders += 1
                            self.execution_handler.on_order(event)

                        elif isinstance(event, FillEvent):
                            self.fills += 1
                            self.portfolio.on_fill(event)

            time.sleep(self.heartbeat)

    def _output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        equity_curve = self.portfolio.calc_equity_curve()

        logger.info("Creating equity curve...")
        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)
        print()

        logger.info("Creating summary stats...")
        stats = self.portfolio.calc_metric(equity_curve)
        print('\n'.join(stats))

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self._run_backtest()
        self._output_performance()
