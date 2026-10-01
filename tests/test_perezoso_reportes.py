from datetime import date

from core import didactico as d
from core.funciones import total_venta
from core.perezoso import (cuadrados_generador, cuadrados_lista, en_lotes, escribir_ventas,
                           folios, hasta_alcanzar, leer_ventas, numeros, simular_ventas, tomar)
from core.reportes import (agrupar, clave_categoria, clave_mes, comisiones_por_vendedor,
                           meses_entre, paginar, resumen, serie_mensual, total_general,
                           total_paginas)


# ----------------------------- perezoso ------------------------------------
def test_secuencia_infinita():
    assert tomar(3, numeros()) == (1, 2, 3)
    assert tomar(2, folios()) == ("F-0000001", "F-0000002")


def test_generador_equivale_a_lista():
    assert list(cuadrados_generador(10)) == cuadrados_lista(10)


def test_en_lotes():
    assert list(en_lotes(range(7), 3)) == [(0, 1, 2), (3, 4, 5), (6,)]


def test_simulacion_reproducible():
    a = tomar(50, simular_ventas(semilla=7))
    b = tomar(50, simular_ventas(semilla=7))
    assert a == b


def test_hasta_alcanzar_termina_con_flujo_infinito():
    pares = tuple(hasta_alcanzar(simular_ventas(), 50_000))
    assert pares and pares[-1][1] <= 50_000


def test_csv_ida_y_vuelta(tmp_path):
    originales = tomar(100, simular_ventas(dias=None))
    ruta = tmp_path / "v.csv"
    assert escribir_ventas(str(ruta), iter(originales)) == 100
    assert tuple(leer_ventas(str(ruta))) == originales


# ----------------------------- reportes ------------------------------------
def test_total_general_y_resumen(ventas):
    esperado = round(sum(map(total_venta, ventas)), 2)
    assert total_general(ventas) == esperado
    r = resumen(ventas)
    assert r["transacciones"] == 4
    assert r["total"] == esperado
    assert r["unidades"] == 14


def test_agrupar(ventas):
    por_raiz = agrupar(ventas, clave_categoria(1), lambda v: 1)
    assert por_raiz == {"Electrónica": 2, "Hogar": 1, "Papelería": 1}
    assert set(agrupar(ventas, clave_mes)) == {"2026-01", "2026-03"}


def test_meses_entre_con_range():
    assert meses_entre(date(2025, 11, 1), date(2026, 2, 1)) == \
        ("2025-11", "2025-12", "2026-01", "2026-02")


def test_serie_rellena_meses_vacios(ventas):
    serie = dict(serie_mensual(ventas, date(2026, 1, 1), date(2026, 3, 1)))
    assert serie["2026-02"] == 0.0


def test_comisiones(ventas):
    filas = comisiones_por_vendedor(ventas)
    assert filas[0][0] == "Ana Torres"
    assert filas[0][1] == 20200.0


def test_paginacion():
    datos = tuple(range(25))
    assert total_paginas(25, 10) == 3
    assert paginar(datos, 10, 3) == (20, 21, 22, 23, 24)


# ----------------------------- didáctico -----------------------------------
def test_imperativo_y_funcional_dan_lo_mismo(ventas):
    for nombre, problema in d.PROBLEMAS.items():
        entrada = range(1, 11) if problema["entrada"] == "numeros" else ventas
        assert problema["imperativo"](entrada) == problema["funcional"](entrada), nombre


def test_suma_cuadrados_pares_es_220():
    assert d.suma_cuadrados_pares_funcional(range(1, 11)) == 220


def test_impura_vs_pura():
    d.reiniciar_total()
    assert (d.agregar(5), d.agregar(5)) == (5, 10)     # misma entrada, distinta salida
    assert (d.cuadrado(5), d.cuadrado(5)) == (25, 25)


def test_recursividad():
    assert d.factorial(5) == 120
    traza = d.factorial_traza(3)
    assert traza[0] == "factorial(3)" and traza[-1] == "3 * 2 * 1 * 1"


def test_memoizacion_reduce_llamadas():
    sin_memo, contador_sin = d.nuevo_fibonacci_contado(False)
    con_memo, contador_con = d.nuevo_fibonacci_contado(True)
    assert sin_memo(20) == con_memo(20) == 6765
    assert contador_con.llamadas < contador_sin.llamadas


def test_flujo_constructor():
    r = d.ejecutar_flujo(1, 11, 1, "es par", "x² (cuadrado)", "suma (operator.add)")
    assert r["resultado"] == 220
    funcional, comprension = d.codigo_flujo(1, 11, 1, "es par", "x² (cuadrado)",
                                            "suma (operator.add)")
    assert "reduce(operator.add" in funcional and comprension.startswith("resultado = sum(")
