#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import print_function

import logging
import pandas as pd
from matplotlib import pyplot as plt
from datetime import datetime, timedelta

from stockstar.event import *
from stockstar.costposition import CostPosition
from stockstar.exceptions import AttrNotSet
from stockstar.io.datahandler import DataHandler
from .utils import create_sharpe_ratio, create_drawdowns

logger = logging.getLogger(__name__)


class Portfolio(object):

    def __init__(self, bars: DataHandler, initial_capital: float):
        self.bars = bars
        self.events = bars.events
        self.start_date = bars.cur_date
        self.initial_capital = initial_capital

        self.costpos = CostPosition(bars, initial_capital)
        self.hist_holdings = []    # a list

        self._exechandler = None
        self._strategy = None
        self.equity_curve = None

    @property
    def exechandler(self):
        if self._exechandler is not None:
            return self._exechandler
        else:
            raise AttrNotSet("exechandler")

    @exechandler.setter
    def exechandler(self, exechandler):
        self._exechandler = exechandler

    @property
    def strategy(self):
        if self._strategy is not None:
            return self._strategy
        else:
            raise AttrNotSet("strategy")

    @strategy.setter
    def strategy(self, strategy):
        self._strategy = strategy

    def update_timeindex(self, date: str):
        if len(self.hist_holdings) == 0:
            last_trade_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            last_trade_date = (last_trade_date - timedelta(days=1)).strftime("%Y-%m-%d")
            init_holding = {
                'cash': self.initial_capital,
                'fee': 0.0,
                'total': self.initial_capital,
                'datetime': last_trade_date
            }
            self.hist_holdings.append(init_holding)
        else:
            last_holdding = self.hist_holdings[-1]
            cur_holdding = self.costpos.get_holdding(last_holdding, date)

            self.hist_holdings.append(cur_holdding)

    def update_fill(self, event: FillEvent):
        if event.direction == Direction.OPEN_BUY:
            self.costpos.open_long(event)
        elif event.direction == Direction.OPEN_SELL:
                self.costpos.open_short(event)
        elif event.direction == Direction.ADDING_BUY:
            self.costpos.add_long(event)
        elif event.direction == Direction.ADDING_SEL:
            self.costpos.add_short(event)
        elif event.direction == Direction.LIGHTEN_BUY:
            self.costpos.lighten_short(event)
        elif event.direction == Direction.LIGHTEN_SEL:
            self.costpos.lighten_long(event)
        elif event.direction == Direction.EXIT_BUY:
            self.costpos.close_short(event)
        else:  # Exit
            self.costpos.close_long(event)

    # ========================
    # POST-BACKTEST STATISTICS
    # ========================

    def create_equity_curve_dataframe(self):
        """
        Creates a pandas DataFrame from the hist_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.hist_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change() + 1.0
        curve['equity_curve'] = curve['returns'].cumprod()
        self.equity_curve = curve

    def output_summary_stats(self):
        """
        Creates a list of summary statistics for the portfolio.
        """
        if self.equity_curve is None:
            self.create_equity_curve_dataframe()

        total_return = self.equity_curve['equity_curve'][-1]
        returns = self.equity_curve['returns']
        pnl = self.equity_curve['equity_curve']

        sharpe_ratio = create_sharpe_ratio(returns, periods=252)
        drawdown, max_dd, dd_duration = create_drawdowns(pnl)
        self.equity_curve['drawdown'] = drawdown

        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        self.equity_curve['total'].plot()

        plt.show()

        # self.equity_curve.to_csv('equity.csv')
        return stats
