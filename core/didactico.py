"""
didactico.py — Ejemplos para el Laboratorio.

Contiene:
    * Pares de soluciones IMPERATIVA vs FUNCIONAL para el mismo problema.
    * El ejemplo de función impura vs pura (diapositiva 6).
    * Recursividad: factorial con traza y Fibonacci con/sin memoización.
    * Un catálogo de funciones (transformaciones, predicados, reductores)
      guardadas en diccionarios: funciones como objetos de primera clase.
"""

import operator
from functools import lru_cache, reduce

from core.funciones import total_venta
from core.pipeline import contar_llamadas

# ===========================================================================
# 1) IMPERATIVO vs FUNCIONAL
# ===========================================================================

# --- Problema 1: cuadrados (diapositiva 4) ---------------------------------
def cuadrados_imperativo(numeros):
    # Imperativo: lista vacía + ciclo + append (la lista cambia en cada vuelta).
    cuadrados = []
    for numero in numeros:
        cuadrados.append(numero ** 2)
    return cuadrados


def cuadrados_funcional(numeros):
    # [PF 2.5 map] Aplicar una función a cada elemento. [PF 2.2 lambda] La función es anónima.
    return list(map(lambda x: x ** 2, numeros))


# --- Problema 2: suma de cuadrados de pares (diapositiva 19) ----------------
def suma_cuadrados_pares_imperativo(numeros):
    # Imperativo: un acumulador que se modifica dentro del ciclo.
    total = 0
    for n in numeros:
        if n % 2 == 0:
            total += n ** 2
    return total


def suma_cuadrados_pares_funcional(numeros):
    # [PF 2.5 filter] selecciona -> [PF 2.5 map] transforma -> [PF 2.5 reduce] acumula.
    pares = filter(lambda x: x % 2 == 0, numeros)
    cuadrados = map(lambda x: x ** 2, pares)
    return reduce(lambda a, b: a + b, cuadrados, 0)


# --- Problema 3: ventas > 1000 con aumento del 10 % (diapositiva 21) --------
def aumento_ventas_grandes_imperativo(ventas):
    # Imperativo: ciclo + if + append.
    resultado = []
    for v in ventas:
        t = total_venta(v)
        if t > 1000:
            resultado.append(round(t * 1.10, 2))
    return resultado


def aumento_ventas_grandes_funcional(ventas):
    # [PF 2.5 map] [PF 2.5 filter] [PF 2.5 comprensión] El flujo de la diapositiva 21.
    totales = map(total_venta, ventas)
    mayores = filter(lambda t: t > 1000, totales)
    return [round(t * 1.10, 2) for t in mayores]


# --- Problema 4: total vendido por vendedor --------------------------------
def total_por_vendedor_imperativo(ventas):
    # Imperativo: un diccionario que se va modificando.
    totales = {}
    for v in ventas:
        if v.vendedor not in totales:
            totales[v.vendedor] = 0
        totales[v.vendedor] += total_venta(v)
    for vendedor in totales:
        totales[vendedor] = round(totales[vendedor], 2)
    return totales


def total_por_vendedor_funcional(ventas):
    # [PF 2.5 comprensión] set comprehension + dict comprehension; nada se modifica.
    vendedores = {v.vendedor for v in ventas}
    return {
        nombre: round(sum(total_venta(v) for v in ventas if v.vendedor == nombre), 2)
        for nombre in vendedores
    }


# --- Problema 5: la venta más grande ---------------------------------------
def venta_mayor_imperativo(ventas):
    # Imperativo: una variable que se reasigna cada vez que aparece una venta mayor.
    mayor = None
    for v in ventas:
        if mayor is None or total_venta(v) > total_venta(mayor):
            mayor = v
    return mayor.folio if mayor else None


def venta_mayor_funcional(ventas):
    if not ventas:
        return None
    # [PF 2.5 reduce] Reduce para máximos: de cada par se queda con la venta mayor.
    return reduce(lambda a, b: a if total_venta(a) >= total_venta(b) else b, ventas).folio


