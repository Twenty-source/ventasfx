"""Laboratorio: demostraciones interactivas de cada tema de la Unidad 2."""

import inspect
import operator
import re
import sys
from dataclasses import FrozenInstanceError
from functools import reduce

import streamlit as st

from core import arbol as A
from core import didactico as d
from core.modelos import CATALOGO, CATEGORIAS_RAIZ, INDICE_PRODUCTOS, TASA_IVA, VENDEDORES
from core.perezoso import cuadrados_generador, cuadrados_lista, numeros
from core.pipeline import aplicar, compose, cronometrar
from ui.componentes import encabezado, flujo, panel_concepto
from ui.estado import ventas_historicas

encabezado("Laboratorio funcional", "Cada pestaña demuestra un tema de la presentación con el código real.",
           ("Unidad 2 completa",))

tabs = st.tabs(["⚖️ Imperativo vs funcional", "🔒 Pureza", "🧱 Tipos", "🧩 Constructor de flujos",
                "🔁 Recursividad", "🌲 Árbol", "♾️ Generadores"])

# =========================================================================
# 1. IMPERATIVO vs FUNCIONAL
# =========================================================================
with tabs[0]:
    nombre = st.selectbox("Problema", tuple(d.PROBLEMAS))
    problema = d.PROBLEMAS[nombre]
    st.caption(problema["descripcion"])

    if problema["entrada"] == "numeros":
        n = st.select_slider("Números del 1 al…", (10, 100, 1_000, 10_000, 100_000, 1_000_000), value=10,
                             format_func=lambda x: f"{x:,}", help="Prueba con valores grandes para comparar tiempos")
        entrada = range(1, n + 1)
        st.caption(f"Entrada: `range(1, {n + 1})`")
    else:
        n = st.slider("¿Cuántas ventas usar?", 100, len(ventas_historicas()), 5_000, step=100)
        entrada = ventas_historicas()[:n]
        st.caption(f"Entrada: las primeras {n:,} ventas del historial")

    izq, der = st.columns(2)
    for col, estilo in ((izq, "imperativo"), (der, "funcional")):
        with col:
            st.markdown(f"**{estilo.capitalize()}**")
            st.code(inspect.getsource(problema[estilo]), language="python", wrap_lines=True)

    if st.button("Ejecutar ambas", type="primary", icon=":material/play_arrow:"):
        r_imp, t_imp = cronometrar(problema["imperativo"])(entrada)
        r_fun, t_fun = cronometrar(problema["funcional"])(entrada)
        c1, c2, c3 = st.columns(3)
        c1.metric("Imperativo", f"{t_imp:,.1f} ms")
        c2.metric("Funcional", f"{t_fun:,.1f} ms")
        c3.metric("¿Mismo resultado?", "Sí ✅" if r_imp == r_fun else "No ❌")
        vista = r_fun if not isinstance(r_fun, (list, dict)) else (
            r_fun[:20] if isinstance(r_fun, list) else dict(list(r_fun.items())[:8]))
        st.write("Resultado (vista previa):", vista)
    st.info("Pregunta al grupo: **¿qué cambió en la forma de pensar el problema?** "
            "El imperativo describe *cómo* (ciclos, acumuladores que cambian); "
            "el funcional describe *qué* (filtrar, transformar, combinar).")

