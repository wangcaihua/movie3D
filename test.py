import pandas as pd 
from queue import Queue
from quant.data.sqlitedatahandler import SQLiteDataHandler
from quant.backtest import Backtest

plate = ['HK.BK1001',
 'HK.BK1002',
 'HK.BK1003',
 'HK.BK1004',
 'HK.BK1005',
 'HK.BK1007',
 'HK.BK1008',
 'HK.BK1009',
 'HK.BK1010',
 'HK.BK1011',
 'HK.BK1012',
 'HK.BK1013',
 'HK.BK1014',
 'HK.BK1015',
 'HK.BK1016',
 'HK.BK1017',
 'HK.BK1019',
 'HK.BK1020',
 'HK.BK1021',
 'HK.BK1022',
 'HK.BK1025',
 'HK.BK1026',
 'HK.BK1027',
 'HK.BK1028',
 'HK.BK1029',
 'HK.BK1030',
 'HK.BK1031',
 'HK.BK1032',
 'HK.BK1033',
 'HK.BK1034',
 'HK.BK1035',
 'HK.BK1037',
 'HK.BK1039',
 'HK.BK1040',
 'HK.BK1041',
 'HK.BK1042',
 'HK.BK1043',
 'HK.BK1044',
 'HK.BK1045',
 'HK.BK1046',
 'HK.BK1047',
 'HK.BK1048',
 'HK.BK1049',
 'HK.BK1050',
 'HK.BK1051',
 'HK.BK1052',
 'HK.BK1053',
 'HK.BK1054',
 'HK.BK1055',
 'HK.BK1056',
 'HK.BK1058',
 'HK.BK1059',
 'HK.BK1061',
 'HK.BK1062',
 'HK.BK1063',
 'HK.BK1064',
 'HK.BK1065',
 'HK.BK1066',
 'HK.BK1067',
 'HK.BK1068',
 'HK.BK1069',
 'HK.BK1070',
 'HK.BK1071',
 'HK.BK1072',
 'HK.BK1073',
 'HK.BK1074',
 'HK.BK1075',
 'HK.BK1076',
 'HK.BK1077',
 'HK.BK1078',
 'HK.BK1079',
 'HK.BK1080',
 'HK.BK1082',
 'HK.BK1083',
 'HK.BK1084',
 'HK.BK1086',
 'HK.BK1087',
 'HK.BK1089',
 'HK.BK1090',
 'HK.BK1091',
 'HK.BK1093',
 'HK.BK1094',
 'HK.BK1095',
 'HK.BK1096',
 'HK.BK1097',
 'HK.BK1098',
 'HK.BK1099',
 'HK.BK1100']

events = Queue()
sdh = SQLiteDataHandler(plate, events, '2020-01-01')
# sdh.update_local_kline_db()
sdh.load_kline_from_local_db()
sdh.init_hist_time_line()
read = set(sdh.get_local_symbols())
print(len(read), len(plate), read - set(plate)) 


print(sdh.cur_datetime, sdh.hist_index, sdh.hist_time_line[sdh.hist_index])


while sdh.continue_backtest:
    sdh.update_bars()
    print(sdh.cur_datetime)
    print(sdh.snapshot)
    print()


sdh.close()
print("hello world!")
