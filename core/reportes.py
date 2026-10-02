"""
reportes.py — Agregación con reduce y comprensiones (Tema 2.5).

    map transforma · filter selecciona · reduce acumula

Todas las funciones reciben una colección de ventas y devuelven
un valor NUEVO (número, diccionario o tupla). Nunca modifican la entrada.
"""

import operator
from datetime import date
from functools import reduce
from operator import itemgetter
from typing import Callable, Iterable

from core.funciones import comision, importe_bruto, tasa_comision, total_venta, utilidad
from core.modelos import TASA_IVA, Venta


# ---------------------------------------------------------------------------
# Totales
# ---------------------------------------------------------------------------
def total_general(ventas: Iterable[Venta]) -> float:
    """reduce(operator.add, ...) == sumar todo (diapositiva 18)."""
    # [PF 2.5 map] Cada venta se transforma en su total.
    # [PF 2.5 reduce] Los totales se combinan en un solo número.
    # [PF 2.4 operator] operator.add es el operador + como función.
    return round(reduce(operator.add, map(total_venta, ventas), 0.0), 2)


def _acumular_resumen(acc: tuple, venta: Venta) -> tuple:
    """Paso del reduce: recibe el acumulado y una venta, devuelve un acumulado NUEVO."""
    # [PF inmutable] El acumulador es una tupla: no se modifica, se devuelve otra.
    n, total, unidades, ganancia, mayor = acc
    t = total_venta(venta)
    return (n + 1, total + t, unidades + venta.cantidad, ganancia + utilidad(venta), max(mayor, t))


def resumen(ventas: Iterable[Venta]) -> dict:
    """
    Calcula TODOS los indicadores en UNA sola pasada con reduce.
    El acumulador es una tupla (inmutable) que se reemplaza en cada paso.
    """
    # [PF 2.5 reduce] Los 5 indicadores del Dashboard en una sola pasada.
    # (0, 0.0, 0, 0.0, 0.0) es el valor inicial: (ventas, total, unidades, utilidad, mayor).
    n, total, unidades, ganancia, mayor = reduce(_acumular_resumen, ventas, (0, 0.0, 0, 0.0, 0.0))
    return {
        "transacciones": n,
        "total": round(total, 2),
        "unidades": unidades,
        "utilidad": round(ganancia, 2),
        "ticket_promedio": round(total / n, 2) if n else 0.0,
        "venta_mayor": round(mayor, 2),
        "margen": ganancia / (total / (1 + TASA_IVA)) if total else 0.0,
    }


# ---------------------------------------------------------------------------
# Agrupaciones
# ---------------------------------------------------------------------------
def _sumar_en(acc: dict, par: tuple) -> dict:
    """
    Paso del reduce para agrupar. Muta `acc`, PERO `acc` es un diccionario
    recién creado dentro de `agrupar` y nadie más lo ve: la función `agrupar`
    sigue siendo pura hacia afuera ("mutación local controlada").
    Copiar el diccionario en cada paso sería O(n·k) sin beneficio real.
    """
    clave, valor = par
    # [PF efecto] Única mutación del núcleo, confinada a un dict que nadie más ve.
    acc[clave] = acc.get(clave, 0) + valor
    return acc


def agrupar(ventas: Iterable[Venta], clave: Callable, valor: Callable = total_venta) -> dict:
    """
    Agrupa y suma: {clave(venta): suma de valor(venta)}.
    `clave` y `valor` son FUNCIONES recibidas como argumento (orden superior).
    """
    # [PF 2.2 orden superior] Cambiar el reporte = cambiar qué funciones se pasan.
    # [PF 2.5 map] La expresión generadora transforma cada venta en (clave, valor).
    # [PF 2.5 reduce] _sumar_en acumula los pares en un diccionario.
    return reduce(_sumar_en, ((clave(v), valor(v)) for v in ventas), {})


def clave_mes(venta: Venta) -> str:
    return f"{venta.fecha.year}-{venta.fecha.month:02d}"


