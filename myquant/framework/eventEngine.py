# encoding: UTF-8

from threading import Thread
from queue import Queue, Empty
from collections import defaultdict

# 第三方模块
from qtpy.QtCore import QTimer
from typing import Callable, List, Dict

__all__ = ['Event', 'EventEngine']


class Event:
    """事件对象"""
    # 系统相关
    TIMER = 'eTimer'  # 计时器事件，每隔1秒发送一次
    LOG = 'eLog'  # 日志事件，全局通用

    # Gateway相关
    TICK = 'eTick.'  # TICK行情事件，可后接具体的vtSymbol
    TRADE = 'eTrade.'  # 成交回报事件
    ORDER = 'eOrder.'  # 报单回报事件
    POSITION = 'ePosition.'  # 持仓回报事件
    ACCOUNT = 'eAccount.'  # 账户回报事件
    CONTRACT = 'eContract.'  # 合约基础信息回报事件
    ERROR = 'eError.'  # 错误回报事件

    # CTA模块事件
    CTA_LOG = 'eCtaLog'  # CTA相关的日志事件
    CTA_STRATEGY = 'eCtaStrategy.'  # CTA策略状态变化事件

    # 行情记录模块事件
    DATARECORDER_LOG = 'eDataRecorderLog'  # 行情记录日志更新事件

    # 快速下单相关事件
    SPREADTRADING_TICK = 'eSpreadTradingTick.'
    SPREADTRADING_POS = 'eSpreadTradingPos.'
    SPREADTRADING_LOG = 'eSpreadTradingLog'
    SPREADTRADING_ALGO = 'eSpreadTradingAlgo.'
    SPREADTRADING_ALGOLOG = 'eSpreadTradingAlgoLog'

    def __init__(self, type_: str = None):
        """Constructor"""
        self.type_: str = type_  # 事件类型
        self.dict_: dict = {}  # 字典用于保存具体的事件数据


class EventEngine(object):
    """
    事件驱动引擎
    事件驱动引擎中所有的变量都设置为了私有，这是为了防止不小心
    从外部修改了这些变量的值或状态，导致bug。

    变量说明
    __queue：私有变量，事件队列
    __active：私有变量，事件引擎开关
    __thread：私有变量，事件处理线程
    __timer：私有变量，计时器
    __handlers：私有变量，事件处理函数字典


    方法说明
    __run: 私有方法，事件处理线程连续运行用
    __process: 私有方法，处理事件，调用注册在引擎中的监听函数
    __onTimer：私有方法，计时器固定事件间隔触发后，向事件队列中存入计时器事件
    start: 公共方法，启动引擎
    stop：公共方法，停止引擎
    register：公共方法，向引擎中注册监听函数
    unregister：公共方法，向引擎中注销监听函数
    put：公共方法，向事件队列中存入新的事件

    事件监听函数必须定义为输入参数仅为一个event对象，即：

    函数
    def func(event)
        ...

    对象方法
    def method(self, event)
        ...

    """

    def __init__(self):
        """初始化事件引擎"""
        # 事件队列
        self.__queue: Queue = Queue()

        # 事件引擎开关
        self.__active: bool = False

        # 事件处理线程
        self.__thread: Thread = Thread(target=self.__run)

        # 计时器，用于触发计时器事件
        self.__timer: QTimer = QTimer()
        self.__timer.timeout.connect(self.__onTimer)

        # 这里的__handlers是一个字典，用来保存对应的事件调用关系
        # 其中每个键对应的值是一个列表，列表中保存了对该事件进行监听的函数功能
        self.__handlers: Dict[str, List[Callable]] = defaultdict(list)

        # __generalHandlers是一个列表，用来保存通用回调函数（所有事件均调用）
        self.__generalHandlers: List[Callable] = []

    def __run(self):
        """引擎运行"""
        while self.__active:
            try:
                # 获取事件的阻塞时间设为1秒
                event = self.__queue.get(block=True, timeout=1)
                self.__process(event)
            except Empty:
                pass

    def __process(self, event: Event):
        """处理事件"""
        # 检查是否存在对该事件进行监听的处理函数
        if event.type_ in self.__handlers:
            # 若存在，则按顺序将事件传递给处理函数执行
            for handler in self.__handlers[event.type_]:
                handler(event)

        # 调用通用处理函数进行处理
        if self.__generalHandlers:
            for handler in self.__generalHandlers:
                handler(event)

    def __onTimer(self):
        """向事件队列中存入计时器事件"""
        # 创建计时器事件
        event = Event(type_=Event.TIMER)

        # 向队列中存入计时器事件
        self.put(event)

    def start(self, timer: bool = True):
        """
        引擎启动
        timer：是否要启动计时器
        """
        # 将引擎设为启动
        self.__active = True

        # 启动事件处理线程
        self.__thread.start()

        # 启动计时器，计时器事件间隔默认设定为1秒
        if timer:
            self.__timer.start(1000)

    def stop(self):
        """停止引擎"""
        # 将引擎设为停止
        self.__active = False

        # 停止计时器
        self.__timer.stop()

        # 等待事件处理线程退出
        self.__thread.join()

    def register(self, type_: str, handler: Callable):
        """注册事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无defaultDict会自动创建新的list
        handlerList = self.__handlers[type_]

        # 若要注册的处理器不在该事件的处理器列表中，则注册该事件
        if handler not in handlerList:
            handlerList.append(handler)

    def unregister(self, type_: str, handler: Callable):
        """注销事件处理函数监听"""
        # 尝试获取该事件类型对应的处理函数列表，若无则忽略该次注销请求
        handlerList = self.__handlers[type_]

        # 如果该函数存在于列表中，则移除
        if handler in handlerList:
            handlerList.remove(handler)

        # 如果函数列表为空，则从引擎中移除该事件类型
        if not handlerList:
            del self.__handlers[type_]

    def put(self, event: Event):
        """向事件队列中存入事件"""
        self.__queue.put(event)

    def registerGeneralHandler(self, handler: Callable):
        """注册通用事件处理函数监听"""
        if handler not in self.__generalHandlers:
            self.__generalHandlers.append(handler)

    def unregisterGeneralHandler(self, handler: Callable):
        """注销通用事件处理函数监听"""
        if handler in self.__generalHandlers:
            self.__generalHandlers.remove(handler)
