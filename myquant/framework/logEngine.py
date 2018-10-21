# encoding: UTF-8

import logging
from myquant.dataStruct import *
from ..framework import Event
from datetime import datetime
from ..utils import getTempPath


class LogEngine(object):
    """日志引擎"""
    __metaclass__ = VtSingleton

    # 日志级别
    LEVEL_DEBUG = logging.DEBUG
    LEVEL_INFO = logging.INFO
    LEVEL_WARN = logging.WARN
    LEVEL_ERROR = logging.ERROR
    LEVEL_CRITICAL = logging.CRITICAL

    def __init__(self):
        """Constructor"""
        self.logger: logging.Logger = logging.getLogger()
        self.formatter = logging.Formatter('%(asctime)s  %(levelname)s: %(message)s')
        self.level = self.LEVEL_CRITICAL

        self.consoleHandler = None
        self.fileHandler = None

        # 添加NullHandler防止无handler的错误输出
        nullHandler = logging.NullHandler()
        self.logger.addHandler(nullHandler)

        # 日志级别函数映射
        self.levelFunctionDict = {
            self.LEVEL_DEBUG: self.debug,
            self.LEVEL_INFO: self.info,
            self.LEVEL_WARN: self.warn,
            self.LEVEL_ERROR: self.error,
            self.LEVEL_CRITICAL: self.critical,
        }

    def setLogLevel(self, level):
        """设置日志级别"""
        self.logger.setLevel(level)
        self.level = level

    def addConsoleHandler(self):
        """添加终端输出"""
        if not self.consoleHandler:
            self.consoleHandler = logging.StreamHandler()
            self.consoleHandler.setLevel(self.level)
            self.consoleHandler.setFormatter(self.formatter)
            self.logger.addHandler(self.consoleHandler)

    def addFileHandler(self, filename=''):
        """添加文件输出"""
        if not self.fileHandler:
            if not filename:
                filename = 'vt_' + datetime.now().strftime('%Y%m%d') + '.log'
            filepath = getTempPath(filename)
            self.fileHandler = logging.FileHandler(filepath)
            self.fileHandler.setLevel(self.level)
            self.fileHandler.setFormatter(self.formatter)
            self.logger.addHandler(self.fileHandler)

    def debug(self, msg):
        """开发时用"""
        self.logger.debug(msg)

    def info(self, msg):
        """正常输出"""
        self.logger.info(msg)

    def warn(self, msg):
        """警告信息"""
        self.logger.warning(msg)

    def error(self, msg):
        """报错输出"""
        self.logger.error(msg)

    def exception(self, msg):
        """报错输出+记录异常信息"""
        self.logger.exception(msg)

    def critical(self, msg):
        """影响程序运行的严重错误"""
        self.logger.critical(msg)

    def processLogEvent(self, event: Event):
        """处理日志事件"""
        log = event.dict_['data']
        # 获取日志级别对应的处理函数
        func = self.levelFunctionDict[log.logLevel]
        msg = '\t'.join([log.gatewayName, log.logContent])
        func(msg)
