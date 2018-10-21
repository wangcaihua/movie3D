# encoding: UTF-8

import time
from logging import INFO

from copy import copy
from myquant.constant import *
from typing import List, Dict

__all__ = ['VtBaseData', 'VtTickData', 'VtBarData', 'VtTradeData', 'VtOrderData', 'VtPositionData',
           'VtAccountData', 'VtAccountData', 'VtErrorData', 'VtContractData', 'VtSubscribeReq', 'VtOrderReq',
           'VtCancelOrderReq', 'VtSingleton', 'VtLogData', 'VtPositionDetail']


class VtBaseData(object):
    """回调函数推送数据的基础类，其他数据类继承于此"""

    def __init__(self):
        """Constructor"""
        self.gatewayName = EMPTY_STRING  # Gateway名称
        self.rawData = None  # 原始数据


class VtTickData(VtBaseData):
    """Tick行情数据类"""

    def __init__(self):
        """Constructor"""
        super(VtTickData, self).__init__()

        # 代码相关
        self.symbol = EMPTY_STRING  # 合约代码
        self.exchange = EMPTY_STRING  # 交易所代码
        self.vtSymbol = EMPTY_STRING  # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码

        # 成交数据
        self.lastPrice = EMPTY_FLOAT  # 最新成交价
        self.lastVolume = EMPTY_INT  # 最新成交量
        self.volume = EMPTY_INT  # 今天总成交量
        self.openInterest = EMPTY_INT  # 持仓量
        self.time = EMPTY_STRING  # 时间 11:20:56.5
        self.date = EMPTY_STRING  # 日期 20151009
        self.datetime = None  # python的datetime时间对象

        # 常规行情
        self.openPrice = EMPTY_FLOAT  # 今日开盘价
        self.highPrice = EMPTY_FLOAT  # 今日最高价
        self.lowPrice = EMPTY_FLOAT  # 今日最低价
        self.preClosePrice = EMPTY_FLOAT

        self.upperLimit = EMPTY_FLOAT  # 涨停价
        self.lowerLimit = EMPTY_FLOAT  # 跌停价

        # 五档行情
        self.bidPrice1 = EMPTY_FLOAT
        self.bidPrice2 = EMPTY_FLOAT
        self.bidPrice3 = EMPTY_FLOAT
        self.bidPrice4 = EMPTY_FLOAT
        self.bidPrice5 = EMPTY_FLOAT

        self.askPrice1 = EMPTY_FLOAT
        self.askPrice2 = EMPTY_FLOAT
        self.askPrice3 = EMPTY_FLOAT
        self.askPrice4 = EMPTY_FLOAT
        self.askPrice5 = EMPTY_FLOAT

        self.bidVolume1 = EMPTY_INT
        self.bidVolume2 = EMPTY_INT
        self.bidVolume3 = EMPTY_INT
        self.bidVolume4 = EMPTY_INT
        self.bidVolume5 = EMPTY_INT

        self.askVolume1 = EMPTY_INT
        self.askVolume2 = EMPTY_INT
        self.askVolume3 = EMPTY_INT
        self.askVolume4 = EMPTY_INT
        self.askVolume5 = EMPTY_INT


class VtBarData(VtBaseData):
    """K线数据"""

    def __init__(self):
        """Constructor"""
        super(VtBarData, self).__init__()

        self.vtSymbol = EMPTY_STRING  # vt系统代码
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所

        self.open = EMPTY_FLOAT  # OHLC
        self.high = EMPTY_FLOAT
        self.low = EMPTY_FLOAT
        self.close = EMPTY_FLOAT

        self.date = EMPTY_STRING  # bar开始的时间，日期
        self.time = EMPTY_STRING  # 时间
        self.datetime = None  # python的datetime时间对象

        self.volume = EMPTY_INT  # 成交量
        self.openInterest = EMPTY_INT  # 持仓量


