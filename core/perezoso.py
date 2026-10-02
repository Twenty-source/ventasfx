"""
perezoso.py — Evaluación perezosa: iteradores y generadores (Tema 2.7).

Evaluación ANSIOSA: calcula todo de inmediato y lo guarda (una lista).
Evaluación PEREZOSA: calcula cada valor solo cuando alguien lo pide.

Python no es perezoso como Haskell, pero tiene:
    - range()          -> intervalo que no guarda sus elementos
    - map / filter     -> devuelven iteradores, no listas
    - generadores      -> funciones con `yield`
    - itertools        -> count, islice, takewhile, accumulate...

Aquí todo el procesamiento de archivos se hace fila por fila: un CSV de
un millón de ventas se puede totalizar usando muy poca memoria.
"""

import csv
import random
import tracemalloc
from collections import deque
from datetime import date, timedelta
from itertools import accumulate, count, islice, takewhile, tee
from typing import Callable, Iterable, Iterator

from core.funciones import total_venta
from core.modelos import CATALOGO, VENDEDORES, Venta

CAMPOS_CSV = Venta._fields


# ---------------------------------------------------------------------------
# Ejemplos de la presentación (diapositivas 26 y 27)
# ---------------------------------------------------------------------------
def numeros() -> Iterator[int]:
    """Secuencia INFINITA: no se guarda, se genera elemento por elemento."""
    # [PF 2.7 generador] Diapositiva 27. `yield` pausa la función y entrega un valor;
    # el siguiente next() la reanuda justo después. El while True nunca "termina".
    n = 1
    while True:
        yield n
        n += 1


def cuadrados_lista(n: int) -> list:
    """Versión ANSIOSA: construye toda la lista en memoria."""
    # Estilo imperativo a propósito (diapositiva 26), para comparar con la versión de abajo.
    resultado = []
    for i in range(n):
        resultado.append(i ** 2)
    return resultado


def cuadrados_generador(n: int) -> Iterator[int]:
    """Versión PEREZOSA: produce cada cuadrado cuando se pide."""
    # [PF 2.7 generador] Mismo resultado que cuadrados_lista, sin guardar la lista.
    for i in range(n):
        yield i ** 2


# ---------------------------------------------------------------------------
# Generadores infinitos del sistema
# ---------------------------------------------------------------------------
def folios(prefijo: str = "F", inicio: int = 1) -> Iterator[str]:
    """Folios de factura infinitos: F-0000001, F-0000002, ..."""
    # [PF 2.7 perezoso] count() es infinito y map() es perezoso: cada folio se
    # calcula solo cuando se pide con next().
    # [PF 2.2 lambda] Da formato al número.
    return map(lambda n: f"{prefijo}-{n:07d}", count(inicio))


def _factor_temporada(categoria: str, mes: int) -> float:
    """Patrones de temporada para que los datos simulados sean realistas."""
    raiz = categoria.split("/")[0]
    temporadas = {
        "Electrónica": {11: 1.8, 12: 2.2, 5: 1.3},
        "Papelería": {1: 1.6, 7: 1.5, 8: 2.4},
        "Deportes": {1: 2.0, 2: 1.4, 6: 1.2},
        "Hogar": {5: 1.7, 12: 1.6, 11: 1.3},
    }
    return temporadas.get(raiz, {}).get(mes, 1.0)


def simular_ventas(semilla: int = 42, fecha_inicio: date = date(2024, 10, 1),
                   dias: int = None, ventas_por_dia: int = 60,
                   catalogo: tuple = CATALOGO) -> Iterator[Venta]:
    """
    Generador de ventas simuladas.
        dias=None  -> flujo INFINITO (itertools.count)
        dias=730   -> exactamente dos años (range)
    El generador conserva su propio estado (random, fecha, folio) entre
    cada `yield`; ese estado no es visible ni modificable desde afuera.
    """
    # [PF efecto] Los números aleatorios usan una semilla fija: la misma semilla
    # produce siempre las mismas ventas, así el resultado es reproducible.
    rng = random.Random(semilla)
    generador_folios = folios()
    pesos_vendedor = tuple(1.0 + 0.25 * i for i in range(len(VENDEDORES)))[::-1]
    pesos_base = tuple(1 / (p.precio ** 0.55) for p in catalogo)

    # [PF 2.3 range] range(dias) = intervalo finito; [PF 2.7 perezoso] count() = infinito.
    for d in (count() if dias is None else range(dias)):
        fecha = fecha_inicio + timedelta(days=d)
        pesos = tuple(
            base * _factor_temporada(p.categoria, fecha.month)
            for base, p in zip(pesos_base, catalogo)
        )
        fin_de_semana = 1.3 if fecha.weekday() >= 5 else 1.0
        crecimiento = 1 + d / 1500          # el negocio crece poco a poco
        n = int(rng.gauss(ventas_por_dia, ventas_por_dia * 0.15) * fin_de_semana * crecimiento)
        # [PF 2.7 generador] Cada venta se produce con `yield` cuando alguien la pide.
        for producto in rng.choices(catalogo, weights=pesos, k=max(n, 1)):
            maximo = 12 if producto.precio < 1000 else (4 if producto.precio < 6000 else 2)
            yield Venta(
                folio=next(generador_folios),
                fecha=fecha,
                sku=producto.sku,
                producto=producto.nombre,
                categoria=producto.categoria,
                precio=producto.precio,
                costo=producto.costo,
                cantidad=rng.randint(1, maximo),
                descuento=rng.choice((0.0, 0.0, 0.0, 0.0, 0.05, 0.10, 0.15)),
                vendedor=rng.choices(VENDEDORES, weights=pesos_vendedor)[0],
            )