# [PF 2.2 primera clase] Diccionario de problemas: cada valor guarda FUNCIONES,
# que la pantalla Laboratorio busca por nombre y ejecuta.
PROBLEMAS = {
    "Cuadrados de una lista": {
        "entrada": "numeros",
        "descripcion": "Elevar al cuadrado cada número (diapositiva 4).",
        "imperativo": cuadrados_imperativo,
        "funcional": cuadrados_funcional,
    },
    "Suma de cuadrados de pares": {
        "entrada": "numeros",
        "descripcion": "Filtrar pares → elevar al cuadrado → sumar (diapositiva 19).",
        "imperativo": suma_cuadrados_pares_imperativo,
        "funcional": suma_cuadrados_pares_funcional,
    },
    "Ventas > $1,000 con aumento de 10 %": {
        "entrada": "ventas",
        "descripcion": "El ejemplo de puente a Ciencia de Datos (diapositiva 21), con ventas reales.",
        "imperativo": aumento_ventas_grandes_imperativo,
        "funcional": aumento_ventas_grandes_funcional,
    },
    "Total vendido por vendedor": {
        "entrada": "ventas",
        "descripcion": "Agrupar ventas por vendedor y sumar sus totales.",
        "imperativo": total_por_vendedor_imperativo,
        "funcional": total_por_vendedor_funcional,
    },
    "Venta más grande": {
        "entrada": "ventas",
        "descripcion": "Encontrar el folio de la venta de mayor total (reduce para máximos).",
        "imperativo": venta_mayor_imperativo,
        "funcional": venta_mayor_funcional,
    },
}


# ===========================================================================
# 2) FUNCIÓN IMPURA vs PURA (diapositiva 6)
# ===========================================================================
# Estado global a propósito: es el contraejemplo de la diapositiva 6.
total = 0


def agregar(x):
    """IMPURA: depende y modifica una variable global."""
    # [PF efecto] Contraejemplo: agregar(5) devuelve 5 y luego 10 con la misma entrada.
    global total
    total += x
    return total


def reiniciar_total():
    global total
    total = 0


def cuadrado(x):
    """PURA: misma entrada, misma salida, sin efectos."""
    # [PF pura] cuadrado(5) siempre es 25.
    return x * x


# ===========================================================================
# 3) RECURSIVIDAD
# ===========================================================================
def factorial(n: int) -> int:
    """Diapositiva 22. ¿Dónde está el for? No hace falta."""
    # [PF recursividad] Caso base.
    if n == 0:
        return 1
    # [PF recursividad] Caso recursivo: el problema se reduce a uno más pequeño.
    return n * factorial(n - 1)


def factorial_traza(n: int, prefijo: str = "") -> tuple:
    """
    Devuelve cada paso de la expansión, como en la diapositiva 22:
        factorial(3)
        3 * factorial(2)
        3 * 2 * factorial(1) ...
    También es recursiva.
    """
    # [PF recursividad] [PF inmutable] Cada llamada devuelve una tupla nueva que se concatena.
    if n == 0:
        return (f"{prefijo}factorial(0)", f"{prefijo}1")
    return (f"{prefijo}factorial({n})",) + factorial_traza(n - 1, f"{prefijo}{n} * ")


def fibonacci_ingenuo(n: int) -> int:
    """Recursión directa: recalcula los mismos valores muchísimas veces."""
    return n if n < 2 else fibonacci_ingenuo(n - 1) + fibonacci_ingenuo(n - 2)


def nuevo_fibonacci_contado(memoizar: bool):
    """
    Crea una función Fibonacci NUEVA que cuenta sus llamadas.
    Se puede memoizar con lru_cache SOLO porque es pura: si la salida
    dependiera de algo externo, guardar resultados sería incorrecto.
    """
    # [PF pura] Memoizar (lru_cache) = recordar resultados; solo es válido en funciones puras.
    # [PF 2.2 orden superior] lru_cache y contar_llamadas reciben una función y devuelven otra.
    # [PF recursividad] fib se llama a sí misma a través de fib_interna.
    @contar_llamadas
    def fib(n: int) -> int:
        return n if n < 2 else fib_interna(n - 1) + fib_interna(n - 2)

    fib_interna = lru_cache(maxsize=None)(fib) if memoizar else fib
    return fib_interna, fib


# ===========================================================================
# 4) FUNCIONES COMO VALORES: catálogos para el constructor de pipelines
#    Cada entrada: (función, código lambda, expresión para comprensión)
# ===========================================================================
def es_primo(x: int) -> bool:
    # [PF 2.4 predicado] [PF 2.3 range] all() sobre los posibles divisores.
    return x > 1 and all(x % d for d in range(2, int(x ** 0.5) + 1))


