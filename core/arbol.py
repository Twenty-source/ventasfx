"""
arbol.py — Recursividad y árboles (Tema 2.6).

Dos tipos de árbol, ambos hechos SOLO con tuplas (inmutables):

1) Árbol binario de búsqueda (BST), igual que en la diapositiva 24:
       nodo = (valor, izquierda, derecha)      hoja vacía = None
   Se usa para ordenar productos por precio y buscar por rangos.

2) Árbol n-ario de categorías:
       NodoCategoria(nombre, ruta, total, hijos)   hijos = tupla de nodos
   Se usa para el catálogo: Catálogo > Electrónica > Cómputo > Laptops > producto

Todas las funciones son recursivas: cada una tiene un CASO BASE
(árbol vacío / nodo sin hijos) y un CASO RECURSIVO (procesar subárboles).
"""

from functools import reduce
from typing import Any, Callable, Iterator, NamedTuple, Optional

# ===========================================================================
# 1) ÁRBOL BINARIO DE BÚSQUEDA CON TUPLAS
# ===========================================================================
# [PF 2.6 árbol] Cada nodo es (valor, izquierda, derecha); el árbol vacío es None.
# Valores menores van a la izquierda y mayores a la derecha.

# [PF 2.6 árbol] Ejemplo exacto de la presentación (diapositivas 23 y 24).
# [PF inmutable] Todo el árbol son tuplas anidadas: ningún nodo se puede modificar.
ARBOL_EJEMPLO = (
    10,
    (5, (2, None, None), (7, None, None)),
    (15, (12, None, None), (20, None, None)),
)


def identidad(x: Any) -> Any:
    return x


def suma_arbol(arbol: Optional[tuple], valor_de: Callable = identidad) -> float:
    """Diapositiva 24: suma todos los valores del árbol."""
    # [PF recursividad] Caso base: el árbol vacío suma 0.
    if arbol is None:
        return 0
    valor, izquierda, derecha = arbol
    # [PF recursividad] Caso recursivo: valor del nodo + suma de cada subárbol.
    # [PF 2.2 orden superior] valor_de es una función: permite sumar precios de Producto.
    return valor_de(valor) + suma_arbol(izquierda, valor_de) + suma_arbol(derecha, valor_de)


def contar_nodos(arbol: Optional[tuple]) -> int:
    if arbol is None:
        return 0
    _, izquierda, derecha = arbol
    return 1 + contar_nodos(izquierda) + contar_nodos(derecha)


def altura(arbol: Optional[tuple]) -> int:
    """Número de niveles. Árbol vacío = 0, solo raíz = 1."""
    # [PF recursividad] Altura = 1 + la altura del subárbol más alto.
    if arbol is None:
        return 0
    _, izquierda, derecha = arbol
    return 1 + max(altura(izquierda), altura(derecha))


def contar_hojas(arbol: Optional[tuple]) -> int:
    if arbol is None:
        return 0
    _, izquierda, derecha = arbol
    if izquierda is None and derecha is None:
        return 1
    return contar_hojas(izquierda) + contar_hojas(derecha)


def insertar(arbol: Optional[tuple], valor: Any, clave: Callable = identidad) -> tuple:
    """
    Inserta SIN modificar el árbol original: devuelve un árbol NUEVO.
    Solo se recrean los nodos del camino; el resto se comparte
    (esto es seguro precisamente porque las tuplas son inmutables).
    """
    # [PF recursividad] Caso base: lugar vacío -> se crea la hoja.
    if arbol is None:
        return (valor, None, None)
    # [PF inmutable] Se arma una tupla NUEVA para el nodo actual; la rama que no
    # se toca se reutiliza tal cual (se comparte con el árbol original).
    actual, izquierda, derecha = arbol
    if clave(valor) < clave(actual):
        return (actual, insertar(izquierda, valor, clave), derecha)
    return (actual, izquierda, insertar(derecha, valor, clave))


def construir_bst(valores, clave: Callable = identidad) -> Optional[tuple]:
    """Construye el árbol insertando uno a uno con reduce."""
    # [PF 2.5 reduce] El acumulador es el árbol: cada paso devuelve un árbol nuevo.
    # [PF 2.2 lambda] La lambda adapta insertar() a la firma (acumulado, elemento).
    return reduce(lambda arbol, v: insertar(arbol, v, clave), valores, None)


