import csv
from socket import MSG_BCAST
import paho.mqtt.client as paho
import time
from random import *

from sqlalchemy import true

broker="localhost"
port=1883


def on_publish(client,userdata,result):             
    print("data published \n")
    pass


with open('dataset_MP1.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=';', quotechar='|')
    data = []
    for row in reader:
        data.append(row)
    
    headers = data[0]

    data = data[1:]

    data_dict = {}
    for row in data:
        k = row[2]
        if k not in data_dict.keys():
            data_dict[k] = []
        data_dict[k].append(row)

    data_len_dict = {}
    for k in data_dict.keys():
        data_len_dict[k] = len(data_dict[k])
    # print(data_len_dict)
    n_msg = 6000
    msg = []
    for i in range(n_msg):
        for k in data_dict.keys():
            max_len = data_len_dict[k]
            msg.append(data_dict[k][i%max_len])
    #print(msg)

    while(true):
        client1= paho.Client("control1")                          
        client1.on_publish = on_publish                         
        client1.connect(broker,port)
        message = str(msg[randint(0, 6000)])
        print(message)                                
        ret= client1.publish("myfirst/test", message)    
