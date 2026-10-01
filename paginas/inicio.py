"""Inicio: presentación del sistema y mapa de conceptos de la Unidad 2."""

import streamlit as st

from core.modelos import CATALOGO, CATEGORIAS_RAIZ, VENDEDORES
from core.reportes import resumen
from ui.componentes import dinero_corto
from ui.estado import todas_las_ventas

ventas = todas_las_ventas()
datos = resumen(ventas)

st.title("📊 VentasFx")
st.subheader("Sistema administrativo de ventas e inventario, construido con programación funcional")
st.markdown(
    "Toda la lógica de negocio está escrita como **funciones puras** que transforman datos "
    "**inmutables**. La interfaz es solo una capa delgada que muestra resultados."
)

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Ventas registradas", f"{datos['transacciones']:,}")
c2.metric("Total vendido", dinero_corto(datos["total"]))
c3.metric("Productos", len(CATALOGO))
c4.metric("Categorías raíz", len(CATEGORIAS_RAIZ))
c5.metric("Vendedores", len(VENDEDORES))

st.divider()

izq, der = st.columns([1.15, 1])

with izq:
    st.markdown("#### Arquitectura: núcleo funcional, capa imperativa delgada")
    st.graphviz_chart("""
    digraph {
      rankdir=TB; bgcolor="transparent"; nodesep=0.25; ranksep=0.45;
      node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=12, fillcolor="#EEF2FF", color="#4F46E5"];
      edge [color="#64748B"];
      ui [label="Capa imperativa · Streamlit\\nclics, formularios, session_state", fillcolor="#FEF3C7", color="#F59E0B", width=4.2];
      subgraph cluster_core { label="Núcleo funcional (core/)"; style="rounded"; color="#4F46E5"; fontname="Helvetica"; fontsize=12;
        {rank=same; pre [label="predicados\\n(operator)"]; pip [label="pipeline\\n(orden superior)"]; arb [label="arbol\\n(recursividad)"]; per [label="perezoso\\n(generadores)"];}
        {rank=same; fun [label="funciones\\n(puras)"]; rep [label="reportes\\n(reduce)"];}
        mod [label="modelos (tipos inmutables)", width=3];
      }
      csv [label="ventas.csv", shape=cylinder, fillcolor="#ECFDF5", color="#10B981"];
      ui -> {pre pip arb per};
      pre -> fun; pip -> rep; rep -> fun; fun -> mod; arb -> mod; per -> mod;
      csv -> per [label=" yield", fontname="Helvetica", fontsize=10];
    }
    """, width="stretch")
    st.info(
        "**Flujo de toda la app:** datos → filtrar (`filter`) → transformar (`map`) → "
        "agregar (`reduce`) → resultado",
        icon="🔁",
    )

with der:
    st.markdown("#### Mapa conceptual de la Unidad 2")
    st.graphviz_chart("""
    digraph {
      bgcolor="transparent"; node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=10, fillcolor="#EEF2FF", color="#4F46E5"];
      pf [label="Programación\\nfuncional", fillcolor="#4F46E5", fontcolor="white"];
      pf -> {pura inm val ord};
      pura [label="Funciones puras"]; inm [label="Inmutabilidad"]; val [label="Funciones\\ncomo valores"]; ord [label="Orden superior"];
      ord -> {lam mfr}; lam [label="lambda"]; mfr [label="map / filter /\\nreduce"];
      val -> rec; rec [label="Recursividad"]; rec -> arb; arb [label="Árboles"];
      mfr -> rng; rng [label="range"]; rng -> it; it [label="Iteradores"]; it -> gen; gen [label="Generadores\\n(yield)"];
    }
    """)

st.divider()
st.markdown("#### ¿Dónde está cada tema de la presentación?")
st.markdown("""
| Tema | Pantalla | Archivo |
|---|---|---|
| Imperativo vs. funcional | Laboratorio → *Imperativo vs funcional* | `core/didactico.py` |
| Funciones puras | Todo el sistema · Laboratorio → *Pureza* | `core/funciones.py`, `tests/` |
| Inmutabilidad | Ventas → *Registrar* / *Historial* (deshacer) · Catálogo → precios | `core/modelos.py`, `ui/estado.py` |
| 2.1 Tipos de datos | Laboratorio → *Tipos* | `core/modelos.py` |
| 2.2 Funciones de primera clase, orden superior, lambda | Ventas → *Explorar* · Laboratorio → *Constructor de flujos* | `core/pipeline.py`, `core/predicados.py` |
| 2.3 Intervalos `range()` | Reportes (meses), paginación, Carga masiva, Laboratorio | `core/reportes.py` |
| 2.4 Operadores y predicados | Ventas → reglas `campo operador valor` | `core/predicados.py` |
| 2.5 map / filter / reduce, comprensiones | Dashboard, Ventas, Reportes | `core/reportes.py` |
| Recursividad | Laboratorio → *Recursividad* | `core/didactico.py` |
| 2.6 Árboles | Catálogo → árbol de categorías y BST por precio | `core/arbol.py` |
| 2.7 Evaluación perezosa, generadores | Carga masiva · ticker en vivo · Laboratorio | `core/perezoso.py` |
""")
st.caption("Cada pantalla tiene un panel **🧠 Concepto aplicado** con la explicación y el código real que se ejecuta.")
