"""Catálogo e inventario: árboles recursivos y transformación inmutable de precios."""

from operator import attrgetter

import pandas as pd
import plotly.express as px
import streamlit as st

from core import arbol as A
from core.funciones import ajustar_precio
from core.modelos import Producto
from core.reportes import agrupar
from ui.componentes import COLORES, dinero, dinero_md, dinero_corto, encabezado, panel_concepto
from ui.estado import estado_actual, registrar_estado, todas_las_ventas

encabezado("Catálogo e inventario", "Las categorías y los precios se organizan en árboles hechos con tuplas.",
           ("recursividad", "árboles", "yield from", "inmutabilidad", "map"))

estado = estado_actual()
ventas = todas_las_ventas()
catalogo = estado.catalogo

tab_cat, tab_bst, tab_inv = st.tabs(
    ["🌳 Árbol de categorías", "🔢 Árbol de búsqueda por precio", "📦 Inventario y precios"])

# =========================================================================
# ÁRBOL N-ARIO DE CATEGORÍAS
# =========================================================================
with tab_cat:
    anios = sorted({v.fecha.year for v in ventas}, reverse=True)
    anio = st.segmented_control("Año de ventas", anios, default=anios[0])
    anio = anio or anios[0]

    # rutas de hojas: categoría/producto  ->  árbol de 5 niveles
    rutas = tuple(f"{p.categoria}/{p.nombre}" for p in catalogo)
    montos = agrupar((v for v in ventas if v.fecha.year == anio),
                     lambda v: f"{v.categoria}/{v.producto}")
    arbol = A.con_totales(A.construir_arbol_categorias(rutas), montos)

    m = st.columns(4)
    m[0].metric("Total del año", dinero_corto(arbol.total))
    m[1].metric("Profundidad", A.profundidad(arbol))
    m[2].metric("Hojas (productos)", sum(1 for _ in A.hojas(arbol)))
    m[3].metric("Nodos totales", sum(1 for _ in A.aplanar(arbol)))

    filas = tuple(A.aplanar(arbol))
    izq, der = st.columns([1.3, 1])
    with izq:
        fig = px.sunburst(
            ids=[f[2] for f in filas], names=[f[1] for f in filas],
            parents=[f[3] if f[0] else "" for f in filas], values=[f[4] for f in filas],
            branchvalues="total", color_discrete_sequence=COLORES,
        )
        fig.update_layout(height=520, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig)
        st.caption("Al hacer clic en un sector se entra a ese subárbol.")

    with der:
        internos = tuple(f[2] for f in filas if A.buscar_nodo(arbol, f[2]).hijos)
        ruta = st.selectbox("Explorar subárbol", internos, index=min(1, len(internos) - 1))
        nodo = A.buscar_nodo(arbol, ruta)
        hoja_top = max(A.hojas(nodo), key=attrgetter("total"))
        st.markdown(f"**{nodo.nombre}** · total {dinero_md(nodo.total)}  \n"
                    f"Profundidad {A.profundidad(nodo)} · {sum(1 for _ in A.hojas(nodo))} productos · "
                    f"más vendido: *{hoja_top.nombre}*")
        with st.container(height=430, border=False):
            st.code("\n".join(A.a_texto(nodo, lambda n: f"{n.nombre}  ({dinero_corto(n.total)})")),
                    language="text")

    panel_concepto(
        "árbol n-ario construido y recorrido con recursividad",
        """
* `construir_arbol_categorias` agrupa las rutas por su primer segmento y **se llama a sí misma**
  con el resto. Caso base: no quedan segmentos.
* `con_totales` devuelve un **árbol nuevo** donde cada nodo suma los totales de sus hijos
  (de abajo hacia arriba). El árbol original queda con total 0.
* `aplanar` y `hojas` son **generadores recursivos** (`yield from`) que alimentan la gráfica.
* `buscar_nodo` busca en profundidad y se detiene en cuanto encuentra (perezoso con `next`).
""",
        (A.construir_arbol_categorias, A.con_totales, A.aplanar, A.profundidad, A.buscar_nodo),
    )