class VtTradeData(VtBaseData):
    """成交数据类"""

    def __init__(self):
        """Constructor"""
        super(VtTradeData, self).__init__()

        # 代码编号相关
        self.symbol = EMPTY_STRING  # 合约代码
        self.exchange = EMPTY_STRING  # 交易所代码
        self.vtSymbol = EMPTY_STRING  # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码

        self.tradeID = EMPTY_STRING  # 成交编号
        self.vtTradeID = EMPTY_STRING  # 成交在vt系统中的唯一编号，通常是 Gateway名.成交编号

        self.orderID = EMPTY_STRING  # 订单编号
        self.vtOrderID = EMPTY_STRING  # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号

        # 成交相关
        self.direction = EMPTY_UNICODE  # 成交方向
        self.offset = EMPTY_UNICODE  # 成交开平仓
        self.price = EMPTY_FLOAT  # 成交价格
        self.volume = EMPTY_INT  # 成交数量
        self.tradeTime = EMPTY_STRING  # 成交时间


class VtOrderData(VtBaseData):
    """订单数据类"""

    def __init__(self):
        """Constructor"""
        super(VtOrderData, self).__init__()

        # 代码编号相关
        self.symbol = EMPTY_STRING  # 合约代码
        self.exchange = EMPTY_STRING  # 交易所代码
        self.vtSymbol = EMPTY_STRING  # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码

        self.orderID = EMPTY_STRING  # 订单编号
        self.vtOrderID = EMPTY_STRING  # 订单在vt系统中的唯一编号，通常是 Gateway名.订单编号

        # 报单相关
        self.direction = EMPTY_UNICODE  # 报单方向
        self.offset = EMPTY_UNICODE  # 报单开平仓
        self.price = EMPTY_FLOAT  # 报单价格
        self.totalVolume = EMPTY_INT  # 报单总数量
        self.tradedVolume = EMPTY_INT  # 报单成交数量
        self.status = EMPTY_UNICODE  # 报单状态

        self.orderTime = EMPTY_STRING  # 发单时间
        self.cancelTime = EMPTY_STRING  # 撤单时间

        # CTP/LTS相关
        self.frontID = EMPTY_INT  # 前置机编号
        self.sessionID = EMPTY_INT  # 连接编号


class VtPositionData(VtBaseData):
    """持仓数据类"""

    def __init__(self):
        """Constructor"""
        super(VtPositionData, self).__init__()

        # 代码编号相关
        self.symbol = EMPTY_STRING  # 合约代码
        self.exchange = EMPTY_STRING  # 交易所代码
        self.vtSymbol = EMPTY_STRING  # 合约在vt系统中的唯一代码，合约代码.交易所代码

        # 持仓相关
        self.direction = EMPTY_STRING  # 持仓方向
        self.position = EMPTY_INT  # 持仓量
        self.frozen = EMPTY_INT  # 冻结数量
        self.price = EMPTY_FLOAT  # 持仓均价
        self.vtPositionName = EMPTY_STRING  # 持仓在vt系统中的唯一代码，通常是vtSymbol.方向
        self.ydPosition = EMPTY_INT  # 昨持仓
        self.positionProfit = EMPTY_FLOAT  # 持仓盈亏


class VtAccountData(VtBaseData):
    """账户数据类"""

    def __init__(self):
        """Constructor"""
        super(VtAccountData, self).__init__()

        # 账号代码相关
        self.accountID = EMPTY_STRING  # 账户代码
        self.vtAccountID = EMPTY_STRING  # 账户在vt中的唯一代码，通常是 Gateway名.账户代码

        # 数值相关
        self.preBalance = EMPTY_FLOAT  # 昨日账户结算净值
        self.balance = EMPTY_FLOAT  # 账户净值
        self.available = EMPTY_FLOAT  # 可用资金
        self.commission = EMPTY_FLOAT  # 今日手续费
        self.margin = EMPTY_FLOAT  # 保证金占用
        self.closeProfit = EMPTY_FLOAT  # 平仓盈亏
        self.positionProfit = EMPTY_FLOAT  # 持仓盈亏


