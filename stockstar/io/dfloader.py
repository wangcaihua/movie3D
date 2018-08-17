import time
import pickle
import logging
import pandas as pd
import tushare as ts
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class DFLoader(object):
    _zz500s = None
    _hs300s = None
    _index = None
    _industry = None
    _concept = None
    _area = None
    _sme = None

    def __init__(self, codes, quotefile, retry=5, start='2008-01-01', end=''):
        self._codes = None
        self.codes = codes
        self.quotesdata = {}
        self.quotefile = quotefile
        self._basics = None
        self.retry = retry
        self.start = start
        self.end = end

    @property
    def codes(self):
        return self._codes

    @codes.setter
    def codes(self, values):
        validate_codes = set(list(ts.get_area_classified().code))
        assert len(set(values) - validate_codes) == 0
        self._codes = values

    @classmethod
    def zz500s(cls):
        if cls._zz500s is None:
            cls._zz500s = ts.get_zz500s().set_index("code")
        return cls._zz500s

    @classmethod
    def hs300s(cls):
        if cls._hs300s is None:
            cls._hs300s = ts.get_hs300s().set_index("code")

        return cls._hs300s

    @classmethod
    def index(cls):
        if cls._index is None:
            cls._index = ts.get_index().set_index("code")

        return cls._index

    @classmethod
    def industry(cls):
        if cls._industry is None:
            cls._industry = ts.get_industry_classified().set_index("code")

        return cls._industry

    @classmethod
    def concept(cls):
        if cls._concept is None:
            cls._concept = ts.get_concept_classified().set_index("code")

        return cls._concept

    @classmethod
    def area(cls):
        if cls._area is None:
            cls._area = ts.get_area_classified().set_index("code")

        return cls._area

    @classmethod
    def sme(cls):
        if cls._sme is None:
            cls._sme = ts.get_sme_classified().set_index("code")

        return cls._sme

    @staticmethod
    def fromcsv(fname, **args):
        return pd.read_csv(fname, **args)

    @property
    def basics(self):
        if self._basics is None:
            self._basics = ts.get_stock_basics().loc[self.codes]

        return self._basics

    def __getitem__(self, item):
        if item in self.quotesdata:
            return self.quotesdata[item]
        else:
            return None

    def downloadquotes(self):
        for code in self.codes:
            temp = None
            while True:
                try_times = 0
                try:
                    temp = ts.get_k_data(code, index=False, start=self.start, end=self.end)
                    try_times += 1
                    break
                except Exception as _:
                    time.sleep(5)
                    if try_times >= self.retry:
                        break
                    else:
                        continue

            if temp is not None and len(temp) > 0:
                temp = temp.set_index("date")
                del temp["code"]
                self.quotesdata[code] = temp

    def loadquotes(self):
        fid = open(self.quotefile, "rb")
        self.quotesdata = pickle.load(fid)
        fid.close()

    def savequotes(self):
        fid = open(self.quotefile, "wb")
        pickle.dump(self.quotesdata, fid)
        fid.close()

    def updatequotes(self):
        latest = datetime.today().date()
        timespan = timedelta(days=1)
        while latest.weekday() in [6, 7]:
            latest = latest - timespan

        for key in self.codes:
            if key in self.quotesdata:
                lastdate = datetime.strptime(self.quotesdata[key].iloc[-1].name, "%Y-%m-%d").date()
            else:
                lastdate = datetime.strptime(self.start, "%Y-%m-%d").date() - timespan

            if latest > lastdate:
                temp = None
                start = (lastdate + timespan).strftime("%Y-%m-%d")
                while True:
                    try_times = 0
                    try:
                        temp = ts.get_k_data(key, index=False, start=start)
                        try_times += 1
                        break
                    except Exception as _:
                        time.sleep(5)
                        if try_times >= self.retry:
                            break
                        else:
                            continue

                if temp is not None and len(temp) > 0:
                    temp = temp.set_index("date")
                    del temp["code"]
                    if key in self.quotesdata:
                        self.quotesdata[key] = self.quotesdata[key].append(
                            temp, verify_integrity=True)
                    else:
                        self.quotesdata[key] = temp
