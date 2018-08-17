from .exceptions import *
from .event import *
from .io.datahandler import DataHandler

import logging

logger = logging.getLogger(__name__)


class CostPosition(object):
    def __init__(self, bars: DataHandler, initial_capital: float):
        self.initial_capital = initial_capital
        self.fee = 0.0
        self.cash = initial_capital
        self.costpos = {}
        self.bars = bars

    def open_long(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * fill.quantity
            fee = fill.fee

            self.fee += fee
            self.cash -= cost + fee
            self.costpos[fill.symbol] = (cost, fill.quantity)
        except DataNotAvailable as e:
            logger.info(e.msg)

    def open_short(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * fill.quantity
            fee = fill.fee

            self.fee += fee
            self.cash -= cost + fee
            self.costpos[fill.symbol] = (cost, -fill.quantity)
        except DataNotAvailable as e:
            logger.info(e.msg)

    def add_long(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * fill.quantity
            fee = fill.fee

            assert fill.direction == Direction.ADDING_BUY
            assert self.costpos[fill.symbol][1] >= 0

            self.fee += fee
            self.cash -= cost + fee
            self.costpos[fill.symbol] = (
                self.costpos[fill.symbol][0] + cost,
                self.costpos[fill.symbol][1] + fill.quantity
            )

        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("LONG and SHORT cannot be executed at the same time!")

    def add_short(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * fill.quantity
            fee = fill.fee

            assert fill.direction == Direction.ADDING_SEL
            assert self.costpos[fill.symbol][1] <= 0

            self.fee += fee
            self.cash -= cost + fee
            self.costpos[fill.symbol] = (
                self.costpos[fill.symbol][0] + cost,
                self.costpos[fill.symbol][1] - fill.quantity
            )
        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("LONG and SHORT cannot be executed at the same time!")

    def lighten_long(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            avg_price = self.costpos[fill.symbol][0] / abs(self.costpos[fill.symbol][1])
            fee = fill.fee

            assert fill.quantity <= abs(self.costpos[fill.symbol][1])

            assert fill.direction == Direction.LIGHTEN_SEL
            self.fee += fee
            cost = avg_price * fill.quantity
            self.cash += cur_price * fill.quantity - fee
            self.costpos[fill.symbol] = (
                self.costpos[fill.symbol][0] - cost,
                self.costpos[fill.symbol][1] - fill.quantity
            )
        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("The lightening quantity cannot exceed total quantity !")

    def lighten_short(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            avg_price = self.costpos[fill.symbol][0] / abs(self.costpos[fill.symbol][1])
            fee = fill.fee

            assert fill.quantity <= abs(self.costpos[fill.symbol][1])

            assert fill.direction == Direction.LIGHTEN_BUY  # SHORT
            self.fee += fee
            cost = avg_price * fill.quantity
            self.cash += (2 * avg_price - cur_price) * fill.quantity - fee
            self.costpos[fill.symbol] = (
                self.costpos[fill.symbol][0] - cost,
                self.costpos[fill.symbol][1] + fill.quantity
            )

        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("The lightening quantity cannot exceed total quantity !")

    def close_long(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * abs(fill.quantity)
            fee = fill.fee

            assert fill.quantity == abs(self.costpos[fill.symbol][1])
            assert fill.direction == Direction.EXIT_SEL  # SHORT

            self.fee += fee
            self.cash += cost - fee
            del self.costpos[fill.symbol]
        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("The fill quantity must equal to total quantity !")

    def close_short(self, fill: FillEvent):
        try:
            cur_price = self.bars.cur_bar_value(fill.symbol, "open")
            cost = cur_price * abs(fill.quantity)
            fee = fill.fee

            assert fill.quantity == abs(self.costpos[fill.symbol][1])
            assert fill.direction == Direction.EXIT_BUY  # SHORT

            self.fee += fee
            self.cash += (2*self.costpos[fill.symbol][0] - cost) - fee
            del self.costpos[fill.symbol]
        except DataNotAvailable as e:
            logger.info(e.msg)
        except AssertionError as _:
            logger.info("The fill quantity must equal to total quantity !")

    def getsymbolcost(self, symbol: str):
        if symbol in self.costpos:
            return self.costpos[symbol][0]
        else:
            return 0.0

    def getposition(self, symbol: str) -> float:
        if symbol in self.costpos:
            return self.costpos[symbol][1]
        else:
            return 0.0

    def isout(self, symbol: str) -> bool:
        return symbol not in self.costpos

    def islong(self, symbol: str) -> bool:
        return symbol in self.costpos and self.costpos[symbol][1] > 0

    def isshort(self, symbol: str) -> bool:
        return symbol in self.costpos and self.costpos[symbol][1] < 0

    def get_holdding(self, last_holdding: dict, date: str) -> dict:
        holdding = {}
        for symbol in self.costpos:
            try:
                cur_price = self.bars.date_bar_value(date, symbol, "close")
                (cost, quantity) = self.costpos[symbol]

                if quantity >= 0:
                    holdding[symbol] = cur_price * quantity
                else:
                    holdding[symbol] = 2 * cost + cur_price * quantity
            except DataNotAvailable as e:
                if symbol in last_holdding:
                    holdding[symbol] = last_holdding[symbol]
                    logger.info(e.msg + " use last last_holdding")
                else:
                    holdding[symbol] = self.costpos[symbol][0]
                    logger.info(e.msg + " use cost")

        holdding['cash'] = self.cash
        holdding['total'] = sum(holdding.values())
        holdding['fee'] = self.fee
        holdding['datetime'] = date

        return holdding
