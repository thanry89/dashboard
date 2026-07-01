from functions import connect, extract_data_energia, extract_data_emu, join_data
import os
import pandas as pd


import warnings
warnings.filterwarnings("ignore")

# Extraer archivos MML
# DSP PMU
connect('10.64.42.6','42597', 'Huawei.123')
connect('10.64.42.7','42597', 'Changeme_123')

# DSP EMU
connect('10.64.42.6','45514', 'Huawei.123')
connect('10.64.42.7','45514', 'Changeme_123')


zipFiles = os.listdir('data')

# Extraer Datos
# DSP PMU

mmlEnergia = pd.DataFrame(columns=['Name', 'VDC[V]', 'Load DC [A]', 'VAC[V]', 'Tiempo'])
ziped = [item for item in zipFiles if item.startswith('MMLTask_ENERGIA')]
for item in ziped:
    df = extract_data_energia(item)
    mmlEnergia = pd.concat([mmlEnergia, df])

mmlEnergia.sort_values(by=['Tiempo'], inplace=True)
mmlEnergia.reset_index(inplace=True, drop=True)

# DSP EMU

mmlEMU = pd.DataFrame(columns=['Name', 'Temperature', 'Humidity', 'Voltage', 'Tiempo'])
ziped = [item for item in zipFiles if item.startswith('MMLTask_EMU')]
for item in ziped:
    df = extract_data_emu(item)
    mmlEMU = pd.concat([mmlEMU, df])
mmlEMU.sort_values(by=['Tiempo'], inplace=True)
mmlEMU.reset_index(inplace=True, drop=True)

res = pd.merge(mmlEMU,mmlEnergia, how='outer', on=['Name', 'Tiempo'])

res = res[['Name', 'Tiempo', 'VAC[V]', 'Load DC [A]', 'VDC[V]', 'Voltage',
           'Temperature', 'Humidity']]


join_data(res)
