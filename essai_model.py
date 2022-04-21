import paho.mqtt.client as paho
import time
import ast
from datetime import datetime
import matplotlib.pyplot as plt


import itertools
import warnings
import statsmodels.api as sm
import numpy as np
import pandas as pd


broker="localhost"
port=1883

data=[]
data_h=[]
data_l=[]
data_m=[]

def on_message(client, userdata, message):
    print("received message: ")
    message_list = ast.literal_eval(message.payload.decode("utf-8"))
    now = datetime.now()
    if message_list[2] == "L":
        donne = {
            "date": now,
            "type": message_list[2],
            "temperature": message_list[3],
            "Speed": message_list[5],
        }
        data_l.append(donne)
    if message_list[2] == "M":
        donne = {
            "date": now,
            "type": message_list[2],
            "temperature": message_list[3],
            "Speed": message_list[5],
        }
        data_m.append(donne)
    if message_list[2] == "H":
        donne = {
            "date": now,
            "type": message_list[2],
            "temperature": message_list[3],
            "Speed": message_list[5],
        }
        data_h.append(donne)


client= paho.Client("test")                                                   
client.connect(broker,port)

client.loop_start()
print("attend message")
client.subscribe("myfirst/test")
client.on_message=on_message 

time.sleep(5)
client.loop_stop()

plot_date = []
plot_temp = []
for l in data_l:
    plot_date.append(l.get("date"))
    plot_temp.append(float(l.get("temperature")))

# plt.plot(plot_date, plot_temp)
# plt.title('Température pour le capteur L')  
# plt.ylabel('T [K]')         
# plt.xlabel('Time')         
# plt.grid()              
# plt.show()





# Mise en forme des données 
temp_df = pd.DataFrame({'datetime': plot_date,
                        'T_mu': plot_temp})
temp_df.head(10)

predicted_df = temp_df["T_mu"].to_frame().shift(1).rename(columns = {"T_mu": "T_mu_pred" })
actual_df = temp_df["T_mu"].to_frame().rename(columns = {"T_mu": "T_mu_actual" })

one_step_df = pd.concat([actual_df,predicted_df],axis=1)
one_step_df = one_step_df[1:]
one_step_df.head(10)

p = d = q = range(0, 2)
pdq = list(itertools.product(p, d, q))

seasonal_pdq = [(x[0], x[1], x[2], 12) for x in list(itertools.product(p, d, q))]
print('Examples of parameter combinations for Seasonal ARIMA...')
print('SARIMAX: {} x {}'.format(pdq[1], seasonal_pdq[1]))

warnings.filterwarnings("ignore") # specify to ignore warning messages

for param in pdq:
    for param_seasonal in seasonal_pdq:
        try:
            mod = sm.tsa.statespace.SARIMAX(one_step_df.T_mu_actual,
                                            order=param,
                                            seasonal_order=param_seasonal,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)

            results = mod.fit()

            #print('SARIMA{}x{}12 - AIC:{}'.format(param, param_seasonal, results.aic))
        except:
            continue

# Fit the SARIMAX model using optimal parameters
mod = sm.tsa.statespace.SARIMAX(one_step_df.T_mu_actual,
                                order=(1, 1, 1),
                                seasonal_order=(1, 1, 1, 12),
                                enforce_stationarity=False,
                                enforce_invertibility=False)

results = mod.fit()

# results.plot_diagnostics(figsize=(15, 12))
# plt.show()

date_first = datetime.now()

pred = results.get_prediction(start=pd.to_datetime(plot_date[-1]), dynamic=False)
pred_ci = pred.conf_int()
ax = one_step_df.T_mu_actual.plot(label='observed')
pred.predicted_mean.plot(ax=ax, label='Forecast') 

ax.fill_between(pred_ci.index,
                pred_ci.iloc[:, 0],
                pred_ci.iloc[:, 1], color='k', alpha=.2)

ax.set_xlabel('Date')
ax.set_ylabel('Temperature (in Kelvin)')
plt.ylim([-20,30])
plt.legend()
plt.show()



