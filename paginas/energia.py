import streamlit as st
import altair as alt
import pickle
import plotly.express as px

alt.themes.enable("dark")

st.subheader('Consumo Energia')


# Open the file in read-binary mode

with open('data/energia.pkl', 'rb') as file:
    data = pickle.load(file)
    
st.dataframe(data, hide_index=True, width=5000)

site = st.selectbox(
    'Seleccionar Sitio',
    data['Name'].sort_values().unique(),
    index=None,
    placeholder='Seleccionar Sitio...'
    )

filt_df=data[data['Name']==site].sort_values(by='Tiempo')
st.dataframe(filt_df, hide_index=True, width=5000)

tab1, tab2 = st.tabs(["VOLTAJE DC", "TEMPERATURA"])
with tab1:
    figDC = px.line(
            filt_df,
            x="Tiempo",
            y=["Voltage", "VDC[V]"],
            title = site,
            range_y = [42,55]
            )
    st.plotly_chart(figDC, use_container_width=True)
    
with tab2:
    figTemp = px.line(
            filt_df,
            x="Tiempo",
            y="Temperature",
            title = site,
            )
    figTemp.add_hline(y=45, line_width=2, line_dash="dash", line_color="red")
    st.plotly_chart(figTemp, use_container_width=True)