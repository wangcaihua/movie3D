# encoding: UTF-8

import sys

# vn.trader模块
from myquant import EventEngine, MainEngine, createQApp, MainWindow

# 加载底层接口
from myquant.gateway.futuGateway import FutuGateway

# 加载上层应用
from myquant.app import ctaStrategy, spreadTrading, riskManager


def main():
    """主程序入口"""
    # 创建Qt应用对象
    qApp = createQApp()

    # 创建事件引擎
    ee = EventEngine()

    # 创建主引擎
    me = MainEngine(ee)

    # 添加交易接口
    futuGateway = FutuGateway(ee, host="127.0.0.1", port=123456, market='HK',
                              password='123456', env=1)
    me.addGateway("Futu", "Futu", "", futuGateway)

    # 添加上层应用
    me.addApp(ctaStrategy)
    me.addApp(riskManager)
    me.addApp(spreadTrading)

    # 创建主窗口
    mw = MainWindow(me, ee)
    mw.showMaximized()

    # 在主线程中启动Qt事件循环
    sys.exit(qApp.exec_())


if __name__ == '__main__':
    main()
