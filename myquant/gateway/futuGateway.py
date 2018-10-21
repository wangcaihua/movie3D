# encoding: UTF-8

'''
富途证券的gateway接入
'''

from time import sleep
from copy import copy
from pandas import DataFrame
from datetime import datetime
from collections import OrderedDict

import futuquant as ft
from futuquant import RET_ERROR, RET_OK
from futuquant import StockQuoteHandlerBase, OrderBookHandlerBase
from futuquant import TradeOrderHandlerBase, TradeDealHandlerBase
from futuquant.trade.open_trade_context import (OpenTradeContextBase,
                                                OpenHKTradeContext,
                                                OpenUSTradeContext,
                                                OpenHKCCTradeContext,
                                                OpenCNTradeContext)

from myquant.framework import *
from myquant.constant import *
from myquant.dataStruct import *
from myquant.utils import getJsonPath

# 调用一次datetime，保证初始化
tmp = datetime.strptime('20171123', '%Y%m%d')

# 常量数据映射
productMap = OrderedDict()
productMap[PRODUCT_EQUITY] = ft.SecurityType.STOCK
productMap[PRODUCT_INDEX] = ft.SecurityType.IDX
productMap[PRODUCT_ETF] = ft.SecurityType.ETF
productMap[PRODUCT_WARRANT] = ft.SecurityType.WARRANT
productMap[PRODUCT_BOND] = ft.SecurityType.BOND
productMap[PRODUCT_DRVT] = ft.SecurityType.DRVT
productMap[PRODUCT_NONE] = ft.SecurityType.NONE

directionMap = {}
directionMap[DIRECTION_LONG] = '0'
directionMap[DIRECTION_SHORT] = '1'
directionMapReverse = {v: k for k, v in directionMap.items()}

statusMapReverse = {}
statusMapReverse['0'] = STATUS_UNKNOWN
statusMapReverse['1'] = STATUS_NOTTRADED
statusMapReverse['2'] = STATUS_PARTTRADED
statusMapReverse['3'] = STATUS_ALLTRADED
statusMapReverse['4'] = STATUS_CANCELLED
statusMapReverse['5'] = STATUS_REJECTED
statusMapReverse['6'] = STATUS_CANCELLED
statusMapReverse['7'] = STATUS_CANCELLED
statusMapReverse['8'] = STATUS_UNKNOWN
statusMapReverse['21'] = STATUS_UNKNOWN
statusMapReverse['22'] = STATUS_UNKNOWN
statusMapReverse['23'] = STATUS_UNKNOWN


