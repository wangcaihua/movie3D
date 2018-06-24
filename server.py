import json
from flask import Flask, url_for
from flask import request, make_response, Response
from flask import render_template

app = Flask(__name__)


'''
1. route
'''


@app.route('/')
def index():
    return render_template('index.html')

'''
{
    "上证指数": [point, various, label],
    "恒生指数": [point, various, label],
    "道琼斯指数": [point, various, label],
    ------
    "保险": [point, various, label],
    "半导体": [点数, 涨跌幅, 标记],
    ......
}
'''


@app.route('/get_index_and_block', methods=["GET"])
def get_index_and_block():
    pass


'''
{
    "code": [name, price, various],
    "code": [name, price, various],
    ......
}
'''


@app.route('/get_stocks_in_block', methods=["GET"])
def get_stocks_in_block():
    pass

'''
{
    kline: [
                [time, open, high, close, low],
                [time, open, high, close, low],
                [time, open, high, close, low],
            ],
    mavg: [
                [time, ma5, ma10, ma20, predict],
                [time, ma5, ma10, ma20, predict],
                [time, ma5, ma10, ma20, predict]
            ],
    volume: [
                [time, volume],
                [time, volume],
                [time, volume]
            ],
    starttime: "2005-12-9",
    stoptime: "2018-5-21",
    length: "3908"
}
'''


@app.route('/get_stock_data', methods=["GET"])
def get_stock_data():
    pass


if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=True)
