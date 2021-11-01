import logging
import pandas as pd
from queue import Queue
from matplotlib import pyplot as plt
from quant.data.sqlitedatahandler import SQLiteDataHandler
from quant.core.portfolio import Portfolio
from quant.core.strategy import Strategy
from quant.strategy.turtle_strategy import TurtleStrategy
from quant.riskmgr.turtle_mgr import TurtleMgr
from quant.executor.echoexecutor import EchoExecutionHandler
from quant.backtest import Backtest

logging.basicConfig(level=logging.WARN,
                    format='%(asctime)s - %(name)s:%(funcName)s:%(lineno)d - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

plate_stocks = ['HK.BK1093',
                'HK.01113',
                'HK.00992',
                'HK.BK1078',
                'HK.03333',
                'HK.BK1090',
                'HK.02208',
                'HK.03360',
                'HK.BK1026',
                'HK.01299',
                'HK.02628',
                'HK.01157',
                'HK.00101',
                'HK.00968',
                'HK.06881',
                'HK.00376',
                'HK.01778',
                'HK.BK1028',
                'HK.00763',
                'HK.01349',
                'HK.BK1033',
                'HK.01398',
                'HK.01958',
                'HK.00116',
                'HK.00003',
                'HK.00874',
                'HK.01257',
                'HK.00772',
                'HK.BK1041',
                'HK.03606',
                'HK.03692',
                'HK.BK1098',
                'HK.01038',
                'HK.03396',
                'HK.00939',
                'HK.00144',
                'HK.03380',
                'HK.BK1040',
                'HK.BK1075',
                'HK.00390',
                'HK.BK1058',
                'HK.00152',
                'HK.BK1027',
                'HK.BK1046',
                'HK.02880',
                'HK.01233',
                'HK.03328',
                'HK.03836',
                'HK.00354',
                'HK.BK1031',
                'HK.BK1068',
                'HK.01810',
                'HK.01585',
                'HK.00590',
                'HK.BK1072',
                'HK.BK1021',
                'HK.02186',
                'HK.02858',
                'HK.00151',
                'HK.00696',
                'HK.BK1054',
                'HK.01521',
                'HK.00941',
                'HK.BK1084',
                'HK.00027',
                'HK.BK1025',
                'HK.02356',
                'HK.01776',
                'HK.01381',
                'HK.00780',
                'HK.BK1097',
                'HK.BK1082',
                'HK.02359',
                'HK.03311',
                'HK.00083',
                'HK.01772',
                'HK.00066',
                'HK.00086',
                'HK.BK1048',
                'HK.BK1066',
                'HK.01766',
                'HK.BK1083',
                'HK.01316',
                'HK.BK1004',
                'HK.06178',
                'HK.00257',
                'HK.BK1063',
                'HK.02039',
                'HK.00861',
                'HK.BK1009',
                'HK.03968',
                'HK.09988',
                'HK.BK1049',
                'HK.01888',
                'HK.02318',
                'HK.01789',
                'HK.00388',
                'HK.01668',
                'HK.BK1094',
                'HK.00347',
                'HK.01114',
                'HK.01896',
                'HK.BK1087',
                'HK.01528',
                'HK.BK1069',
                'HK.00016',
                'HK.BK1067',
                'HK.BK1056',
                'HK.06837',
                'HK.09923',
                'HK.01119',
                'HK.00489',
                'HK.03877',
                'HK.02007',
                'HK.01070',
                'HK.06066',
                'HK.01816',
                'HK.09618',
                'HK.01788',
                'HK.00268',
                'HK.02269',
                'HK.02689',
                'HK.BK1022',
                'HK.BK1001',
                'HK.00788',
                'HK.01141',
                'HK.00189',
                'HK.00552',
                'HK.00799',
                'HK.00005',
                'HK.BK1091',
                'HK.01268',
                'HK.01177',
                'HK.00836',
                'HK.01913',
                'HK.01478',
                'HK.01928',
                'HK.BK1070',
                'HK.02388',
                'HK.00011',
                'HK.BK1045',
                'HK.00728',
                'HK.02342',
                'HK.00688',
                'HK.01169',
                'HK.01515',
                'HK.00737',
                'HK.BK1034',
                'HK.BK1017',
                'HK.01211',
                'HK.02202',
                'HK.BK1007',
                'HK.01302',
                'HK.01186',
                'HK.BK1089',
                'HK.BK1012',
                'HK.00023',
                'HK.03339',
                'HK.02013',
                'HK.00914',
                'HK.02607',
                'HK.01313',
                'HK.00883',
                'HK.BK1029',
                'HK.01929',
                'HK.BK1059',
                'HK.00700',
                'HK.01093',
                'HK.03908',
                'HK.06806',
                'HK.03690',
                'HK.06869',
                'HK.01109',
                'HK.02899',
                'HK.01558',
                'HK.01031',
                'HK.06808',
                'HK.00819',
                'HK.BK1051',
                'HK.01347',
                'HK.00004',
                'HK.00751',
                'HK.BK1047',
                'HK.03988',
                'HK.BK1020',
                'HK.00386',
                'HK.BK1003',
                'HK.BK1080',
                'HK.BK1077',
                'HK.00285',
                'HK.01052',
                'HK.00522',
                'HK.01476',
                'HK.01530',
                'HK.BK1095',
                'HK.01606',
                'HK.BK1030',
                'HK.00570',
                'HK.00175',
                'HK.06099',
                'HK.00019',
                'HK.02333',
                'HK.01919',
                'HK.01666',
                'HK.BK1099',
                'HK.BK1043',
                'HK.01813',
                'HK.00293',
                'HK.BK1008',
                'HK.BK1042',
                'HK.00881',
                'HK.01044',
                'HK.03958',
                'HK.00017',
                'HK.BK1039',
                'HK.06198',
                'HK.03669',
                'HK.00530',
                'HK.BK1096',
                'HK.00012',
                'HK.BK1014',
                'HK.00002',
                'HK.00267',
                'HK.00598',
                'HK.BK1013',
                'HK.BK1005',
                'HK.BK1065',
                'HK.02018',
                'HK.BK1011',
                'HK.BK1035',
                'HK.BK1032',
                'HK.BK1015',
                'HK.BK1050',
                'HK.00857',
                'HK.BK1086',
                'HK.01873',
                'HK.03883',
                'HK.02382',
                'HK.BK1055',
                'HK.BK1062',
                'HK.03969',
                'HK.00665',
                'HK.BK1064',
                'HK.03320',
                'HK.00631',
                'HK.BK1076',
                'HK.01951',
                'HK.BK1037',
                'HK.00135',
                'HK.BK1053',
                'HK.BK1079',
                'HK.BK1044',
                'HK.00006',
                'HK.00056',
                'HK.02888',
                'HK.00323',
                'HK.BK1061',
                'HK.03309',
                'HK.BK1100',
                'HK.BK1002',
                'HK.BK1010',
                'HK.BK1019',
                'HK.01905',
                'HK.01638',
                'HK.00981',
                'HK.00256',
                'HK.BK1074',
                'HK.01686',
                'HK.02319',
                'HK.00777',
                'HK.00136',
                'HK.02611',
                'HK.01088',
                'HK.02196',
                'HK.00753',
                'HK.BK1073',
                'HK.06030',
                'HK.BK1016',
                'HK.BK1052',
                'HK.01800',
                'HK.02238',
                'HK.00762',
                'HK.00001',
                'HK.00373',
                'HK.06826',
                'HK.02883',
                'HK.BK1071',
                'HK.06088',
                'HK.01072',
                'HK.02666',
                'HK.06886'
                ]

# 1) create event queue
events = Queue()

# 2) create data hamdler
start_date = '2020-01-01'
sdh = SQLiteDataHandler(plate_stocks, events, start_date)
# sdh.update_local_kline_db()
sdh.load_kline_from_local_db()
sdh.init_time_line()
sdh.load_basicinfo_from_local_db()
try:
    sdh.update_snapshot()
except Exception as e:
    logger.info('update_snapshot Exception:' + str(e))

read = set(sdh.get_local_symbols())

# 3) create portofino
portofino = Portfolio(data_handler=sdh, events=events, start_date=start_date, initial_capital=1000000)

# 4) create strategy
strategy = Strategy(portofino)
turtle = TurtleStrategy(portofino)
strategy.regist(turtle)

# 5) create risk manager
risk_mgr = TurtleMgr(portfolio=portofino)

# 6) create execute
execute = EchoExecutionHandler(portofino)

# 7) create backtest
backtest = Backtest(events, 0.1, sdh, strategy, risk_mgr, execute, portofino)

backtest.simulate_trading()

equity_curve = backtest.portfolio.calc_equity_curve()

plt.plot(equity_curve['total'].values)
plt.show()

sdh.close()
print("finished backtest!")