# encoding: UTF-8

from collections import OrderedDict

from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from pymongo.errors import ConnectionFailure

from myquant.mainUI.uiText import *

from .gateway import *
from .logEngine import *
from .dataEngine import *
from .riskEngine import *

from ..utils import globalSetting

from typing import List, Dict


class MainEngine(object):
    """主引擎"""

    def __init__(self, eventEngine: EventEngine):
        """Constructor"""
        # 记录今日日期
        self.todayDate = datetime.now().strftime('%Y%m%d')

        # 绑定事件引擎
        self.eventEngine: EventEngine = eventEngine
        self.eventEngine.start()

        # 创建数据引擎
        self.dataEngine: DataEngine = DataEngine(self.eventEngine)

        # MongoDB数据库相关, MongoDB客户端对象
        self.dbClient: MongoClient = None

        # 接口实例
        self.gatewayDict: Dict[str, VtGateway] = OrderedDict()
        self.gatewayDetailList: list = []

        # 应用模块实例
        self.appDict: dict = OrderedDict()
        self.appDetailList: list = []

        # 风控引擎实例（特殊独立对象）
        self.rmEngine: RiskEngine = None

        # 日志引擎实例
        self.logEngine = None
        self.initLogEngine()

    def exit(self):
        """退出程序前调用，保证正常退出"""
        # 安全关闭所有接口
        for gateway in self.gatewayDict.values():
            gateway.close()

        # 停止事件引擎
        self.eventEngine.stop()

        # 停止上层应用引擎
        for appEngine in self.appDict.values():
            appEngine.stop()

        # 关闭MongoDB
        self.dbClient.close()

        # 保存数据引擎里的合约数据到硬盘
        self.dataEngine.saveContracts()

    ###########################
    #      apps operations    #
    ###########################

    def addApp(self, appModule):
        """添加上层应用"""
        appName = appModule.appName

        # 创建应用实例
        self.appDict[appName] = appModule.appEngine(self, self.eventEngine)

        # 将应用引擎实例添加到主引擎的属性中
        self.__dict__[appName] = self.appDict[appName]

        # 保存应用信息
        appInfo = {
            'appName': appModule.appName,
            'appDisplayName': appModule.appDisplayName,
            'appWidget': appModule.appWidget,
            'appIco': appModule.appIco
        }
        self.appDetailList.append(appInfo)

    def getApp(self, appName: str):
        """获取APP引擎对象"""
        return self.appDict[appName]

    def getAllAppDetails(self):
        """查询引擎中所有上层应用的信息"""
        return self.appDetailList

    ###########################
    #    gateway operations   #
    ###########################

    def addGateway(self, gatewayName: str, displayName: str,
                   gatewayType: str, gateway: VtGateway):
        """添加底层接口"""
        # 创建接口实例
        self.gatewayDict[gatewayName] = gateway

        # 保存接口详细信息
        gwInfo = {
            'gatewayName': gatewayName,
            'gatewayDisplayName': displayName,
            'gatewayType': gatewayType
        }
        self.gatewayDetailList.append(gwInfo)

    def getGateway(self, gatewayName: str) -> VtGateway:
        """获取接口"""
        if gatewayName in self.gatewayDict:
            return self.gatewayDict[gatewayName]
        else:
            self.writeLog(GATEWAY_NOT_EXIST.format(gateway=gatewayName))
            return None

    def getAllGatewayDetails(self):
        """查询引擎中所有底层接口的信息"""
        return self.gatewayDetailList

    def connect(self, gatewayName: str):
        """连接特定名称的接口"""
        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            gateway.connect()

            # 接口连接后自动执行数据库连接的任务
            self.dbConnect()

    def subscribe(self, subscribeReq: VtSubscribeReq, gatewayName: str):
        """订阅特定接口的行情"""
        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            gateway.subscribe(subscribeReq)

    def sendOrder(self, orderReq: VtOrderReq, gatewayName: str):
        """对特定接口发单"""
        # 如果创建了风控引擎，且风控检查失败则不发单
        if self.rmEngine and not self.rmEngine.checkRisk(orderReq, gatewayName):
            return ''

        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            vtOrderID = gateway.sendOrder(orderReq)
            # 更新发出的委托请求到数据引擎中
            self.dataEngine.updateOrderReq(orderReq, vtOrderID)
            return vtOrderID
        else:
            return ''

    def cancelOrder(self, cancelOrderReq: VtCancelOrderReq, gatewayName: str):
        """对特定接口撤单"""
        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            gateway.cancelOrder(cancelOrderReq)

    def qryAccount(self, gatewayName: str):
        """查询特定接口的账户"""
        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            gateway.qryAccount()

    def qryPosition(self, gatewayName: str):
        """查询特定接口的持仓"""
        gateway: VtGateway = self.getGateway(gatewayName)

        if gateway:
            gateway.qryPosition()

    ###########################
    #    MongoDB operations   #
    ###########################

    def dbConnect(self):
        """连接MongoDB数据库"""
        if not self.dbClient:
            # 读取MongoDB的设置
            try:
                # 设置MongoDB操作的超时时间为0.5秒
                self.dbClient = MongoClient(globalSetting['mongoHost'],
                                            globalSetting['mongoPort'],
                                            connectTimeoutMS=500)

                # 调用server_info查询服务器状态，防止服务器异常并未连接成功
                self.dbClient.server_info()

                self.writeLog(DATABASE_CONNECTING_COMPLETED)

                # 如果启动日志记录，则注册日志事件监听函数
                if globalSetting['mongoLogging']:
                    self.eventEngine.register(Event.LOG, self.dbLogging)

            except ConnectionFailure:
                self.writeLog(DATABASE_CONNECTING_FAILED)

    def dbInsert(self, dbName: str, collectionName: str, data: dict):
        """向MongoDB中插入数据，d是具体数据"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection: Collection = db[collectionName]
            collection.insert_one(data)
        else:
            self.writeLog(DATA_INSERT_FAILED)

    def dbQuery(self, dbName: str, collectionName: str, qry: dict, sortKey: str = '', sortDirection: int = ASCENDING):
        """从MongoDB中读取数据，qry是查询要求，返回的是数据库查询的指针"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection: Collection = db[collectionName]

            if sortKey:
                cursor = collection.find(qry).sort(sortKey, sortDirection)  # 对查询出来的数据进行排序
            else:
                cursor = collection.find(qry)

            if cursor:
                return list(cursor)
            else:
                return []
        else:
            self.writeLog(DATA_QUERY_FAILED)
            return []

    def dbUpdate(self, dbName: str, collectionName: str, data: dict, flt: dict, upsert: bool = False):
        """向MongoDB中更新数据，data是具体数据，flt是过滤条件，upsert代表若无是否要插入"""
        if self.dbClient:
            db = self.dbClient[dbName]
            collection: Collection = db[collectionName]
            collection.replace_one(flt, data, upsert)
        else:
            self.writeLog(DATA_UPDATE_FAILED)

    def dbLogging(self, event: Event):
        """向MongoDB中插入日志"""
        log = event.dict_['data']
        logItem = {
            'content': log.logContent,
            'time': log.logTime,
            'gateway': log.gatewayName
        }
        self.dbInsert(LOG_DB_NAME, self.todayDate, logItem)

    ###########################
    #   get data operations   #
    ###########################

    def getContract(self, vtSymbol: str) -> VtContractData:
        """查询合约"""
        return self.dataEngine.getContract(vtSymbol)

    def getAllContracts(self) -> List[VtContractData]:
        """查询所有合约（返回列表）"""
        return self.dataEngine.getAllContracts()

    def getOrder(self, vtOrderID: str) -> VtOrderData:
        """查询委托"""
        return self.dataEngine.getOrder(vtOrderID)

    def getPositionDetail(self, vtSymbol: str) -> VtPositionDetail:
        """查询持仓细节"""
        return self.dataEngine.getPositionDetail(vtSymbol)

    def getAllWorkingOrders(self) -> List[VtOrderData]:
        """查询所有的活跃的委托（返回列表）"""
        return self.dataEngine.getAllWorkingOrders()

    def getAllOrders(self) -> List[VtOrderData]:
        """查询所有委托"""
        return self.dataEngine.getAllOrders()

    def getAllTrades(self) -> List[VtTradeData]:
        """查询所有成交"""
        return self.dataEngine.getAllTrades()

    def getAllAccounts(self) -> List[VtAccountData]:
        """查询所有账户"""
        return self.dataEngine.getAllAccounts()

    def getAllPositions(self) -> List[VtPositionData]:
        """查询所有持仓"""
        return self.dataEngine.getAllPositions()

    def getAllPositionDetails(self) -> List[VtPositionDetail]:
        """查询本地持仓缓存细节"""
        return self.dataEngine.getAllPositionDetails()

    def convertOrderReq(self, req: VtOrderReq) -> List[VtOrderReq]:
        """转换委托请求"""
        return self.dataEngine.convertOrderReq(req)

    def getLog(self) -> List[VtLogData]:
        """查询日志"""
        return self.dataEngine.getLog()

    def getError(self) -> List[VtErrorData]:
        """查询错误"""
        return self.dataEngine.getError()

    ###########################
    #      log operations     #
    ###########################

    def initLogEngine(self):
        """初始化日志引擎"""
        if not globalSetting["logActive"]:
            return

        # 创建引擎
        self.logEngine = LogEngine()

        # 设置日志级别
        levelDict = {
            "debug": LogEngine.LEVEL_DEBUG,
            "info": LogEngine.LEVEL_INFO,
            "warn": LogEngine.LEVEL_WARN,
            "error": LogEngine.LEVEL_ERROR,
            "critical": LogEngine.LEVEL_CRITICAL,
        }
        level = levelDict.get(globalSetting["logLevel"], LogEngine.LEVEL_CRITICAL)
        self.logEngine.setLogLevel(level)

        # 设置输出
        if globalSetting['logConsole']:
            self.logEngine.addConsoleHandler()

        if globalSetting['logFile']:
            self.logEngine.addFileHandler()

        # 注册事件监听
        self.registerLogEvent(Event.LOG)

    def registerLogEvent(self, eventType: str):
        """注册日志事件监听"""
        if self.logEngine:
            self.eventEngine.register(eventType, self.logEngine.processLogEvent)

    def writeLog(self, content: str):
        """快速发出日志事件"""
        log = VtLogData()
        log.logContent = content
        log.gatewayName = 'MAIN_ENGINE'
        event = Event(type_=Event.LOG)
        event.dict_['data'] = log
        self.eventEngine.put(event)