# =========================================================================
# 2. PUREZA E INMUTABILIDAD
# =========================================================================
with tabs[1]:
    st.markdown("#### Función impura vs función pura (diapositiva 6)")
    izq, der = st.columns(2)
    with izq:
        st.code(inspect.getsource(d.agregar), language="python")
        if "llamadas_agregar" not in st.session_state:
            d.reiniciar_total()
            st.session_state.llamadas_agregar = ()
        b1, b2 = st.columns(2)
        if b1.button("agregar(5)"):
            st.session_state.llamadas_agregar += (d.agregar(5),)
        if b2.button("Reiniciar"):
            d.reiniciar_total()
            st.session_state.llamadas_agregar = ()
        for i, r in enumerate(st.session_state.llamadas_agregar, 1):
            st.write(f"llamada {i}: `agregar(5)` → **{r}**")
        st.caption("Misma entrada, salida distinta: depende de la variable global `total`.")
    with der:
        st.code(inspect.getsource(d.cuadrado), language="python")
        veces = st.number_input("¿Cuántas veces llamar cuadrado(5)?", 1, 10, 3)
        st.write([d.cuadrado(5) for _ in range(veces)])
        st.caption("Siempre 25. Se puede probar, memoizar y componer sin sorpresas.")

    st.divider()
    st.markdown("#### Inmutabilidad: lista vs tupla (diapositiva 7)")
    izq, der = st.columns(2)
    with izq:
        st.markdown("**Lista mutable**")
        lista = [1, 2, 3]
        id_antes = id(lista)
        lista.append(4)
        st.code("numeros = [1, 2, 3]\nnumeros.append(4)", language="python")
        st.write(f"Resultado: `{lista}` · ¿Es el mismo objeto? **{id(lista) == id_antes}** "
                 "→ se modificó el original.")
    with der:
        st.markdown("**Tupla inmutable**")
        tupla = (1, 2, 3)
        nuevos = tupla + (4,)
        st.code("numeros = (1, 2, 3)\nnuevos = numeros + (4,)", language="python")
        st.write(f"Original: `{tupla}` · Nuevo: `{nuevos}` · ¿Mismo objeto? **{tupla is nuevos}** "
                 "→ se produjo otro valor.")

    st.markdown("**¿Qué pasa si intento modificar algo inmutable del sistema?**")
    intentos = {
        "tupla[0] = 99": lambda: operator.setitem((1, 2, 3), 0, 99),
        "CATALOGO[0].precio = 1": lambda: setattr(CATALOGO[0], "precio", 1),
        "venta.cantidad = 5": lambda: setattr(ventas_historicas()[0], "cantidad", 5),
    }
    for codigo, intento in intentos.items():
        try:
            intento()
            st.write(f"`{codigo}` → se modificó (no debería pasar)")
        except (TypeError, AttributeError, FrozenInstanceError) as error:
            st.write(f"`{codigo}` → ❌ `{type(error).__name__}`: {error}")

# =========================================================================
# 3. TIPOS DE DATOS
# =========================================================================
with tabs[2]:
    st.markdown("#### 2.1 Tipos de datos usados en el sistema")
    ejemplo = CATALOGO[0]
    tipos = (
        ("int", "stock de un producto", ejemplo.stock, "No (valor)"),
        ("float", "precio de un producto", ejemplo.precio, "No (valor)"),
        ("bool", "¿producto activo?", ejemplo.activo, "No (valor)"),
        ("str", "nombre de un producto", ejemplo.nombre, "No"),
        ("tuple", "VENDEDORES", VENDEDORES[:3] + ("…",), "No ✅"),
        ("set", "CATEGORIAS_RAIZ", CATEGORIAS_RAIZ, "Sí"),
        ("frozenset", "vendedores en por_vendedor()", frozenset(VENDEDORES[:2]), "No ✅"),
        ("dict", "INDICE_PRODUCTOS (sku → Producto)", f"{{'{ejemplo.sku}': Producto(...), …}} ({len(INDICE_PRODUCTOS)} claves)", "Sí"),
        ("list", "selecciones del usuario en la interfaz", ["Hogar", "Deportes"], "Sí"),
        ("NamedTuple", "Venta", "Venta(folio, fecha, sku, …)", "No ✅"),
        ("dataclass(frozen)", "Producto", "Producto(sku, nombre, …)", "No ✅"),
        ("range", "periodos y paginación", range(0, 25), "No ✅"),
        ("function", "total_venta", "<function total_venta>", "Es un valor más"),
    )
    st.dataframe(
        [{"tipo": t, "dónde se usa": u, "ejemplo": str(e), "¿mutable?": m} for t, u, e, m in tipos],
        hide_index=True,
    )
    st.info("Punto clave: **datos originales → transformación → nuevos datos**. "
            f"Ejemplo: `TASA_IVA = {TASA_IVA}` es un float que ninguna función cambia.")

