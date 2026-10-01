from datetime import date

from core.pipeline import Paso, compose, ejecutar_pipeline, pipe
from core.predicados import (entre_fechas, es_par, no_, o_, por_categoria, por_vendedor,
                             regla, y_)


def test_es_par():
    assert list(filter(es_par, [1, 2, 3, 4, 5, 6])) == [2, 4, 6]


def test_regla_con_operator(ventas):
    assert [v.folio for v in filter(regla("cantidad", ">=", 2), ventas)] == ["F-1", "F-4"]


def test_combinadores(ventas):
    electronica_de_ana = y_(por_categoria("Electrónica"), por_vendedor("Ana Torres"))
    assert [v.folio for v in filter(electronica_de_ana, ventas)] == ["F-1", "F-3"]

    hogar_o_papeleria = o_(por_categoria("Hogar"), por_categoria("Papelería"))
    assert [v.folio for v in filter(hogar_o_papeleria, ventas)] == ["F-2", "F-4"]

    assert [v.folio for v in filter(no_(por_vendedor("Ana Torres")), ventas)] == ["F-2", "F-4"]


def test_entre_fechas(ventas):
    enero = entre_fechas(date(2026, 1, 1), date(2026, 1, 31))
    assert len(tuple(filter(enero, ventas))) == 2


def test_compose_y_pipe():
    doble = lambda x: x * 2
    mas_uno = lambda x: x + 1
    assert compose(doble, mas_uno)(5) == 12     # doble(mas_uno(5))
    assert pipe(5, doble, mas_uno) == 11        # mas_uno(doble(5))


def test_pipeline_de_la_presentacion():
    """Diapositiva 19: suma de cuadrados de pares del 1 al 10 = 220."""
    pasos = (
        Paso("filter pares", lambda xs: tuple(filter(es_par, xs))),
        Paso("map cuadrados", lambda xs: tuple(map(lambda x: x ** 2, xs))),
        Paso("reduce suma", sum),
    )
    etapas = ejecutar_pipeline(range(1, 11), pasos)
    assert etapas[1] == (2, 4, 6, 8, 10)
    assert etapas[2] == (4, 16, 36, 64, 100)
    assert etapas[-1] == 220
