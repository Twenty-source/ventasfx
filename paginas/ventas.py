"""Ventas: explorar con un pipeline de predicados y registrar ventas inmutables."""

from datetime import date
from functools import reduce
from operator import add, attrgetter

import streamlit as st

from core.funciones import (actualizar_stock, calcular_iva, crear_venta, subtotal, total_venta,
                            validar_venta)
from core.modelos import VENDEDORES
from core.pipeline import Paso, ejecutar_pipeline
from core.predicados import (CAMPOS, OPERADORES, entre_fechas, monto_minimo, no_, o_,
                             por_categoria, por_vendedor, regla, siempre, y_)
from core.reportes import indices_pagina, total_paginas
from ui.componentes import CONFIG_VENTAS, dinero, dinero_md, encabezado, flujo, panel_concepto
from ui.estado import (a_dataframe, deshacer, estado_actual, registrar_estado,
                       todas_las_ventas)

encabezado("Ventas", "Explora el historial con filtros que son funciones, y registra ventas sin mutar nada.",
           ("predicados", "operator", "orden superior", "lambda", "inmutabilidad"))

ventas = todas_las_ventas()
estado = estado_actual()

tab_explorar, tab_registrar, tab_historial = st.tabs(
    ["🔎 Explorar (pipeline)", "🧾 Registrar venta", "🕘 Historial de versiones"])

