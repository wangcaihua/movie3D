import sqlite3
import datetime

import talib
import math
from futu import *
from queue import Queue
import pandas as pd
import logging
from datetime import datetime, timedelta

from quant.core.event import DataEvent
from quant.core.datahandler import DataHandler, SField, KField

from typing import Optional, Set

logger = logging.getLogger(__name__)


class SQLiteDataHandler(DataHandler):
    def __init__(self, symbol_list: list, events: Queue, start_date: str, run_type: str = "back_test",
                 hist_kline_start: str = '2011-01-01', sqllite_db: str = 'hist_data.db',
                 futu_host: str = '127.0.0.1', futu_port: int = 11111):
        super(SQLiteDataHandler, self).__init__(symbol_list, events, start_date)
        self.hist_kline_start: str = hist_kline_start
        self.hist_kline: dict = {}
        self.hist_index: int = -1
        self.time_line: list = []
        self.run_type: str = run_type
        self.basicinfo: Optional[pd.DataFrame] = None

        # data base and futu initial
        logger.info("start sqlite ...")
        self.conn: sqlite3.Connection = sqlite3.connect(sqllite_db)
        self.cursor: sqlite3.Cursor = self.conn.cursor()

        logger.info("start futu ...")
        self.ktype = SubType.K_DAY
        self.autype = AuType.QFQ
        self.quote_ctx: OpenQuoteContext = OpenQuoteContext(host=futu_host, port=futu_port)

        self.benchmark: str = "HK.800000"  # 恒生指数
        if self.benchmark not in self.symbol_list:
            self.symbol_list.insert(0, self.benchmark)
            temp = self.get_kline_from_futu(self.benchmark, hist_kline_start,
                                            datetime.today().strftime(self.tfmt))
            assert temp is not None
            temp['time_key'] = temp.time_key.str[0:10]
            temp.set_index('time_key', inplace=True)
            temp[KField.atr.name] = talib.ATR(temp[KField.high.name],
                                              temp[KField.low.name],
                                              temp[KField.close.name], timeperiod=20)
            self.hist_kline[self.benchmark] = temp

        # init short_set
        ret, data = self.quote_ctx.get_plate_stock(plate_code='HK.BK1000')
        assert ret == RET_OK
        self._short_set = set(data.code.to_list())

        ret, plate_list = self.quote_ctx.get_plate_list(Market.HK, Plate.ALL)
        assert ret == RET_OK
        self.plate_symbols: Set[str] = set(plate_list.code.to_list())

    def close(self):
        logger.info('close sqllit connection ...')
        self.conn.close()
        logger.info("close futu ...")
        self.quote_ctx.close()

    def can_short(self, symbol) -> bool:
        return symbol in self._short_set

    def init_time_line(self):
        if len(self.time_line) == 0:
            self.time_line = self.hist_kline[self.benchmark].index.values.tolist()

        delta = timedelta(days=1)
        while self.cur_datetime not in self.time_line:
            cur_datetime = datetime.strptime(self.cur_datetime, self.tfmt)
            self.cur_datetime = (cur_datetime + delta).strftime(self.tfmt)

        # 上一个交易日对应的索引
        self.hist_index = self.time_line.index(self.cur_datetime) - 1
        # 当前交易日
        self.cur_datetime = self.time_line[self.hist_index + 1]

    def update_snapshot(self):
        if self.run_type == "back_test":
            snapshot = []
            # update hist_index/cur_datetime
            for symbol in self.symbol_list:
                try:
                    if symbol in self.hist_kline:
                        if self.cur_datetime >= self.hist_kline[symbol].index[0]:
                            snapshot.append(self.hist_kline[symbol].loc[self.cur_datetime])
                        else:
                            raise ValueError('the stock ' + symbol + ' has not been IPO yet in ' + self.cur_datetime)
                except ValueError as e:
                    logger.info(str(e))
                except KeyError as e:
                    logger.info('cannot found data in' + str(e) + " for symbol " + symbol + ", maybe closed that day")

            if snapshot:
                snapshot = pd.DataFrame(snapshot)
                snapshot.set_index("code", inplace=True)
                self.snapshot = snapshot
        else:
            ret, snapshot = self.quote_ctx.get_market_snapshot(self.symbol_list)
            snapshot.set_index("code", inplace=True)
            self.snapshot = snapshot
            assert ret == RET_OK

            # update cur_datetime
            self.cur_datetime = self.snapshot.update_time.max()[0:10]

    def snapshot_extend(self):
        all_symbols, batch_size = self.basicinfo.index.values.tolist(), 400
        num_batch = (len(all_symbols) + batch_size - 1) // batch_size

        snapshots, max_retry = [], 3
        for i in range(num_batch):
            start = i * batch_size
            end = (i + 1) * batch_size if (i + 1) * batch_size < len(all_symbols) else len(all_symbols)
            retry = 0
            ret, snapshot = self.quote_ctx.get_market_snapshot(all_symbols[start:end])
            while ret != RET_OK and retry < max_retry:
                time.sleep(0.5)
                retry += 1
                ret, snapshot = self.quote_ctx.get_market_snapshot(all_symbols[start:end])

            if ret == RET_OK:
                snapshots.append(snapshot)

            time.sleep(0.5)

        if snapshots:
            snapshots = pd.concat(snapshots)
            snapshots.set_index('code', inplace=True)
            snapshots = pd.concat([snapshots, self.basicinfo], axis=1)
            return snapshots
        else:
            return None

    def get_local_symbols(self):
        # get all table from sqlite
        sql_get_all_tables = "SELECT name FROM sqlite_master WHERE sqlite_master.type = 'table'"
        local_tables = list({table[0] for table in self.cursor.execute(sql_get_all_tables)} & set(self.symbol_list))
        if 'basicinfo' in local_tables:
            local_tables.remove('basicinfo')
        return local_tables

    def get_kline_from_futu(self, symbol, start, end):
        retry, max_retry = 0, 3
        data_splits = []

        if retry < max_retry:
            try:
                ret, data, page_req_key = self.quote_ctx.request_history_kline(
                    symbol, start=start, end=end, max_count=250)
                while ret != RET_OK and retry < max_retry:
                    retry += 1
                    time.sleep(0.5)
                    ret, data, page_req_key = self.quote_ctx.request_history_kline(
                        symbol, start=start, end=end, max_count=250)
                if ret == RET_OK:
                    data_splits.append(data)

                while ret == RET_OK and page_req_key is not None:
                    ret, data, page_req_key = self.quote_ctx.request_history_kline(
                        symbol, start=start, end=end, max_count=250, page_req_key=page_req_key)
                    if ret == RET_OK:
                        data_splits.append(data)
                    else:
                        logger.info('request_history_kline error!')
                        retry += 1

                if len(data_splits) > 0:
                    data_splits = pd.concat(data_splits, axis=0, join='outer', ignore_index=True)
                logger.info(symbol + " download kline finished!")
            except Exception as e:
                logger.info(symbol + " download Exception: " + str(e) + ", retry ...")
                retry += 1
        else:
            logger.warning(symbol + " download kline form futu fail!")

        if isinstance(data_splits, pd.DataFrame):
            data_splits["time_key"] = data_splits.time_key.str[0:10]
            return data_splits
        else:
            return None

    def update_local_kline_db(self, symbol_list=None):
        if symbol_list is None:
            symbol_list = self.symbol_list
        local_tables = self.get_local_symbols()

        # get trading_days from futu
        ret, trading_days = self.quote_ctx.get_trading_days(Market.HK)
        assert ret == RET_OK
        year_trading_days = [td['time'] for td in trading_days if td['trade_date_type'] in ['WHOLE', 'MORNING']]

        sql_last_date = "SELECT max(time_key) FROM `{table}`"
        need_update = []
        for table in local_tables:
            self.cursor.execute(sql_last_date.format(table=table))
            res = self.cursor.fetchone()
            if res is not None:
                last_date = res[0][0:10]  # yyyy-mm-dd
                num = len(year_trading_days) - year_trading_days.index(last_date) - 1
                if num > 0:
                    need_update.append((table, num))

        num_batch = (len(need_update) + 99) // 100
        for i in range(num_batch):
            start = i * 100
            end = (i + 1) * 100 if (i + 1) * 100 < len(need_update) else len(need_update)

            # subscribe stocks
            ret, err_message = self.quote_ctx.subscribe(list(local_tables), [self.ktype], subscribe_push=False)
            assert ret == RET_OK

            for j in range(start, end):
                table, num = need_update[j]
                ret, kline = self.quote_ctx.get_cur_kline(table, num, ktype=self.ktype, autype=self.autype)
                assert ret == RET_OK
                kline["time_key"] = kline.time_key.str[0:10]
                kline.to_sql(table, self.conn, if_exists='append', chunksize=250, index=False)
                self.conn.commit()

            time.sleep(60)
            self.quote_ctx.unsubscribe_all()  # unsubscribe stocks

    def build_local_kline_db(self, symbol_list=None):
        today = datetime.today().strftime("%Y-%m-%d")
        if symbol_list is None:
            symbol_list = self.symbol_list
        assert len(symbol_list) < 300

        fail_symbols = []
        for symbol in symbol_list:
            symbol_kline = self.get_kline_from_futu(symbol, start=self.hist_kline_start, end=today)
            if isinstance(symbol_kline, pd.DataFrame):
                symbol_kline.to_sql(symbol, self.conn, if_exists='replace', chunksize=250, index=False)
                self.conn.commit()
            else:
                fail_symbols.append(symbol)
            time.sleep(0.5)

        if fail_symbols:
            logger.warning('fail_symbols: ' + ','.join(fail_symbols))

    def build_local_basicinfo_db(self):
        # get_plate_list
        ret, plate_list = self.quote_ctx.get_plate_list(Market.HK, Plate.INDUSTRY)
        assert ret == RET_OK

        fields = ['code', 'stock_name', 'plate_code', 'plate_name', 'lot_size', 'list_time']

        max_retry = 3
        plate_stocks = []
        for idx, row in plate_list.iterrows():
            plate = row.code
            plate_name = row.plate_name
            retry = 0
            ret, plate_stock = self.quote_ctx.get_plate_stock(plate)
            while ret != RET_OK and retry < max_retry:
                time.sleep(3)
                retry += 1
                ret, plate_stock = self.quote_ctx.get_plate_stock(plate)

            if ret == RET_OK:
                plate_stock['plate_code'] = plate
                plate_stock['plate_name'] = plate_name
                plate_stocks.append(plate_stock)
                logger.info(plate + ", " + plate_name, ' done!')

            time.sleep(3)

        if plate_stocks:
            basicinfo = pd.concat(plate_stocks)[fields]
            basicinfo.to_sql('basicinfo', self.conn, if_exists='replace', chunksize=250, index=False)
            self.conn.commit()

    def load_kline_from_local_db(self):
        local_tables = self.get_local_symbols()
        sql_read_table = "SELECT * FROM `{table}`"

        for table in local_tables:
            temp = pd.read_sql(sql_read_table.format(table=table), self.conn)
            temp.set_index('time_key', inplace=True)
            temp[KField.atr.name] = talib.ATR(temp[KField.high.name],
                                              temp[KField.low.name],
                                              temp[KField.close.name], timeperiod=20)
            self.hist_kline[table] = temp

    def load_basicinfo_from_local_db(self):
        temp = pd.read_sql("SELECT * FROM basicinfo", self.conn)
        temp.set_index('code', inplace=True)
        self.basicinfo = temp

    def get_lot_size(self, symbol) -> int:
        if self.basicinfo is None:
            raise ValueError('basicinfo is None')
        else:
            try:
                return self.basicinfo.loc[symbol, SField.lot_size.name]
            except KeyError as e:
                logger.info('cannot found ' + str(e) + ' in basicinfo')
                ret, basicinfo = self.quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, [symbol])
                assert ret == RET_OK
                basicinfo.set_index('code', inplace=True)
                lot_size = basicinfo.loc[symbol, SField.lot_size.name]

                if lot_size is None or math.isnan(lot_size):
                    raise ValueError('cannot get lot_size from futu for ' + symbol + ' in ' + self.cur_datetime)
                else:
                    return lot_size

    def get_curr_bar_value(self, symbol, field: KField, rool_back=False):
        """
        Returns one of the Open, High, Low, Close, Volume or OI
        from the last bar.
        """
        try:
            value = self.snapshot.loc[symbol, field.name]
            if math.isnan(value) or value is None:
                raise ValueError("the value of " + symbol + ":" + field.name + " is NaN/None")
            else:
                return value
        except KeyError as e:
            if rool_back:
                if symbol in self.hist_kline:
                    hist_kline = self.hist_kline[symbol]
                    dates = hist_kline.index
                    if self.cur_datetime < dates[0]:
                        raise ValueError("the stock " + symbol + ' has not been IPO yet in ' + self.cur_datetime)

                    last_date = self.time_line[self.hist_index]
                    detla = timedelta(days=1)
                    while last_date not in dates:
                        last_date = datetime.strptime(last_date, self.tfmt) - detla
                        last_date = last_date.strftime(self.tfmt)

                    if last_date in dates:
                        value = self.hist_kline[symbol].loc[last_date, field.name]
                        if math.isnan(value) or value is None:
                            raise ValueError("the value of " + symbol + ":" + field.name + " is NaN/None")
                        else:
                            return value
            raise e

    def get_hist_bars(self, symbol: str, n: int) -> pd.DataFrame:
        if symbol in self.hist_kline:
            start, end = self.time_line[self.hist_index - n + 1], self.time_line[self.hist_index]
            return self.hist_kline[symbol].loc[start:end]
        else:
            ret, kline = self.quote_ctx.get_cur_kline(symbol, n + 1, ktype=self.ktype, autype=self.autype)
            assert ret == RET_OK
            kline.set_index('time_key', inplace=True)
            return kline.iloc[0:-1]

    def get_hist_bars_values(self, symbol: str, val_type: KField, n: int) -> pd.Series:
        return self.get_hist_bars(symbol, n)[val_type.name]

    def update_bars(self):
        if self.run_type == 'back_test':
            self.hist_index += 1
            assert self.hist_index < len(self.time_line)
            self.cur_datetime = self.time_line[self.hist_index + 1]
            try:
                self.update_snapshot()
            except Exception as e:
                raise e

            if len(self.time_line) <= self.hist_index + 2:
                self.continue_backtest = False
        else:
            try:
                self.update_snapshot()
            except Exception as e:
                raise e

        self.events.put(DataEvent(self.cur_datetime))
