import paramiko
import datetime
import os
import pandas as pd
import re
import numpy as np


def del_folder():
    if os.path.exists('temp/'):
        for x in os.listdir('temp/'):
            os.remove('temp/'+x)
        os.rmdir('temp')


def get_file():
    
    hostName = '10.64.42.13'
    userName = 'sopuser'
    passWord = 'Changeme_123'
    port = 22
    
    client= paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=hostName, port=port, username=userName,
                       password= passWord, look_for_keys= False)
    
    day = datetime.datetime.today().strftime("%Y%m%d")
    
    folder = '/export/home/sysm/opt/oss/server/var/fileint/fm/' + day + '/'
    
    del_folder()
    
    os.mkdir('temp')
    home = os.getcwd() + '/temp'
    
    with client.open_sftp() as sftp:
        files = sftp.listdir(folder)
        files.sort()
        last_file = files[-1]
        if last_file[-5].isdigit():
            count = -1
            for i in range(int(last_file[-5]),0,-1):
                lf = files[count]
                count = count-1
                src = folder + lf
                dst = home + '/' + lf
                sftp.get(src, dst)
        else:
            src = folder + files[-1]
            dst = home + '/' + last_file
            sftp.get(src, dst)
    client.close()
    
    file = os.listdir('temp')[0]

    reportTime = file[3:17]

    alarms = pd.read_csv('temp/'+file)

    del_folder()

    return(alarms, pd.to_datetime(reportTime, format='%Y%m%d%H%M%S'))

def get_alarms():
    
    data, reportTime = get_file()
    
    # Tratamiento previo de la data
    data = data[['Log Serial Number','NEName', 'AlarmName', 'OccurrenceTime',
                 'Alarm ID', 'Object Identity Name', 'LocationInformation', 
                 'Status']]
    
    data.columns = ['Log Serial Number','Sitio', 'Alarma', 'Fecha',
                 'Alarm ID', 'Object Identity Name', 'LocationInformation', 
                 'Status']
    
    data['Fecha'] = [pd.to_datetime(row['Fecha'][0:len(row['Fecha'])-10], 
                                    format = '%Y/%m/%d %H:%M:%S') 
                     for _, row in data.iterrows()]
    
    data['Fecha'] = [row['Fecha'].strftime('%d/%m/%Y %I:%M:%S %p') 
                     for _, row in data.iterrows()]
    
    
    # Eliminar alarmas 
    alms = ['Task execution failure alarm', 'The Data Transmission Channel Between the Trace Server and the NE Is Disrupted',
            'Users Having Not Logged In for an Excessively Long Time', 'Board Powered Off',
            "The User in the SMManagers Group Changes a User's Password",'Statistical Alarm',
            'Number of Resources Used Reaching Alarm Threshold Specified by License',
            'Performance Threshold Default Alarm']
    
    idx = data[data.Alarma.isin(alms)].index
    data.drop(index=idx, inplace=True)
    data.reset_index(drop=True,inplace=True)
    
    # Alarma NE Is Disconnected
    idx = data[data.Alarma == 'NE Is Disconnected'].index
    for i in idx:
        data.loc[i, 'Sitio'] = data.iloc[i]['Object Identity Name']
    
    # Alarmas RNC de NEs
    # Nombres =NE
    alms = ['IP PM Activation Failure', 'Path Fault', 'UMTS Cell Max DL Power Mismatch']
    idx = data[data.Alarma.isin(alms)].index
    for i in idx:
        txt = re.findall('NodeB Name=(.*)', data.iloc[i]['LocationInformation'])
        if txt:
            data.loc[i, 'Sitio'] = txt[0]
    
    # Nombres =NE,
    alms = ['NodeB Unavailable', 'SCTP Link Fault', 'UMTS Cell Blocked', 
            'UMTS Cell HSUPA Function Fault', 'UMTS Cell Setup Failed', 'UMTS Cell Unavailable']
    idx = data[data.Alarma.isin(alms)].index
    for i in idx:
        txt = re.findall('NodeB Name=(.*?),', data.iloc[i]['LocationInformation'])
        if txt:
            data.loc[i, 'Sitio'] = txt[0]
    
    # Archivos Base
    bitacora = pd.read_excel('data/Bitacora.xlsx')
    sites = pd.read_excel('data/Sitios.xlsx', sheet_name='Escalamiento')
    sitios3G = pd.read_excel('data/Sitios.xlsx', sheet_name='Sitios3G')
    cluster = pd.read_excel('data/Sitios.xlsx', sheet_name='Cluster')
    
    # Cambiar Nombre 3G a Nombre Gestor    
    x = pd.merge(data['Sitio'], sites, on='Sitio', how ='left')
    x_filt = x[x['Escalamiento'].isnull()]
    x = pd.merge(x_filt, sitios3G, left_on='Sitio', right_on='Nombre3G', how='left')
    x_filt = x[x['Sitio_y'].notnull()][['Sitio_x','Sitio_y']].drop_duplicates()
    old = x_filt['Sitio_x'].to_list()
    new = x_filt['Sitio_y'].to_list()
    data['Sitio'] = data['Sitio'].replace(to_replace=old, value=new)
    
    # Completar Informacion de Bitacora
    keys = ['Sitio','Alarm ID','LocationInformation']
    cols = ['Sitio','Alarm ID','LocationInformation','Cluster', 
            'Escalamiento', 'Observación', 'Estado']
    data = pd.merge(data, bitacora[cols], on=keys, how ='left')
    
    
    #Incluir Escalamiento
    x_filt = data[data['Escalamiento'].isnull()]
    y = pd.merge(x_filt['Sitio'], sites, on='Sitio', how ='left')
    idx = x_filt.index
    y.set_index(idx, inplace=True)
    data.loc[idx, 'Escalamiento'] = y['Escalamiento']
    data = data[['Log Serial Number','Sitio','Alarma','Fecha','Alarm ID','Cluster','Escalamiento','Observación','Estado',
                 'Object Identity Name','LocationInformation','Status']]
    
    # Incluir Escalamiento Alarmas X2
    data.loc[(data['Alarma'].isin(['X2 Interface Fault', 'gNodeB X2 Interface Fault']))&(data['Escalamiento'] != 'O&M TX GYE'), 
             'Escalamiento'] = 'O&M RI OPT'
    
    # Incluir Cluster
    
    x_filt = data[data['Cluster'].isnull()]
    y = pd.merge(x_filt['Sitio'], cluster, on='Sitio', how ='left')
    idx = x_filt.index
    y.set_index(idx, inplace=True)
    data.loc[idx, 'Cluster'] = y['Cluster']
    data = data[['Log Serial Number','Sitio','Alarma','Fecha','Alarm ID','Cluster','Escalamiento','Observación','Estado',
                 'Object Identity Name','LocationInformation','Status']]
    
    data.sort_values(by='Log Serial Number',inplace=True)
    data.reset_index(drop=True,inplace=True)
    
    return(data, reportTime)


