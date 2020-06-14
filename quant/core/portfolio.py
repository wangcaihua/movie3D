#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd

from quant.core.datahandler import KField
from quant.core.event import *
from quant.core.metric import *

from typing import Optional


class Portfolio(object):
    """
    The Portfolio class handles the positions and market
    value of all instruments at a resolution of a "bar",
    i.e. secondly, minutely, 5-min, 30-min, 60 min or EOD.

    The positions DataFrame stores a time-index of the 
    quantity of positions held. 

    The holdings DataFrame stores the cash and total market
    holdings value of each symbol for a particular 
    time-index, as well as the percentage change in 
    portfolio total across bars.
    """

    def __init__(self, data_handler, events, start_date, initial_capital=100000.0):
        """
        Initialises the portfolio with data handler and an event queue. 
        Also includes a starting datetime index and initial capital 
        (USD unless otherwise stated).

        Parameters:
        data_handler - The DataHandler object with current market data.
        events - The Event Queue object.
        start_date - The start date (bar) of the portfolio.
        initial_capital - The starting capital in USD.
        """
        self.data_handler = data_handler
        self.events = events
        self.symbol_list = self.data_handler.symbol_list
        self.start_date = start_date
        self.initial_capital = initial_capital

        # position: List[Dict], symbol->volume, datetime -> timestamp
        self.all_positions = self.init_all_positions()  # historical positions
        self.current_positions = {symbol: 0 for symbol in self.symbol_list}  # since current, no date

        # holding: 
        self.all_holdings = self.init_all_holdings()
        self.current_holdings = self.construct_current_holdings()

        # fill events
        self.fill_events = {symbol: [] for symbol in self.symbol_list}  # since current, no date

    def init_all_positions(self):
        """
        Constructs the positions list using the start_date
        to determine when the time index will begin.
        """
        positions = {'datetime': self.start_date}
        # symbol -> volume
        positions.update({symbol: 0 for symbol in self.symbol_list})
        return [positions]

    def init_all_holdings(self):
        """
        Constructs the holdings list using the start_date
        to determine when the time index will begin.
        """
        holding = {
            'datetime': self.start_date,
            'cash': self.initial_capital,
            'commission': 0.0,  # 交易拥金
            'total': self.initial_capital
        }

        holding.update({symbol: 0.0 for symbol in self.symbol_list})

        return [holding]

    def construct_current_holdings(self):
        """
        This constructs the dictionary which will hold the instantaneous
        value of the portfolio across all symbols.
        """
        holding = {
            'cash': self.initial_capital,
            'commission': 0.0,  # 交易拥金
            'total': self.initial_capital
        }

        holding.update({symbol: 0.0 for symbol in self.symbol_list})
        return holding

    def update_timeindex(self, cur_datetime):
        """
        Adds a new record to the positions matrix for the current 
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """

        # Update positions
        # ================
        position = {'datetime': cur_datetime}
        position.update({symbol: self.current_positions[symbol] for symbol in self.symbol_list})
        self.all_positions.append(position)

        # Update holdings
        # ===============
        holding = {
            'datetime': cur_datetime,
            'cash': self.current_holdings['cash'],
            'commission': self.current_holdings['commission'],
            'total': self.current_holdings['cash']
        }

        for symbol in self.symbol_list:
            if self.current_positions[symbol] > 0:
                market_value = self.current_positions[symbol] * \
                               self.data_handler.get_latest_bar_value(symbol, KField.close)
                holding[symbol] = market_value
                holding['total'] += market_value
            else:
                holding[symbol] = 0.0

        self.all_holdings.append(holding)

    def has_position(self, symbol: str) -> bool:
        return symbol in self.current_positions

    def get_curr_position(self, sybmol: str) -> int:
        return self.current_positions[sybmol]

    def get_curr_cash(self) -> float:
        return self.current_holdings['cash']

    def get_curr_total(self) -> float:
        return self.current_holdings['total']

    def get_fill_events(self, symbol):
        if symbol in self.fill_events:
            return self.fill_events[symbol]
        else:
            return None

    def get_fill_events_len(self, symbol) -> int:
        if symbol in self.fill_events:
            return len(self.fill_events[symbol])
        else:
            return 0

    def get_fill_event(self, symbol, index=0) -> Optional[FillEvent]:
        if symbol in self.fill_events:
            if len(self.fill_events[symbol]) > 0 and abs(index) < len(self.fill_events[symbol]):
                return self.fill_events[symbol][index]
            else:
                return None
        else:
            return None

    def get_first_fill_event(self, symbol) -> Optional[FillEvent]:
        return self.get_fill_event(symbol, 0)

    def get_last_fill_event(self, symbol) -> Optional[FillEvent]:
        return self.get_fill_event(symbol, -1)

    def on_fill(self, event: FillEvent):
        """
        Updates the portfolio current positions and holdings 
        from a FillEvent.
        """
        if isinstance(event, FillEvent):
            # Check whether the fill is a buy or sell
            assert event.direction in FillEvent.directions
            fill_dir = 1 if event.direction == 'BUY' else -1

            # update postion
            self.current_positions[event.symbol] += fill_dir * event.quantity

            # update fill_events
            if self.current_positions[event.symbol] == 0:
                self.fill_events = []
            else:
                self.fill_events.append(event)

            # update holding
            fill_cost = self.data_handler.get_latest_bar_value(event.symbol, KField.close)
            cost = fill_dir * fill_cost * event.quantity
            self.current_holdings[event.symbol] += cost
            self.current_holdings['commission'] += event.commission
            self.current_holdings['cash'] -= (cost + event.commission)
            self.current_holdings['total'] -= (cost + event.commission)

    # ========================
    # STATISTICS
    # ========================

    def calc_equity_curve(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame(self.all_holdings)
        curve.set_index('datetime', inplace=True)
        curve['returns'] = curve['total'].pct_change()
        curve['equity_curve'] = (1.0 + curve['returns']).cumprod()
        return curve

    @staticmethod
    def calc_metric(curve: pd.DataFrame, filename: str = None):
        """
        Creates a list of summary statistics for the portfolio.
        """

        sharpe_ratio = calc_sharpe_ratio(curve.returns, periods=252 * 60 * 6.5)
        drawdown, max_dd, dd_duration = calc_drawdowns(curve.equity_curve)
        curve['drawdown'] = drawdown

        total_return = curve.equity_curve[-1]
        stats = [("Total Return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                 ("Sharpe Ratio", "%0.2f" % sharpe_ratio),
                 ("Max Drawdown", "%0.2f%%" % (max_dd * 100.0)),
                 ("Drawdown Duration", "%d" % dd_duration)]

        if filename is not None:
            curve.to_csv(filename)

        return stats