# =========================================================================
# EXPLORAR
# =========================================================================
with tab_explorar:
    subcategorias = sorted({"/".join(v.categoria.split("/")[:2]) for v in ventas})
    fecha_max = max(map(attrgetter("fecha"), ventas))

    with st.container(border=True):
        st.markdown("**1 · Filtros básicos** (cada uno es un predicado)")
        c1, c2, c3, c4 = st.columns([2, 2, 2, 1.3])
        cats = c1.multiselect("Subcategorías", subcategorias, placeholder="Todas")
        vends = c2.multiselect("Vendedores", VENDEDORES, placeholder="Todos")
        rango = c3.date_input("Fechas", value=(date(fecha_max.year, fecha_max.month, 1), fecha_max),
                              format="DD/MM/YYYY")
        minimo = c4.number_input("Total mínimo $", min_value=0, value=0, step=500)

        st.markdown("**2 · Reglas personalizadas** `campo  operador  valor` (usan el módulo `operator`)")
        n_reglas = st.segmented_control("Número de reglas", (0, 1, 2, 3), default=1)
        reglas = []
        for i in range(n_reglas or 0):
            r1, r2, r3 = st.columns([2, 1, 2])
            campo = r1.selectbox("Campo", tuple(CAMPOS), key=f"campo{i}",
                                 index=i % len(CAMPOS))
            simbolo = r2.selectbox("Operador", tuple(OPERADORES), key=f"op{i}", index=3)
            valor = r3.number_input("Valor", key=f"val{i}",
                                    value={"cantidad": 3.0, "precio": 1000.0,
                                           "descuento": 0.1, "total": 5000.0}[campo])
            reglas.append((campo, simbolo, valor))

        c5, c6, c7 = st.columns(3)
        combinar = c5.radio("Combinar reglas con", ("Y (todas)", "O (alguna)"), horizontal=True)
        negar = c6.toggle("Negar reglas (NOT)")
        orden = c7.selectbox("Ordenar por", ("total", "fecha", "cantidad", "precio"))

    # ---- Construcción del predicado: funciones que producen funciones ----
    # [PF 2.4 predicado] Cada filtro de la pantalla se convierte en una función True/False.
    # [PF 2.2 orden superior] por_categoria, por_vendedor... DEVUELVEN predicados.
    basicos = [
        por_categoria(*cats) if cats else siempre,
        por_vendedor(*vends) if vends else siempre,
        entre_fechas(*rango) if len(rango) == 2 else siempre,
        monto_minimo(minimo) if minimo else siempre,
    ]
    # [PF 2.4 operator] Cada regla "campo operador valor" usa operator.gt, operator.eq...
    funciones_regla = [regla(*r) for r in reglas]
    combinador = y_ if combinar.startswith("Y") else o_
    personalizadas = combinador(*funciones_regla) if funciones_regla else siempre
    if negar and funciones_regla:
        personalizadas = no_(personalizadas)
    # [PF 2.2 orden superior] Todo se combina en UN solo predicado con y_/o_/no_.
    predicado = y_(*basicos, personalizadas)

    # [PF 2.2 primera clase] La clave de orden es una función guardada en una variable.
    clave_orden = total_venta if orden == "total" else attrgetter(orden)

    # ---- Pipeline con pasos visibles ----
    # [PF 2.5 filter] -> sorted -> [PF 2.5 map] -> [PF 2.5 reduce]
    # [PF 2.2 lambda] Cada paso es una función anónima guardada en una tupla.
    pasos = (
        Paso("filter(predicado)", lambda vs: tuple(filter(predicado, vs))),
        Paso("sorted(key)", lambda vs: tuple(sorted(vs, key=clave_orden, reverse=True))),
        Paso("map(total_venta)", lambda vs: (vs, tuple(map(total_venta, vs)))),
        Paso("reduce(add)", lambda par: (par[0], reduce(add, par[1], 0.0))),
    )
    etapas = ejecutar_pipeline(ventas, pasos)
    filtradas, total = etapas[-1]

    st.markdown("**Pipeline ejecutado** — cada tarjeta es el resultado intermedio de un paso:")
    flujo((
        ("datos", f"{len(etapas[0]):,} ventas"),
        ("filter", f"{len(etapas[1]):,} ventas"),
        ("sorted", f"por {orden}"),
        ("map", f"{len(etapas[3][1]):,} totales"),
        ("reduce", dinero(total)),
    ))

    texto_reglas = ", ".join(f'regla("{c}", "{s}", {v:g})' for c, s, v in reglas)
    expresion = f"{'o_' if combinador is o_ else 'y_'}({texto_reglas})" if reglas else "siempre"
    if negar and reglas:
        expresion = f"no_({expresion})"
    st.code(
        "predicado = y_(\n"
        f"    {'por_categoria(' + ', '.join(map(repr, cats)) + ')' if cats else 'siempre'},\n"
        f"    {'por_vendedor(' + ', '.join(map(repr, vends)) + ')' if vends else 'siempre'},\n"
        f"    entre_fechas{tuple(map(str, rango))},\n"
        f"    {'monto_minimo(' + str(minimo) + ')' if minimo else 'siempre'},\n"
        f"    {expresion},\n)",
        language="python",
    )

    # ---- Resultado paginado con range ----
    if filtradas:
        tam = 25
        paginas = total_paginas(len(filtradas), tam)
        p1, p2 = st.columns([1, 4])
        pagina = p1.number_input(f"Página (de {paginas:,})", 1, paginas, 1)
        # [PF 2.3 range] Solo se convierten a tabla las filas del rango visible.
        indices = indices_pagina(len(filtradas), tam, pagina)
        p2.caption(f"Mostrando {indices}  →  filas {indices.start + 1}–{indices.stop} "
                   f"de {len(filtradas):,}")
        df = a_dataframe(tuple(filtradas[i] for i in indices))
        st.dataframe(df, hide_index=True, column_config=CONFIG_VENTAS)
        st.download_button("Descargar resultado (CSV)", a_dataframe(filtradas).to_csv(index=False),
                           file_name="ventas_filtradas.csv", mime="text/csv", icon=":material/download:")
    else:
        st.info("Ninguna venta cumple el predicado.")

    panel_concepto(
        "predicados, operator y funciones de orden superior",
        """
* `regla(campo, operador, valor)` **devuelve una función**. El operador se busca en el
  diccionario `OPERADORES`, donde `>` es `operator.gt`, `==` es `operator.eq`, etc.
* `y_`, `o_` y `no_` reciben predicados y **devuelven un predicado nuevo** (AND / OR / NOT).
* El resultado es UN solo predicado que se pasa a `filter`.
* `ejecutar_pipeline` usa `itertools.accumulate` para conservar cada resultado intermedio
  y poder dibujar las tarjetas del flujo.
* La paginación usa `range()`: solo se convierten a tabla las 25 filas visibles.
""",
        (regla, y_, o_, no_, ejecutar_pipeline, indices_pagina),
    )

