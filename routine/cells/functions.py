import os
import re
import pandas as pd
import paramiko
import datetime


def connect():
    
    hostName = '10.64.42.6'
    userName = 'sopuser'
    passWord = 'Huawei.123'
    port = 22
    
    client= paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostName, port=port, username=userName,
                       password= passWord, look_for_keys= False)
    
    today = datetime.datetime.today().strftime("%Y%m%d")
    yesterday = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y%m%d")
    folder_today = '/export/home/sysm/opt/oss/server/var/fileint/pm/pmexport_' + today + '/'
    folder_yesterday = '/export/home/sysm/opt/oss/server/var/fileint/pm/pmexport_' + yesterday + '/'
    
    #os.mkdir('temp')
    home = os.getcwd() + '/data'
    
    with client.open_sftp() as sftp:
        #today
        files_today = sftp.listdir(folder_today)
        files_yesterday = sftp.listdir(folder_yesterday)
        kpi = ['Trafico_Diario_3G','Trafico_Diario_LTE']
        filtFiles = list(filter(lambda x: any(y in x for y in kpi), files_today))
        for file in filtFiles:
            src = folder_today + file
            dst = home + '/' +file
            sftp.get(src, dst)
        filtFiles = list(filter(lambda x: any(y in x for y in kpi), files_yesterday))
        for file in filtFiles:
            src = folder_yesterday + file
            dst = home + '/' +file
            sftp.get(src, dst)
    client.close()
    

def unir():
    connect()
    data_3g = []
    data_lte = []
    files = os.listdir('data')
    files_3g = [file for file in files if 'Trafico_Diario_3G' in file]
    files_lte = [file for file in files if 'Trafico_Diario_LTE' in file]
    # Data 3G
    for x in files_3g:
        rd = pd.read_csv('data/'+x)
        rd.drop(0, inplace=True)
        data_3g.append(rd)
    result_3g = pd.concat(data_3g)
    result_3g.reset_index(drop=True,inplace=True)
    # Data LTE
    for x in files_lte:
        rd = pd.read_csv('data/'+x)
        rd.drop(0, inplace=True)
        data_lte.append(rd)
    result_lte = pd.concat(data_lte)
    result_lte.reset_index(drop=True,inplace=True)
    return [result_3g, result_lte]


def prep_data():
    [data_3g, data_lte] = unir()
    
    #for x in os.listdir('data/'):
    #   os.remove('data/'+x)
    
    #os.rmdir('temp')
    
    
    # Prepare Data 3G
    data_3g.drop(['Granularity Period', 'Reliability'], inplace=True, axis=1)
    data_3g.columns = ['Tiempo', 'Object', 'AMR TRAFFIC VOLUME', 
                    'PS TRAFFIC VOLUME']
    data_3g['RNC'] = data_3g.apply(lambda row: re.findall('RNC(.*)/', 
                                                    row['Object'])[0], axis=1)
    data_3g['CellID'] = data_3g.apply(lambda row: re.findall('CellID=(.*)',
                                                             row['Object'])[0], axis=1)
    data_3g['CellName'] = data_3g.apply(lambda row: re.findall('Label=(.*),',
                                                   row['Object'])[0], axis=1)
      
    data_3g.Tiempo = pd.to_datetime(data_3g.Tiempo, format='%Y-%m-%d %H:%M')
    
    data_3g= data_3g[['Tiempo', 'RNC', 'CellID', 'CellName', 
                     'AMR TRAFFIC VOLUME', 'PS TRAFFIC VOLUME']]
    
    # Prepare Data LTE
    data_lte.drop(['Granularity Period', 'Reliability'], inplace=True, axis=1)
    data_lte.columns = ['Tiempo', 'Object', 'DOWNLINK TRAFFIC VOLUME', 
                    'UPLINK TRAFFIC VOLUME']
    data_lte['eNodeB'] = data_lte.apply(lambda row: re.findall('(.*)/', 
                                                    row['Object'])[0], axis=1)
    data_lte['eNodeBID'] = data_lte.apply(lambda row: re.findall('eNodeB ID=(.*),',
                                                   row['Object'])[0], axis=1)  
    data_lte['CellName'] = data_lte.apply(lambda row: re.findall('Cell Name=(.*?),',
                                                   row['Object'])[0], axis=1)
    data_lte['LocalCellID'] = data_lte.apply(lambda row: re.findall('Local Cell ID=(.*?),',
                                                   row['Object'])[0], axis=1)
    
    data_lte.Tiempo = pd.to_datetime(data_lte.Tiempo, format='%Y-%m-%d %H:%M')
    
    data_lte= data_lte[['Tiempo', 'eNodeB', 'CellName', 'eNodeBID', 
                        'LocalCellID', 'DOWNLINK TRAFFIC VOLUME',
                        'UPLINK TRAFFIC VOLUME']]
    return([data_3g, data_lte])