def construir_balanceado(valores_ordenados: tuple) -> Optional[tuple]:
    """
    Construye un árbol balanceado tomando el elemento de en medio como raíz
    y repitiendo recursivamente con cada mitad.
    """
    # [PF recursividad] Divide y vencerás: raíz = el de en medio, cada mitad = subárbol.
    if not valores_ordenados:
        return None
    medio = len(valores_ordenados) // 2
    return (
        valores_ordenados[medio],
        construir_balanceado(valores_ordenados[:medio]),
        construir_balanceado(valores_ordenados[medio + 1:]),
    )


# --- Recorridos: son GENERADORES recursivos (árboles + evaluación perezosa) ---
# [PF 2.7 generador] `yield from` entrega los valores del subárbol uno por uno,
# sin construir una lista con todo el recorrido.
def inorden(arbol: Optional[tuple]) -> Iterator:
    """izquierda -> raíz -> derecha. En un BST entrega los valores ORDENADOS."""
    # [PF recursividad] + [PF 2.7 generador]
    if arbol is not None:
        valor, izquierda, derecha = arbol
        yield from inorden(izquierda)
        yield valor
        yield from inorden(derecha)


def preorden(arbol: Optional[tuple]) -> Iterator:
    """raíz -> izquierda -> derecha."""
    if arbol is not None:
        valor, izquierda, derecha = arbol
        yield valor
        yield from preorden(izquierda)
        yield from preorden(derecha)


def postorden(arbol: Optional[tuple]) -> Iterator:
    """izquierda -> derecha -> raíz."""
    if arbol is not None:
        valor, izquierda, derecha = arbol
        yield from postorden(izquierda)
        yield from postorden(derecha)
        yield valor


def buscar_rango(arbol: Optional[tuple], minimo: float, maximo: float,
                 clave: Callable = identidad) -> Iterator:
    """
    Entrega (en orden) los valores cuya clave está en [minimo, maximo].
    PODA: si la clave del nodo es menor que el mínimo, no tiene caso
    visitar la rama izquierda (todo ahí es todavía más chico).
    """
    if arbol is None:
        return
    valor, izquierda, derecha = arbol
    k = clave(valor)
    # [PF recursividad] Solo se baja a las ramas que pueden tener resultados (poda).
    if k > minimo:
        yield from buscar_rango(izquierda, minimo, maximo, clave)
    if minimo <= k <= maximo:
        yield valor
    if k < maximo:
        yield from buscar_rango(derecha, minimo, maximo, clave)


def a_dot(arbol: Optional[tuple], etiqueta: Callable = str) -> str:
    """Convierte el árbol a lenguaje DOT (Graphviz) para dibujarlo."""
    def nodos(sub: Optional[tuple], ident: str) -> Iterator[str]:
        if sub is None:
            return
        valor, izquierda, derecha = sub
        texto = etiqueta(valor).replace('"', "'")
        yield f'"{ident}" [label="{texto}"];'
        tiene_hijos = izquierda is not None or derecha is not None
        for lado, hijo in (("L", izquierda), ("R", derecha)):
            if hijo is not None:
                yield f'"{ident}" -> "{ident}{lado}";'
                yield from nodos(hijo, ident + lado)
            elif tiene_hijos:
                # Nodo invisible: así se nota si el único hijo es izquierdo o derecho
                yield f'"{ident}{lado}" [style=invis, label="", width=0.3];'
                yield f'"{ident}" -> "{ident}{lado}" [style=invis];'

    cuerpo = "\n  ".join(nodos(arbol, "n"))
    return (
        "digraph G {\n  ordering=out;\n  node [shape=box, style=\"rounded,filled\", "
        "fillcolor=\"#EEF2FF\", color=\"#4F46E5\", fontname=\"Helvetica\"];\n"
        f"  {cuerpo}\n}}"
    )


# ===========================================================================
# 2) ÁRBOL N-ARIO DE CATEGORÍAS
# ===========================================================================
# [PF 2.6 árbol] Nodo n-ario inmutable: los hijos son una tupla de nodos.
class NodoCategoria(NamedTuple):
    nombre: str
    ruta: str
    total: float
    hijos: tuple


