"""Carga masiva: evaluación perezosa con archivos grandes y flujos infinitos."""

import sys
import time
from datetime import date
from itertools import islice

import plotly.express as px
import streamlit as st

from core.funciones import total_venta
from core.perezoso import (en_lotes, escribir_ventas, folios, hasta_alcanzar, leer_ventas,
                           medir_memoria, simular_ventas, tomar)
from core.predicados import por_categoria, regla, y_
from core.reportes import total_general
from ui.componentes import CONFIG_VENTAS, COLORES, dinero, dinero_md, encabezado, flujo, panel_concepto
from ui.estado import EN_LA_NUBE, RUTA_MASIVO, a_dataframe

encabezado("Carga masiva", "Procesar muchos datos sin cargarlos en memoria, y trabajar con flujos infinitos.",
           ("range", "iteradores", "generadores", "yield", "itertools"))


def con_progreso(iterable, total: int, barra):
    """
    Generador 'envoltura': deja pasar cada elemento tal cual y, de paso,
    actualiza la barra de progreso. Encadenar generadores = pipeline perezoso.
    """
    # [PF 2.7 generador] Se intercala entre otros generadores sin cargar nada en memoria.
    # [PF efecto] Mover la barra es un efecto de interfaz; por eso vive en la página.
    for i, elemento in enumerate(iterable, start=1):
        if i % 5000 == 0 or i == total:
            barra.progress(min(i / total, 1.0), text=f"{i:,} de {total:,}")
        yield elemento


# =========================================================================
st.markdown("### 1 · `range()` no guarda sus elementos")
c1, c2, c3 = st.columns(3)
grande = range(1, 1_000_000_000)
c1.metric("range(1, 1_000_000_000)", f"{sys.getsizeof(grande)} bytes")
c2.metric("list(range(1_000_000))", f"{sys.getsizeof(list(range(1_000_000))) / 1e6:.1f} MB")
c3.metric("Elemento 500 000 000 del range", f"{grande[499_999_999]:,}")
st.caption("El range de mil millones ocupa lo mismo que uno de diez: solo guarda inicio, fin y paso.")

st.divider()

# =========================================================================
st.markdown("### 2 · Generar un archivo grande con un generador")
g1, g2 = st.columns([2, 1])
# En la nube la memoria es limitada: la versión ANSIOSA de la sección 3 con un millón de
# ventas necesita ~600 MB. Ahí solo se ofrecen tamaños seguros.
opciones = (50_000, 100_000, 250_000) if EN_LA_NUBE else (100_000, 250_000, 500_000, 1_000_000)
filas = g1.select_slider("Número de ventas", options=opciones, value=100_000 if EN_LA_NUBE else 250_000,
                         format_func=lambda n: f"{n:,}")
if EN_LA_NUBE:
    g1.caption("Versión en línea: máximo 250 000 ventas para no rebasar la memoria del servidor.")
existe = RUTA_MASIVO.exists()
g2.markdown(f"Archivo actual: **{'masivo.csv · ' + format(RUTA_MASIVO.stat().st_size / 1e6, '.1f') + ' MB' if existe else 'no existe'}**")

if g2.button("Generar archivo", type="primary", icon=":material/bolt:"):
    barra = st.progress(0.0, text="Generando…")
    inicio = time.perf_counter()
    # Flujo INFINITO -> islice toma solo n -> progreso -> escritura (todo perezoso)
    flujo_ventas = islice(simular_ventas(semilla=99, fecha_inicio=date(2024, 1, 1)), filas)
    escritas = escribir_ventas(str(RUTA_MASIVO), con_progreso(flujo_ventas, filas, barra))
    st.success(f"{escritas:,} ventas escritas en {time.perf_counter() - inicio:.1f} s")
    st.rerun()

st.code("escribir_ventas(ruta, con_progreso(islice(simular_ventas(), n), n, barra))", language="python")

if not RUTA_MASIVO.exists():
    st.info("Al generar el archivo se habilitan las siguientes demostraciones.")
    st.stop()

st.divider()

