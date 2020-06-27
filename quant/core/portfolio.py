#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from queue import Queue
from copy import deepcopy
from datetime import datetime

from quant.core.event import *
from quant.core.metric import *
from quant.core.datahandler import KField, DataHandler

from typing import Optional, List, Dict


class Holdings(object):
    def __init__(self, datahandler: DataHandler, fill_events: Dict[str, List[FillEvent]],
                 cash: float, ratio: float, commission: float = 0.0, interest_rate: float = 0.0005):
        self.datahandler: DataHandler = datahandler
        self.symbol_list: List[str] = datahandler.symbol_list
        self.ratio: float = ratio

        self.fill_events: Dict[str, List[FillEvent]] = fill_events
        self.interest_rate = interest_rate

        # 个股持股净值, 与当前市场相关
        self.holding: Dict[str, float] = {}

        # 量, 股数. 做多为正, 做空为负
        self.position: Dict[str, int] = {}

        # 保证金, 归属于你, 但持仓期间不能支配
        # 对于做多, 买入时支付, 平仓时退回; 对于做空, 卖出时支付, 平仓时退回
        self.deposit: Dict[str, float] = {}

        # 融资, 就是你借的钱(用负值表示), 你可以用, 但不属于你
        # 对于做多, 买入时借钱, 平仓时还钱; 对于做空, 卖出时借钱, 平仓时退回
        self.finance: Dict[str, float] = {}

        # 虚拟资金(辅助变量, 可正可负), 归属于你, 只能在平仓时可以兑现
        self.dummy_cash: Dict[str, float] = {}

        # 两个等式
        # 1) 等价交易: 保证金 + abs(融资) == abs(股票价值)
        # 2) 交易前后portofino不变: 交易前现金 = 交易后现金 + 保证金 + 融资 + 股票价值 + 虚拟资金
        # 3) 做多: 股票价值 = abs(融资) + abs(虚拟资金)
        # 4) 做空: 虚拟资金 = abs(融资) + abs(股票价值)

        self.datetime: Optional[str] = None
        self.cash: float = cash
        self.commission: float = commission

    @property
    def total(self) -> float:
        if len(self.holding) == 0:
            total_value = self.cash
            for symbol in self.position:
                curr_mkt_value = self.position[symbol] * self.datahandler.get_latest_bar_value(symbol, KField.close)
                total_value += curr_mkt_value + self.deposit[symbol]
                total_value += self.finance[symbol] + self.dummy_cash[symbol]
            return total_value
        else:
            return sum(self.holding.values()) + self.cash

    def copy_and_create(self):
        holdings = Holdings(self.datahandler, self.fill_events, self.ratio,
                            self.cash, self.commission, self.interest_rate)
        holdings.position = deepcopy(self.position)
        holdings.deposit = deepcopy(self.deposit)
        holdings.finance = deepcopy(self.finance)
        holdings.dummy_cash = deepcopy(self.dummy_cash)

        return holdings

    def __contains__(self, symbol):
        return symbol in self.position and self.position[symbol] != 0

    def _get_interest(self, fill: FillEvent):
        fmt = '%Y-%m-%d'
        curr_date = datetime.strptime(fill.timestamp, fmt)
        interest = 0.0
        if fill.symbol in self.fill_events:
            for event in self.fill_events[fill.symbol]:
                days = (curr_date - datetime.strptime(event.timestamp, fmt)).days
                interest += event.quantity * event.fill_price * (1 - self.ratio) * self.interest_rate * days

        return interest

    def is_affordable(self, symbol: str, pos: int) -> bool:
        net_value = self.datahandler.get_latest_bar_value(symbol, KField.close) * pos
        est_commission = net_value * 0.01
        return self.cash > net_value * self.ratio + est_commission

    def add(self, fill: FillEvent):
        if fill.symbol not in self.position[fill.symbol]:
            self.position[fill.symbol] = 0

        if fill.direction == FillEvent.BUY and self.position[fill.symbol] > 0:
            # extend long
            self.position[fill.symbol] += fill.quantity
            # 买股票所花
            stock_net_value = fill.quantity * fill.fill_price
            this_deposit = stock_net_value * self.ratio  # 保证金额, 自动转为成本
            this_finance = stock_net_value - this_deposit  # 融资额

            # 交保证金
            self.cash -= this_deposit
            self.deposit[fill.symbol] += this_deposit

            # 融资
            self.finance[fill.symbol] -= this_finance

            # 计算dummy_cash
            self.dummy_cash[fill.symbol] -= this_deposit
        elif fill.direction == FillEvent.SELL and self.position[fill.symbol] > 0:
            # close long, lighten is not allowed
            if abs(self.position[fill.symbol]) != fill.quantity:
                print("lighten is not allowed")
                return

            self.position[fill.symbol] -= fill.quantity

            # 卖股票所得
            stock_net_value = fill.quantity * fill.fill_price

            # 还融资
            stock_net_value += self.finance[fill.symbol]
            self.cash -= self._get_interest(fill)  # 还利息
            self.finance[fill.symbol] = 0.0

            # 还dummy_cash
            stock_net_value += self.dummy_cash[fill.symbol]
            self.dummy_cash[fill.symbol] = 0.0

            # 取回保证金
            stock_net_value += self.deposit[fill.symbol]
            self.deposit[fill.symbol] = 0.0

            # 剩的放回现金库
            self.cash += stock_net_value

            if self.position[fill.symbol] != 0:
                raise Exception("lighten is not allowed")
        elif fill.direction == FillEvent.BUY and self.position[fill.symbol] < 0:
            # close short, lighten is not allowed
            if abs(self.position[fill.symbol]) != fill.quantity:
                print("lighten is not allowed")
                return

            self.position[fill.symbol] += fill.quantity

            # 做空, 买回股票
            self.dummy_cash[fill.symbol] -= fill.quantity * fill.fill_price

            # 做空, 还融资
            self.dummy_cash[fill.symbol] += self.finance[fill.symbol]
            self.cash -= self._get_interest(fill)  # 还利息
            self.finance[fill.symbol] = 0.0

            # 做空, 取回保证金
            self.dummy_cash[fill.symbol] += self.deposit[fill.symbol]
            self.deposit[fill.symbol] = 0.0

            # 剩的放回现金库
            self.cash += self.dummy_cash[fill.symbol]
            self.dummy_cash[fill.symbol] = 0.0
        elif fill.direction == FillEvent.SELL and self.position[fill.symbol] < 0:
            # extend short
            self.position[fill.symbol] -= fill.quantity

            stock_net_value = fill.quantity * fill.fill_price
            this_deposit = stock_net_value * self.ratio  # 保证金, 自动转为成本
            this_finance = stock_net_value - this_deposit  # 融资

            # 交保证金
            self.cash -= this_deposit
            self.deposit[fill.symbol] += this_deposit

            # 融资
            self.finance[fill.symbol] -= this_finance

            # 计算dummy_cash
            self.dummy_cash[fill.symbol] += this_deposit + 2 * this_finance
        elif fill.direction == FillEvent.BUY and self.position[fill.symbol] == 0:
            # open long
            self.position[fill.symbol] += fill.quantity
            # 买股票所花
            stock_net_value = fill.quantity * fill.fill_price
            this_deposit = stock_net_value * self.ratio  # 保证金额, 自动转为成本
            this_finance = stock_net_value - this_deposit  # 融资额

            # 交保证金
            self.cash -= this_deposit
            self.deposit[fill.symbol] = this_deposit

            # 融资
            self.finance[fill.symbol] = -this_finance

            # 计算dummy_cash
            self.dummy_cash[fill.symbol] = -this_deposit
        else:
            # open short
            self.position[fill.symbol] -= fill.quantity

            stock_net_value = fill.quantity * fill.fill_price
            this_deposit = stock_net_value * self.ratio  # 保证金, 自动转为成本
            this_finance = stock_net_value - this_deposit  # 融资

            # 交保证金
            self.cash -= this_deposit
            self.deposit[fill.symbol] = this_deposit

            # 融资
            self.finance[fill.symbol] = -this_finance

            # 计算dummy_cash
            self.dummy_cash[fill.symbol] = this_deposit + 2 * this_finance

        # 交易佣金
        self.cash -= fill.commission
        self.commission += fill.commission

        if self.position[fill.symbol] == 0:
            # 平仓, 删除记录
            del self.position[fill.symbol]
            del self.deposit[fill.symbol]
            del self.finance[fill.symbol]
            del self.dummy_cash[fill.symbol]
            del self.fill_events[fill.symbol]
        else:
            if fill.symbol in self.fill_events:
                self.fill_events[fill.symbol].append(fill)
            else:
                self.fill_events[fill.symbol] = [fill]

    def mk_snapshot(self, cur_datetime: str):
        self.datetime = cur_datetime
        for symbol in self.position:
            curr_mkt_value = self.position[symbol] * self.datahandler.get_latest_bar_value(symbol, KField.close)
            self.holding[symbol] = curr_mkt_value + self.deposit[symbol]
            self.holding[symbol] += self.finance[symbol] + self.dummy_cash[symbol]

    def to_dict(self):
        temp = {symbol: self.holding[symbol] if symbol in self.holding else 0.0
                for symbol in self.symbol_list}
        temp['cash'] = self.cash
        temp['datetime'] = self.datetime
        temp['total'] = self.total
        temp['commission'] = self.commission

        return temp


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

    def __init__(self, data_handler: DataHandler, events: Queue, start_date: str,
                 initial_capital: float = 100000.0, ratio: float = 1.0, interest_rate: float = 0.0005):
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
        self.data_handler: DataHandler = data_handler
        self.events: Queue = events
        self.symbol_list: List[str] = self.data_handler.symbol_list
        self.start_date: str = start_date
        self.initial_capital: float = initial_capital
        self.ratio = ratio
        self.interest_rate = interest_rate

        # fill events
        self.fill_events: Dict[str, List[FillEvent]] = {}  # since current, no date

        # holding:
        self.all_holdings: List[Holdings] = []
        self.current_holdings: Holdings = Holdings(self.data_handler, self.fill_events, initial_capital,
                                                   ratio, interest_rate)

    def update_timeindex(self, cur_datetime):
        """
        Adds a new record to the positions matrix for the current 
        market data bar. This reflects the PREVIOUS bar, i.e. all
        current market data at this stage is known (OHLCV).

        Makes use of a MarketEvent from the events queue.
        """

        # Update positions
        # ================
        self.current_holdings.mk_snapshot(cur_datetime)
        self.all_holdings.append(self.current_holdings)
        self.current_holdings = self.current_holdings.copy_and_create()

    def has_position(self, symbol: str) -> bool:
        return symbol in self.current_holdings

    def get_position(self, sybmol: str) -> int:
        return self.current_holdings.position[sybmol]

    @property
    def cash(self) -> float:
        return self.current_holdings.cash

    @property
    def total(self) -> float:
        return self.current_holdings.total

    def is_affordable(self, symbol: str, pos: int) -> bool:
        return self.current_holdings.is_affordable(symbol, pos)

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
            self.current_holdings.add(event)

    # ========================
    # STATISTICS
    # ========================

    def calc_equity_curve(self):
        """
        Creates a pandas DataFrame from the all_holdings
        list of dictionaries.
        """
        curve = pd.DataFrame([holdings.to_dict() for holdings in self.all_holdings])
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
