"""
VentasFx — Sistema administrativo de ventas e inventario
construido con el paradigma de programación funcional en Python.

Ejecutar:   streamlit run app.py
"""

import streamlit as st

from ui.componentes import estilos
from ui.estado import iniciar_sesion

st.set_page_config(page_title="VentasFx", page_icon="📊", layout="wide")
estilos()
iniciar_sesion()

paginas = {
    "General": [
        st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True),
        st.Page("paginas/dashboard.py", title="Dashboard", icon=":material/monitoring:"),
    ],
    "Operación": [
        st.Page("paginas/ventas.py", title="Ventas", icon=":material/point_of_sale:"),
        st.Page("paginas/catalogo.py", title="Catálogo e inventario", icon=":material/account_tree:"),
        st.Page("paginas/reportes.py", title="Reportes", icon=":material/summarize:"),
        st.Page("paginas/carga_masiva.py", title="Carga masiva", icon=":material/dataset:"),
    ],
    "Aprendizaje": [
        st.Page("paginas/laboratorio.py", title="Laboratorio funcional", icon=":material/science:"),
    ],
}

with st.sidebar:
    st.markdown("### 📊 VentasFx")
    st.caption("Programación Lógica y Funcional · Unidad 2")

st.navigation(paginas).run()
