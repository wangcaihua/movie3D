# encoding: UTF-8

import shelve
from myquant.dataStruct import *
from .eventEngine import *
from ..constant import *
from ..utils import getTempPath, globalSetting

from typing import Dict, List

__all__ = ['DataEngine']


class DataEngine(object):
    """数据引擎"""
    contractFileName = 'ContractData.vt'
    contractFilePath = getTempPath(contractFileName)
    FINISHED_STATUS = [STATUS_ALLTRADED, STATUS_REJECTED, STATUS_CANCELLED]

    def __init__(self, eventEngine: EventEngine):
        """Constructor"""
        self.eventEngine: EventEngine = eventEngine

        # 保存数据的字典和列表
        self.contractDict: Dict[str, VtContractData] = {}
        self.orderDict: Dict[str, VtOrderData] = {}
        self.workingOrderDict: Dict[str, VtOrderData] = {}  # 可撤销委托
        self.tradeDict: Dict[str, VtTradeData] = {}
        self.accountDict: Dict[str, VtAccountData] = {}
        self.positionDict: Dict[str, VtPositionData] = {}
        self.logList: List[VtLogData] = []
        self.errorList: List[VtErrorData] = []

        # 持仓细节相关
        self.detailDict: Dict[str, VtPositionDetail] = {}  # vtSymbol:PositionDetail
        self.tdPenaltyList = globalSetting['tdPenalty']  # 平今手续费惩罚的产品代码列表

        # 读取保存在硬盘的合约数据
        self.loadContracts()

        # 注册事件监听
        self.registerEvent()

    def registerEvent(self):
        """注册事件监听"""
        self.eventEngine.register(Event.CONTRACT, self.processContractEvent)
        self.eventEngine.register(Event.ORDER, self.processOrderEvent)
        self.eventEngine.register(Event.TRADE, self.processTradeEvent)
        self.eventEngine.register(Event.POSITION, self.processPositionEvent)
        self.eventEngine.register(Event.ACCOUNT, self.processAccountEvent)
        self.eventEngine.register(Event.LOG, self.processLogEvent)
        self.eventEngine.register(Event.ERROR, self.processErrorEvent)

    def processContractEvent(self, event: Event):
        """处理合约事件"""
        contract: VtContractData = event.dict_['data']
        # vtSymbol:(交易所); symbol
        self.contractDict[contract.vtSymbol] = contract
        self.contractDict[contract.symbol] = contract  # 使用常规代码（不包括交易所）可能导致重复

    def processOrderEvent(self, event: Event):
        """处理委托事件"""
        order: VtOrderData = event.dict_['data']
        self.orderDict[order.vtOrderID] = order

        # 如果订单的状态是全部成交或者撤销，则需要从workingOrderDict中移除
        if order.status in self.FINISHED_STATUS:
            if order.vtOrderID in self.workingOrderDict:
                del self.workingOrderDict[order.vtOrderID]
        # 否则则更新字典中的数据
        else:
            self.workingOrderDict[order.vtOrderID] = order

        # 更新到持仓细节中
        detail = self.getPositionDetail(order.vtSymbol)
        detail.updateOrder(order)

    def processTradeEvent(self, event: Event):
        """处理成交事件"""
        trade: VtTradeData = event.dict_['data']

        self.tradeDict[trade.vtTradeID] = trade

        # 更新到持仓细节中
        detail = self.getPositionDetail(trade.vtSymbol)
        detail.updateTrade(trade)

    def processPositionEvent(self, event: Event):
        """处理持仓事件"""
        pos: VtPositionData = event.dict_['data']

        self.positionDict[pos.vtPositionName] = pos

        # 更新到持仓细节中
        detail = self.getPositionDetail(pos.vtSymbol)
        detail.updatePosition(pos)

    def processAccountEvent(self, event: Event):
        """处理账户事件"""
        account: VtAccountData = event.dict_['data']
        self.accountDict[account.vtAccountID] = account

    def processLogEvent(self, event: Event):
        """处理日志事件"""
        log: VtLogData = event.dict_['data']
        self.logList.append(log)

    def processErrorEvent(self, event: Event):
        """处理错误事件"""
        error: VtErrorData = event.dict_['data']
        self.errorList.append(error)

    def getContract(self, vtSymbol: str) -> VtContractData:
        """查询合约对象"""
        try:
            return self.contractDict[vtSymbol]
        except KeyError:
            return None

    def getAllContracts(self) -> List[VtContractData]:
        """查询所有合约对象（返回列表）"""
        return self.contractDict.values()

    def saveContracts(self):
        """保存所有合约对象到硬盘"""
        f = shelve.open(self.contractFilePath)
        f['data'] = self.contractDict
        f.close()

    def loadContracts(self):
        """从硬盘读取合约对象"""
        f = shelve.open(self.contractFilePath)
        if 'data' in f:
            d = f['data']
            for key, value in d.items():
                self.contractDict[key] = value
        f.close()

    def getOrder(self, vtOrderID: str) -> VtOrderData:
        """查询委托"""
        try:
            return self.orderDict[vtOrderID]
        except KeyError:
            return None

    def getAllWorkingOrders(self) -> List[VtOrderData]:
        """查询所有活动委托（返回列表）"""
        return self.workingOrderDict.values()

    def getAllOrders(self) -> List[VtOrderData]:
        """获取所有委托"""
        return self.orderDict.values()

    def getAllTrades(self) -> List[VtTradeData]:
        """获取所有成交"""
        return self.tradeDict.values()

    def getAllPositions(self) -> List[VtPositionData]:
        """获取所有持仓"""
        return self.positionDict.values()

    def getAllAccounts(self) -> List[VtAccountData]:
        """获取所有资金"""
        return self.accountDict.values()

    def getPositionDetail(self, vtSymbol: str) -> VtPositionDetail:
        """查询持仓细节"""
        if vtSymbol in self.detailDict:
            detail = self.detailDict[vtSymbol]
        else:
            contract = self.getContract(vtSymbol)
            detail = VtPositionDetail(vtSymbol, contract)
            self.detailDict[vtSymbol] = detail

            # 设置持仓细节的委托转换模式
            contract = self.getContract(vtSymbol)

            if contract:
                detail.exchange = contract.exchange

                # 上期所合约
                if contract.exchange == EXCHANGE_SHFE:
                    detail.mode = detail.MODE_SHFE

                # 检查是否有平今惩罚
                for productID in self.tdPenaltyList:
                    if str(productID) in contract.symbol:
                        detail.mode = detail.MODE_TDPENALTY

        return detail

    def getAllPositionDetails(self) -> List[VtPositionDetail]:
        """查询所有本地持仓缓存细节"""
        return self.detailDict.values()

    def updateOrderReq(self, req: VtOrderReq, vtOrderID: str):
        """委托请求更新"""
        vtSymbol = req.vtSymbol

        detail = self.getPositionDetail(vtSymbol)
        detail.updateOrderReq(req, vtOrderID)

    def convertOrderReq(self, req: VtOrderReq) -> List[VtOrderReq]:
        """根据规则转换委托请求"""
        detail: VtPositionDetail = self.detailDict.get(req.vtSymbol, None)
        if not detail:
            return [req]
        else:
            return detail.convertOrderReq(req)

    def getLog(self) -> List[VtLogData]:
        """获取日志"""
        return self.logList

    def getError(self) -> List[VtErrorData]:
        """获取错误"""
        return self.errorList
