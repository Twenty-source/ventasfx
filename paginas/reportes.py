"""Reportes: comisiones, categorías, rankings y comparativos con reduce y range."""

from datetime import date
from operator import attrgetter, itemgetter

import pandas as pd
import plotly.express as px
import streamlit as st

from core.funciones import tasa_comision, total_venta, utilidad
from core.modelos import TABLA_COMISIONES
from core.reportes import (agrupar, clave_categoria, clave_mes, comisiones_por_vendedor,
                           meses_entre, serie_mensual, top_n)
from ui.componentes import COLORES, dinero, dinero_md, encabezado, panel_concepto
from ui.estado import todas_las_ventas

encabezado("Reportes", "Agregaciones con reduce, funciones como parámetros y periodos generados con range().",
           ("reduce", "comprensiones", "orden superior", "range", "itemgetter"))

ventas = todas_las_ventas()
fecha_min = min(map(attrgetter("fecha"), ventas))
fecha_max = max(map(attrgetter("fecha"), ventas))
meses = meses_entre(fecha_min, fecha_max)

tab_com, tab_cat, tab_top, tab_comp = st.tabs(
    ["💰 Comisiones", "🗂️ Por categoría", "🏆 Rankings", "📈 Comparativo anual"])

# =========================================================================
with tab_com:
    mes = st.selectbox("Mes", meses[::-1], key="mes_com")
    del_mes = tuple(filter(lambda v: clave_mes(v) == mes, ventas))
    filas = comisiones_por_vendedor(del_mes)

    df = pd.DataFrame(filas, columns=("Vendedor", "Vendido (sin IVA)", "Tasa", "Comisión"))
    c1, c2 = st.columns([1.2, 1])
    with c1:
        st.dataframe(df, hide_index=True, column_config={
            "Vendido (sin IVA)": st.column_config.NumberColumn(format="dollar"),
            "Tasa": st.column_config.NumberColumn(format="percent"),
            "Comisión": st.column_config.NumberColumn(format="dollar"),
        })
        st.metric("Total de comisiones del mes", dinero(sum(map(itemgetter(3), filas))))
    with c2:
        fig = px.bar(df, x="Vendedor", y="Vendido (sin IVA)", color=df["Tasa"].map("{:.0%}".format),
                     color_discrete_sequence=COLORES[1:], labels={"color": "Tasa"})
        for minimo, tasa in TABLA_COMISIONES[1:]:
            fig.add_hline(y=minimo, line_dash="dot", line_color="#94A3B8",
                          annotation_text=f"{tasa:.0%}", annotation_position="right")
        fig.update_layout(height=380, xaxis_title="", margin=dict(l=0, r=40, t=30, b=0),
                          legend=dict(orientation="h", y=1.12, title_text="Tasa "))
        st.plotly_chart(fig)

    st.markdown("**Tabla de comisiones** (tupla de tuplas en `core/modelos.py`): " + " · ".join(
        f"desde {dinero_md(m)} → {t:.0%}" for m, t in TABLA_COMISIONES))

    panel_concepto(
        "comisión escalonada como función pura",
        """
`tasa_comision` recorre la tabla con una **expresión generadora** y se queda con el `max` de las
tasas cuyo mínimo se alcanzó: sin `if/elif` encadenados ni variables que cambian.
`comisiones_por_vendedor` agrupa con `reduce` y arma las filas con una **comprensión**.
""",
        (tasa_comision, comisiones_por_vendedor, agrupar),
    )

