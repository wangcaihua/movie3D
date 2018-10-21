# encoding: UTF-8

from .utils import globalSetting

lang = globalSetting['language']

__all__ = ["CURRENCY_CNY", "CURRENCY_HKD", "CURRENCY_NONE", "CURRENCY_UNKNOWN", "CURRENCY_USD",
           "DIRECTION_COVEREDSHORT", "DIRECTION_LONG", "DIRECTION_NET", "DIRECTION_NONE", "DIRECTION_SELL",
           "DIRECTION_SHORT", "DIRECTION_UNKNOWN", "EMPTY_FLOAT", "EMPTY_INT", "EMPTY_STRING", "EMPTY_UNICODE",
           "EXCHANGE_CFFEX", "EXCHANGE_CME", "EXCHANGE_COINCHECK", "EXCHANGE_CZCE", "EXCHANGE_DCE",
           "EXCHANGE_FXCM", "EXCHANGE_GLOBEX", "EXCHANGE_HKEX", "EXCHANGE_HKFE", "EXCHANGE_HUOBI",
           "EXCHANGE_ICE", "EXCHANGE_IDEALPRO", "EXCHANGE_INE", "EXCHANGE_KORBIT", "EXCHANGE_LBANK",
           "EXCHANGE_LME", "EXCHANGE_NONE", "EXCHANGE_NYMEX", "EXCHANGE_OANDA", "EXCHANGE_OKCOIN",
           "EXCHANGE_OKEX", "EXCHANGE_SGE", "EXCHANGE_SHFE", "EXCHANGE_SMART", "EXCHANGE_SSE", "EXCHANGE_SZSE",
           "EXCHANGE_UNKNOWN", "EXCHANGE_ZAIF", "EXCHANGE_ZB", "GATEWAYTYPE_BTC", "GATEWAYTYPE_DATA",
           "GATEWAYTYPE_EQUITY", "GATEWAYTYPE_FUTURES", "GATEWAYTYPE_INTERNATIONAL", "LOG_DB_NAME",
           "OFFSET_CLOSE", "OFFSET_CLOSETODAY", "OFFSET_CLOSEYESTERDAY", "OFFSET_NONE", "OFFSET_OPEN",
           "OFFSET_UNKNOWN", "OPTION_CALL", "OPTION_PUT", "PRICETYPE_FAK", "PRICETYPE_FOK", "PRICETYPE_LIMITPRICE",
           "PRICETYPE_MARKETPRICE", "PRODUCT_COMBINATION", "PRODUCT_DEFER", "PRODUCT_EQUITY", "PRODUCT_FOREX",
           "PRODUCT_FUTURES", "PRODUCT_INDEX", "PRODUCT_NONE", "PRODUCT_OPTION", "PRODUCT_SPOT", "PRODUCT_UNKNOWN",
           "STATUS_ALLTRADED", "STATUS_CANCELLED", "STATUS_NOTTRADED", "STATUS_PARTTRADED", "STATUS_REJECTED",
           "STATUS_UNKNOWN", 'PRODUCT_ETF', 'PRODUCT_WARRANT', 'PRODUCT_BOND', 'PRODUCT_DRVT']

EMPTY_FLOAT = 0.0
EMPTY_INT = 0
EMPTY_STRING = ''
EMPTY_UNICODE = u''

