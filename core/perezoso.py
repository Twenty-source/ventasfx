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
    n = 1
    while True:
        yield n
        n += 1


def cuadrados_lista(n: int) -> list:
    """Versión ANSIOSA: construye toda la lista en memoria."""
    resultado = []
    for i in range(n):
        resultado.append(i ** 2)
    return resultado


def cuadrados_generador(n: int) -> Iterator[int]:
    """Versión PEREZOSA: produce cada cuadrado cuando se pide."""
    for i in range(n):
        yield i ** 2


# ---------------------------------------------------------------------------
# Generadores infinitos del sistema
# ---------------------------------------------------------------------------
def folios(prefijo: str = "F", inicio: int = 1) -> Iterator[str]:
    """Folios de factura infinitos: F-0000001, F-0000002, ..."""
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
    rng = random.Random(semilla)
    generador_folios = folios()
    pesos_vendedor = tuple(1.0 + 0.25 * i for i in range(len(VENDEDORES)))[::-1]
    pesos_base = tuple(1 / (p.precio ** 0.55) for p in catalogo)

    for d in (count() if dias is None else range(dias)):
        fecha = fecha_inicio + timedelta(days=d)
        pesos = tuple(
            base * _factor_temporada(p.categoria, fecha.month)
            for base, p in zip(pesos_base, catalogo)
        )
        fin_de_semana = 1.3 if fecha.weekday() >= 5 else 1.0
        crecimiento = 1 + d / 1500          # el negocio crece poco a poco
        n = int(rng.gauss(ventas_por_dia, ventas_por_dia * 0.15) * fin_de_semana * crecimiento)
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
    with open(ruta, newline="", encoding="utf-8") as archivo:
        yield from csv.DictReader(archivo)


def leer_ventas(ruta: str) -> Iterator[Venta]:
    """map es perezoso: cada fila se convierte solo cuando se necesita."""
    return map(fila_a_venta, leer_filas(ruta))


def escribir_ventas(ruta: str, ventas: Iterable[Venta]) -> int:
    """
    Escribe las ventas conforme el generador las produce (efecto de E/S:
    vive en la orilla del sistema). Devuelve cuántas filas escribió.
    """
    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)
        escritor.writerow(CAMPOS_CSV)
        return sum(1 for _ in map(escritor.writerow, map(venta_a_fila, ventas)))


# ---------------------------------------------------------------------------
# Utilidades perezosas
# ---------------------------------------------------------------------------
def tomar(n: int, iterable: Iterable) -> tuple:
    """Toma solo los primeros n elementos (funciona con iterables infinitos)."""
    return tuple(islice(iterable, n))


def en_lotes(iterable: Iterable, tamano: int) -> Iterator[tuple]:
    """Agrupa un flujo en lotes de `tamano` elementos, de forma perezosa."""
    iterador = iter(iterable)
    return takewhile(bool, (tuple(islice(iterador, tamano)) for _ in count()))


def con_acumulado(ventas: Iterable[Venta]) -> Iterator[tuple]:
    """
    (venta, total acumulado hasta esa venta), de forma perezosa.
    tee duplica el flujo: una copia pasa tal cual y la otra se acumula.
    """
    copia_1, copia_2 = tee(ventas)
    return zip(copia_1, accumulate(map(total_venta, copia_2)))


def hasta_alcanzar(ventas: Iterable[Venta], meta: float) -> Iterator[tuple]:
    """
    Entrega (venta, acumulado) mientras el acumulado no supere la meta.
    takewhile deja de LEER en cuanto se rebasa la meta: aunque el flujo
    sea infinito, el cálculo termina.
    """
    return takewhile(lambda par: par[1] <= meta, con_acumulado(ventas))


def promedio_movil(valores: Iterable[float], ventana: int) -> Iterator[float]:
    """Promedio de los últimos `ventana` valores, calculado sobre la marcha."""
    ultimos: deque = deque(maxlen=ventana)
    for valor in valores:
        ultimos.append(valor)
        yield sum(ultimos) / len(ultimos)


def medir_memoria(funcion: Callable, *args) -> tuple:
    """Ejecuta la función y devuelve (resultado, pico de memoria en bytes)."""
    tracemalloc.start()
    try:
        resultado = funcion(*args)
        _, pico = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    return resultado, pico
