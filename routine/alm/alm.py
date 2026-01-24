from functions import get_alarms, alm_report
import pickle
import os
import time
import datetime

start_time = time.perf_counter()
home = os.getcwd().replace('routine/alm','')

try:
    data, reportTime = get_alarms()
except Exception as e:
    print(f'An error ocurred: {e}')
    reportTime = datetime.datetime.now()
else:
    with open(home+'data/alarms.pkl','wb') as file:
        pickle.dump([data,reportTime], file)

    report = alm_report(data)
    with open(home+'data/report.pkl','wb') as file:
        pickle.dump([report,reportTime], file)

end_time = time.perf_counter()
print('Inicio de Rutina:')
print('Hora de Último Reporte: ', reportTime)
elapsed_time = end_time - start_time
print(f"Execution time: {elapsed_time:.6f} seconds")

nextRun = reportTime + datetime.timedelta(seconds=300)
waitSec = int((nextRun - datetime.datetime.now()).total_seconds())+6
datetime.datetime.now() + datetime.timedelta(seconds=waitSec)
print('Hora de Siguiente Reporte: ', nextRun)
print('Hora actual', datetime.datetime.now())
time.sleep(waitSec)

while True:
    start_time = time.perf_counter()
    try:
        data, reportTime = get_alarms()
    except Exception as e:
        print(e)
        reportTime = datetime.datetime.now()
    else:
        with open(home+'data/alarms.pkl','wb') as file:
            pickle.dump([data,reportTime], file)
        report = alm_report(data)
        with open(home+'data/report.pkl','wb') as file:
            pickle.dump([report,reportTime], file)

    end_time = time.perf_counter()

    print('--------------------------')
    print('Hora de Reporte: ', reportTime)
    nextRun = reportTime + datetime.timedelta(seconds=300)
    print('Hora de Siguiente Reporte: ', nextRun)
    print('Hora actual', datetime.datetime.now())
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.6f} seconds")
    time.sleep(300)