# ---------------------------------------------------------------------------
# Lectura y escritura perezosa de CSV
# ---------------------------------------------------------------------------
def venta_a_fila(venta: Venta) -> tuple:
    return tuple(venta._replace(fecha=venta.fecha.isoformat()))


def fila_a_venta(fila: dict) -> Venta:
    """Función pura: convierte un dict de texto (CSV) en una Venta tipada."""
    # [PF pura] Solo transforma: texto de entrada -> Venta de salida.
    return Venta(
        folio=fila["folio"],
        fecha=date.fromisoformat(fila["fecha"]),
        sku=fila["sku"],
        producto=fila["producto"],
        categoria=fila["categoria"],
        precio=float(fila["precio"]),
        costo=float(fila["costo"]),
        cantidad=int(fila["cantidad"]),
        descuento=float(fila["descuento"]),
        vendedor=fila["vendedor"],
    )


def leer_filas(ruta: str) -> Iterator[dict]:
    """Lee el archivo línea por línea; nunca lo carga completo."""
    # [PF 2.7 generador] yield from: cada fila sale del archivo solo cuando se pide.
    # [PF efecto] Leer un archivo es E/S; se aísla en esta función de la orilla.
    with open(ruta, newline="", encoding="utf-8") as archivo:
        yield from csv.DictReader(archivo)


def leer_ventas(ruta: str) -> Iterator[Venta]:
    """map es perezoso: cada fila se convierte solo cuando se necesita."""
    # [PF 2.5 map] + [PF 2.7 perezoso] Devuelve un iterador, no una lista.
    # [PF 2.2 primera clase] fila_a_venta se pasa como valor a map.
    return map(fila_a_venta, leer_filas(ruta))


def escribir_ventas(ruta: str, ventas: Iterable[Venta]) -> int:
    """
    Escribe las ventas conforme el generador las produce (efecto de E/S:
    vive en la orilla del sistema). Devuelve cuántas filas escribió.
    """
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(CAMPOS_CSV)
        # [PF efecto] Escribir es un efecto: vive aquí, no en las reglas de negocio.
        # [PF 2.5 map] Venta -> fila -> escritura, una a la vez conforme llegan.
        return sum(1 for _ in map(escritor.writerow, map(venta_a_fila, ventas)))


# ---------------------------------------------------------------------------
# Utilidades perezosas
# ---------------------------------------------------------------------------
def tomar(n: int, iterable: Iterable) -> tuple:
    """Toma solo los primeros n elementos (funciona con iterables infinitos)."""
    # [PF 2.7 perezoso] islice deja de pedir elementos al llegar a n.
    return tuple(islice(iterable, n))


def en_lotes(iterable: Iterable, tamano: int) -> Iterator[tuple]:
    """Agrupa un flujo en lotes de `tamano` elementos, de forma perezosa."""
    iterador = iter(iterable)
    # [PF 2.7 perezoso] Cada lote se arma cuando se pide; takewhile(bool, ...) se
    # detiene en el primer lote vacío (fin del flujo).
    return takewhile(bool, (tuple(islice(iterador, tamano)) for _ in count()))


def con_acumulado(ventas: Iterable[Venta]) -> Iterator[tuple]:
    """
    (venta, total acumulado hasta esa venta), de forma perezosa.
    tee duplica el flujo: una copia pasa tal cual y la otra se acumula.
    """
    copia_1, copia_2 = tee(ventas)
    # [PF 2.5 reduce] accumulate entrega cada suma parcial (un reduce "paso a paso").
    # [PF 2.5 map] Cada venta se transforma en su total antes de acumular.
    return zip(copia_1, accumulate(map(total_venta, copia_2)))


def hasta_alcanzar(ventas: Iterable[Venta], meta: float) -> Iterator[tuple]:
    """
    Entrega (venta, acumulado) mientras el acumulado no supere la meta.
    takewhile deja de LEER en cuanto se rebasa la meta: aunque el flujo
    sea infinito, el cálculo termina.
    """
    # [PF 2.7 perezoso] Funciona sobre un flujo infinito porque takewhile corta.
    # [PF 2.4 predicado] La lambda decide si se sigue tomando (True) o se para (False).
    return takewhile(lambda par: par[1] <= meta, con_acumulado(ventas))


def promedio_movil(valores: Iterable[float], ventana: int) -> Iterator[float]:
    """Promedio de los últimos `ventana` valores, calculado sobre la marcha."""
    # [PF 2.7 generador] Produce un promedio por cada valor que llega.
    # [PF efecto] El deque es estado local del generador; nadie de afuera lo ve.
    ultimos: deque = deque(maxlen=ventana)
    for valor in valores:
        ultimos.append(valor)
        yield sum(ultimos) / len(ultimos)


def medir_memoria(funcion: Callable, *args) -> tuple:
    """Ejecuta la función y devuelve (resultado, pico de memoria en bytes)."""
    # [PF 2.2 orden superior] Recibe la función a medir como argumento.
    # [PF efecto] Medir memoria es un efecto; solo se usa en la pantalla Carga masiva.
    tracemalloc.start()
    try:
        resultado = funcion(*args)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return resultado, pico
