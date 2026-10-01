"""
pipeline.py — Funciones como valores y orden superior (Tema 2.2).

    datos -> función -> función -> función -> resultado

Aquí las funciones se guardan, se pasan como argumento, se devuelven
y se COMPONEN para formar flujos de procesamiento (pipelines).
"""

import time
from functools import reduce, wraps
from itertools import accumulate
from typing import Any, Callable, NamedTuple


# ---------------------------------------------------------------------------
# Composición
# ---------------------------------------------------------------------------
def aplicar(funcion: Callable, valor: Any) -> Any:
    """El ejemplo clásico de la diapositiva 10: recibe una función y un valor."""
    return funcion(valor)


def identidad(x: Any) -> Any:
    return x


def compose(*funciones: Callable) -> Callable:
    """
    compose(f, g, h)(x) == f(g(h(x)))   (de derecha a izquierda, como en matemáticas)
    Se construye con reduce: combina muchas funciones en UNA sola.
    """
    return reduce(lambda f, g: lambda x: f(g(x)), funciones, identidad)


def pipe(valor: Any, *funciones: Callable) -> Any:
    """
    pipe(x, h, g, f) == f(g(h(x)))   (de izquierda a derecha, como se lee un flujo)
    """
    return reduce(lambda acumulado, f: f(acumulado), funciones, valor)


# ---------------------------------------------------------------------------
# Pipeline con pasos con nombre: permite VER cada etapa intermedia
# ---------------------------------------------------------------------------
class Paso(NamedTuple):
    nombre: str
    funcion: Callable


def ejecutar_pipeline(datos: Any, pasos: tuple) -> tuple:
    """
    Ejecuta los pasos en orden y devuelve TODOS los resultados intermedios.
    itertools.accumulate es como reduce, pero entrega cada valor parcial.
        resultado[0] = datos
        resultado[1] = paso1(datos)
        resultado[2] = paso2(paso1(datos)) ...
    """
    return tuple(accumulate(pasos, lambda acc, paso: paso.funcion(acc), initial=datos))


# ---------------------------------------------------------------------------
# Decoradores: funciones que reciben una función y devuelven otra
# ---------------------------------------------------------------------------
def cronometrar(funcion: Callable) -> Callable:
    """
    Envuelve una función para que devuelva (resultado, milisegundos).
    Nota honesta: medir el tiempo es un efecto (depende del reloj), por eso
    este decorador vive en la "orilla" del sistema y no en las reglas de negocio.
    """
    @wraps(funcion)
    def envoltura(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = funcion(*args, **kwargs)
        return resultado, (time.perf_counter() - inicio) * 1000
    return envoltura


def contar_llamadas(funcion: Callable) -> Callable:
    """
    Decorador didáctico: cuenta cuántas veces se llama a una función.
    Se usa en el Laboratorio para comparar Fibonacci con y sin memoización.
    El contador vive en un atributo de la envoltura (estado explícito).
    """
    @wraps(funcion)
    def envoltura(*args):
        envoltura.llamadas += 1
        return funcion(*args)
    envoltura.llamadas = 0
    return envoltura