def alm_report(alarms):
    # Leer los sitios a cargo de RI
    sitiosRI = pd.read_excel('data/SitiosRI.xlsx', sheet_name='Sitios')
    seguimiento = pd.read_excel('data/Sitios3G.xlsx', sheet_name='Seguimiento')

    # Alarmas de Energía
    almEnergia = alarms[alarms['Alarma'].isin(['Falla de AC', 'Falla de Red Publica, Falla AC'])]
    almEnergia = almEnergia[almEnergia.Status == 'Unacknowledged and uncleared Alarm']
    filter = almEnergia['LocationInformation'].str.contains('AC Overvoltage')
    almEnergia = almEnergia[~filter]

    almEnergia = almEnergia[['Sitio', 'Alarma', 'Fecha']]
    almEnergia['Fecha'] = pd.to_datetime(almEnergia['Fecha'], format='%d/%m/%Y %I:%M:%S %p')
    almEnergia.sort_values(by='Fecha', ascending=False, inplace=True)
    # Añádir Tiempo de Caida
    almEnergia['Tiempo'] = datetime.datetime.now() - almEnergia['Fecha']
    almEnergia = almEnergia[almEnergia.Sitio.isin(sitiosRI['Nombre Gestor'])]

    # Presentar alarmas de NEs sin servicio
    NE = alarms[alarms['Alarma'] == 'NE Is Disconnected'][['Sitio', 'Fecha', 'Status']]
    NodeB = alarms[alarms['Alarma'] == 'NodeB Unavailable'][['Sitio', 'Fecha', 'Status']]
    NE['Sin Gestion'] = 'X' 
    NodeB['Sin Servicio 3G'] = 'X'
    caidos = NE.merge(NodeB, on='Sitio', how='outer')
    idx = np.where(caidos['Fecha_x'].isna())[0]
    caidos.loc[idx, 'Fecha_x'] = caidos['Fecha_y'][idx]
    idx = np.where(caidos['Status_x'].isna())[0]
    caidos.loc[idx, 'Status_x'] = caidos['Status_y'][idx]
    caidos = caidos[['Sitio', 'Sin Gestion', 'Sin Servicio 3G', 'Fecha_x', 
                    'Status_x']]
    caidos = caidos[caidos['Status_x'] == 'Unacknowledged and uncleared Alarm']
    caidos.columns= ['Sitio', 'Sin Gestion', 'Sin Servicio 3G', 'Fecha', 'Status']
    caidos = caidos[['Sitio', 'Sin Gestion', 'Sin Servicio 3G', 'Fecha']]
    # Alarmas previas de energia
    caidos = caidos.merge(almEnergia[['Sitio', 'Fecha']], on='Sitio', how='left')
    caidos.columns =['Sitio', 'Sin Gestion', 'Sin Servicio 3G', 'Fecha', 'Hora de Falla AC']
    caidos = caidos[['Sitio', 'Sin Gestion', 'Sin Servicio 3G', 'Hora de Falla AC','Fecha']]
    caidos.drop_duplicates(subset='Sitio',inplace=True)

    # Dar formato a fecha
    caidos['Fecha'] = pd.to_datetime(caidos['Fecha'], format='%d/%m/%Y %I:%M:%S %p')
    caidos.sort_values(by='Fecha', ascending=False, inplace=True)
    # Añádir Tiempo de Caida
    caidos['Tiempo'] = datetime.datetime.now() - caidos['Fecha']
    caidos = caidos[caidos.Sitio.isin(sitiosRI['Nombre Gestor'])]
    caidos = caidos[~caidos.Sitio.isin(seguimiento['Sitio'])]

    return([caidos, almEnergia])
    