# =========================================================================
# 4. CONSTRUCTOR DE FLUJOS: range + predicado + map + reduce
# =========================================================================
with tabs[3]:
    st.markdown("#### Funciones como valores: elige funciones de un diccionario y combínalas")
    c1, c2, c3 = st.columns(3)
    inicio = c1.number_input("range: inicio", -100, 1000, 1)
    fin = c2.number_input("range: fin (excluido)", -100, 10_000, 11)
    paso = c3.number_input("range: paso", -10, 10, 1)
    paso = paso or 1
    c4, c5, c6 = st.columns(3)
    pred = c4.selectbox("filter con el predicado", tuple(d.PREDICADOS))
    trans = c5.selectbox("map con la transformación", tuple(d.TRANSFORMACIONES))
    red = c6.selectbox("reduce con", tuple(d.REDUCTORES))

    r = d.ejecutar_flujo(inicio, fin, paso, pred, trans, red)

    def corto(t):
        return str(t[:8])[:-1] + (", …)" if len(t) > 8 else ")") if t else "()"

    flujo((
        (f"range({inicio}, {fin}, {paso})", f"{len(r['intervalo'])} números"),
        ("filter", f"{len(r['filtrados'])} pasan"),
        ("map", trans.split(" ")[0]),
        ("reduce", f"{r['resultado']:,}" if isinstance(r["resultado"], int) else f"{r['resultado']:,.2f}"),
    ))
    st.write(f"Intervalo: `{corto(r['intervalo'])}`  \nFiltrados: `{corto(r['filtrados'])}`  \n"
             f"Transformados: `{corto(r['transformados'])}`")

    funcional, comprension = d.codigo_flujo(inicio, fin, paso, pred, trans, red)
    izq, der = st.columns(2)
    izq.markdown("**Con map / filter / reduce**")
    izq.code(funcional, language="python")
    der.markdown("**Con comprensión de listas** (estilo idiomático)")
    der.code(comprension, language="python", wrap_lines=True)
    st.caption("Advertencia didáctica: programar funcionalmente en Python no significa abusar de lambda, map y filter. "
               "A veces la comprensión es más legible.")

    st.divider()
    st.markdown("#### Composición y orden superior")
    elegidas = st.multiselect("Componer estas transformaciones (se aplican de derecha a izquierda)",
                              tuple(d.TRANSFORMACIONES), default=("x + 10", "x² (cuadrado)"))
    valor = st.number_input("Valor de entrada", -1000, 1000, 3)
    funciones = tuple(d.TRANSFORMACIONES[e][0] for e in elegidas)
    compuesta = compose(*funciones)
    # Expresión equivalente: se sustituye x de adentro hacia afuera (también con reduce)
    expresiones = [d.TRANSFORMACIONES[e][2] for e in elegidas]
    expresion = reduce(lambda acc, ex: re.sub(r"\bx\b", f"({acc})", ex), reversed(expresiones), str(valor))
    st.write(f"`compose({', '.join(d.TRANSFORMACIONES[e][1] for e in elegidas)})({valor})`  ≡  `{expresion}`")
    st.write(f"`aplicar(compuesta, {valor})` → **{aplicar(compuesta, valor)}**")

    panel_concepto(
        "funciones de primera clase y orden superior",
        """
Las funciones viven en **diccionarios** (`PREDICADOS`, `TRANSFORMACIONES`, `REDUCTORES`):
se buscan por nombre, se guardan en variables y se pasan a `filter`, `map` y `reduce`.
`compose` recibe funciones y **devuelve una función nueva**, construida a su vez con `reduce`.
""",
        (d.ejecutar_flujo, compose, aplicar),
    )

# =========================================================================
# 5. RECURSIVIDAD
# =========================================================================
with tabs[4]:
    izq, der = st.columns(2)
    with izq:
        st.markdown("#### Factorial (diapositiva 22)")
        n = st.slider("n", 0, 12, 5, key="n_factorial")
        st.code("\n".join(d.factorial_traza(n)) + f"\n= {d.factorial(n):,}", language="text")
        st.code(inspect.getsource(d.factorial), language="python")
        st.caption("Pregunta: ¿dónde está el `for`? No existe: el caso base detiene la recursión.")
    with der:
        st.markdown("#### Fibonacci: recursión ingenua vs memoizada")
        n = st.slider("n", 5, 27, 20, key="n_fibonacci")
        sin_memo, contador_sin = d.nuevo_fibonacci_contado(False)
        con_memo, contador_con = d.nuevo_fibonacci_contado(True)
        r1, t1 = cronometrar(sin_memo)(n)
        r2, t2 = cronometrar(con_memo)(n)
        c1, c2 = st.columns(2)
        c1.metric(f"Sin memoizar · {t1:,.1f} ms", f"{contador_sin.llamadas:,} llamadas")
        c2.metric(f"Con lru_cache · {t2:,.2f} ms", f"{contador_con.llamadas:,} llamadas")
        st.write(f"fib({n}) = **{r1:,}** (ambas dan {r2:,})")
        st.caption("Memoizar solo es correcto porque la función es **pura**: el mismo n siempre da el mismo resultado.")
        st.code(inspect.getsource(d.nuevo_fibonacci_contado), language="python", wrap_lines=True)

