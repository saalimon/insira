import pandas as pd
import numpy as np
import math
# from statsmodels.tsa.seasonal import seasonal_decompose
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima_model import ARIMA
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from scipy import stats

class Timeanalyze():
    def __init__(self, df,target=None):
        # super().__init__(df)
        self.df = pd.Series(df['y'], index=df.index)
        self.x = df['x'].get_values()
        self.y = df['y'].get_values()
    def _isStationarity(self):
        # print('Augment Dicky Fuller Test:')
        adftest = adfuller(self.df, autolag='AIC')
        adfoutput = pd.Series(adftest[0:4], index=['Test Statistic','P-Value','#Lags','Number of Observations'])

        # print('Test_Statistic :' + str(adfoutput[0]))
        # print('p-values :' + str(adfoutput[1]))
        # print('Number of observation :' + str(adfoutput[3]))
        if adfoutput[1] < 0.05:
            return True
        else:
            return False
    def _ETS(self):
        model = ExponentialSmoothing(self.df, trend='add')
        model_fit = model.fit()
        print(model_fit.summary())
        return 'ETS'
    def _trend(self):
        # print(type(self.df))
        try:
            model = ARIMA(self.df , order=(5,1,0))
            model_fit = model.fit(disp=0)
            print(model_fit.summary())
            return "yes"
        except:
            return "no"
        # try:
        #     print(type(self.y))
        #     # print(self.y[1])
        #     slope, intercept, r_value, p_value, std_err = stats.linregress(self.x,self.y)
        #     return  slope, intercept, r_value, p_value, std_err
        # except:
        #     print("error")
        #     return None
    def _seasonal(self):
        pass


    

