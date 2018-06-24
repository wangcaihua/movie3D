import pandas as pd
import tushare as ts
import sqlite3 as lite


class DataBase:
    def __init__(self, name):
        self.name = name
        self.conn = lite.connect(name)
        self.cur = self.conn.cursor()
        self.tables = {}

    def create_table(self, name, dtypes, columns):
        table = Table(name, self.conn)
        table.create(dtypes, columns)
        self.tables[name] = table

    def drop_table(self, name):
        stmt = "DROP TABLE {name};".format(name=name)
        self.conn.execute(stmt)

    def get_table(self, name):
        if name in self.tables:
            return self.tables[name]
        else:
            table = Table(name, self.conn)
            self.tables[name] = table
            return table

    def close(self):
        self.conn.close()


class Table:
    def __init__(self, name, conn):
        self.name = name
        self.conn = conn
        self.dtypes_ = None
        self.columns_ = None

    def create(self, dtypes, columns):
        self.dtypes_ = dtypes
        self.columns_ = columns
        stmt = "CREATE TABLE {name} ({col_type});".format(
            name=self.name,
            col_type=",".join(["{column} {dtype}".format(column=column, dtype=dtype)
                               for column, dtype in zip(columns, dtypes)])
        )
        self.conn.execute(stmt)

    def insert(self, data):
        pass

    def delete(self):
        pass

    def update(self):
        pass

    def slect(self):
        pass

    @property
    def dtypes(self):
        if self.dtypes is None or len(self.dtypes) == 0:
            return []
        else:
            return self.dtypes_

    @property
    def columns(self):
        if self.columns_ is None or len(self.columns_) == 0:
            cur = self.conn.cursor()
            res = cur.execute("PRAGMA table_info({tbname})".format(tbname="name"))
            self.columns_ = [tp[1] for tp in res.fetchall()]
            cur.close()
            return self.columns_
        else:
            return self.columns_


conn = lite.connect("data.db")
cur = conn.cursor()
res1 = cur.execute("select name from sqlite_master where type = 'table' order by name")
res2 = cur.execute("select * from {tbname} where 0=1".format(tbname="name"))
res3 = cur.execute("PRAGMA table_info({tbname})".format(tbname="name"))

print(res3.fetchall())