# =========================================================================
# REGISTRAR
# =========================================================================
with tab_registrar:
    activos = tuple(p for p in estado.catalogo if p.activo)
    izq, der = st.columns([1.2, 1])

    with izq:
        with st.form("nueva_venta", border=True):
            st.markdown("**Nueva venta**")
            producto = st.selectbox(
                "Producto", activos,
                format_func=lambda p: f"{p.nombre} · {dinero(p.precio)} · stock {estado.inventario[p.sku]}")
            f1, f2 = st.columns(2)
            cantidad = f1.number_input("Cantidad", 1, 999, 1)
            descuento = f2.select_slider("Descuento", options=(0.0, 0.05, 0.10, 0.15, 0.20, 0.30),
                                         format_func=lambda d: f"{d:.0%}")
            f3, f4 = st.columns(2)
            vendedor = f3.selectbox("Vendedor", VENDEDORES)
            fecha = f4.date_input("Fecha", value=date.today(), format="DD/MM/YYYY")
            enviado = st.form_submit_button("Registrar venta", type="primary", icon=":material/add:")

        if enviado:
            venta = crear_venta(next(st.session_state.folios), fecha, producto, int(cantidad),
                                descuento, vendedor)
            errores = validar_venta(venta, estado.inventario)
            if errores:
                for e in errores:
                    st.error(e)
            else:
                # [PF inmutable] Un estado NUEVO: inventario nuevo + tupla de ventas nueva.
                # El estado anterior queda intacto en el historial (por eso se puede deshacer).
                registrar_estado(estado._replace(
                    inventario=actualizar_stock(estado.inventario, venta.sku, -venta.cantidad),
                    ventas_nuevas=estado.ventas_nuevas + (venta,),
                    descripcion=f"Venta {venta.folio}: {venta.cantidad} × {venta.producto}",
                ))
                st.session_state.ultimo_ticket = venta
                st.rerun()

    with der:
        ticket = st.session_state.get("ultimo_ticket")
        if ticket:
            with st.container(border=True):
                st.markdown(f"**Ticket {ticket.folio}** · {ticket.fecha:%d/%m/%Y}")
                st.markdown(f"{ticket.cantidad} × {ticket.producto} @ {dinero_md(ticket.precio)}")
                st.markdown(f"Descuento: {ticket.descuento:.0%}  ·  Vendedor: {ticket.vendedor}")
                st.markdown(f"Subtotal: {dinero_md(subtotal(ticket))}  \nIVA: {dinero_md(calcular_iva(subtotal(ticket)))}")
                st.markdown(f"### Total: {dinero_md(total_venta(ticket))}")
        if st.button("Deshacer última acción", icon=":material/undo:",
                     disabled=len(st.session_state.historial) == 1):
            deshacer()
            st.session_state.pop("ultimo_ticket", None)
            st.rerun()
        st.caption("Deshacer es trivial porque ningún estado se modificó: solo se vuelve al anterior.")

    st.markdown(f"**Ventas registradas en esta sesión:** {len(estado.ventas_nuevas)}")
    if estado.ventas_nuevas:
        st.dataframe(a_dataframe(estado.ventas_nuevas), hide_index=True, column_config=CONFIG_VENTAS)

    panel_concepto(
        "inmutabilidad: cada acción produce un estado nuevo",
        """
* `crear_venta` construye una `Venta` (NamedTuple: inmutable).
* `validar_venta` devuelve una **tupla de errores** construida con una comprensión.
* `actualizar_stock` devuelve un **diccionario nuevo** con `{**inventario, sku: ...}`.
* El nuevo `EstadoTienda` se crea con `_replace` y se agrega al historial.
* El folio sale de un **generador infinito** (`folios()`): cada `next()` produce el siguiente.
""",
        (crear_venta, validar_venta, actualizar_stock),
    )

# =========================================================================
# HISTORIAL
# =========================================================================
with tab_historial:
    historial = st.session_state.historial
    st.markdown(f"Hay **{len(historial)}** versiones del estado de la tienda. "
                "Ninguna fue modificada: cada acción agregó una nueva.")
    st.dataframe(
        [{"versión": i, "acción": e.descripcion, "ventas nuevas": len(e.ventas_nuevas),
          "unidades en inventario": sum(e.inventario.values()),
          "precio promedio catálogo": round(sum(p.precio for p in e.catalogo) / len(e.catalogo), 2)}
         for i, e in enumerate(historial)],
        hide_index=True,
    )
    if len(historial) > 1:
        a, b = st.columns(2)
        va = a.selectbox("Comparar versión", range(len(historial)), index=0)
        vb = b.selectbox("contra versión", range(len(historial)), index=len(historial) - 1)
        ea, eb = historial[va], historial[vb]
        # Dos comprensiones: una para stock y otra para precios
        cambios = [(sku, "stock", ea.inventario[sku], eb.inventario[sku])
                   for sku in ea.inventario if ea.inventario[sku] != eb.inventario[sku]]
        precios = [(pa.sku, "precio", pa.precio, pb.precio)
                   for pa, pb in zip(ea.catalogo, eb.catalogo) if pa.precio != pb.precio]
        st.markdown(f"**Diferencias entre la versión {va} y la {vb}** (calculadas con comprensiones):")
        if cambios or precios:
            st.dataframe([{"sku": k, "campo": c, "antes": a, "después": d} for k, c, a, d in cambios + precios],
                         hide_index=True)
        else:
            st.caption("Sin diferencias.")
