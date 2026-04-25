from functions import prep_data
import pickle
import pandas as pd
import os
import schedule
import time

def get_data():
    # Prepare Data

    [data_3g_actual, data_lte_actual] = prep_data()

    file_path = os.getcwd().replace('routine/cells','') + 'data/cells.pkl'

    # Unir Data
    with open(file_path, 'rb') as file:
        [data_3g_previo, data_lte_previo] = pickle.load(file)

    data_3g = pd.concat([data_3g_previo, data_3g_actual]).drop_duplicates().reset_index(drop=True)
    data_lte = pd.concat([data_lte_previo, data_lte_actual]).drop_duplicates().reset_index(drop=True)

    # Save data
    with open(file_path,'wb') as file:
        pickle.dump([data_3g, data_lte], file)

def start_interval():
    # Triggers every 30 minutes once the first start happens
    schedule.every(30).minutes.do(get_data)
    # Also run the routine immediately at the start time
    get_data()
    return schedule.CancelJob


tiempo = pd.Timestamp.now()
minu = tiempo.minute
hour = tiempo.hour
if minu < 30:
    minutos = '37'
    hora = hour
else:
    minutos = '07'
    hora = hour + 1
txt = str(hora) + ':' + minutos

schedule.every().day.at(txt).do(start_interval)

while True:
    schedule.run_pending()
    time.sleep(1)