# =========================================================================
st.markdown("### 3 · Ansioso vs perezoso: el mismo total, distinta memoria")
st.caption("Se mide el pico de memoria con `tracemalloc` (la medición hace todo un poco más lento).")


def total_ansioso(ruta):
    """Carga TODAS las ventas en una lista y luego suma."""
    # Evaluación ANSIOSA: list() materializa todo el archivo en memoria.
    todas = list(leer_ventas(ruta))
    return total_general(todas)


def total_perezoso(ruta):
    """Suma conforme lee: nunca existe la colección completa."""
    # [PF 2.7 perezoso] El iterador va directo al reduce: una venta a la vez.
    return total_general(leer_ventas(ruta))


if st.button("Comparar", icon=":material/compare_arrows:"):
    resultados = {}
    for nombre, funcion in (("Ansioso (list)", total_ansioso), ("Perezoso (generador)", total_perezoso)):
        with st.spinner(f"Ejecutando {nombre}…"):
            inicio = time.perf_counter()
            total, pico = medir_memoria(funcion, str(RUTA_MASIVO))
            resultados[nombre] = (total, pico / 1e6, time.perf_counter() - inicio)
    st.session_state.comparacion = resultados

if "comparacion" in st.session_state:
    res = st.session_state.comparacion
    m = st.columns(len(res) + 1)
    for col, (nombre, (total, mb, seg)) in zip(m, res.items()):
        col.metric(nombre, f"{mb:,.1f} MB", help=f"Total: {dinero(total)} · {seg:.1f} s")
    (ans, per) = (res["Ansioso (list)"][1], res["Perezoso (generador)"][1])
    m[-1].metric("Ahorro de memoria", f"{ans / per:,.0f}× menos" if per else "—")
    fig = px.bar(x=list(res), y=[r[1] for r in res.values()], color=list(res),
                 color_discrete_sequence=(COLORES[4], COLORES[2]), labels={"x": "", "y": "MB pico"})
    fig.update_layout(height=280, showlegend=False, margin=dict(l=0, r=0, t=10, b=0))
    st.plotly_chart(fig)
    st.caption(f"Ambos totales son iguales: **{res['Ansioso (list)'][0] == res['Perezoso (generador)'][0]}**")

st.divider()

# =========================================================================
st.markdown("### 4 · Leer solo lo necesario")
b1, b2, b3 = st.columns(3)
categoria = b1.selectbox("Categoría", ("Electrónica", "Hogar", "Deportes", "Papelería"))
monto = b2.number_input("Total mayor a $", 0, 200_000, 20_000, step=5_000)
cuantas = b3.number_input("¿Cuántas quiero?", 1, 100, 10)

predicado = y_(por_categoria(categoria), regla("total", ">", monto))
inicio = time.perf_counter()
# enumerate numera las filas conforme se leen; así se sabe cuántas se leyeron realmente.
# [PF 2.7 perezoso] filter + islice (dentro de tomar) dejan de leer al tener `cuantas`.
numeradas = enumerate(leer_ventas(str(RUTA_MASIVO)), start=1)
pares = tomar(cuantas, filter(lambda par: predicado(par[1]), numeradas))
primeras = tuple(venta for _, venta in pares)
ms = (time.perf_counter() - inicio) * 1000
leidas = f"{pares[-1][0]:,} filas" if len(pares) == cuantas else "todo el archivo"
flujo((("archivo", "CSV en disco"), ("enumerate", f"{leidas}"), ("filter", "predicado"),
       ("islice", f"{len(primeras)} ventas"), ("tiempo", f"{ms:,.0f} ms")))
st.caption("`islice` deja de pedir datos al alcanzar la cantidad: el resto del archivo **nunca se lee**.")
if primeras:
    st.dataframe(a_dataframe(primeras), hide_index=True, column_config=CONFIG_VENTAS, height=250)

st.markdown("**Procesamiento por lotes:** totales de los primeros 10 lotes de 10 000 ventas")


