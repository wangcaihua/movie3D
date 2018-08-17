#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import time
import pprint
import logging
from queue import *

from stockstar.event import *
from stockstar.portfolio import Portfolio
from stockstar.exceptions import EndOfData
from stockstar.io.datahandler import DataHandler

logger = logging.getLogger(__name__)


class Backtest(object):

    def __init__(self, data_handler: DataHandler, portfolio: Portfolio,
                 delta_time: int, heartbeat: float = 0.0):
        self.symbol_pool = data_handler.symbol_list
        self.initial_capital = portfolio.initial_capital
        self.events = portfolio.events
        self.data_handler = data_handler
        self.portfolio = portfolio
        self.heartbeat = heartbeat
        self.delta_time = delta_time
        self.last_date = None

        self.signals = 0
        self.orders = 0
        self.fills = 0

    def run_backtest(self):
        """
        Executes the backtest.
        """
        logger.info("Start run_backtest !")
        while True:
            # Update the market bars
            try:
                logger.info("Update_bars !")
                self.data_handler.update_bars(self.delta_time)
            except EndOfData as e:
                logger.info(e.msg)
                break

            # Handle the events
            while True:
                try:
                    event = self.events.get(False)
                except Empty:
                    break
                else:
                    assert event is not None
                    if Event.ismarket(event):
                        logger.info("process MARKET event at {date} !".format(date=event.date))
                        self.portfolio.strategy.send_signals(event)
                        self.portfolio.update_timeindex(self.last_date)
                        self.last_date = event.date

                    elif Event.issignal(event):
                        if isinstance(event, SimpleSignalEvent):
                            logger.info("process SIGNAL event for symbol {symbol} {signal_type} {strength}!"
                                        .format(symbol=event.symbol,
                                                signal_type=event.signal_type,
                                                strength=event.strength
                                                )
                                        )
                        else:
                            logger.info("BatchSignalEvent at {date} !".format(date=event.date))

                        self.signals += 1
                        self.portfolio.strategy.place_order(event)

                    elif Event.isorder(event):
                        logger.info("process ORDER event for symbol {symbol} {order_type}, {quantity}, {direction}!"
                                    .format(symbol=event.symbol,
                                            order_type=event.order_type,
                                            quantity=event.quantity,
                                            direction=event.direction
                                            )
                                    )

                        self.orders += 1
                        self.portfolio.exechandler.execute_order(event)

                    elif Event.isfill(event):
                        logger.info("process FILL event for symbol {symbol}, {exchange}, {quantity}, {direction} !"
                                    .format(symbol=event.symbol,
                                            exchange=event.exchange,
                                            quantity=event.quantity,
                                            direction=event.direction
                                            )
                                    )

                        self.fills += 1
                        self.portfolio.update_fill(event)

            time.sleep(self.heartbeat)

    def output_performance(self):
        """
        Outputs the strategy performance from the backtest.
        """
        self.portfolio.create_equity_curve_dataframe()
        
        print("Creating summary stats...")
        stats = self.portfolio.output_summary_stats()
        
        print("Creating equity curve...")
        print(self.portfolio.equity_curve.tail(10))
        pprint.pprint(stats)

        print("Signals: %s" % self.signals)
        print("Orders: %s" % self.orders)
        print("Fills: %s" % self.fills)

    def simulate_trading(self):
        """
        Simulates the backtest and outputs portfolio performance.
        """
        self.run_backtest()
        self.output_performance()
