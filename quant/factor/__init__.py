# Load the necessary packages and modules
import pandas as pd

# Simple Moving Average 
def SMA(data, ndays): 
    SMA = pd.Series(pd.rolling_mean(data['Close'], ndays), name = 'SMA') 
    data = data.join(SMA) 
    return data


# Exponentially-weighted Moving Average 
def EWMA(data, ndays): 
    EMA = pd.Series(pd.ewma(data['Close'], span = ndays, min_periods = ndays - 1), 
    name = 'EWMA_' + str(ndays)) 
    data = data.join(EMA) 
    return data


# Compute the Bollinger Bands 
def BBANDS(data, ndays):
    MA = pd.Series(pd.rolling_mean(data['Close'], ndays)) 
    SD = pd.Series(pd.rolling_std(data['Close'], ndays))

    b1 = MA + (2 * SD)
    B1 = pd.Series(b1, name = 'Upper BollingerBand') 
    data = data.join(B1) 
    
    b2 = MA - (2 * SD)
    B2 = pd.Series(b2, name = 'Lower BollingerBand') 
    data = data.join(B2) 
    
    return data
 

# Commodity Channel Index 
def CCI(data, ndays): 
    TP = (data['High'] + data['Low'] + data['Close']) / 3 
    CCI = pd.Series((TP - pd.rolling_mean(TP, ndays)) / (0.015 * pd.rolling_std(TP, ndays)),
    name = 'CCI') 
    data = data.join(CCI) 
    return data


# Force Index 
def ForceIndex(data, ndays): 
    FI = pd.Series(data['Close'].diff(ndays) * data['Volume'], name = 'ForceIndex') 
    data = data.join(FI) 
    return data


# Rate of Change (ROC)
def ROC(data,n):
    N = data['Close'].diff(n)
    D = data['Close'].shift(n)
    ROC = pd.Series(N/D,name='Rate of Change')
    data = data.join(ROC)
    return data 


# Moving Average Converge Diverage (MACD)
def MACD(data, short, long):
    pass


# (RIS)
def RSI(data):
    pass 


# (KDJ)
def KDJ(data):
    pass