@st.cache_data(show_spinner=False)
def totales_por_lote(ruta: str, version: float, tamano: int = 10_000, cuantos: int = 10) -> tuple:
    """`version` (fecha de modificación del archivo) invalida la caché si se regenera."""
    return tuple(map(total_general, islice(en_lotes(leer_ventas(ruta), tamano), cuantos)))


totales_lotes = totales_por_lote(str(RUTA_MASIVO), RUTA_MASIVO.stat().st_mtime)
st.bar_chart({"Lote": [f"#{i:02d}" for i in range(1, len(totales_lotes) + 1)], "Total": totales_lotes},
             x="Lote", y="Total", color=COLORES[1])

panel_concepto(
    "lectura perezosa de archivos",
    """
* `leer_filas` usa `yield from csv.DictReader(...)`: el archivo se lee **línea por línea**.
* `leer_ventas` es un `map`: convierte cada fila cuando se pide, no antes.
* `filter` + `islice` se detienen en cuanto tienen lo que necesitan.
* `en_lotes` agrupa un flujo en tuplas de tamaño fijo con `islice` + `takewhile`.
""",
    (leer_ventas, en_lotes, tomar),
)

st.divider()

# =========================================================================
st.markdown("### 5 · Una secuencia infinita de ventas")
st.caption("`simular_ventas()` sin número de días es un generador **infinito**. "
           "Solo existe la venta que se pide con `next()`.")

if "ticker" not in st.session_state:
    st.session_state.ticker = simular_ventas(semilla=2026, fecha_inicio=date.today())
    st.session_state.ticker_vistas = ()


def avanzar(n: int):
    nuevas = tomar(n, st.session_state.ticker)
    st.session_state.ticker_vistas = (nuevas[::-1] + st.session_state.ticker_vistas)[:200]  # la más reciente primero


t1, t2, t3, t4 = st.columns(4)
t1.button("next() — 1 venta", on_click=avanzar, args=(1,), icon=":material/skip_next:")
t2.button("islice — 10 ventas", on_click=avanzar, args=(10,), icon=":material/fast_forward:")
en_vivo = t3.toggle("Transmitir en vivo")
if t4.button("Reiniciar generador", icon=":material/restart_alt:"):
    del st.session_state["ticker"]
    st.rerun()


@st.fragment(run_every=1.0 if en_vivo else None)
def ticker():
    if en_vivo:
        avanzar(3)
    vistas = st.session_state.ticker_vistas
    k1, k2, k3 = st.columns(3)
    k1.metric("Ventas consumidas del generador", f"{len(vistas):,}" + ("+" if len(vistas) == 200 else ""))
    k2.metric("Total de las mostradas", dinero(sum(map(total_venta, vistas))))
    k3.metric("Último folio", vistas[0].folio if vistas else "—")
    if vistas:
        st.dataframe(a_dataframe(vistas[:15]), hide_index=True, column_config=CONFIG_VENTAS, height=300)


ticker()

st.markdown("**¿Cuántas ventas se necesitan para llegar a una meta?**")
meta = st.number_input("Meta $", 10_000, 10_000_000, 500_000, step=50_000)
alcanzadas = tuple(hasta_alcanzar(simular_ventas(semilla=7), meta))
st.write(f"Del flujo infinito se consumieron **{len(alcanzadas)}** ventas para acumular "
         f"{dinero_md(alcanzadas[-1][1] if alcanzadas else 0)} sin rebasar {dinero_md(meta)}. "
         "`takewhile` detuvo el flujo.")

panel_concepto(
    "generadores infinitos",
    """
`simular_ventas` usa `itertools.count()` cuando no se indica un número de días: el ciclo
nunca termina, pero no importa, porque **cada venta se produce hasta que alguien la pide**.
El generador guarda su propio estado (fecha, folio, números aleatorios) entre cada `yield`.

`folios()` es `map` sobre `count()`: una secuencia infinita de folios de factura.
`hasta_alcanzar` combina `accumulate` y `takewhile` para cortar el flujo en el momento justo.
""",
    (simular_ventas, folios, hasta_alcanzar),
)
