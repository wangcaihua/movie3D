import numpy as np
from quant.core.datahandler import KField
from quant.core.event import *
from quant.core.strategy import StrategyRule
from quant.core.portfolio import Portfolio
from quant.data.sqlitedatahandler import SQLiteDataHandler

from typing import Optional, Generator, cast

import logging

logger = logging.getLogger(__name__)


class TurtleStrategy(StrategyRule):
    """
    Carries out a basic Moving Average Crossover strategy with a
    short/long simple weighted moving average. Default short/long
    windows are 100/400 periods respectively.
    """

    @property
    def rule_id(self):
        return "TurtleStrategy"

    def __init__(self, portfolio: Portfolio, short_window=100, long_window=400):
        """
        Initialises the buy and hold strategy.

        Parameters:
        portfolio - Portfolio
        short_window - The short moving average lookback.
        long_window - The long moving average lookback.
        """
        super(TurtleStrategy, self).__init__(portfolio)
        self.data_handler: SQLiteDataHandler = cast(SQLiteDataHandler, self.data_handler)

        self.short_window = short_window
        self.long_window = long_window

    def handle(self, event: DataEvent) -> Generator[Signal, None, None]:
        """
        Generates a new set of signals based on the MAC
        SMA with the short window crossing the long window
        meaning a long entry and vice versa for a short entry.    

        Parameters
        event - A DataEvent object.
        """

        assert isinstance(event, DataEvent)
        for symbol in self.symbol_list:
            if symbol in self.data_handler.plate_symbols or symbol == self.data_handler.benchmark:
                continue
            try:
                current_atr: float = self.data_handler.get_curr_bar_value(symbol, KField.atr)
                current_price: float = self.data_handler.get_curr_bar_value(symbol, KField.close)

                highest10: float = np.max(self.data_handler.get_hist_bars_values(symbol, KField.close, 10))
                lowest10: float = np.min(self.data_handler.get_hist_bars_values(symbol, KField.close, 10))
                highest20: float = np.max(self.data_handler.get_hist_bars_values(symbol, KField.close, 20))
                lowest20: float = np.min(self.data_handler.get_hist_bars_values(symbol, KField.close, 20))

                if self.portfolio.has_position(symbol):  # extend/lighten/close
                    fist_fill = self.portfolio.get_first_fill_event(symbol)
                    last_fill = self.portfolio.get_last_fill_event(symbol)
                    hist_fill_events_len = self.portfolio.get_fill_events_len(symbol)
                    if hist_fill_events_len > 4:
                        continue

                    if fist_fill.direction == FillEvent.BUY:
                        if 0.5 * fist_fill.attr['atr'] + last_fill.fill_price <= current_price:
                            yield Signal(symbol=symbol, signal_type=Signal.Extend, confidence=1.0, attr={
                                "index": self.data_handler.hist_index,
                                "atr": current_atr,
                                "rule_id": self.rule_id
                            })
                        else:
                            hold_days = self.data_handler.hist_index - fist_fill.attr['index']
                            hold_max = self.data_handler.get_hist_bars_values(symbol, KField.high, hold_days).max()

                            if hold_max - 2 * fist_fill.attr['atr'] > current_price:
                                yield Signal(symbol=symbol, signal_type=Signal.Close, confidence=1.0, attr={
                                    "index": self.data_handler.hist_index,
                                    "atr": current_atr,
                                    "rule_id": self.rule_id
                                })
                            elif lowest10 > current_price:
                                yield Signal(symbol=symbol, signal_type=Signal.Close, confidence=1.0, attr={
                                    "index": self.data_handler.hist_index,
                                    "atr": current_atr,
                                    "rule_id": self.rule_id
                                })
                            else:
                                yield None
                    else:  # SELL
                        if last_fill.fill_price - 0.5 * fist_fill.attr['atr'] >= current_price:
                            yield Signal(symbol=symbol, signal_type=Signal.Extend, confidence=1.0, attr={
                                "index": self.data_handler.hist_index,
                                "atr": current_atr,
                                "rule_id": self.rule_id
                            })
                        else:
                            hold_days = self.data_handler.hist_index - fist_fill.attr['index']
                            hold_min = self.data_handler.get_hist_bars_values(symbol, KField.low, hold_days).min()

                            if hold_min + 2 * fist_fill.attr['atr'] < current_price:
                                yield Signal(symbol=symbol, signal_type=Signal.Close, confidence=1.0, attr={
                                    "index": self.data_handler.hist_index,
                                    "atr": current_atr,
                                    "rule_id": self.rule_id
                                })
                            elif highest10 < current_price:
                                yield Signal(symbol=symbol, signal_type=Signal.Close, confidence=1.0, attr={
                                    "index": self.data_handler.hist_index,
                                    "atr": current_atr,
                                    "rule_id": self.rule_id
                                })
                            else:
                                yield None
                else:  # open long/short
                    if current_price > highest20:
                        yield Signal(symbol=symbol, signal_type=Signal.OpenLong, confidence=1.0, attr={
                            "index": self.data_handler.hist_index,
                            "atr": current_atr,
                            "rule_id": self.rule_id
                        })
                    elif current_price < lowest20:
                        yield Signal(symbol=symbol, signal_type=Signal.OpenShort, confidence=1.0, attr={
                            "index": self.data_handler.hist_index,
                            "atr": current_atr,
                            "rule_id": self.rule_id
                        })
                    else:
                        yield None
            except KeyError as e:
                logger.info('cannot find data for ' + str(e) + ' in ' + self.data_handler.cur_datetime)
                continue
            except Exception as e:
                logger.info(str(e))
                continue
