# encoding: UTF-8

import psutil

from .uiBasicWidget import *

from myquant.mainUI.uiText import *


class MainWindow(QtWidgets.QMainWindow):
    """主窗口"""

    signalStatusBar = QtCore.Signal(type(Event()))

    def __init__(self, mainEngine: MainEngine, eventEngine: EventEngine):
        """Constructor"""
        super(MainWindow, self).__init__()

        self.mainEngine: MainEngine = mainEngine
        self.eventEngine: EventEngine = eventEngine

        self.gatewayNameList = [d['gatewayName'] for d in self.mainEngine.getAllGatewayDetails()]

        self.widgetDict = {}  # 用来保存子窗口的字典

        # 获取主引擎中的上层应用信息
        self.appDetailList = self.mainEngine.getAllAppDetails()

        self.initUi()
        self.loadWindowSettings('custom')

    def initUi(self):
        """初始化界面"""
        self.setWindowTitle('MyQuant')
        self.initCentral()
        self.initMenu()
        self.initStatusBar()

    def initCentral(self):
        """初始化中心区域"""
        widgetMarketM, dockMarketM = self.createDock(MarketMonitor, MARKET_DATA, QtCore.Qt.RightDockWidgetArea)
        widgetLogM, dockLogM = self.createDock(LogMonitor, LOG, QtCore.Qt.BottomDockWidgetArea)
        widgetErrorM, dockErrorM = self.createDock(ErrorMonitor, ERROR, QtCore.Qt.BottomDockWidgetArea)
        widgetTradeM, dockTradeM = self.createDock(TradeMonitor, TRADE, QtCore.Qt.BottomDockWidgetArea)
        widgetOrderM, dockOrderM = self.createDock(OrderMonitor, ORDER, QtCore.Qt.RightDockWidgetArea)
        widgetWorkingOrderM, dockWorkingOrderM = self.createDock(WorkingOrderMonitor, WORKING_ORDER,
                                                                 QtCore.Qt.BottomDockWidgetArea)
        widgetPositionM, dockPositionM = self.createDock(PositionMonitor, POSITION,
                                                         QtCore.Qt.BottomDockWidgetArea)
        widgetAccountM, dockAccountM = self.createDock(AccountMonitor, ACCOUNT, QtCore.Qt.BottomDockWidgetArea)
        widgetTradingW, dockTradingW = self.createDock(TradingWidget, TRADING, QtCore.Qt.LeftDockWidgetArea)

        self.tabifyDockWidget(dockTradeM, dockErrorM)
        self.tabifyDockWidget(dockTradeM, dockLogM)
        self.tabifyDockWidget(dockPositionM, dockAccountM)
        self.tabifyDockWidget(dockPositionM, dockWorkingOrderM)

        dockTradeM.raise_()
        dockPositionM.raise_()

        # 连接组件之间的信号
        widgetPositionM.itemDoubleClicked.connect(widgetTradingW.closePosition)

        # 保存默认设置
        self.saveWindowSettings('default')

    def initMenu(self):
        """初始化菜单"""
        # 创建菜单
        menubar = self.menuBar()

        # 设计为只显示存在的接口
        gatewayDetails = self.mainEngine.getAllGatewayDetails()

        sysMenu = menubar.addMenu(SYSTEM)

        for d in gatewayDetails:
            if d['gatewayType'] == GATEWAYTYPE_FUTURES:
                self.addConnectAction(sysMenu, d['gatewayName'], d['gatewayDisplayName'])
        sysMenu.addSeparator()

        for d in gatewayDetails:
            if d['gatewayType'] == GATEWAYTYPE_EQUITY:
                self.addConnectAction(sysMenu, d['gatewayName'], d['gatewayDisplayName'])
        sysMenu.addSeparator()

        for d in gatewayDetails:
            if d['gatewayType'] == GATEWAYTYPE_INTERNATIONAL:
                self.addConnectAction(sysMenu, d['gatewayName'], d['gatewayDisplayName'])
        sysMenu.addSeparator()

        for d in gatewayDetails:
            if d['gatewayType'] == GATEWAYTYPE_BTC:
                self.addConnectAction(sysMenu, d['gatewayName'], d['gatewayDisplayName'])
        sysMenu.addSeparator()

        for d in gatewayDetails:
            if d['gatewayType'] == GATEWAYTYPE_DATA:
                self.addConnectAction(sysMenu, d['gatewayName'], d['gatewayDisplayName'])

        sysMenu.addSeparator()
        sysMenu.addAction(
            self.createAction(CONNECT_DATABASE, self.mainEngine.dbConnect, loadIconPath('database.ico')))
        sysMenu.addSeparator()
        sysMenu.addAction(self.createAction(EXIT, self.close, loadIconPath('exit.ico')))

        # 功能应用
        appMenu = menubar.addMenu(APPLICATION)

        for appDetail in self.appDetailList:
            # 如果没有应用界面，则不添加菜单按钮
            if not appDetail['appWidget']:
                continue

            function = self.createOpenAppFunction(appDetail)
            action = self.createAction(appDetail['appDisplayName'], function, loadIconPath(appDetail['appIco']))
            appMenu.addAction(action)

        # 帮助
        helpMenu = menubar.addMenu(HELP)
        helpMenu.addAction(self.createAction(CONTRACT_SEARCH, self.openContract, loadIconPath('contract.ico')))
        helpMenu.addAction(self.createAction(EDIT_SETTING, self.openSettingEditor, loadIconPath('editor.ico')))
        helpMenu.addSeparator()
        helpMenu.addAction(self.createAction(RESTORE, self.restoreWindow, loadIconPath('restore.ico')))
        helpMenu.addAction(self.createAction(ABOUT, self.openAbout, loadIconPath('about.ico')))
        helpMenu.addSeparator()
        helpMenu.addAction(self.createAction(TEST, self.test, loadIconPath('test.ico')))

    def initStatusBar(self):
        """初始化状态栏"""
        self.statusLabel = QtWidgets.QLabel()
        self.statusLabel.setAlignment(QtCore.Qt.AlignLeft)

        self.statusBar().addPermanentWidget(self.statusLabel)
        self.statusLabel.setText(self.getCpuMemory())

        self.sbCount = 0
        self.sbTrigger = 10  # 10秒刷新一次
        self.signalStatusBar.connect(self.updateStatusBar)
        self.eventEngine.register(Event.TIMER, self.signalStatusBar.emit)

    def updateStatusBar(self, event):
        """在状态栏更新CPU和内存信息"""
        self.sbCount += 1

        if self.sbCount == self.sbTrigger:
            self.sbCount = 0
            self.statusLabel.setText(self.getCpuMemory())

    def getCpuMemory(self):
        """获取CPU和内存状态信息"""
        cpuPercent = psutil.cpu_percent()
        memoryPercent = psutil.virtual_memory().percent
        return CPU_MEMORY_INFO.format(cpu=cpuPercent, memory=memoryPercent)

    def addConnectAction(self, menu, gatewayName, displayName=''):
        """增加连接功能"""
        if gatewayName not in self.gatewayNameList:
            return

        def connect():
            self.mainEngine.connect(gatewayName)

        if not displayName:
            displayName = gatewayName

        actionName = CONNECT + displayName
        connectAction = self.createAction(actionName, connect,
                                          loadIconPath('connect.ico'))
        menu.addAction(connectAction)

    def createAction(self, actionName, function, iconPath=''):
        """创建操作功能"""
        action = QtWidgets.QAction(actionName, self)
        action.triggered.connect(function)

        if iconPath:
            icon = QtGui.QIcon(iconPath)
            action.setIcon(icon)

        return action

    def createOpenAppFunction(self, appDetail):
        """创建打开应用UI的函数"""

        def openAppFunction():
            appName = appDetail['appName']
            try:
                self.widgetDict[appName].show()
            except KeyError:
                appEngine = self.mainEngine.getApp(appName)
                self.widgetDict[appName] = appDetail['appWidget'](appEngine, self.eventEngine)
                self.widgetDict[appName].show()

        return openAppFunction

    def test(self):
        """测试按钮用的函数"""
        # 有需要使用手动触发的测试函数可以写在这里
        pass

    def openAbout(self):
        """打开关于"""
        try:
            self.widgetDict['aboutW'].show()
        except KeyError:
            self.widgetDict['aboutW'] = AboutWidget(self)
            self.widgetDict['aboutW'].show()

    def openContract(self):
        """打开合约查询"""
        try:
            self.widgetDict['contractM'].show()
        except KeyError:
            self.widgetDict['contractM'] = ContractManager(self.mainEngine)
            self.widgetDict['contractM'].show()

    def openSettingEditor(self):
        """打开配置编辑"""
        try:
            self.widgetDict['settingEditor'].show()
        except KeyError:
            self.widgetDict['settingEditor'] = SettingEditor(self.mainEngine)
            self.widgetDict['settingEditor'].show()

    def closeEvent(self, event):
        """关闭事件"""
        reply = QtWidgets.QMessageBox.question(self, EXIT,
                                               CONFIRM_EXIT, QtWidgets.QMessageBox.Yes |
                                               QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if reply == QtWidgets.QMessageBox.Yes:
            for widget in self.widgetDict.values():
                widget.close()
            self.saveWindowSettings('custom')

            self.mainEngine.exit()
            event.accept()
        else:
            event.ignore()

    def createDock(self, widgetClass, widgetName, widgetArea):
        """创建停靠组件"""
        widget = widgetClass(self.mainEngine, self.eventEngine)
        dock = QtWidgets.QDockWidget(widgetName)
        dock.setWidget(widget)
        dock.setObjectName(widgetName)
        dock.setFeatures(dock.DockWidgetFloatable | dock.DockWidgetMovable)
        self.addDockWidget(widgetArea, dock)
        return widget, dock

    def saveWindowSettings(self, settingName):
        """保存窗口设置"""
        settings = QtCore.QSettings('vn.trader', settingName)
        settings.setValue('state', self.saveState())
        settings.setValue('geometry', self.saveGeometry())

    def loadWindowSettings(self, settingName):
        """载入窗口设置"""
        settings = QtCore.QSettings('vn.trader', settingName)
        state = settings.value('state')
        geometry = settings.value('geometry')

        # 尚未初始化
        if state is None:
            return
        # 老版PyQt
        elif isinstance(state, QtCore.QVariant):
            self.restoreState(state.toByteArray())
            self.restoreGeometry(geometry.toByteArray())
        # 新版PyQt
        elif isinstance(state, QtCore.QByteArray):
            self.restoreState(state)
            self.restoreGeometry(geometry)
        # 异常
        else:
            content = u'载入窗口配置异常，请检查'
            self.mainEngine.writeLog(content)

    def restoreWindow(self):
        """还原默认窗口设置（还原停靠组件位置）"""
        self.loadWindowSettings('default')
        self.showMaximized()


class AboutWidget(QtWidgets.QDialog):
    """显示关于信息"""

    def __init__(self, parent=None):
        """Constructor"""
        super(AboutWidget, self).__init__(parent)

        self.initUi()

    def initUi(self):
        """"""
        self.setWindowTitle(ABOUT + 'VnTrader')

        text = u"""
            Developed by Traders, for Traders.

            License：MIT
            
            Website：www.vnpy.org

            Github：www.github.com/vnpy/vnpy
            
            """

        label = QtWidgets.QLabel()
        label.setText(text)
        label.setMinimumWidth(500)

        vbox = QtWidgets.QVBoxLayout()
        vbox.addWidget(label)

        self.setLayout(vbox)
