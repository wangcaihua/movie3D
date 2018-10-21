from ....utils import globalSetting

lang = globalSetting['language']

__all__ = ["CLEAR_ORDER_FLOW_COUNT", "CLEAR_TOTAL_FILL_COUNT",
           "CONTRACT_CANCEL_LIMIT", "MARGIN_RATIO_LIMIT", "ORDER_FLOW_CLEAR", "ORDER_FLOW_LIMIT",
           "ORDER_SIZE_LIMIT", "RISK_MANAGER", "RISK_MANAGER_RUNNING", "RISK_MANAGER_STOP", "SAVE_SETTING",
           "TOTAL_TRADE_LIMIT", "WORKING_ORDER_LIMIT", "WORKING_STATUS"]

CLEAR_ORDER_FLOW_COUNT = u"Clear Flow Count" if lang == 'english' else u"清空流控计数"
CLEAR_TOTAL_FILL_COUNT = u"Clear Fill Count" if lang == 'english' else u"清空总成交计数"
CONTRACT_CANCEL_LIMIT = u"Contract Cancel Limit" if lang == 'english' else u"单合约撤单上限"
MARGIN_RATIO_LIMIT = u"Margin Ratio Limit" if lang == 'english' else u"保证金占比上限"
ORDER_FLOW_CLEAR = u"Flow Clear(s)" if lang == 'english' else u"流控清空（秒）"
ORDER_FLOW_LIMIT = u"Flow Limit" if lang == 'english' else u"流控上限"
ORDER_SIZE_LIMIT = u"Order Size Limit" if lang == 'english' else u"单笔委托上限"
RISK_MANAGER = u"Risk Manager" if lang == 'english' else u"风控管理"
RISK_MANAGER_RUNNING = u"RM Running" if lang == 'english' else u"风控模块运行中"
RISK_MANAGER_STOP = u"RM Stop" if lang == 'english' else u"风控模块未启动"
SAVE_SETTING = u"Save Setting" if lang == 'english' else u"保存设置"
TOTAL_TRADE_LIMIT = u"Total Fill Limit" if lang == 'english' else u"总成交上限"
WORKING_ORDER_LIMIT = u"Working Order Limit" if lang == 'english' else u"活动订单上限"
WORKING_STATUS = u"Working Status" if lang == 'english' else u"工作状态"