# =========================================================================
# 6. ÁRBOL DE LA PRESENTACIÓN
# =========================================================================
with tabs[5]:
    st.markdown("#### El árbol de las diapositivas 23 y 24")
    izq, der = st.columns([1, 1.2])
    with izq:
        st.graphviz_chart(A.a_dot(A.ARBOL_EJEMPLO))
    with der:
        st.code("arbol = (\n    10,\n    (5, (2, None, None), (7, None, None)),\n"
                "    (15, (12, None, None), (20, None, None))\n)\n# Cada nodo: (valor, izquierda, derecha)",
                language="python")
        st.code(inspect.getsource(A.suma_arbol), language="python")
    m = st.columns(4)
    m[0].metric("suma_arbol(arbol)", A.suma_arbol(A.ARBOL_EJEMPLO))
    m[1].metric("Nodos", A.contar_nodos(A.ARBOL_EJEMPLO))
    m[2].metric("Altura", A.altura(A.ARBOL_EJEMPLO))
    m[3].metric("Hojas", A.contar_hojas(A.ARBOL_EJEMPLO))
    st.write(f"Inorden: `{list(A.inorden(A.ARBOL_EJEMPLO))}` · Preorden: `{list(A.preorden(A.ARBOL_EJEMPLO))}` · "
             f"Postorden: `{list(A.postorden(A.ARBOL_EJEMPLO))}`")

    valor = st.number_input("Insertar un valor (devuelve un árbol nuevo)", -100, 100, 6)
    nuevo = A.insertar(A.ARBOL_EJEMPLO, valor)
    st.graphviz_chart(A.a_dot(nuevo, lambda v: f"★ {v}" if v == valor else str(v)))
    st.caption(f"El árbol original sigue sumando {A.suma_arbol(A.ARBOL_EJEMPLO)}; "
               f"el nuevo suma {A.suma_arbol(nuevo)}. Integra funciones, tuplas, inmutabilidad y recursividad.")

# =========================================================================
# 7. GENERADORES
# =========================================================================
with tabs[6]:
    izq, der = st.columns(2)
    with izq:
        st.markdown("#### Secuencia infinita (diapositiva 27)")
        st.code(inspect.getsource(numeros), language="python")
        if "gen_numeros" not in st.session_state:
            st.session_state.gen_numeros = numeros()
            st.session_state.salidas_numeros = ()
        b1, b2 = st.columns(2)
        if b1.button("next(generador)"):
            st.session_state.salidas_numeros += (next(st.session_state.gen_numeros),)
        if b2.button("Nuevo generador"):
            st.session_state.gen_numeros = numeros()
            st.session_state.salidas_numeros = ()
        st.write(" → ".join(map(str, st.session_state.salidas_numeros[-25:])) or "Aún no se pide ningún valor.")
        st.info("¿Cómo puede existir una secuencia infinita si la memoria es finita? "
                "**No se almacena completa: se genera elemento por elemento cuando se necesita.**")
    with der:
        st.markdown("#### Lista vs generador (diapositiva 26)")
        n = st.select_slider("n", (1_000, 10_000, 100_000, 1_000_000), value=100_000, key="n_generador",
                             format_func=lambda x: f"{x:,}")
        lista = cuadrados_lista(n)
        gen = cuadrados_generador(n)
        c1, c2 = st.columns(2)
        c1.metric("cuadrados_lista(n)", f"{sys.getsizeof(lista) / 1024:,.0f} KB")
        c2.metric("cuadrados_generador(n)", f"{sys.getsizeof(gen)} bytes")
        st.write(f"Primeros valores del generador: `{next(gen)}, {next(gen)}, {next(gen)}` …")
        st.code(inspect.getsource(cuadrados_generador), language="python")
        st.caption("`yield` produce valores conforme se solicitan, sin construir toda la colección por adelantado. "
                   "Los generadores aplicados a ventas reales están en **Carga masiva**.")
