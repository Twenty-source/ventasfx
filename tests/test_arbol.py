from core.arbol import (ARBOL_EJEMPLO, altura, buscar_nodo, buscar_rango,
                        construir_arbol_categorias, construir_balanceado, construir_bst,
                        con_totales, contar_hojas, contar_nodos, inorden, insertar, postorden,
                        preorden, profundidad, suma_arbol)


def test_suma_arbol_de_la_presentacion():
    assert suma_arbol(ARBOL_EJEMPLO) == 71


def test_metricas():
    assert contar_nodos(ARBOL_EJEMPLO) == 7
    assert altura(ARBOL_EJEMPLO) == 3
    assert contar_hojas(ARBOL_EJEMPLO) == 4
    assert altura(None) == 0


def test_recorridos():
    assert list(inorden(ARBOL_EJEMPLO)) == [2, 5, 7, 10, 12, 15, 20]
    assert list(preorden(ARBOL_EJEMPLO)) == [10, 5, 2, 7, 15, 12, 20]
    assert list(postorden(ARBOL_EJEMPLO)) == [2, 7, 5, 12, 20, 15, 10]


def test_insertar_no_modifica_el_original():
    nuevo = insertar(ARBOL_EJEMPLO, 6)
    assert 6 in list(inorden(nuevo))
    assert 6 not in list(inorden(ARBOL_EJEMPLO))
    assert nuevo[2] is ARBOL_EJEMPLO[2]   # la rama derecha se comparte


def test_construir_y_rango():
    arbol = construir_bst([50, 30, 70, 20, 40, 60, 80])
    assert list(inorden(arbol)) == [20, 30, 40, 50, 60, 70, 80]
    assert list(buscar_rango(arbol, 35, 65)) == [40, 50, 60]


def test_balanceado_es_mas_bajo():
    valores = tuple(range(1, 32))
    assert altura(construir_bst(valores)) == 31          # degenerado
    assert altura(construir_balanceado(valores)) == 5    # log2(32)


def test_arbol_categorias():
    rutas = ("A/x/1", "A/x/2", "A/y/3", "B/z/4")
    arbol = construir_arbol_categorias(rutas)
    assert [h.nombre for h in arbol.hijos] == ["A", "B"]
    assert profundidad(arbol) == 4
    con_t = con_totales(arbol, {"A/x/1": 10, "A/x/2": 5, "A/y/3": 1, "B/z/4": 100})
    assert con_t.total == 116
    assert buscar_nodo(con_t, "A/x").total == 15
    assert arbol.total == 0.0   # el árbol original no cambió
