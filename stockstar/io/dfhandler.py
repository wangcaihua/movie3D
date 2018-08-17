#!/usr/bin/python
# -*- coding: utf-8 -*-
import logging

import pandas as pd
from .datahandler import DataHandler
from .dfloader import DFLoader
from datetime import datetime, timedelta
from ..event import MarketEvent
from stockstar.exceptions import DataNotAvailable, EndOfData

logger = logging.getLogger(__name__)


class DFHander(DataHandler):

    def __init__(self, quotefile: str, symbol_pool: list,
                 trade_start_date: str, data_start_date: str, data_end_date: str, retry: int=5):
        super(DFHander, self).__init__(symbol_pool, trade_start_date)
        self.dfloader = DFLoader(symbol_pool, quotefile, retry, data_start_date, data_end_date)
        self.cur_date = trade_start_date
        self.max_date = data_end_date
        self.isfirstday = True

        self._load()
        self.symbol_data = self.dfloader.quotesdata
        logger.info("DFHander init finished!")

    def _load(self):
        logger.info("load quotes from {quotefile}".format(quotefile=self.dfloader.quotefile))
        self.dfloader.downloadquotes()

        logger.info("update quotes")
        # self.dfloader.updatequotes()

    def _dump(self):
        self.dfloader.savequotes()

    def cur_bar_value(self, symbol: str, val_type: str) -> float:
        try:
            return self.symbol_data[symbol].loc[self.cur_date, val_type]
        except KeyError as _:
            raise DataNotAvailable(symbol, self.cur_date)

    def date_bar_value(self, date: str, symbol: str, val_type: str) -> float:
        try:
            return self.symbol_data[symbol].loc[date, val_type]
        except KeyError as _:
            raise DataNotAvailable(symbol, date)

    def latest_bars_values(self, symbol: str, val_type: str, n: int=1) -> pd.Series:
        try:
            end = self.symbol_data[symbol].index.get_loc(self.cur_date)
            start = end - n
            return self.symbol_data[symbol][val_type].iloc[start:end]
        except KeyError as _:
            raise DataNotAvailable(symbol, self.cur_date)

    def cur_bar(self, symbol: str) -> pd.Series:
        try:
            return self.symbol_data[symbol].loc[self.cur_date]
        except KeyError as _:
            raise DataNotAvailable(symbol, self.cur_date)

    def date_bar(self, date: str, symbol: str) -> pd.Series:
        try:
            return self.symbol_data[symbol].loc[date]
        except KeyError as _:
            raise DataNotAvailable(symbol, date)

    def update_bars(self, delta: int=1):
        if self.isfirstday:
            cur_date = self.cur_date
            self.isfirstday = False
        else:
            cur_date = datetime.strptime(self.cur_date, "%Y-%m-%d")
            cur_date = (cur_date + timedelta(days=delta)).strftime("%Y-%m-%d")
            self.cur_date = cur_date

        if cur_date >= self.max_date:
            self._dump()
            raise EndOfData(self.cur_date)

        data = None
        for symbol in self.symbol_list:
            try:
                data = self.symbol_data[symbol].loc[cur_date]
                self.events.put(MarketEvent(cur_date))
                break
            except KeyError as _:
                continue

        if data is None:
            logger.info("No data is available in {date} !".format(date=cur_date))

    def latest_bars(self, symbol: str, n: int=1) -> pd.DataFrame:
        try:
            end = self.symbol_data[symbol].index.get_loc(self.cur_date)
            start = end - n
            return self.symbol_data[symbol].iloc[start:end]
        except KeyError as _:
            raise DataNotAvailable(symbol, self.cur_date)

    def get_history_bars(self, symbol):
        try:
            end = self.symbol_data[symbol].index.get_loc(self.cur_date)
            return self.symbol_data[symbol].loc[:end]
        except KeyError as _:
            raise DataNotAvailable(symbol, self.cur_date)