class VtErrorData(VtBaseData):
    """错误数据类"""

    def __init__(self):
        """Constructor"""
        super(VtErrorData, self).__init__()

        self.errorID = EMPTY_STRING  # 错误代码
        self.errorMsg = EMPTY_UNICODE  # 错误信息
        self.additionalInfo = EMPTY_UNICODE  # 补充信息

        self.errorTime = time.strftime('%X', time.localtime())  # 错误生成时间


class VtLogData(VtBaseData):
    """日志数据类"""

    def __init__(self):
        """Constructor"""
        super(VtLogData, self).__init__()

        self.logTime = time.strftime('%X', time.localtime())  # 日志生成时间
        self.logContent = EMPTY_UNICODE  # 日志信息
        self.logLevel = INFO  # 日志级别


class VtContractData(VtBaseData):
    """合约详细信息类"""

    def __init__(self):
        """Constructor"""
        super(VtContractData, self).__init__()

        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所代码
        self.vtSymbol = EMPTY_STRING  # 合约在vt系统中的唯一代码，通常是 合约代码.交易所代码
        self.name = EMPTY_UNICODE  # 合约中文名

        self.productClass = EMPTY_UNICODE  # 合约类型
        self.size = EMPTY_INT  # 合约大小
        self.priceTick = EMPTY_FLOAT  # 合约最小价格TICK

        # 期权相关
        self.strikePrice = EMPTY_FLOAT  # 期权行权价
        self.underlyingSymbol = EMPTY_STRING  # 标的物合约代码
        self.optionType = EMPTY_UNICODE  # 期权类型
        self.expiryDate = EMPTY_STRING  # 到期日


class VtSubscribeReq(object):
    """订阅行情时传入的对象类"""

    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所

        # 以下为IB相关
        self.productClass = EMPTY_UNICODE  # 合约类型
        self.currency = EMPTY_STRING  # 合约货币
        self.expiry = EMPTY_STRING  # 到期日
        self.strikePrice = EMPTY_FLOAT  # 行权价
        self.optionType = EMPTY_UNICODE  # 期权类型


class VtOrderReq(object):
    """发单时传入的对象类"""

    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所
        self.vtSymbol = EMPTY_STRING  # VT合约代码
        self.price = EMPTY_FLOAT  # 价格
        self.volume = EMPTY_INT  # 数量

        self.priceType = EMPTY_STRING  # 价格类型
        self.direction = EMPTY_STRING  # 买卖
        self.offset = EMPTY_STRING  # 开平

        # 以下为IB相关
        self.productClass = EMPTY_UNICODE  # 合约类型
        self.currency = EMPTY_STRING  # 合约货币
        self.expiry = EMPTY_STRING  # 到期日
        self.strikePrice = EMPTY_FLOAT  # 行权价
        self.optionType = EMPTY_UNICODE  # 期权类型
        self.lastTradeDateOrContractMonth = EMPTY_STRING  # 合约月,IB专用
        self.multiplier = EMPTY_STRING  # 乘数,IB专用


class VtCancelOrderReq(object):
    """撤单时传入的对象类"""

    def __init__(self):
        """Constructor"""
        self.symbol = EMPTY_STRING  # 代码
        self.exchange = EMPTY_STRING  # 交易所
        self.vtSymbol = EMPTY_STRING  # VT合约代码

        # 以下字段主要和CTP、LTS类接口相关
        self.orderID = EMPTY_STRING  # 报单号
        self.frontID = EMPTY_STRING  # 前置机号
        self.sessionID = EMPTY_STRING  # 会话号


class VtSingleton(type):
    """
    单例，应用方式:静态变量 __metaclass__ = Singleton
    """

    _instances = {}

    def __call__(cls, *args, **kwargs):
        """调用"""
        if cls not in cls._instances:
            cls._instances[cls] = super(VtSingleton, cls).__call__(*args, **kwargs)

        return cls._instances[cls]


