
__all__ = ["EndOfData", "DataNotAvailable", "AttrNotSet"]


class DataNotAvailable(Exception):
    def __init__(self, symbol: str, date: str):
        self.symbol = symbol
        self.msg = "Data of {symbol} in {date} is not available !".format(
            symbol=symbol, date=date
        )


class EndOfData(Exception):
    def __init__(self, date: str):
        self.msg = "End of Data at {date}!".format(date=date)


class AttrNotSet(Exception):
    def __init__(self, attr: str):
        self.msg = "Attribution {attr} is not set !".format(attr=attr)
