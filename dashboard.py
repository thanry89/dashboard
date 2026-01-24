import streamlit as st

alarm_page = st.Page('paginas/alarm.py', title='Alarmas')
#iub_page = st.Page('paginas/iub.py', title='IPPATH')
cell_page = st.Page('paginas/cells.py', title='Celdas')
#energia_page = st.Page('paginas/energia.py', title='Energia')
#mona_page = st.Page('paginas/mona.py', title='Mona_KPI')

pg = st.navigation([alarm_page, cell_page])

# Page configuration
st.set_page_config(
    page_title="O&M RI",
    layout="wide",
    initial_sidebar_state="expanded")
pg.run()