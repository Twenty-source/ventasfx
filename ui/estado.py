"""
estado.py — La "capa imperativa delgada".

Streamlit vuelve a ejecutar cada página en cada clic, así que necesita
guardar cosas entre ejecuciones (st.session_state). Ese es el ÚNICO lugar
con estado mutable de la app, y aun así lo usamos de forma funcional:

    * Cada acción del usuario produce un EstadoTienda NUEVO (inmutable).
    * Los estados se apilan en un historial: deshacer = volver al anterior.
    * Las ventas históricas se cargan una sola vez como TUPLA, por lo que
      se pueden compartir entre páginas sin miedo a que alguien las altere.
"""

import os
from pathlib import Path
from typing import NamedTuple

import pandas as pd
import streamlit as st

from core.funciones import total_venta, utilidad
from core.modelos import CATALOGO, Venta
from core.perezoso import folios, leer_ventas

RAIZ = Path(__file__).resolve().parent.parent

# ¿Corre en Streamlit Community Cloud? Allá el código vive en /mount/src y el usuario
# del sistema es "appuser". También se puede forzar con la variable VENTASFX_NUBE=1.
EN_LA_NUBE = (
    os.environ.get("VENTASFX_NUBE") == "1"
    or Path("/mount/src").exists()
    or os.environ.get("HOME") == "/home/appuser"
)
RUTA_VENTAS = RAIZ / "data" / "ventas.csv"
RUTA_MASIVO = RAIZ / "data" / "masivo.csv"


class EstadoTienda(NamedTuple):
    catalogo: tuple        # tupla de Producto
    inventario: dict       # sku -> existencias
    ventas_nuevas: tuple   # ventas registradas en esta sesión
    descripcion: str       # qué acción produjo este estado


@st.cache_resource(show_spinner="Generando y cargando ventas históricas…")
def ventas_historicas() -> tuple:
    """Carga el CSV una sola vez. Si no existe, lo genera (perezosamente)."""
    if not RUTA_VENTAS.exists():
        from data.generar_datos import generar
        generar(RUTA_VENTAS)
    return tuple(leer_ventas(str(RUTA_VENTAS)))


def a_dataframe(ventas) -> pd.DataFrame:
    """Puente a Ciencia de Datos: de tuplas a un DataFrame de pandas."""
    df = pd.DataFrame(list(ventas), columns=Venta._fields)
    if not df.empty:
        df["total"] = list(map(total_venta, ventas))
        df["utilidad"] = list(map(utilidad, ventas))
    return df


def iniciar_sesion() -> None:
    if "historial" not in st.session_state:
        inicial = EstadoTienda(
            catalogo=CATALOGO,
            inventario={p.sku: p.stock for p in CATALOGO},
            ventas_nuevas=(),
            descripcion="Estado inicial",
        )
        st.session_state.historial = [inicial]
        st.session_state.folios = folios(prefijo="N")


def estado_actual() -> EstadoTienda:
    iniciar_sesion()
    return st.session_state.historial[-1]


def registrar_estado(nuevo: EstadoTienda) -> None:
    st.session_state.historial.append(nuevo)


def deshacer() -> bool:
    if len(st.session_state.historial) > 1:
        st.session_state.historial.pop()
        return True
    return False


def todas_las_ventas() -> tuple:
    """Históricas + las registradas en la sesión (concatenación de tuplas)."""
    return ventas_historicas() + estado_actual().ventas_nuevas