CURRENCY_CNY = u'CNY' if lang == 'english' else u'CNY'
CURRENCY_HKD = u'HKD' if lang == 'english' else u'HKD'
CURRENCY_NONE = u'' if lang == 'english' else u''
CURRENCY_UNKNOWN = u'UNKNOWN' if lang == 'english' else u'UNKNOWN'
CURRENCY_USD = u'USD' if lang == 'english' else u'USD'
DIRECTION_COVEREDSHORT = u'covered short' if lang == 'english' else u'备兑空'
DIRECTION_LONG = u'long' if lang == 'english' else u'多'
DIRECTION_NET = u'net' if lang == 'english' else u'净'
DIRECTION_NONE = u'none' if lang == 'english' else u'无方向'
DIRECTION_SELL = u'sell' if lang == 'english' else u'卖出'
DIRECTION_SHORT = u'short' if lang == 'english' else u'空'
DIRECTION_UNKNOWN = u'unknown' if lang == 'english' else u'未知'
EXCHANGE_CFFEX = u'CFFEX' if lang == 'english' else u'CFFEX'
EXCHANGE_CME = u'CME' if lang == 'english' else u'CME'
EXCHANGE_COINCHECK = u'COINCHECK' if lang == 'english' else u'COINCHECK'
EXCHANGE_CZCE = u'CZCE' if lang == 'english' else u'CZCE'
EXCHANGE_DCE = u'DCE' if lang == 'english' else u'DCE'
EXCHANGE_FXCM = u'FXCM' if lang == 'english' else u'FXCM'
EXCHANGE_GLOBEX = u'GLOBEX' if lang == 'english' else u'GLOBEX'
EXCHANGE_HKEX = u'HKEX' if lang == 'english' else u'HKEX'
EXCHANGE_HKFE = u'HKFE' if lang == 'english' else u'HKFE'
EXCHANGE_HUOBI = u'HUOBI' if lang == 'english' else u'HUOBI'
EXCHANGE_ICE = u'ICE' if lang == 'english' else u'ICE'
EXCHANGE_IDEALPRO = u'IDEALPRO' if lang == 'english' else u'IDEALPRO'
EXCHANGE_INE = u'INE' if lang == 'english' else u'INE'
EXCHANGE_KORBIT = u'KORBIT' if lang == 'english' else u'KORBIT'
EXCHANGE_LBANK = u'LBANK' if lang == 'english' else u'LBANK'
EXCHANGE_LME = u'LME' if lang == 'english' else u'LME'
EXCHANGE_NONE = u'' if lang == 'english' else u''
EXCHANGE_NYMEX = u'NYMEX' if lang == 'english' else u'NYMEX'
EXCHANGE_OANDA = u'OANDA' if lang == 'english' else u'OANDA'
EXCHANGE_OKCOIN = u'OKCOIN' if lang == 'english' else u'OKCOIN'
EXCHANGE_OKEX = u'OKEX' if lang == 'english' else u'OKEX'
EXCHANGE_SGE = u'SGE' if lang == 'english' else u'SGE'
EXCHANGE_SHFE = u'SHFE' if lang == 'english' else u'SHFE'
EXCHANGE_SMART = u'SMART' if lang == 'english' else u'SMART'
EXCHANGE_SSE = u'SSE' if lang == 'english' else u'SSE'
EXCHANGE_SZSE = u'SZSE' if lang == 'english' else u'SZSE'
EXCHANGE_UNKNOWN = u'UNKNOWN' if lang == 'english' else u'UNKNOWN'
EXCHANGE_ZAIF = u'ZAIF' if lang == 'english' else u'ZAIF'
EXCHANGE_ZB = u'ZB' if lang == 'english' else u'ZB'
GATEWAYTYPE_BTC = u'btc' if lang == 'english' else u'btc'
GATEWAYTYPE_DATA = u'data' if lang == 'english' else u'data'
GATEWAYTYPE_EQUITY = u'equity' if lang == 'english' else u'equity'
GATEWAYTYPE_FUTURES = u'futures' if lang == 'english' else u'futures'
GATEWAYTYPE_INTERNATIONAL = u'international' if lang == 'english' else u'international'
LOG_DB_NAME = u'VnTrader_Log_Db' if lang == 'english' else u'VnTrader_Log_Db'
OFFSET_CLOSE = u'close' if lang == 'english' else u'平仓'
OFFSET_CLOSETODAY = u'close today' if lang == 'english' else u'平今'
OFFSET_CLOSEYESTERDAY = u'close yesterday' if lang == 'english' else u'平昨'
OFFSET_NONE = u'none' if lang == 'english' else u'无开平'
OFFSET_OPEN = u'open' if lang == 'english' else u'开仓'
OFFSET_UNKNOWN = u'unknown' if lang == 'english' else u'未知'
OPTION_CALL = u'call' if lang == 'english' else u'看涨期权'
OPTION_PUT = u'put' if lang == 'english' else u'看跌期权'
PRICETYPE_FAK = u'FAK' if lang == 'english' else u'FAK'
PRICETYPE_FOK = u'FOK' if lang == 'english' else u'FOK'
PRICETYPE_LIMITPRICE = u'limit order' if lang == 'english' else u'限价'
PRICETYPE_MARKETPRICE = u'market order' if lang == 'english' else u'市价'
PRODUCT_COMBINATION = u'combination' if lang == 'english' else u'组合'
PRODUCT_DEFER = u'defer' if lang == 'english' else u'延期'
PRODUCT_EQUITY = u'equity' if lang == 'english' else u'股票'
PRODUCT_STOCK = u'stock' if lang == 'english' else u'股票'
PRODUCT_FOREX = u'forex' if lang == 'english' else u'外汇'
PRODUCT_FUTURES = u'futures' if lang == 'english' else u'期货'
PRODUCT_INDEX = u'index' if lang == 'english' else u'指数'
PRODUCT_ETF = u'etf' if lang == 'english' else u'交易所交易基金'
PRODUCT_BOND = u'bond' if lang == 'english' else u'债券'
PRODUCT_WARRANT = u'warrant' if lang == 'english' else u'港股涡轮牛熊证'
PRODUCT_DRVT = u'drvt' if lang == 'english' else u'期权'
PRODUCT_NONE = u'none' if lang == 'english' else u'未知'
PRODUCT_OPTION = u'option' if lang == 'english' else u'期权'
PRODUCT_SPOT = u'spot' if lang == 'english' else u'现货'
PRODUCT_UNKNOWN = u'unknown' if lang == 'english' else u'未知'
STATUS_ALLTRADED = u'filled' if lang == 'english' else u'全部成交'
STATUS_CANCELLED = u'cancelled' if lang == 'english' else u'已撤销'
STATUS_NOTTRADED = u'pending' if lang == 'english' else u'未成交'
STATUS_PARTTRADED = u'partial filled' if lang == 'english' else u'部分成交'
STATUS_REJECTED = u'rejected' if lang == 'english' else u'拒单'
STATUS_UNKNOWN = u'unknown' if lang == 'english' else u'未知'
