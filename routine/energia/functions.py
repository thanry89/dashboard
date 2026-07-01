import paramiko
import tarfile
import os
from numpy import NaN
import re
import pandas as pd
import pickle



def connect(serverIP, taskID, clave):
    
    hostName = serverIP
    userName = 'sopuser'
    passWord = clave
    port = 22
    
    client= paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostName, port=port, username=userName,
                       password= passWord, look_for_keys= False)
    
    folder = '/export/home/sysm/ftproot/MMLTaskResult/'+taskID+'/history/'
    route = os.getcwd() + '/data/'
    
    with client.open_sftp() as sftp:
        files = sftp.listdir(folder)
        for file in files:
            src = folder + file
            dst = route + file
            sftp.get(src, dst)
    client.close()


def extract_data_energia(tgz_file):
    # Extraer archivo txt
    file = tarfile.open('data/'+tgz_file)
    file.extractall('data/')
    file.close()
    
    # Leer archivo txt
    files = os.listdir('data')
    txt_file = [file for file in files if file.endswith(".txt")]
    
    doc = open('data/'+txt_file[0])
    content = doc.readlines()
    doc.close()
    os.remove('data/'+txt_file[0])
    names_idx=[]
    count = 0
    for line in content:
        if line.startswith('NE Name:'):
            names_idx.append(count+1)
        count= count + 1
    results_idx = [x+2 for x in names_idx]
    names = [content[i].strip() for i in names_idx]
    results = [content[i].strip() for i in results_idx]
    
    empty = [NaN, NaN, NaN]
    for idx, item in enumerate(results):
        if item in ['Ne is not connected.', 'NE response time out.']:
            results[idx] = empty
        if item.startswith('+'):
            if content[results_idx[idx]+3].strip() == 'RETCODE = 0  Operation succeeded.':
                measr = []
                measr.append(content[results_idx[idx]+13].strip())
                measr.append(content[results_idx[idx]+15].strip())
                measr.append(content[results_idx[idx]+18].strip())
                results[idx] = [float(re.search('=  (.+)', x).group(1)) 
                                for x in measr]
            else:
                results[idx] = empty
            
    
    voltdc = [x[0] for x in results]
    load = [x[1] for x in results]
    voltac = [x[2] for x in results]
    date =  tgz_file[24:39]
    df = pd.DataFrame(list(zip(names, voltdc, load, voltac)), columns =['Name', 'VDC[V]', 'Load DC [A]', 'VAC[V]'])
    date = pd.to_datetime(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[9:11]+':'+
                  date[11:13]+':'+date[13:15])
    df['Tiempo'] = date
    
    return(df)



def extract_data_emu(tgz_file):
    # Extraer archivo txt
    file = tarfile.open('data/'+tgz_file)
    file.extractall('data/')
    file.close()
    
    # Leer archivo txt
    files = os.listdir('data')
    txt_file = [file for file in files if file.endswith(".txt")]
    
    doc = open('data/'+txt_file[0])
    content = doc.readlines()
    doc.close()
    os.remove('data/'+txt_file[0])
    names_idx=[]
    count = 0
    for line in content:
        if line.startswith('NE Name:'):
            names_idx.append(count+1)
        count= count + 1
    results_idx = [x+2 for x in names_idx]
    names = [content[i].strip() for i in names_idx]
    results = [content[i].strip() for i in results_idx]
    
    empty = [NaN, NaN, NaN]
    for idx, item in enumerate(results):
        if item == 'Ne is not connected.':
            results[idx] = empty
        if item.startswith('+'):
            if content[results_idx[idx]+3].strip() == 'RETCODE = 0  Operation succeeded.':
                measr = []
                measr.append(content[results_idx[idx]+10].strip())
                measr.append(content[results_idx[idx]+11].strip())
                measr.append(content[results_idx[idx]+12].strip())
                results[idx] = [float(re.search('=  (.+)', x).group(1)) for x in measr]
            else:
                results[idx] = empty
    
    temp = [x[0] for x in results]
    humi = [x[1] for x in results]
    volt = [x[2] for x in results]
    
    date =  tgz_file[12:27]
    df = pd.DataFrame(list(zip(names, temp, humi, volt)), columns =['Name', 'Temperature', 'Humidity', 'Voltage'])
    date = pd.to_datetime(date[0:4]+'-'+date[4:6]+'-'+date[6:8]+' '+date[9:11]+':'+
                  date[11:13]+':'+date[13:15])
    df['Tiempo'] = date
    
    return(df)



def join_data(df):
    route = os.getcwd().replace('routine/energia', 'data/')
    if os.path.isfile(route+'energia.pkl'):
        with open('data/files/energia.pkl', 'rb') as f:
            histDf = pickle.load(f)
        for i in range(len(histDf)):
            df[i] = pd.concat([df[i], histDf[i]]).drop_duplicates() 
    
    with open(route+'energia.pkl', 'wb') as file:
        pickle.dump(df, file)