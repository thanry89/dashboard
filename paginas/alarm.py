import streamlit as st
import pandas as pd
import altair as alt
import pickle
import datetime
import warnings
import numpy as np

warnings.filterwarnings("ignore")

alt.themes.enable("dark")

# Load data
with open('data/alarms.pkl', 'rb') as file:
    alarms, reportTime = pickle.load(file)

# Leer los sitios a cargo de RI
sitiosRI = pd.read_excel('data/SitiosRI.xlsx', sheet_name='Sitios')
seguimiento = pd.read_excel('data/Sitios3G.xlsx', sheet_name='Seguimiento')

# Alarmas de Energía
almEnergia = alarms[alarms['Alarma'].isin(['Falla de AC', 'Falla AC'])]
almEnergia = almEnergia[almEnergia.Status == 'Unacknowledged and uncleared Alarm']
filter = almEnergia['LocationInformation'].str.contains('AC Overvoltage|AC Undervoltage')
almEnergia = almEnergia[~filter]

almEnergia = almEnergia[['Sitio', 'Alarma', 'Fecha']]
almEnergia['Fecha'] = pd.to_datetime(almEnergia['Fecha'], format='%d/%m/%Y %I:%M:%S %p')
almEnergia.sort_values(by='Fecha', ascending=False, inplace=True)
# Añádir Tiempo de Caida
almEnergia['Tiempo'] = datetime.datetime.now() - almEnergia['Fecha']
almEnergia = almEnergia[almEnergia.Sitio.isin(sitiosRI['Nombre Gestor'])]
NEs = ['PIC_UIO_ODEBRECHT_UL', 'PI_UIO_CARCELEN_UL', 'PI_UIO_LDU_UL', 'PI_UIO_HERMANO_MIGUEL_UL', 'PI_UIO_CONOCOTO_UL']
almEnergia = almEnergia[~almEnergia['Sitio'].isin(NEs)]

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
atencion = caidos[~caidos.Sitio.isin(seguimiento['Sitio'])]
seguimiento = caidos[caidos.Sitio.isin(seguimiento['Sitio'])]

st.subheader('Sitios Caidos')

if "Refresh" not in st.session_state:
    st.session_state.Refresh = False

if st.button("Refresh"):
    Refresh = st.session_state.Refresh
    st.session_state.Refresh = not Refresh

if st.session_state.Refresh:
    st.session_state.Refresh = False
    st.rerun()

st.write(f'Hora de Reporte: {reportTime}')
st.write(f'Siguiente Reporte: {reportTime + datetime.timedelta(minutes=5)}')

st.dataframe(atencion, hide_index=True, width=5000)

# Presentar alarmas de energía
st.subheader('Fallas de Energia')
st.dataframe(almEnergia, hide_index=True, width=5000)

st.subheader('Seguimiento')
st.dataframe(seguimiento, hide_index=True, width=5000)

#with col1:
site = st.selectbox(
    'Seleccionar Sitio',
    alarms['Sitio'].sort_values().unique(),
    index=None,
    placeholder='Seleccionar Sitio...'
    )
cols = ['Sitio', 'Alarma', 'Fecha', 'Cluster', 'Escalamiento', 'Observación', 'Estado']
st.dataframe(alarms[alarms['Sitio']==site][cols], hide_index=True, width=3000)

@st.cache_data
def convert_for_download(df):
    return df.to_csv(index=False).encode('UTF-8')
csv = convert_for_download(alarms)

st.download_button(
    label="Descargar Alarmas CSV",
    data=csv,
    file_name="alarmas.csv",
    mime='text/csv',
)