def clave_categoria(nivel: int) -> Callable:
    """
    Fábrica de funciones: devuelve una función clave para el nivel pedido.
        nivel 1 -> "Electrónica"   nivel 2 -> "Electrónica/Cómputo" ...
    """
    # [PF 2.2 orden superior] Devuelve una función distinta según el nivel.
    # [PF 2.2 lambda] La lambda "recuerda" el valor de `nivel` (closure).
    return lambda venta: "/".join(venta.categoria.split("/")[:nivel])


def top_n(diccionario: dict, n: int = 10, mayor_primero: bool = True) -> tuple:
    """Ordena los pares (clave, valor) por valor con itemgetter(1)."""
    # [PF 2.4 operator] itemgetter(1) equivale a lambda par: par[1].
    # [PF inmutable] sorted() devuelve una lista nueva; el diccionario no cambia.
    return tuple(sorted(diccionario.items(), key=itemgetter(1), reverse=mayor_primero)[:n])


# ---------------------------------------------------------------------------
# Series de tiempo con range()
# ---------------------------------------------------------------------------
def meses_entre(inicio: date, fin: date) -> tuple:
    """
    Todos los meses entre dos fechas como "AAAA-MM", generados con range().
    El mes se numera de forma absoluta: año*12 + (mes-1).
    """
    a = inicio.year * 12 + inicio.month - 1
    b = fin.year * 12 + fin.month - 1
    # [PF 2.3 range] range(a, b + 1) genera todos los meses del intervalo.
    # [PF 2.5 comprensión] Cada número de mes se transforma en texto "AAAA-MM".
    return tuple(f"{m // 12}-{m % 12 + 1:02d}" for m in range(a, b + 1))


def serie_mensual(ventas: Iterable[Venta], inicio: date, fin: date,
                  valor: Callable = total_venta) -> tuple:
    """Serie (mes, valor) que incluye con 0 los meses sin ventas."""
    por_mes = agrupar(ventas, clave_mes, valor)
    # [PF 2.5 comprensión] Recorre TODOS los meses (de range) y pone 0 donde no hubo ventas.
    return tuple((mes, round(por_mes.get(mes, 0.0), 2)) for mes in meses_entre(inicio, fin))


# ---------------------------------------------------------------------------
# Comisiones y rankings
# ---------------------------------------------------------------------------
def comisiones_por_vendedor(ventas: Iterable[Venta]) -> tuple:
    """
    (vendedor, vendido, tasa, comisión) para cada vendedor.
    La comisión se calcula sobre el importe sin IVA.
    """
    # [PF 2.2 primera clase] importe_bruto se pasa como valor, sin llamarla.
    vendido = agrupar(ventas, operator.attrgetter("vendedor"), importe_bruto)
    # [PF 2.5 comprensión] Una fila por vendedor, ordenadas de mayor a menor.
    return tuple(
        (vendedor, round(monto, 2), tasa_comision(monto), comision(monto))
        for vendedor, monto in sorted(vendido.items(), key=itemgetter(1), reverse=True)
    )


def ranking_productos(ventas: Iterable[Venta], n: int = 10) -> tuple:
    """Top n productos por total vendido (map + agrupar + top_n)."""
    return top_n(agrupar(ventas, operator.attrgetter("producto")), n)


# ---------------------------------------------------------------------------
# Paginación con range() y rebanadas
# ---------------------------------------------------------------------------
def total_paginas(cantidad: int, tamano: int) -> int:
    return max(1, -(-cantidad // tamano))   # división techo sin math.ceil


def paginar(secuencia: tuple, tamano: int, pagina: int) -> tuple:
    """Devuelve los elementos de la página (empezando en 1)."""
    inicio = (pagina - 1) * tamano
    return secuencia[inicio:inicio + tamano]


def indices_pagina(cantidad: int, tamano: int, pagina: int) -> range:
    """range de los índices que muestra la página: no crea ninguna lista."""
    inicio = (pagina - 1) * tamano
    # [PF 2.3 range] Se devuelve el intervalo, no los elementos: ocupa lo mismo
    # sin importar el tamaño de la página.
    return range(inicio, min(inicio + tamano, cantidad))
