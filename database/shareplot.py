import datetime
import tushare as ts
import mpl_finance as mpf
import matplotlib.pyplot as plt
from matplotlib.pylab import date2num

# 对tushare获取到的数据转换成candlestick_ohlc()方法可读取的格式
'''
1. 获取个股历史交易记录
get_hist_data(
    code=None,      # string 股票代码 e.g. 600848
    start=None,     # string 开始日期 format：YYYY-MM-DD 为空时取到API所提供的最早日期数据
    end=None,       # string 结束日期 format：YYYY-MM-DD 为空时取到最近一个交易日数据
    ktype='D',      # string 数据类型，D=日k线 W=周 M=月 5=5分钟 15=15分钟 30=30分钟 60=60分钟，默认为D
    retry_count=3,  # int, 默认 3 如遇网络等问题重复执行的次数
    pause=0.001     # int, 默认 0 重复请求数据过程中暂停的秒数，防止请求间隔时间太短出现的问题
    )

返回DataFrame属性:
    - 'open': 开盘价
    - 'high': 最高价
    - 'close': 收盘价
    - 'low': 最低价
    - 'volume': 交易量
    - 'price_change': 价格振幅
    - 'p_change': 百分比振幅
    - 'ma5': 5日均值
    - 'ma10': 10日均值
    - 'ma20': 20日均值
    - 'v_ma5': 量5日均值
    - 'v_ma10': 量5日均值
    - 'v_ma20': 量5日均值
    - '': 换手率

例子:
    ts.get_hist_data('600848', ktype='W') #获取周k线数据
    ts.get_hist_data('600848', ktype='M') #获取月k线数据
    ts.get_hist_data('600848', ktype='5') #获取5分钟k线数据
    ts.get_hist_data('600848', ktype='15') #获取15分钟k线数据
    ts.get_hist_data('600848', ktype='30') #获取30分钟k线数据
    ts.get_hist_data('600848', ktype='60') #获取60分钟k线数据
    ts.get_hist_data('sh'）#获取上证指数k线数据，其它参数与个股一致，下同
    ts.get_hist_data('sz'）#获取深圳成指k线数据
    ts.get_hist_data('hs300'）#获取沪深300指数k线数据
    ts.get_hist_data('sz50'）#获取上证50指数k线数据
    ts.get_hist_data('zxb'）#获取中小板指数k线数据
    ts.get_hist_data('cyb'）#获取创业板指数k线数据


--------------------------------------------------------------------------------------
get_today_all
'''
hist_data = ts.get_hist_data('600848')
print(hist_data.columns)

'''

'''




'''
data_list = []
for dates, row in hist_data.iterrows():
    # 将时间转换为数字
    date_time = datetime.datetime.strptime(dates, '%Y-%m-%d')
    t = date2num(date_time)
    o, h, l, c = row[:4]
    datas = (t, o, h, l, c)
    data_list.append(datas)


# 创建子图
fig, ax = plt.subplots()
fig.subplots_adjust(bottom=0.2)
# 设置X轴刻度为日期时间
ax.xaxis_date()
plt.xticks(rotation=45)
plt.yticks()
plt.title("Shared Code: 600848")
plt.xlabel("Time")
plt.ylabel("Price(RMB)")
mpf.candlestick_ohlc(ax, data_list, width=1.5, colorup='r', colordown='green')
plt.grid()

plt.show()
'''
