# encoding: UTF-8

from myquant.dataStruct import *
from .eventEngine import *
from abc import ABCMeta, abstractmethod

__all__ = ['VtGateway']


class VtGateway(metaclass=ABCMeta):
    """交易接口"""

    def __init__(self, eventEngine: EventEngine, gatewayName: str):
        """Constructor"""
        self.eventEngine: EventEngine = eventEngine
        self.gatewayName: str = gatewayName

    def onTick(self, tick: VtTickData):
        """市场行情推送"""
        # 通用事件
        event1 = Event(type_=Event.TICK)
        event1.dict_['data'] = tick
        self.eventEngine.put(event1)

        # 特定合约代码的事件
        event2 = Event(type_=Event.TICK + tick.vtSymbol)
        event2.dict_['data'] = tick
        self.eventEngine.put(event2)

    def onTrade(self, trade: VtTradeData):
        """成交信息推送"""
        # 通用事件
        event1 = Event(type_=Event.TRADE)
        event1.dict_['data'] = trade
        self.eventEngine.put(event1)

        # 特定合约的成交事件
        event2 = Event(type_=Event.TRADE + trade.vtSymbol)
        event2.dict_['data'] = trade
        self.eventEngine.put(event2)

    def onOrder(self, order: VtOrderData):
        """订单变化推送"""
        # 通用事件
        event1 = Event(type_=Event.ORDER)
        event1.dict_['data'] = order
        self.eventEngine.put(event1)

        # 特定订单编号的事件
        event2 = Event(type_=Event.ORDER + order.vtOrderID)
        event2.dict_['data'] = order
        self.eventEngine.put(event2)

    def onPosition(self, position: VtPositionData):
        """持仓信息推送"""
        # 通用事件
        event1 = Event(type_=Event.POSITION)
        event1.dict_['data'] = position
        self.eventEngine.put(event1)

        # 特定合约代码的事件
        event2 = Event(type_=Event.POSITION + position.vtSymbol)
        event2.dict_['data'] = position
        self.eventEngine.put(event2)

    def onAccount(self, account: VtAccountData):
        """账户信息推送"""
        # 通用事件
        event1 = Event(type_=Event.ACCOUNT)
        event1.dict_['data'] = account
        self.eventEngine.put(event1)

        # 特定合约代码的事件
        event2 = Event(type_=Event.ACCOUNT + account.vtAccountID)
        event2.dict_['data'] = account
        self.eventEngine.put(event2)

    def onError(self, error: VtErrorData):
        """错误信息推送"""
        # 通用事件
        event1 = Event(type_=Event.ERROR)
        event1.dict_['data'] = error
        self.eventEngine.put(event1)

    def onLog(self, log: VtLogData):
        """日志推送"""
        # 通用事件
        event1 = Event(type_=Event.LOG)
        event1.dict_['data'] = log
        self.eventEngine.put(event1)

    def onContract(self, contract: VtContractData):
        """合约基础信息推送"""
        # 通用事件
        event1 = Event(type_=Event.CONTRACT)
        event1.dict_['data'] = contract
        self.eventEngine.put(event1)

    @abstractmethod
    def connect(self):
        """连接"""
        pass

    @abstractmethod
    def subscribe(self, subscribeReq: VtSubscribeReq):
        """订阅行情"""
        pass

    @abstractmethod
    def sendOrder(self, orderReq: VtOrderReq):
        """发单"""
        pass

    @abstractmethod
    def cancelOrder(self, cancelOrderReq: VtCancelOrderReq):
        """撤单"""
        pass

    @abstractmethod
    def qryAccount(self):
        """查询账户资金"""
        pass

    @abstractmethod
    def qryPosition(self):
        """查询持仓"""
        pass

    @abstractmethod
    def close(self):
        """关闭"""
        pass