def construir_arbol_categorias(rutas: tuple, nombre: str = "Catálogo",
                               ruta: str = "") -> NodoCategoria:
    """
    Construye el árbol a partir de rutas separadas por '/'.
        ("Electrónica/Cómputo/Laptops/Laptop Pro 14", ...)
    Caso base: ya no quedan segmentos -> nodo hoja.
    Caso recursivo: agrupar por el primer segmento y construir cada subárbol.
    """
    # [PF 2.5 comprensión] set comprehension: primeros segmentos sin repetir.
    segmentos = tuple(r.split("/") for r in rutas if r)
    primeros = sorted({s[0] for s in segmentos})
    # [PF recursividad] Cada hijo se construye llamando a esta misma función con el
    # resto de la ruta. Caso base implícito: sin rutas -> `hijos` queda vacío.
    hijos = tuple(
        construir_arbol_categorias(
            tuple("/".join(s[1:]) for s in segmentos if s[0] == primero),
            primero,
            f"{ruta}/{primero}" if ruta else primero,
        )
        for primero in primeros
    )
    return NodoCategoria(nombre, ruta, 0.0, hijos)


def con_totales(nodo: NodoCategoria, montos_hoja: dict) -> NodoCategoria:
    """
    Devuelve un árbol NUEVO donde cada nodo tiene el total de su subárbol.
    Hojas: el monto viene del diccionario. Internos: suma de los hijos.
    """
    # [PF recursividad] Caso base: hoja. Caso recursivo: primero los hijos, luego la suma.
    # [PF inmutable] _replace devuelve nodos nuevos; el árbol original queda con total 0.
    if not nodo.hijos:
        return nodo._replace(total=montos_hoja.get(nodo.ruta, 0.0))
    hijos = tuple(con_totales(h, montos_hoja) for h in nodo.hijos)
    return nodo._replace(total=sum(h.total for h in hijos), hijos=hijos)


def profundidad(nodo: NodoCategoria) -> int:
    return 1 + max((profundidad(h) for h in nodo.hijos), default=0)


def hojas(nodo: NodoCategoria) -> Iterator[NodoCategoria]:
    # [PF recursividad] + [PF 2.7 generador] Entrega solo los nodos sin hijos.
    if not nodo.hijos:
        yield nodo
    for hijo in nodo.hijos:
        yield from hojas(hijo)


def aplanar(nodo: NodoCategoria, nivel: int = 0, padre: str = "") -> Iterator[tuple]:
    """Recorre el árbol y entrega (nivel, nombre, ruta, padre, total) por nodo."""
    # [PF 2.7 generador] Alimenta la gráfica sunburst de la pantalla Catálogo.
    yield (nivel, nodo.nombre, nodo.ruta or nodo.nombre, padre, nodo.total)
    for hijo in nodo.hijos:
        yield from aplanar(hijo, nivel + 1, nodo.ruta or nodo.nombre)


def buscar_nodo(nodo: NodoCategoria, ruta: str) -> Optional[NodoCategoria]:
    """Busca recursivamente el nodo cuya ruta coincide."""
    if (nodo.ruta or nodo.nombre) == ruta:
        return nodo
    # [PF 2.7 perezoso] next() sobre un generador se detiene en el primer resultado:
    # no se siguen explorando los demás hijos.
    return next(
        (r for r in (buscar_nodo(h, ruta) for h in nodo.hijos) if r is not None),
        None,
    )


def a_texto(nodo: NodoCategoria, formato: Callable = lambda n: n.nombre,
            prefijo: str = "", es_ultimo: bool = True, es_raiz: bool = True) -> Iterator[str]:
    """Dibuja el árbol como texto (estilo comando `tree`)."""
    conector = "" if es_raiz else ("└── " if es_ultimo else "├── ")
    yield f"{prefijo}{conector}{formato(nodo)}"
    nuevo_prefijo = prefijo if es_raiz else prefijo + ("    " if es_ultimo else "│   ")
    for i, hijo in enumerate(nodo.hijos):
        yield from a_texto(hijo, formato, nuevo_prefijo, i == len(nodo.hijos) - 1, False)
