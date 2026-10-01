"""Dashboard: indicadores generales calculados con filter + map + reduce."""

from datetime import date
from operator import attrgetter, itemgetter

import pandas as pd
import plotly.express as px
import streamlit as st

from core.funciones import utilidad
from core.perezoso import promedio_movil
from core.predicados import entre_fechas, por_categoria, y_
from core.reportes import (_acumular_resumen, agrupar, clave_categoria, ranking_productos,
                           resumen, serie_mensual)
from ui.componentes import COLORES, dinero, dinero_corto, encabezado, panel_concepto
from ui.estado import todas_las_ventas

ventas = todas_las_ventas()
fecha_min = min(map(attrgetter("fecha"), ventas))
fecha_max = max(map(attrgetter("fecha"), ventas))
categorias = sorted({v.categoria.split("/")[0] for v in ventas})

encabezado("Dashboard", "Indicadores del negocio. Todo se calcula con funciones puras sobre una tupla de ventas.",
           ("filter", "map", "reduce", "range", "generadores"))

# ---------------------------------------------------------------- filtros
with st.container(border=True):
    f1, f2 = st.columns([2, 3])
    periodo = f1.date_input("Periodo", value=(date(fecha_max.year, 1, 1), fecha_max),
                            min_value=fecha_min, max_value=fecha_max, format="DD/MM/YYYY")
    elegidas = f2.multiselect("Categorías", categorias, default=categorias)

inicio, fin = (periodo if len(periodo) == 2 else (periodo[0], periodo[0]))

# El filtro es UN predicado construido combinando otros predicados.
predicado = y_(entre_fechas(inicio, fin), por_categoria(*elegidas))
seleccion = tuple(filter(predicado, ventas)) if elegidas else ()

if not seleccion:
    st.warning("No hay ventas con esos filtros.")
    st.stop()

# ---------------------------------------------------------------- KPIs
datos = resumen(seleccion)
k = st.columns(5)
k[0].metric("Total vendido", dinero_corto(datos["total"]), help=dinero(datos["total"]))
k[1].metric("Transacciones", f"{datos['transacciones']:,}")
k[2].metric("Ticket promedio", dinero(datos["ticket_promedio"]))
k[3].metric("Utilidad", dinero_corto(datos["utilidad"]), help=dinero(datos["utilidad"]))
k[4].metric("Margen", f"{datos['margen']:.1%}")

# ---------------------------------------------------------------- serie mensual
serie = serie_mensual(seleccion, inicio, fin)
meses, totales = zip(*serie)
df_serie = pd.DataFrame({
    "Mes": meses,
    "Total": totales,
    "Promedio móvil 3 meses": tuple(promedio_movil(totales, 3)),
})

g1, g2 = st.columns([3, 2])
with g1:
    st.markdown("##### Ventas por mes")
    fig = px.line(df_serie, x="Mes", y=["Total", "Promedio móvil 3 meses"], markers=True,
                  color_discrete_sequence=(COLORES[0], COLORES[3]))
    fig.update_layout(height=340, legend_title_text="", yaxis_title="", xaxis_title="", xaxis_type="category",
                      margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.1))
    st.plotly_chart(fig)

with g2:
    st.markdown("##### Por categoría")
    por_cat = agrupar(seleccion, clave_categoria(1))
    fig = px.pie(names=list(por_cat), values=list(por_cat.values()), hole=0.55,
                 color_discrete_sequence=COLORES)
    fig.update_layout(height=340, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig)

g3, g4 = st.columns(2)
with g3:
    st.markdown("##### Top 10 productos")
    top = ranking_productos(seleccion, 10)[::-1]
    fig = px.bar(x=tuple(map(itemgetter(1), top)), y=tuple(map(itemgetter(0), top)),
                 orientation="h", color_discrete_sequence=(COLORES[0],))
    fig.update_layout(height=360, xaxis_title="", yaxis_title="", margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig)

with g4:
    st.markdown("##### Vendedores: total vs utilidad")
    por_vendedor = agrupar(seleccion, attrgetter("vendedor"))
    utilidad_vend = agrupar(seleccion, attrgetter("vendedor"), utilidad)
    df_v = pd.DataFrame(
        [(n, t, utilidad_vend[n]) for n, t in sorted(por_vendedor.items(), key=itemgetter(1))],
        columns=("Vendedor", "Total", "Utilidad"),
    )
    fig = px.bar(df_v, y="Vendedor", x=["Total", "Utilidad"], orientation="h", barmode="group",
                 color_discrete_sequence=(COLORES[1], COLORES[2]))
    fig.update_layout(height=360, xaxis_title="", yaxis_title="", legend_title_text="",
                      margin=dict(l=0, r=0, t=10, b=0), legend=dict(orientation="h", y=1.08))
    st.plotly_chart(fig)

# ---------------------------------------------------------------- concepto
panel_concepto(
    "un solo reduce para todos los indicadores",
    """
Los 5 indicadores de arriba salen de **una sola pasada** con `reduce`. El acumulador es una
**tupla** `(n, total, unidades, utilidad, mayor)`: en cada paso no se modifica, se **reemplaza**
por una tupla nueva.

El filtro del periodo y las categorías es **un único predicado** formado con `y_(...)`, que
combina otros predicados (funciones que devuelven funciones).

La serie mensual usa `range()` para generar todos los meses del periodo (incluso los que no
tienen ventas) y el promedio móvil es un **generador**.
""",
    (resumen, _acumular_resumen, y_, serie_mensual, promedio_movil),
)
