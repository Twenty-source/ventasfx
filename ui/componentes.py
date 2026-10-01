"""
componentes.py — Piezas reutilizables de interfaz.

El panel "Concepto aplicado" muestra el código REAL que ejecuta la
pantalla, extraído con inspect.getsource (las funciones son objetos:
se pueden inspeccionar como cualquier otro valor).
"""

import inspect
from typing import Callable, Iterable

import streamlit as st

COLORES = ("#4F46E5", "#0EA5E9", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", "#EC4899", "#64748B")


def dinero(monto: float) -> str:
    return f"${monto:,.2f}"


def dinero_md(monto: float) -> str:
    """Igual que dinero(), pero escapa el $ para que Markdown no lo tome como fórmula LaTeX."""
    return "\\" + dinero(monto)


def dinero_corto(monto: float) -> str:
    for limite, sufijo in ((1e9, " mil M"), (1e6, " M"), (1e3, " k")):
        if abs(monto) >= limite:
            return f"${monto / limite:,.1f}{sufijo}"
    return dinero(monto)


# Formato de columnas para cualquier tabla de ventas
CONFIG_VENTAS = {
    "precio": st.column_config.NumberColumn(format="dollar"),
    "costo": st.column_config.NumberColumn(format="dollar"),
    "total": st.column_config.NumberColumn(format="dollar"),
    "utilidad": st.column_config.NumberColumn(format="dollar"),
    "descuento": st.column_config.NumberColumn(format="percent"),
}


def encabezado(titulo: str, subtitulo: str, temas: Iterable[str] = ()) -> None:
    st.title(titulo)
    st.caption(subtitulo)
    if temas:
        st.markdown(" ".join(f"`{t}`" for t in temas))


def panel_concepto(titulo: str, explicacion: str, funciones: Iterable[Callable] = (),
                   expandido: bool = False) -> None:
    """Desplegable con la explicación del tema y el código fuente real."""
    with st.expander(f"🧠 Concepto aplicado: {titulo}", expanded=expandido):
        st.markdown(explicacion)
        for funcion in funciones:
            modulo = inspect.getmodule(funcion)
            origen = modulo.__name__.replace(".", "/") + ".py" if modulo else ""
            st.caption(f"`{funcion.__name__}` · {origen}")
            st.code(inspect.getsource(funcion), language="python", wrap_lines=True)


def flujo(etapas: Iterable[tuple]) -> None:
    """
    Dibuja un pipeline como tarjetas: [(etiqueta, valor), ...]
    datos → filter → map → reduce → resultado
    """
    etapas = tuple(etapas)
    anchos = tuple(w for i in range(len(etapas)) for w in ((4, 1) if i < len(etapas) - 1 else (4,)))
    columnas = st.columns(anchos, gap="small")
    for i, (etiqueta, valor) in enumerate(etapas):
        with columnas[i * 2]:
            st.markdown(
                f"<div class='etapa'><div class='etq'>{etiqueta}</div>"
                f"<div class='val'>{valor}</div></div>",
                unsafe_allow_html=True,
            )
        if i < len(etapas) - 1:
            with columnas[i * 2 + 1]:
                st.markdown("<div class='flecha'>→</div>", unsafe_allow_html=True)


CSS = """
<style>
.etapa {border:1px solid rgba(79,70,229,.35); border-radius:10px; padding:10px 8px;
        text-align:center; background:rgba(79,70,229,.06); min-height:78px}
.etapa .etq {font-size:.78rem; opacity:.75; font-family:monospace}
.etapa .val {font-size:1.05rem; white-space:nowrap; overflow:hidden; text-overflow:ellipsis; font-weight:700; margin-top:4px}
.flecha {text-align:center; font-size:1.6rem; padding-top:18px; opacity:.6}
.bloque-codigo {font-family:monospace}
div[data-testid="stMetricValue"] {font-size:1.6rem}
</style>
"""


def estilos() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
