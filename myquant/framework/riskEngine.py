# encoding: UTF-8

'''
本文件中实现了风控引擎，用于提供一系列常用的风控功能：
1. 委托流控（单位时间内最大允许发出的委托数量）
2. 总成交限制（每日总成交数量限制）
3. 单笔委托的委托数量控制
'''

from __future__ import division

from myquant.dataStruct import *
from ..constant import *

from .eventEngine import *
from abc import ABCMeta, abstractmethod


class RiskEngine(metaclass=ABCMeta):
    """风控引擎"""

    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        self.mainEngine = mainEngine
        self.eventEngine = eventEngine

        # 绑定自身到主引擎的风控引擎引用上
        mainEngine.rmEngine = self

        # 是否启动风控
        self.active = False

        # 流控相关
        self.orderFlowCount = EMPTY_INT  # 单位时间内委托计数
        self.orderFlowLimit = EMPTY_INT  # 委托限制
        self.orderFlowClear = EMPTY_INT  # 计数清空时间（秒）
        self.orderFlowTimer = EMPTY_INT  # 计数清空时间计时

        # 单笔委托相关
        self.orderSizeLimit = EMPTY_INT  # 单笔委托最大限制

        # 成交统计相关
        self.tradeCount = EMPTY_INT  # 当日成交合约数量统计
        self.tradeLimit = EMPTY_INT  # 当日成交合约数量限制

        # 单品种撤单统计
        self.orderCancelLimit = EMPTY_INT  # 撤单总次数限制
        self.orderCancelDict = {}  # 单一合约对应撤单次数的字典

        # 活动合约相关
        self.workingOrderLimit = EMPTY_INT  # 活动合约最大限制

        # 保证金相关
        self.marginRatioDict = {}  # 保证金占账户净值比例字典
        self.marginRatioLimit = EMPTY_FLOAT  # 最大比例限制

        self.loadSetting()
        self.registerEvent()

    @abstractmethod
    def loadSetting(self):
        pass

    @abstractmethod
    def saveSetting(self):
        pass

    def registerEvent(self):
        """注册事件监听"""
        self.eventEngine.register(Event.TRADE, self.updateTrade)
        self.eventEngine.register(Event.TIMER, self.updateTimer)
        self.eventEngine.register(Event.ORDER, self.updateOrder)
        self.eventEngine.register(Event.ACCOUNT, self.updateAccount)

    def updateOrder(self, event: Event):
        """更新成交数据"""
        # 只需要统计撤单成功的委托
        order: VtOrderData = event.dict_['data']
        if order.status != STATUS_CANCELLED:
            return

        if order.symbol not in self.orderCancelDict:
            self.orderCancelDict[order.symbol] = 1
        else:
            self.orderCancelDict[order.symbol] += 1

    def updateTrade(self, event: Event):
        """更新成交数据"""
        trade: VtTradeData = event.dict_['data']
        self.tradeCount += trade.volume

    def updateTimer(self, event: Event):
        """更新定时器"""
        assert event.type_ == Event.TIMER
        self.orderFlowTimer += 1

        # 如果计时超过了流控清空的时间间隔，则执行清空
        if self.orderFlowTimer >= self.orderFlowClear:
            self.orderFlowCount = 0
            self.orderFlowTimer = 0

    def updateAccount(self, event: Event):
        """账户资金更新"""
        account: VtAccountData = event.dict_['data']

        # 计算保证金占比
        ratio = 0
        if account.balance:
            ratio = account.margin / account.balance

        # 更新到字典中
        self.marginRatioDict[account.gatewayName] = ratio

    @abstractmethod
    def writeRiskLog(self, content: str):
        """快速发出日志事件"""
        pass

    @abstractmethod
    def checkRisk(self, orderReq: VtOrderReq, gatewayName: str) -> bool:
        """检查风险"""
        pass

    def clearOrderFlowCount(self):
        """清空流控计数"""
        self.orderFlowCount = 0
        self.writeRiskLog(u'清空流控计数')

    def clearTradeCount(self):
        """清空成交数量计数"""
        self.tradeCount = 0
        self.writeRiskLog(u'清空总成交计数')

    def setOrderFlowLimit(self, n):
        """设置流控限制"""
        self.orderFlowLimit = n

    def setOrderFlowClear(self, n):
        """设置流控清空时间"""
        self.orderFlowClear = n

    def setOrderSizeLimit(self, n):
        """设置委托最大限制"""
        self.orderSizeLimit = n

    def setTradeLimit(self, n):
        """设置成交限制"""
        self.tradeLimit = n

    def setWorkingOrderLimit(self, n):
        """设置活动合约限制"""
        self.workingOrderLimit = n

    def setOrderCancelLimit(self, n):
        """设置单合约撤单次数上限"""
        self.orderCancelLimit = n

    def setMarginRatioLimit(self, n):
        """设置保证金比例限制"""
        self.marginRatioLimit = n / 100  # n为百分数，需要除以100

    def switchEngineStatus(self):
        """开关风控引擎"""
        self.active = not self.active

        if self.active:
            self.writeRiskLog(u'风险管理功能启动')
        else:
            self.writeRiskLog(u'风险管理功能停止')

    def stop(self):
        """停止"""
        self.saveSetting()