# [PF 2.2 primera clase] Funciones guardadas en diccionarios, elegidas por nombre en la app.
# [PF 2.2 lambda] La mayoría son lambdas de una sola expresión.
TRANSFORMACIONES = {
    "x² (cuadrado)": (lambda x: x ** 2, "lambda x: x ** 2", "x ** 2"),
    "x³ (cubo)": (lambda x: x ** 3, "lambda x: x ** 3", "x ** 3"),
    "x × 2 (doble)": (lambda x: x * 2, "lambda x: x * 2", "x * 2"),
    "x + 10": (lambda x: x + 10, "lambda x: x + 10", "x + 10"),
    "x × 1.16 (con IVA)": (lambda x: round(x * 1.16, 2), "lambda x: round(x * 1.16, 2)", "round(x * 1.16, 2)"),
    "sin cambio": (lambda x: x, "lambda x: x", "x"),
}

# [PF 2.4 predicado] Todas devuelven True o False; se usan con filter().
PREDICADOS = {
    "es par": (lambda x: x % 2 == 0, "lambda x: x % 2 == 0", "x % 2 == 0"),
    "es impar": (lambda x: x % 2 != 0, "lambda x: x % 2 != 0", "x % 2 != 0"),
    "múltiplo de 3": (lambda x: x % 3 == 0, "lambda x: x % 3 == 0", "x % 3 == 0"),
    "mayor que 10": (lambda x: operator.gt(x, 10), "lambda x: operator.gt(x, 10)", "x > 10"),
    "es primo": (es_primo, "es_primo", "es_primo(x)"),
    "todos (sin filtro)": (lambda x: True, "lambda x: True", "True"),
}

# [PF 2.5 reduce] Funciones de dos argumentos que combinan valores.
# [PF 2.4 operator] operator.add y operator.mul son + y * como funciones.
REDUCTORES = {
    "suma (operator.add)": (operator.add, "operator.add", "sum"),
    "producto (operator.mul)": (operator.mul, "operator.mul", "math.prod"),
    "máximo": (max, "max", "max"),
    "mínimo": (min, "min", "min"),
    "contar": (lambda acc, _: acc + 1, "lambda acc, _: acc + 1", "len"),
}


def ejecutar_flujo(inicio: int, fin: int, paso: int, predicado: str,
                   transformacion: str, reductor: str) -> dict:
    """
    range -> filter -> map -> reduce, usando funciones elegidas por NOMBRE
    desde los diccionarios (las funciones son valores que se buscan y pasan).
    """
    # [PF 2.3 range] El intervalo de entrada no se guarda como lista.
    numeros = range(inicio, fin, paso)
    # [PF 2.2 primera clase] Se obtienen FUNCIONES de los diccionarios por su nombre.
    pred = PREDICADOS[predicado][0]
    trans = TRANSFORMACIONES[transformacion][0]
    red = REDUCTORES[reductor][0]

    # [PF 2.5 filter] -> [PF 2.5 map] -> [PF 2.5 reduce]
    filtrados = tuple(filter(pred, numeros))
    transformados = tuple(map(trans, filtrados))
    inicial = 0 if reductor.startswith("contar") else None
    if not transformados:
        final = 0
    elif inicial is None:
        final = reduce(red, transformados)
    else:
        final = reduce(red, transformados, inicial)
    return {
        "intervalo": tuple(numeros),
        "filtrados": filtrados,
        "transformados": transformados,
        "resultado": final,
    }


def codigo_flujo(inicio: int, fin: int, paso: int, predicado: str,
                 transformacion: str, reductor: str) -> tuple:
    """Genera el código Python equivalente en dos estilos."""
    _, pl, pc = PREDICADOS[predicado]
    _, tl, tc = TRANSFORMACIONES[transformacion]
    _, rl, rc = REDUCTORES[reductor]
    r = f"range({inicio}, {fin}, {paso})"
    estilo_funcional = (
        f"numeros = {r}\n"
        f"filtrados = filter({pl}, numeros)\n"
        f"transformados = map({tl}, filtrados)\n"
        + (f"resultado = reduce({rl}, transformados, 0)" if reductor.startswith("contar")
           else f"resultado = reduce({rl}, transformados)")
    )
    estilo_comprension = f"resultado = {rc}([{tc} for x in {r} if {pc}])"
    return estilo_funcional, estilo_comprension

