import streamlit as st
import pickle
import pandas as pd
import plotly.express as px

st.title("Trafico Celdas")

# Load data
with open('data/cells.pkl', 'rb') as file:
    [data_3g, data_lte] = pickle.load(file)

# Load Cell Info
sitiosRI = pd.read_excel(io='data/SitiosRI.xlsx', sheet_name='Sitios')
celdasRI = pd.read_excel(io='data/SitiosRI.xlsx', sheet_name='Celdas')
celdasRI['CellID'] = celdasRI['CellID'].apply(lambda x: str(x))
seguimiento = pd.read_excel('data/SeguimientoCeldas.xlsx')
seguimiento['CellID'] = seguimiento['CellID'].apply(lambda x: str(x))

#Trafico Promedio 3G
meanTable_3g = data_3g[['CellName', 'CellID']].drop_duplicates()
data_3g['AMR TRAFFIC VOLUME']= pd.to_numeric(data_3g['AMR TRAFFIC VOLUME'], downcast='integer', errors='coerce')
data_3g['PS TRAFFIC VOLUME']= pd.to_numeric(data_3g['PS TRAFFIC VOLUME'], downcast='integer', errors='coerce')
promedios = data_3g.groupby(['CellID'])[['AMR TRAFFIC VOLUME', 'PS TRAFFIC VOLUME']].mean()
meanTable_3g = meanTable_3g.join(promedios, on = 'CellID')

#Trafico Promedio LTE
meanTable_lte = data_lte[['CellName','eNodeBID', 'LocalCellID']].drop_duplicates()
data_lte['DOWNLINK TRAFFIC VOLUME']= pd.to_numeric(data_lte['DOWNLINK TRAFFIC VOLUME'], downcast='integer', errors='coerce')
data_lte['UPLINK TRAFFIC VOLUME']= pd.to_numeric(data_lte['UPLINK TRAFFIC VOLUME'], downcast='integer', errors='coerce')
promedios = data_lte.groupby(['CellName'])[['DOWNLINK TRAFFIC VOLUME', 'UPLINK TRAFFIC VOLUME']].mean()
meanTable_lte = meanTable_lte.join(promedios, on = 'CellName')

# Celdas Caídas

celdasCaidas_3G = meanTable_3g[meanTable_3g['AMR TRAFFIC VOLUME']==0]
celdasCaidas_3G = celdasCaidas_3G[['CellName', 'CellID']]
celdasCaidas_lte = meanTable_lte[meanTable_lte['DOWNLINK TRAFFIC VOLUME']==0]
celdasCaidas_lte['CellID'] = celdasCaidas_lte[['eNodeBID', 'LocalCellID']].apply('-'.join, axis=1)
celdasCaidas_lte = celdasCaidas_lte[['CellName', 'CellID']]

celdasCaidas = pd.concat([celdasCaidas_3G, celdasCaidas_lte])
celdasCaidas = celdasCaidas.merge(seguimiento, on='CellID', how='left')
celdasCaidas = celdasCaidas[['CellName_x', 'CellID', 'Seguimiento']]
celdasCaidas.columns = ['CellName', 'CellID', 'Seguimiento']
celdasCaidas = celdasCaidas.merge(celdasRI[['CellID', 'Nombre Gestor']], on='CellID', how='left')
celdasCaidas = celdasCaidas[celdasCaidas['Nombre Gestor'].isin(sitiosRI['Nombre Gestor'])]
celdasCaidas = celdasCaidas[['Nombre Gestor', 'CellName', 'CellID', 'Seguimiento']].sort_values(by='Seguimiento', ascending=True)
st.subheader('Por Revisar')
st.dataframe(celdasCaidas[celdasCaidas['Seguimiento'].isnull()][['Nombre Gestor', 'CellName', 'CellID']], hide_index=True, width=3000)
st.subheader('Seguimiento')
st.dataframe(celdasCaidas[celdasCaidas['Seguimiento'].notnull()], hide_index=True, width=3000)
site_3g = st.selectbox(
    'Seleccionar Sitio 3G',
    data_3g['CellName'].sort_values().unique(),
    index=None,
    placeholder='Seleccionar Celda 3G...'
    )
filt_df_3g=data_3g[data_3g['CellName']==site_3g]


if site_3g:
    plot = px.line(filt_df_3g, x='Tiempo', y=['AMR TRAFFIC VOLUME', 'PS TRAFFIC VOLUME'])
    st.plotly_chart(plot, use_container_width=True)
    st.dataframe(filt_df_3g, hide_index=True, width=3000)    

site_lte = st.selectbox(
    'Seleccionar Sitio LTE',
    data_lte['CellName'].sort_values().unique(),
    index=None,
    placeholder='Seleccionar eNodeB...'
    )
filt_df_lte=data_lte[data_lte['CellName']==site_lte]

if site_lte:
    plot = px.line(filt_df_lte, x='Tiempo', y=['DOWNLINK TRAFFIC VOLUME', 'UPLINK TRAFFIC VOLUME'])
    st.plotly_chart(plot, use_container_width=True)
    st.dataframe(filt_df_lte, hide_index=True, width=3000)