# =========================================================================
# ÁRBOL BINARIO DE BÚSQUEDA (tuplas: (valor, izquierda, derecha))
# =========================================================================
with tab_bst:
    precio = attrgetter("precio")
    modo = st.radio("Construcción", ("Insertando en orden del catálogo (reduce + insertar)",
                                     "Balanceado (elemento de en medio como raíz)"), horizontal=True)
    if modo.startswith("Insertando"):
        bst = A.construir_bst(catalogo, clave=precio)
    else:
        bst = A.construir_balanceado(tuple(sorted(catalogo, key=precio)))

    m = st.columns(4)
    m[0].metric("Nodos", A.contar_nodos(bst))
    m[1].metric("Altura", A.altura(bst))
    m[2].metric("Hojas", A.contar_hojas(bst))
    m[3].metric("Suma de precios", dinero(A.suma_arbol(bst, precio)))

    st.graphviz_chart(A.a_dot(bst, lambda p: f"{p.nombre}\\n{dinero(p.precio)}"), width="stretch")

    c1, c2 = st.columns(2)
    with c1:
        recorrido = st.selectbox("Recorrido", ("inorden", "preorden", "postorden"))
        funcion = {"inorden": A.inorden, "preorden": A.preorden, "postorden": A.postorden}[recorrido]
        st.write(" → ".join(f"{p.nombre} ({p.precio:,.0f})" for p in funcion(bst)))
        if recorrido == "inorden":
            st.caption("En un árbol de búsqueda, el recorrido inorden entrega los precios ordenados.")
    with c2:
        bajo, alto = st.slider("Buscar productos por rango de precio", 0, 40000, (1000, 6000), step=500)
        encontrados = tuple(A.buscar_rango(bst, bajo, alto, precio))
        st.write(f"**{len(encontrados)}** productos entre {dinero_md(bajo)} y {dinero_md(alto)}:")
        st.write(", ".join(p.nombre for p in encontrados) or "—")

    with st.expander("Insertar un producto nuevo (sin modificar el árbol original)"):
        i1, i2 = st.columns(2)
        nombre = i1.text_input("Nombre", "Tablet 11")
        nuevo_precio = i2.number_input("Precio", 1.0, 100000.0, 7499.0)
        nuevo = Producto("NUEVO", nombre, "Electrónica/Cómputo/Tablets", nuevo_precio, 0.0, 0)
        bst_nuevo = A.insertar(bst, nuevo, precio)
        st.markdown(f"Árbol original: **{A.contar_nodos(bst)}** nodos · "
                    f"árbol nuevo: **{A.contar_nodos(bst_nuevo)}** nodos.  \n"
                    f"¿Comparten la rama que no se tocó? "
                    f"**{bst_nuevo[1] is bst[1] or bst_nuevo[2] is bst[2]}** "
                    "(solo se recrean los nodos del camino de inserción).")
        st.graphviz_chart(A.a_dot(bst_nuevo, lambda p: f"{'★ ' if p.sku == 'NUEVO' else ''}{p.nombre}\\n{dinero(p.precio)}"),
                          width="stretch")

    panel_concepto(
        "árbol binario con tuplas (diapositivas 23 y 24)",
        """
Cada nodo es `(valor, izquierda, derecha)` y el árbol vacío es `None`. **Todo es recursivo**:
`suma_arbol` es exactamente la función de la presentación, generalizada con `valor_de`.

La diferencia de **altura** es clara: insertar en el orden del catálogo produce un árbol más
alto que construirlo balanceado; con 34 productos, el balanceado tiene altura 6.
`buscar_rango` **poda** ramas: no visita subárboles que no pueden contener resultados.
""",
        (A.suma_arbol, A.insertar, A.construir_bst, A.construir_balanceado, A.inorden, A.buscar_rango),
    )

# =========================================================================
# INVENTARIO Y AJUSTE DE PRECIOS
# =========================================================================
with tab_inv:
    df = pd.DataFrame([
        {"sku": p.sku, "producto": p.nombre, "categoría": p.categoria, "precio": p.precio,
         "costo": p.costo, "margen": (p.precio - p.costo) / p.precio,
         "stock": estado.inventario[p.sku], "activo": p.activo}
        for p in catalogo
    ])
    bajo_stock = st.slider("Resaltar stock menor a", 0, 200, 30)
    st.dataframe(
        df.style.apply(lambda fila: ["background-color: rgba(239,68,68,.15)" if fila["stock"] < bajo_stock
                                     else "" for _ in fila], axis=1),
        hide_index=True,
        column_config={"precio": st.column_config.NumberColumn(format="dollar"),
                       "costo": st.column_config.NumberColumn(format="dollar"),
                       "margen": st.column_config.ProgressColumn(format="percent", min_value=0, max_value=1)},
    )

    st.markdown("#### Ajuste masivo de precios")
    raices = sorted({p.categoria.split("/")[0] for p in catalogo})
    a1, a2 = st.columns(2)
    objetivo = a1.multiselect("Categorías a ajustar", raices, default=raices[:1])
    porcentaje = a2.slider("Ajuste", -30, 30, 5, format="%d%%") / 100

    afecta = lambda p: p.categoria.startswith(tuple(objetivo))
    # [PF 2.5 map] [PF 2.2 lambda] map con una lambda condicional.
    # [PF inmutable] Produce un catálogo NUEVO; el actual no se toca.
    propuesta = tuple(map(lambda p: ajustar_precio(p, porcentaje) if afecta(p) else p, catalogo))
    diferencias = [(a.nombre, a.precio, b.precio) for a, b in zip(catalogo, propuesta) if a.precio != b.precio]

    st.markdown(f"Vista previa: **{len(diferencias)}** productos cambiarían de precio.")
    if diferencias:
        st.dataframe(pd.DataFrame(diferencias, columns=("producto", "precio actual", "precio nuevo")),
                     hide_index=True, height=220,
                     column_config={"precio actual": st.column_config.NumberColumn(format="dollar"),
                                    "precio nuevo": st.column_config.NumberColumn(format="dollar")})
        if st.button("Aplicar ajuste", type="primary", icon=":material/check:"):
            registrar_estado(estado._replace(
                catalogo=propuesta,
                descripcion=f"Ajuste de precios {porcentaje:+.0%} en {', '.join(objetivo)}",
            ))
            st.toast("Se creó una nueva versión del catálogo. Puedes deshacerla desde Ventas → Registrar.")
            st.rerun()

    panel_concepto(
        "map para producir un catálogo nuevo",
        """
`ajustar_precio` es pura: recibe un `Producto` (dataclass congelada) y devuelve **otro**
producto con `dataclasses.replace`. Intentar `producto.precio = 10` lanza `FrozenInstanceError`.

La vista previa es solo un `map` sobre el catálogo actual. Como nada se modifica, se puede
calcular, mostrar y descartar sin riesgo; si se aplica, se agrega una nueva versión al historial.
""",
        (ajustar_precio,),
    )
