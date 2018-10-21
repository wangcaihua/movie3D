from ....utils import globalSetting

lang = globalSetting['language']

BAR_LOGGING_MESSAGE = u"Record Bar Data {symbol}, Time:{time}, O:{open}, H:{high}, L:{low}, C:{close}" if lang == 'english' else u"记录分钟线数据{symbol}，时间:{time}, O:{open}, H:{high}, L:{low}, C:{close}"
BAR_RECORD = u"Bar Record" if lang == 'english' else u"Bar记录"
CONTRACT_SYMBOL = u"Contract Symbol" if lang == 'english' else u"合约代码"
DATA_RECORDER = u"Data Recorder" if lang == 'english' else u"行情记录"
DOMINANT_CONTRACT = u"Dominant Contract" if lang == 'english' else u"主力合约"
DOMINANT_SYMBOL = u"Dominant Symbol" if lang == 'english' else u"主力代码"
GATEWAY = u"Gateway" if lang == 'english' else u"接口"
TICK_LOGGING_MESSAGE = u"Record Tick Data {symbol}, Time:{time}, last:{last}, bid:{bid}, ask:{ask}" if lang == 'english' else u"记录Tick数据{symbol}，时间:{time}, last:{last}, bid:{bid}, ask:{ask}"
TICK_RECORD = u"Tick Record" if lang == 'english' else u"Tick记录"
