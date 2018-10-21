# encoding: UTF-8

'''
动态载入所有的策略类
'''

from .strategyMultiTimeframe import MultiTimeframeStrategy
from .strategyAtrRsi import AtrRsiStrategy
from .strategyBollChannel import BollChannelStrategy
from .strategyDoubleMa import DoubleMaStrategy
from .strategyDualThrust import DualThrustStrategy
from .strategyKingKeltner import KkStrategy
from .strategyMultiSignal import MultiSignalStrategy

# 用来保存策略类的字典
STRATEGY_CLASS = {
    "vnpy.trader.app.ctaStrategy.strategy.strategyMultiTimeframey": MultiTimeframeStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyAtrRsi": AtrRsiStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyBollChannel": BollChannelStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyDoubleMa": DoubleMaStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyDualThrust": DualThrustStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyKingKeltner": KkStrategy,
    "vnpy.trader.app.ctaStrategy.strategy.strategyMultiSignal": MultiSignalStrategy,
}
