import pandas as pd
import numpy as np
from sklearn import metrics, ensemble
import os
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa import ar_model, api

df = pd.read_csv(os.path.join(path,'uk-deaths-from-bronchitis-emphys.csv'))
df.info()

df.columns = ['timestamp', 'y']
index = pd.to_datetime(df['timestamp'], format='%Y-%m').copy()
df.index = index
df.drop('timestamp', axis=1, inplace=True)
plt.plot(df)

#rolling mean of the deaths across years
plt.plot(df.rolling(window=12).mean())

#rolling variance of the deaths across years
plt.plot(df.rolling(window=12).std())

#rolling correlation 
tmp = pd.Series([1,3,4,5,6,7,8,9])
print(tmp)
print(tmp.shift(1))
print(tmp.shift(2))
[pd.Series.corr(df.y, df.y.shift(i)) for i in range(24)]
plot_acf(df.y, lags=24)
plot_pacf(df.y, lags=24)

ar = np.array([1, -0.3, 0.4, -0.3])
ma = np.array([1, 0])
ar1 = ArmaProcess(ar=ar)
ar1_data = ar1.generate_sample(nsample=1000)
plt.plot(ar1_data)

x = synthetic_ar1_data(300)
m2 = ar_model.AR(x)
m2.select_order(maxlag=25, ic='aic')
m2 = m2.fit(maxlag=25, ic='aic')
m2.params[0]
m2.params[1]
