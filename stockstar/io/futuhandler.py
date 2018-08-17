import logging
from .datahandler import DataHandler

logger = logging.getLogger(__name__)


class FutuHandler(DataHandler):
    def date_bar_value(self, date, symbol, val_type):
        pass

    def date_bar(self, date, symbol):
        pass

    def latest_bars(self, symbol, n=1):
        pass

    def latest_bars_values(self, symbol, val_type, n=1):
        pass

    def cur_bar_value(self, symbol, val_type):
        pass

    def update_bars(self):
        pass

    def cur_bar(self, symbol):
        pass