class VtPositionDetail(object):
    """本地维护的持仓信息"""
    WORKING_STATUS = [STATUS_UNKNOWN, STATUS_NOTTRADED, STATUS_PARTTRADED]

    MODE_NORMAL = 'normal'  # 普通模式
    MODE_SHFE = 'shfe'  # 上期所今昨分别平仓
    MODE_TDPENALTY = 'tdpenalty'  # 平今惩罚

    def __init__(self, vtSymbol: str, contract: VtContractData = None):
        """Constructor"""
        self.vtSymbol: str = vtSymbol
        self.symbol: str = EMPTY_STRING
        self.exchange: str = EMPTY_STRING
        self.name: str = EMPTY_UNICODE
        self.size: int = 1

        if contract:
            self.symbol = contract.symbol
            self.exchange = contract.exchange
            self.name = contract.name
            self.size = contract.size

        self.longPos: int = EMPTY_INT
        self.longYd: int = EMPTY_INT
        self.longTd: int = EMPTY_INT
        self.longPosFrozen: int = EMPTY_INT
        self.longYdFrozen: int = EMPTY_INT
        self.longTdFrozen: int = EMPTY_INT
        self.longPnl: float = EMPTY_FLOAT
        self.longPrice: float = EMPTY_FLOAT

        self.shortPos: int = EMPTY_INT
        self.shortYd: int = EMPTY_INT
        self.shortTd: int = EMPTY_INT
        self.shortPosFrozen: int = EMPTY_INT
        self.shortYdFrozen: int = EMPTY_INT
        self.shortTdFrozen: int = EMPTY_INT
        self.shortPnl: float = EMPTY_FLOAT
        self.shortPrice: float = EMPTY_FLOAT

        self.lastPrice = EMPTY_FLOAT

        self.mode = self.MODE_NORMAL
        self.exchange: str = EMPTY_STRING

        self.workingOrderDict: Dict[str, VtOrderData] = {}

    def updateTrade(self, trade: VtTradeData):
        """成交更新"""
        # 多头
        if trade.direction is DIRECTION_LONG:
            # 开仓
            if trade.offset is OFFSET_OPEN:
                self.longTd += trade.volume
            # 平今
            elif trade.offset is OFFSET_CLOSETODAY:
                self.shortTd -= trade.volume
            # 平昨
            elif trade.offset is OFFSET_CLOSEYESTERDAY:
                self.shortYd -= trade.volume
            # 平仓
            elif trade.offset is OFFSET_CLOSE:
                # 上期所等同于平昨
                if self.exchange is EXCHANGE_SHFE:
                    self.shortYd -= trade.volume
                # 非上期所，优先平今
                else:
                    self.shortTd -= trade.volume

                    if self.shortTd < 0:
                        self.shortYd += self.shortTd
                        self.shortTd = 0
                        # 空头
        elif trade.direction is DIRECTION_SHORT:
            # 开仓
            if trade.offset is OFFSET_OPEN:
                self.shortTd += trade.volume
            # 平今
            elif trade.offset is OFFSET_CLOSETODAY:
                self.longTd -= trade.volume
            # 平昨
            elif trade.offset is OFFSET_CLOSEYESTERDAY:
                self.longYd -= trade.volume
            # 平仓
            elif trade.offset is OFFSET_CLOSE:
                # 上期所等同于平昨
                if self.exchange is EXCHANGE_SHFE:
                    self.longYd -= trade.volume
                # 非上期所，优先平今
                else:
                    self.longTd -= trade.volume

                    if self.longTd < 0:
                        self.longYd += self.longTd
                        self.longTd = 0

        # 汇总
        self.calculatePrice(trade)
        self.calculatePosition()
        self.calculatePnl()

    def updateOrder(self, order: VtOrderData):
        """委托更新"""
        # 将活动委托缓存下来
        if order.status in self.WORKING_STATUS:
            self.workingOrderDict[order.vtOrderID] = order

        # 移除缓存中已经完成的委托
        else:
            if order.vtOrderID in self.workingOrderDict:
                del self.workingOrderDict[order.vtOrderID]

        # 计算冻结
        self.calculateFrozen()

    def updatePosition(self, pos: VtPositionData):
        """持仓更新"""
        if pos.direction is DIRECTION_LONG:
            self.longPos = pos.position
            self.longYd = pos.ydPosition
            self.longTd = self.longPos - self.longYd
            self.longPnl = pos.positionProfit
            self.longPrice = pos.price
        elif pos.direction is DIRECTION_SHORT:
            self.shortPos = pos.position
            self.shortYd = pos.ydPosition
            self.shortTd = self.shortPos - self.shortYd
            self.shortPnl = pos.positionProfit
            self.shortPrice = pos.price

        # self.output()

    def updateOrderReq(self, req: VtOrderReq, vtOrderID: str):
        """发单更新"""
        vtSymbol = req.vtSymbol

        # 基于请求生成委托对象
        order = VtOrderData()
        order.vtSymbol = vtSymbol
        order.symbol = req.symbol
        order.exchange = req.exchange
        order.offset = req.offset
        order.direction = req.direction
        order.totalVolume = req.volume
        order.status = STATUS_UNKNOWN

        # 缓存到字典中
        self.workingOrderDict[vtOrderID] = order

        # 计算冻结量
        self.calculateFrozen()

    def updateTick(self, tick: VtTickData):
        """行情更新"""
        self.lastPrice = tick.lastPrice
        self.calculatePnl()

    def calculatePnl(self):
        """计算持仓盈亏"""
        self.longPnl = self.longPos * (self.lastPrice - self.longPrice) * self.size
        self.shortPnl = self.shortPos * (self.shortPrice - self.lastPrice) * self.size

    def calculatePrice(self, trade):
        """计算持仓均价（基于成交数据）"""
        # 只有开仓会影响持仓均价
        if trade.offset == OFFSET_OPEN:
            if trade.direction == DIRECTION_LONG:
                cost = self.longPrice * self.longPos
                cost += trade.volume * trade.price
                newPos = self.longPos + trade.volume
                if newPos:
                    self.longPrice = cost / newPos
                else:
                    self.longPrice = 0
            else:
                cost = self.shortPrice * self.shortPos
                cost += trade.volume * trade.price
                newPos = self.shortPos + trade.volume
                if newPos:
                    self.shortPrice = cost / newPos
                else:
                    self.shortPrice = 0

    def calculatePosition(self):
        """计算持仓情况"""
        self.longPos = self.longTd + self.longYd
        self.shortPos = self.shortTd + self.shortYd

    def calculateFrozen(self):
        """计算冻结情况"""
        # 清空冻结数据
        self.longPosFrozen = EMPTY_INT
        self.longYdFrozen = EMPTY_INT
        self.longTdFrozen = EMPTY_INT
        self.shortPosFrozen = EMPTY_INT
        self.shortYdFrozen = EMPTY_INT
        self.shortTdFrozen = EMPTY_INT

        # 遍历统计
        for order in self.workingOrderDict.values():
            # 计算剩余冻结量
            frozenVolume = order.totalVolume - order.tradedVolume

            # 多头委托
            if order.direction is DIRECTION_LONG:
                # 平今
                if order.offset is OFFSET_CLOSETODAY:
                    self.shortTdFrozen += frozenVolume
                # 平昨
                elif order.offset is OFFSET_CLOSEYESTERDAY:
                    self.shortYdFrozen += frozenVolume
                # 平仓
                elif order.offset is OFFSET_CLOSE:
                    self.shortTdFrozen += frozenVolume

                    if self.shortTdFrozen > self.shortTd:
                        self.shortYdFrozen += (self.shortTdFrozen - self.shortTd)
                        self.shortTdFrozen = self.shortTd
            # 空头委托
            elif order.direction is DIRECTION_SHORT:
                # 平今
                if order.offset is OFFSET_CLOSETODAY:
                    self.longTdFrozen += frozenVolume
                # 平昨
                elif order.offset is OFFSET_CLOSEYESTERDAY:
                    self.longYdFrozen += frozenVolume
                # 平仓
                elif order.offset is OFFSET_CLOSE:
                    self.longTdFrozen += frozenVolume

                    if self.longTdFrozen > self.longTd:
                        self.longYdFrozen += (self.longTdFrozen - self.longTd)
                        self.longTdFrozen = self.longTd

            # 汇总今昨冻结
            self.longPosFrozen = self.longYdFrozen + self.longTdFrozen
            self.shortPosFrozen = self.shortYdFrozen + self.shortTdFrozen

    def output(self):
        """"""
        print(self.vtSymbol, '-' * 30)
        print('long, total:%s, td:%s, yd:%s' % (self.longPos, self.longTd, self.longYd))
        print('long frozen, total:%s, td:%s, yd:%s' % (self.longPosFrozen, self.longTdFrozen, self.longYdFrozen))
        print('short, total:%s, td:%s, yd:%s' % (self.shortPos, self.shortTd, self.shortYd))
        print('short frozen, total:%s, td:%s, yd:%s' % (self.shortPosFrozen, self.shortTdFrozen, self.shortYdFrozen))

    def convertOrderReq(self, req: VtOrderReq) -> List[VtOrderReq]:
        """转换委托请求"""
        # 普通模式无需转换
        if self.mode is self.MODE_NORMAL:
            return [req]

        # 上期所模式拆分今昨，优先平今
        elif self.mode is self.MODE_SHFE:
            # 开仓无需转换
            if req.offset is OFFSET_OPEN:
                return [req]

            # 多头
            if req.direction is DIRECTION_LONG:
                posAvailable = self.shortPos - self.shortPosFrozen
                tdAvailable = self.shortTd - self.shortTdFrozen
                ydAvailable = self.shortYd - self.shortYdFrozen
                # 空头
            else:
                posAvailable = self.longPos - self.longPosFrozen
                tdAvailable = self.longTd - self.longTdFrozen
                ydAvailable = self.longYd - self.longYdFrozen

            # 平仓量超过总可用，拒绝，返回空列表
            if req.volume > posAvailable:
                return []
            # 平仓量小于今可用，全部平今
            elif req.volume <= tdAvailable:
                req.offset = OFFSET_CLOSETODAY
                return [req]
            # 平仓量大于今可用，平今再平昨
            else:
                l = []

                if tdAvailable > 0:
                    reqTd = copy(req)
                    reqTd.offset = OFFSET_CLOSETODAY
                    reqTd.volume = tdAvailable
                    l.append(reqTd)

                reqYd = copy(req)
                reqYd.offset = OFFSET_CLOSEYESTERDAY
                reqYd.volume = req.volume - tdAvailable
                l.append(reqYd)

                return l

        # 平今惩罚模式，没有今仓则平昨，否则锁仓
        elif self.mode is self.MODE_TDPENALTY:
            # 多头
            if req.direction is DIRECTION_LONG:
                td = self.shortTd
                ydAvailable = self.shortYd - self.shortYdFrozen
            # 空头
            else:
                td = self.longTd
                ydAvailable = self.longYd - self.longYdFrozen

            # 这里针对开仓和平仓委托均使用一套逻辑

            # 如果有今仓，则只能开仓（或锁仓）
            if td:
                req.offset = OFFSET_OPEN
                return [req]
            # 如果平仓量小于昨可用，全部平昨
            elif req.volume <= ydAvailable:
                if self.exchange is EXCHANGE_SHFE:
                    req.offset = OFFSET_CLOSEYESTERDAY
                else:
                    req.offset = OFFSET_CLOSE
                return [req]
            # 平仓量大于昨可用，平仓再反向开仓
            else:
                l = []

                if ydAvailable > 0:
                    reqClose = copy(req)
                    if self.exchange is EXCHANGE_SHFE:
                        reqClose.offset = OFFSET_CLOSEYESTERDAY
                    else:
                        reqClose.offset = OFFSET_CLOSE
                    reqClose.volume = ydAvailable

                    l.append(reqClose)

                reqOpen = copy(req)
                reqOpen.offset = OFFSET_OPEN
                reqOpen.volume = req.volume - ydAvailable
                l.append(reqOpen)

                return l

        # 其他情况则直接返回空
        return []