# =========================================================================
with tab_cat:
    c1, c2, c3 = st.columns(3)
    nivel = c1.radio("Nivel del árbol", (1, 2, 3), horizontal=True,
                     format_func=lambda n: ("Raíz", "Subcategoría", "Tipo")[n - 1])
    # Diccionario de FUNCIONES: el usuario elige qué función se aplica en el map.
    metricas = {"Total": total_venta, "Utilidad": utilidad, "Unidades": attrgetter("cantidad")}
    metrica = c2.selectbox("Métrica", tuple(metricas))
    anio = c3.selectbox("Año", sorted({v.fecha.year for v in ventas}, reverse=True))

    del_anio = tuple(v for v in ventas if v.fecha.year == anio)
    agrupado = agrupar(del_anio, clave_categoria(nivel), metricas[metrica])
    ordenado = top_n(agrupado, len(agrupado))

    fig = px.bar(x=[k for k, _ in ordenado], y=[v for _, v in ordenado],
                 color_discrete_sequence=(COLORES[0],))
    fig.update_layout(height=400, xaxis_title="", yaxis_title=metrica, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig)

    codigo_metrica = {"Total": "total_venta", "Utilidad": "utilidad",
                      "Unidades": 'attrgetter("cantidad")'}[metrica]
    st.code(f"agrupar(ventas_{anio}, clave_categoria({nivel}), {codigo_metrica})", language="python")

    panel_concepto(
        "funciones que fabrican funciones",
        """
`clave_categoria(nivel)` **devuelve una función** que corta la ruta de la categoría al nivel
pedido. `agrupar` recibe esa función como `clave` y la métrica (`total_venta`, `utilidad` o
`attrgetter("cantidad")`) como `valor`. Cambiar el reporte es cambiar **qué función se pasa**,
no reescribir el código.
""",
        (clave_categoria, agrupar, top_n),
    )

# =========================================================================
with tab_top:
    c1, c2, c3 = st.columns(3)
    n = c1.slider("¿Cuántos?", 3, 20, 10)
    criterio = c2.selectbox("Ordenar por", ("Total", "Utilidad", "Unidades"))
    agrupar_por = c3.selectbox("Agrupar por", ("producto", "vendedor", "sku"))
    funcion_valor = {"Total": total_venta, "Utilidad": utilidad, "Unidades": attrgetter("cantidad")}[criterio]

    ranking = top_n(agrupar(ventas, attrgetter(agrupar_por), funcion_valor), n)
    df = pd.DataFrame(
        [(i, nombre, valor) for i, (nombre, valor) in enumerate(ranking, start=1)],
        columns=("#", agrupar_por.capitalize(), criterio),
    )
    st.dataframe(df, hide_index=True, column_config={
        criterio: st.column_config.ProgressColumn(
            format="dollar" if criterio != "Unidades" else "%d", min_value=0,
            max_value=float(ranking[0][1]) if ranking else 1.0)})
    st.download_button("Descargar ranking (CSV)", df.to_csv(index=False),
                       file_name=f"ranking_{agrupar_por}_{criterio.lower()}.csv", icon=":material/download:")

# =========================================================================
with tab_comp:
    anios = sorted({v.fecha.year for v in ventas})
    # Comprensión anidada: un renglón por (año, mes)
    filas = [
        (anio, int(mes[-2:]), total)
        for anio in anios
        for mes, total in serie_mensual((v for v in ventas if v.fecha.year == anio),
                                        date(anio, 1, 1), date(anio, 12, 1))
    ]
    df = pd.DataFrame(filas, columns=("Año", "Mes", "Total"))
    df = df[df["Total"] > 0]
    fig = px.line(df, x="Mes", y="Total", color=df["Año"].astype(str), markers=True,
                  color_discrete_sequence=COLORES, labels={"color": "Año"})
    fig.update_layout(height=420, xaxis=dict(tickmode="array", tickvals=list(range(1, 13)),
                      ticktext=["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]),
                      yaxis_title="", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig)

    panel_concepto(
        "range() para generar periodos",
        """
`meses_entre` convierte cada fecha a un número de mes absoluto (`año*12 + mes-1`) y usa
`range(a, b + 1)` para generar **todos** los meses intermedios. `serie_mensual` rellena con 0
los meses sin ventas para que las gráficas no tengan huecos.
""",
        (meses_entre, serie_mensual),
    )
