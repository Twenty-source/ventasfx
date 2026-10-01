"""
predicados.py — Operadores y predicados (Tema 2.4).

Un PREDICADO es una función que devuelve True o False.
Aquí los predicados se FABRICAN con funciones de orden superior
(funciones que devuelven funciones) y se COMBINAN entre sí con y_, o_, no_.

El módulo `operator` permite tratar los operadores (> < == ...) como
funciones normales que se pueden guardar en un diccionario.
"""

import operator
from datetime import date
from operator import attrgetter
from typing import Callable

from core.funciones import total_venta

Predicado = Callable[[object], bool]

# Los operadores relacionales como VALORES dentro de un diccionario.
OPERADORES: dict = {
    "==": operator.eq,
    "!=": operator.ne,
    ">": operator.gt,
    ">=": operator.ge,
    "<": operator.lt,
    "<=": operator.le,
}

# Campos numéricos sobre los que el usuario puede crear reglas.
# Cada valor es una FUNCIÓN que extrae el dato de una venta.
CAMPOS: dict = {
    "cantidad": attrgetter("cantidad"),
    "precio": attrgetter("precio"),
    "descuento": attrgetter("descuento"),
    "total": total_venta,
}


# ---------------------------------------------------------------------------
# Predicados simples
# ---------------------------------------------------------------------------
def es_par(x: int) -> bool:
    return x % 2 == 0


def siempre(_: object) -> bool:
    """Predicado neutro: acepta todo (útil como valor inicial)."""
    return True


# ---------------------------------------------------------------------------
# Fábricas de predicados (orden superior: devuelven una función)
# ---------------------------------------------------------------------------
def regla(campo: str, simbolo: str, valor: float) -> Predicado:
    """
    Crea un predicado del tipo  campo <operador> valor.
    Ejemplo: regla("cantidad", ">=", 3) -> lambda v: v.cantidad >= 3
    """
    extraer = CAMPOS[campo]
    comparar = OPERADORES[simbolo]
    return lambda venta: comparar(extraer(venta), valor)


def por_categoria(*prefijos: str) -> Predicado:
    """Acepta ventas cuya categoría empiece con alguno de los prefijos."""
    return lambda venta: venta.categoria.startswith(prefijos)


def por_vendedor(*nombres: str) -> Predicado:
    conjunto = frozenset(nombres)
    return lambda venta: venta.vendedor in conjunto


def entre_fechas(inicio: date, fin: date) -> Predicado:
    return lambda venta: inicio <= venta.fecha <= fin


def monto_minimo(minimo: float) -> Predicado:
    return lambda venta: total_venta(venta) >= minimo


# ---------------------------------------------------------------------------
# Combinadores lógicos (and / or / not como funciones)
# ---------------------------------------------------------------------------
def y_(*predicados: Predicado) -> Predicado:
    """Todos los predicados deben cumplirse (AND)."""
    return lambda x: all(p(x) for p in predicados)


def o_(*predicados: Predicado) -> Predicado:
    """Basta con que uno se cumpla (OR)."""
    return lambda x: any(p(x) for p in predicados)


def no_(predicado: Predicado) -> Predicado:
    """Niega el predicado (NOT)."""
    return lambda x: not predicado(x)
