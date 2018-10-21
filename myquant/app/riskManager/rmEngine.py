# encoding: UTF-8

'''
本文件中实现了风控引擎，用于提供一系列常用的风控功能：
1. 委托流控（单位时间内最大允许发出的委托数量）
2. 总成交限制（每日总成交数量限制）
3. 单笔委托的委托数量控制
'''

from __future__ import division

import json
import platform

from myquant.dataStruct import *
from myquant.constant import *
from myquant.utils import getJsonPath

from myquant.framework import RiskEngine
from myquant.framework.eventEngine import *


class RmEngine(RiskEngine):
    """风控引擎"""
    settingFileName = 'RM_setting.json'
    settingFilePath = getJsonPath(settingFileName, __file__)

    name = u'风控模块'

    def __init__(self, mainEngine, eventEngine):
        """Constructor"""
        super(RmEngine, self).__init__(mainEngine, eventEngine)

    def loadSetting(self):
        """读取配置"""
        with open(self.settingFilePath) as f:
            d = json.load(f)

            # 设置风控参数
            self.active = d['active']

            self.orderFlowLimit = d['orderFlowLimit']
            self.orderFlowClear = d['orderFlowClear']

            self.orderSizeLimit = d['orderSizeLimit']

            self.tradeLimit = d['tradeLimit']

            self.workingOrderLimit = d['workingOrderLimit']

            self.orderCancelLimit = d['orderCancelLimit']

            self.marginRatioLimit = d['marginRatioLimit']

    def saveSetting(self):
        """保存风控参数"""
        with open(self.settingFilePath, 'w') as f:
            # 保存风控参数
            d = {}

            d['active'] = self.active

            d['orderFlowLimit'] = self.orderFlowLimit
            d['orderFlowClear'] = self.orderFlowClear

            d['orderSizeLimit'] = self.orderSizeLimit

            d['tradeLimit'] = self.tradeLimit

            d['workingOrderLimit'] = self.workingOrderLimit

            d['orderCancelLimit'] = self.orderCancelLimit

            d['marginRatioLimit'] = self.marginRatioLimit

            # 写入json
            jsonD = json.dumps(d, indent=4)
            f.write(jsonD)

    def writeRiskLog(self, content: str):
        """快速发出日志事件"""
        # 发出报警提示音

        if platform.uname() == 'Windows':
            import winsound
            winsound.PlaySound("SystemHand", winsound.SND_ASYNC)

        # 发出日志事件
        log = VtLogData()
        log.logContent = content
        log.gatewayName = self.name
        event = Event(type_=Event.LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)

    def checkRisk(self, orderReq: VtOrderReq, gatewayName: str) -> bool:
        """检查风险"""
        # 如果没有启动风控检查，则直接返回成功
        if not self.active:
            return True

        # 检查委托数量
        if orderReq.volume <= 0:
            self.writeRiskLog(u'委托数量必须大于0')
            return False

        if orderReq.volume > self.orderSizeLimit:
            self.writeRiskLog(u'单笔委托数量%s，超过限制%s'
                              % (orderReq.volume, self.orderSizeLimit))
            return False

        # 检查成交合约量
        if self.tradeCount >= self.tradeLimit:
            self.writeRiskLog(u'今日总成交合约数量%s，超过限制%s'
                              % (self.tradeCount, self.tradeLimit))
            return False

        # 检查流控
        if self.orderFlowCount >= self.orderFlowLimit:
            self.writeRiskLog(u'委托流数量%s，超过限制每%s秒%s'
                              % (self.orderFlowCount, self.orderFlowClear, self.orderFlowLimit))
            return False

        # 检查总活动合约
        workingOrderCount = len(self.mainEngine.getAllWorkingOrders())
        if workingOrderCount >= self.workingOrderLimit:
            self.writeRiskLog(u'当前活动委托数量%s，超过限制%s'
                              % (workingOrderCount, self.workingOrderLimit))
            return False

        # 检查撤单次数
        if orderReq.symbol in self.orderCancelDict and self.orderCancelDict[orderReq.symbol] >= self.orderCancelLimit:
            self.writeRiskLog(u'当日%s撤单次数%s，超过限制%s'
                              % (orderReq.symbol, self.orderCancelDict[orderReq.symbol], self.orderCancelLimit))
            return False

        # 检查保证金比例（只针对开仓委托）
        if orderReq.offset == OFFSET_OPEN and gatewayName in self.marginRatioDict and self.marginRatioDict[
            gatewayName] >= self.marginRatioLimit:
            self.writeRiskLog(u'%s接口保证金占比%s，超过限制%s'
                              % (gatewayName, self.marginRatioDict[gatewayName], self.marginRatioLimit))
            return False

        # 对于通过风控的委托，增加流控计数
        self.orderFlowCount += 1

        return True
