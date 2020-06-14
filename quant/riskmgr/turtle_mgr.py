from quant.core.event import *
from quant.core.datahandler import KField
from quant.core.portfolio import Portfolio
from quant.core.riskmanager import RiskManager
from quant.data.sqlitedatahandler import SQLiteDataHandler

from typing import cast


class TurtleMgr(RiskManager):
    def __init__(self, portfolio: Portfolio):
        super(TurtleMgr, self).__init__(portfolio)
        self.data_handler: SQLiteDataHandler = cast(SQLiteDataHandler, self.data_handler)

    def on_signal(self, event: SignalEvent):
        open_events, extlig_event, close_event = [], [], []
        timestamp = event.timestamp
        for signal in event.signals:
            symbol = signal.symbol
            lot_size = self.data_handler.get_lot_size(symbol)
            close = self.data_handler.get_latest_bar_value(symbol, KField.close)
            cash = self.portfolio.get_curr_cash()
            total = self.portfolio.get_curr_total()

            if signal.signal_type == Signal.OpenLong or signal.signal_type == Signal.OpenShort:
                available = total * 0.01 / signal.attr['atr']
                one_hand = lot_size * close
                position = int(available / one_hand) * lot_size  # 头衬
                if position > 0 and cash >= close * position:
                    # timestamp: datetime, symbol: str, order_type: str, quantity: int, direction: str, attr: dict
                    if signal.signal_type == Signal.OpenLong:
                        open_events.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.BUY, attr=signal.attr))
                    else:
                        open_events.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                      OrderEvent.SELL, attr=signal.attr))
            elif signal.signal_type == Signal.Extend:
                fill_event = self.portfolio.get_first_fill_event(symbol)
                position = fill_event.quantity
                if cash >= close * position:
                    if fill_event.direction == FillEvent.BUY:
                        extlig_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                       OrderEvent.BUY, attr=signal.attr))
                    else:  # fill_event.direction == FillEvent.SELL
                        extlig_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                       OrderEvent.SELL, attr=signal.attr))
            elif signal.signal_type == Signal.Close:
                fill_event = self.portfolio.get_first_fill_event(symbol)
                position = self.portfolio.get_curr_position(symbol)
                if fill_event.direction == FillEvent.BUY:
                    close_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                  OrderEvent.SELL, attr=signal.attr))
                else:   # fill_event.direction == FillEvent.SELL
                    close_event.append(OrderEvent(timestamp, symbol, OrderEvent.MKT, position,
                                                  OrderEvent.BUY, attr=signal.attr))
            else:
                pass