class FutuGateway(VtGateway):
    """富途接口"""

    def __init__(self, eventEngine, host: str, port: int, market: str, password: str, env: int = 1):
        """Constructor"""
        super(FutuGateway, self).__init__(eventEngine, gatewayName='FUTU')

        self.quoteCtx: ft.OpenQuoteContext = None
        self.tradeCtx: OpenTradeContextBase = None

        self.host = host
        self.port = port
        self.market = market
        self.password = password
        self.env = env  # 默认仿真交易, env = 1

        self.fileName = self.gatewayName + '_connect.json'
        self.filePath = getJsonPath(self.fileName, __file__)

        self.tickDict = {}
        self.tradeSet = set()  # 保存成交编号的集合，防止重复推送

        self.qryEnabled = True
        self.qryFunctionList = [self.qryAccount, self.qryPosition]
        self.qryCount: int = 0  # 查询触发倒计时
        self.qryTrigger: int = 2  # 查询触发点
        self.qryNextFunction: int = 0  # 上次运行的查询函数索引

    def writeLog(self, content: str):
        """输出日志"""
        log = VtLogData()
        log.gatewayName = self.gatewayName
        log.logContent = content
        self.onLog(log)

    def writeError(self, code: str, msg: str):
        """输出错误"""
        error = VtErrorData()
        error.gatewayName = self.gatewayName
        error.errorID = code
        error.errorMsg = msg
        self.onError(error)

    def connect(self):
        """连接"""
        self.connectQuote()
        self.connectTrade()

        # 等待2秒保证行情和交易接口启动完成
        sleep(2.0)
        self.initQuery()

    def initQuery(self):
        """初始化时查询数据"""
        # 查询合约、成交、委托、持仓、账户
        self.qryContract()
        self.qryTrade()
        self.qryOrder()
        self.qryPosition()
        self.qryAccount()

        # 通过Timer启动循环查询
        if self.qryEnabled:
            self.eventEngine.register(Event.TIMER, self.query)

    def connectQuote(self):
        """连接行情功能"""
        self.quoteCtx = ft.OpenQuoteContext(self.host, self.port)

        # 用于异步处理推送的订阅股票的报价
        class QuoteHandler(StockQuoteHandlerBase):
            """报价处理器"""
            gateway = self  # 缓存Gateway对象

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(QuoteHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.gateway.processQuote(content)
                return RET_OK, content

        # 用于异步处理推送的实时摆盘
        class OrderBookHandler(OrderBookHandlerBase):
            """订单簿处理器"""
            gateway = self

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(OrderBookHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.gateway.processOrderBook(content)
                return RET_OK, content

        # 设置回调处理对象
        self.quoteCtx.set_handler(QuoteHandler())
        self.quoteCtx.set_handler(OrderBookHandler())

        # 启动行情
        self.quoteCtx.start()

        self.writeLog(u'行情接口连接成功')

    def connectTrade(self):
        """连接交易功能"""
        # 连接交易接口
        assert self.market in ["UK", "HK", "CN", "HKCC"]
        if self.market == 'US':
            self.tradeCtx = OpenUSTradeContext(self.host, self.port)
        elif self.market == 'HK':
            self.tradeCtx = OpenHKTradeContext(self.host, self.port)
        elif self.market == "CN":
            self.tradeCtx = OpenCNTradeContext(self.host, self.port)
        else:
            self.tradeCtx = OpenHKCCTradeContext(self.host, self.port)

        # 响应订单推送
        class OrderHandler(TradeOrderHandlerBase):
            """委托处理器"""
            gateway = self  # 缓存Gateway对象

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(OrderHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.gateway.processOrder(content)
                return RET_OK, content

        # 响应成交推送
        class DealHandler(TradeDealHandlerBase):
            """订单簿处理器"""
            gateway = self

            def on_recv_rsp(self, rsp_str):
                ret_code, content = super(DealHandler, self).on_recv_rsp(rsp_str)
                if ret_code != RET_OK:
                    return RET_ERROR, content
                self.gateway.processDeal(content)
                return RET_OK, content

                # 只有港股实盘交易才需要解锁

        if self.market == 'HK' and self.env == 0:
            self.tradeCtx.unlock_trade(self.password)

        # 设置回调处理对象
        self.tradeCtx.set_handler(OrderHandler())
        self.tradeCtx.set_handler(DealHandler())

        # 启动交易接口
        self.tradeCtx.start()

        # 订阅委托推送
        # self.tradeCtx.subscribe_order_deal_push(
        #     [], order_deal_push=True, envtype=self.env)

        self.writeLog(u'交易接口连接成功')

    def subscribe(self, subscribeReq: VtSubscribeReq):
        """订阅行情"""

        for data_type in [ft.SubType.QUOTE, ft.SubType.ORDER_BOOK]:
            ret, err_message = self.quoteCtx.subscribe(subscribeReq.symbol, data_type, True)

            if ret == RET_OK:
                self.writeError(ret, u'订阅行情失败：%s' % err_message)

    def sendOrder(self, orderReq: VtOrderReq):
        """发单"""
        side = directionMap[orderReq.direction]
        orderType = ft.OrderType.NORMAL  # 只支持限价单

        code, data = self.tradeCtx.place_order(
            price=orderReq.price, qty=orderReq.volume, code=orderReq.symbol,
            trd_side=side, order_type=orderType, trd_env=self.env)

        if code:
            self.writeError(code, u'委托失败：%s' % data)
            return ''

        for ix, row in data.iterrows():
            orderID = str(row['orderid'])

        vtOrderID = '.'.join([self.gatewayName, orderID])

        return vtOrderID

    def cancelOrder(self, cancelOrderReq: VtCancelOrderReq):
        """撤单"""
        code, data = self.tradeCtx.modify_order(
            modify_order_op=ft.ModifyOrderOp.CANCEL, order_id=int(cancelOrderReq.orderID),
            qty=0, price=0, trd_env=self.env)

        if code:
            self.writeError(code, u'撤单失败：%s' % data)
            return

    def qryContract(self):
        """查询合约"""
        for vtProductClass, product in productMap.items():
            code, data = self.quoteCtx.get_stock_basicinfo(self.market, product)

            if code:
                self.writeError(code, u'查询合约信息失败：%s' % data)
                return

            for ix, row in data.iterrows():
                contract = VtContractData()
                contract.gatewayName = self.gatewayName

                contract.symbol = row['code']
                contract.vtSymbol = contract.symbol
                contract.name = row['name']
                contract.productClass = vtProductClass
                contract.size = int(row['lot_size'])
                contract.priceTick = 0.01

                self.onContract(contract)

        self.writeLog(u'合约信息查询成功')

    def qryAccount(self):
        """查询账户资金"""
        code, data = self.tradeCtx.accinfo_query(self.env)

        if code:
            self.writeError(code, u'查询账户资金失败：%s' % data)
            return

        for ix, row in data.iterrows():
            account = VtAccountData()
            account.gatewayName = self.gatewayName

            account.accountID = '%s_%s' % (self.gatewayName, self.market)
            account.vtAccountID = '.'.join([self.gatewayName, account.accountID])
            account.balance = float(row['ZCJZ'])
            account.margin = float(row['GPBZJ'])
            account.available = float(row['XJJY'])

            self.onAccount(account)

    def qryPosition(self):
        """查询持仓"""
        code, data = self.tradeCtx.position_list_query(trd_env=self.env)

        if code:
            self.writeError(code, u'查询持仓失败：%s' % data)
            return

        for ix, row in data.iterrows():
            pos = VtPositionData()
            pos.gatewayName = self.gatewayName

            pos.symbol = row['code']
            pos.vtSymbol = pos.symbol

            pos.direction = DIRECTION_LONG
            pos.vtPositionName = '.'.join([pos.vtSymbol, pos.direction])

            pos.position = int(row['qty'])
            pos.price = float(row['cost_price'])
            pos.positionProfit = float(row['pl_val'])
            pos.frozen = int(row['qty']) - int(row['can_sell_qty'])

            if pos.price < 0:
                pos.price = 0
            if pos.positionProfit > 100000000:
                pos.positionProfit = 0

            self.onPosition(pos)

    def qryOrder(self):
        """查询委托"""
        code, data = self.tradeCtx.order_list_query("", trd_env=self.env)

        if code:
            self.writeError(code, u'查询委托失败：%s' % data)
            return

        self.processOrder(data)
        self.writeLog(u'委托查询成功')

    def qryTrade(self):
        """查询成交"""
        code, data = self.tradeCtx.deal_list_query(self.env)

        if code:
            self.writeError(code, u'查询成交失败：%s' % data)
            return

        self.processDeal(data)
        self.writeLog(u'成交查询成功')

    def close(self):
        """关闭"""
        if self.quoteCtx:
            self.quoteCtx.close()
        if self.tradeCtx:
            self.tradeCtx.close()

    def query(self, event: Event):
        """注册到事件处理引擎上的查询函数"""
        assert event.type_ == Event.TIMER

        self.qryCount += 1
        if self.qryCount > self.qryTrigger:
            # 清空倒计时
            self.qryCount = 0

            # 执行查询函数
            func = self.qryFunctionList[self.qryNextFunction]
            func()

            # 计算下次查询函数的索引，如果超过了列表长度，则重新设为0
            self.qryNextFunction += 1
            if self.qryNextFunction == len(self.qryFunctionList):
                self.qryNextFunction = 0

    def setQryEnabled(self, qryEnabled: bool):
        """设置是否要启动循环查询"""
        self.qryEnabled = qryEnabled

    def processQuote(self, data: DataFrame):
        """报价推送"""
        for ix, row in data.iterrows():
            symbol = row['code']

            tick: VtTickData = self.tickDict.get(symbol, None)
            if not tick:
                tick = VtTickData()
                tick.symbol = symbol
                tick.vtSymbol = tick.symbol
                tick.gatewayName = self.gatewayName
                self.tickDict[symbol] = tick

            tick.date = row['data_date'].replace('-', '')
            tick.time = row['data_time']
            tick.datetime = datetime.strptime(' '.join([tick.date, tick.time]), '%Y%m%d %H:%M:%S')
            tick.openPrice = row['open_price']
            tick.highPrice = row['high_price']
            tick.lowPrice = row['low_price']
            tick.preClosePrice = row['prev_close_price']

            tick.lastPrice = row['last_price']
            tick.volume = row['volume']

            if 'price_spread' in row:
                spread = row['price_spread']
                tick.upperLimit = tick.lastPrice + spread * 10
                tick.lowerLimit = tick.lastPrice - spread * 10

            newTick = copy(tick)
            self.onTick(newTick)

    def processOrderBook(self, data):
        """订单簿推送"""
        symbol = data['stock_code']

        tick: VtTickData = self.tickDict.get(symbol, None)
        if not tick:
            tick = VtTickData()
            tick.symbol = symbol
            tick.vtSymbol = tick.symbol
            tick.gatewayName = self.gatewayName
            self.tickDict[symbol] = tick

        for i in range(5):
            (bidPrice, bidVolume) = data['Bid'][i]
            (askPrice, askVolume) = data['Ask'][i]
            n = i + 1

            setattr(tick, 'bidPrice%s' % n, bidPrice)
            setattr(tick, 'bidVolume%s' % n, bidVolume)
            setattr(tick, 'askPrice%s' % n % n, askPrice)
            setattr(tick, 'askVolume%s' % n, askVolume)

        if tick.datetime:
            newTick = copy(tick)
            self.onTick(newTick)

    def processOrder(self, data: DataFrame):
        """处理委托推送"""
        for ix, row in data.iterrows():
            # 如果状态是已经删除，则直接忽略
            if str(row['status']) == '7':
                continue

            order: VtOrderData = VtOrderData()
            order.gatewayName = self.gatewayName

            order.symbol = row['code']
            order.vtSymbol = order.symbol

            order.orderID = str(row['orderid'])
            order.vtOrderID = '.'.join([self.gatewayName, order.orderID])

            order.price = float(row['price'])
            order.totalVolume = int(row['qty'])
            order.tradedVolume = int(row['dealt_qty'])

            submittedTime = datetime.fromtimestamp(float(row['submitted_time']))
            order.orderTime = submittedTime.strftime('%H:%M:%S')

            order.status = statusMapReverse.get(str(row['status']), STATUS_UNKNOWN)
            order.direction = directionMapReverse[str(row['order_side'])]
            self.onOrder(order)

    def processDeal(self, data: DataFrame):
        """处理成交推送"""
        for ix, row in data.iterrows():
            tradeID = row['dealid']
            if tradeID in self.tradeSet:
                continue
            self.tradeSet.add(tradeID)

            trade: VtTradeData = VtTradeData()
            trade.gatewayName = self.gatewayName

            trade.symbol = row['code']
            trade.vtSymbol = trade.symbol

            trade.tradeID = tradeID
            trade.vtTradeID = '.'.join([self.gatewayName, trade.tradeID])

            trade.orderID = row['orderid']
            trade.vtOrderID = '.'.join([self.gatewayName, trade.orderID])

            trade.price = float(row['price'])
            trade.volume = float(row['qty'])
            trade.direction = directionMapReverse[str(row['order_side'])]

            time_ = datetime.fromtimestamp(float(row['time']))
            trade.tradeTime = time_.strftime('%H:%M:%S')

            self.onTrade(trade)
