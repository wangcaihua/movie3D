from ....utils import globalSetting

lang = globalSetting['language']


CTA_ENGINE_STARTED = u"CTA engine started." if lang == 'english' else u"CTA引擎启动成功"
CTA_STRATEGY = u"CTA Strategy" if lang == 'english' else u"CTA策略"
INIT = u"Init" if lang == 'english' else u"初始化"
INIT_ALL = u"Init All" if lang == 'english' else u"全部初始化"
LOAD_STRATEGY = u"Load Strategy" if lang == 'english' else u"加载策略"
SAVE_POSITION_DATA = u"Save Position Data" if lang == 'english' else u"保存持仓"
SAVE_POSITION_QUESTION = u"Do you want to save strategy position data into database?" if lang == 'english' else u"是否要保存策略持仓数据到数据库？"
START = u"Start" if lang == 'english' else u"启动"
START_ALL = u"Start All" if lang == 'english' else u"全部启动"
STOP = u"Stop" if lang == 'english' else u"停止"
STOP_ALL = u"Stop All" if lang == 'english' else u"全部停止"
STRATEGY_LOADED = u"Strategy loaded." if lang == 'english' else u"策略加载成功"