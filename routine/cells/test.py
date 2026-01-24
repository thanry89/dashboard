
from functions import connect
import datetime
import os
import paramiko


#connect()


today = datetime.datetime.today().strftime("%Y%m%d")
yesterday = (datetime.datetime.today() - datetime.timedelta(1)).strftime("%Y%m%d")
folder_today = '/export/home/sysm/opt/oss/server/var/fileint/pm/pmexport_' + today + '/'
folder_yesterday = '/export/home/sysm/opt/oss/server/var/fileint/pm/pmexport_' + yesterday + '/'
home = os.getcwd() + '/temp'

print(today)
print(yesterday)
print(folder_today)
print(folder_yesterday)
print(home)

hostName = '10.64.42.6'
userName = 'sopuser'
passWord = 'Huawei.123'
port = 22
client= paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(hostname=hostName, port=port, username=userName, password= passWord, look_for_keys= False)

with client.open_sftp() as sftp:
#today
    files_today = sftp.listdir(folder_today)
    files_yesterday = sftp.listdir(folder_yesterday)
    kpi = ['Trafico_Diario_3G','Trafico_Diario_LTE']
    filtFiles = list(filter(lambda x: any(y in x for y in kpi), files_today))
    print(filtFiles[0])
    src = folder_today + filtFiles[0]
    dst = home + '/' +filtFiles[0]
    sftp.get(src, dst)
    #print(files_yesterday)
client.close()
