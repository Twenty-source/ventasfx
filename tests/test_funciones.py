"""
Las funciones puras se prueban sin preparar ningún estado:
basta con dar una entrada y comparar la salida.
"""

import pytest

from core.funciones import (actualizar_stock, ajustar_precio, comision, con_descuento,
                            importe_bruto, subtotal, tasa_comision, total_venta, utilidad,
                            validar_venta)
from core.modelos import CATALOGO


def test_importe_es_precio_por_cantidad(venta):
    assert importe_bruto(venta) == 1200.0


def test_subtotal_aplica_descuento(venta):
    assert subtotal(venta) == pytest.approx(1080.0)


def test_total_incluye_iva(venta):
    assert total_venta(venta) == pytest.approx(1252.80)


def test_utilidad(venta):
    assert utilidad(venta) == pytest.approx(480.0)


def test_pureza_misma_entrada_misma_salida(venta):
    assert {total_venta(venta) for _ in range(100)} == {total_venta(venta)}


@pytest.mark.parametrize("monto, tasa", [
    (0, 0.02), (999_999, 0.02), (1_000_000, 0.03), (2_000_000, 0.04), (9_000_000, 0.05),
])
def test_tasa_comision_escalonada(monto, tasa):
    assert tasa_comision(monto) == tasa


def test_comision():
    assert comision(2_000_000) == 80_000


def test_con_descuento_no_modifica_original(venta):
    nueva = con_descuento(venta, 0.25)
    assert nueva.descuento == 0.25
    assert venta.descuento == 0.10          # la original sigue igual
    assert nueva is not venta


def test_ajustar_precio_devuelve_otro_producto():
    original = CATALOGO[0]
    nuevo = ajustar_precio(original, 0.10)
    assert nuevo.precio == round(original.precio * 1.10, 2)
    assert original.precio == CATALOGO[0].precio


def test_producto_es_inmutable():
    with pytest.raises(Exception):
        CATALOGO[0].precio = 1  # frozen dataclass


def test_actualizar_stock_no_muta(venta):
    inventario = {"A": 10}
    nuevo = actualizar_stock(inventario, "A", -3)
    assert nuevo == {"A": 7}
    assert inventario == {"A": 10}


def test_validar_venta(venta):
    assert validar_venta(venta, {venta.sku: 100}) == ()
    errores = validar_venta(venta._replace(cantidad=0, descuento=0.9), {venta.sku: 100})
    assert len(errores) == 2
    assert "stock" in validar_venta(venta, {venta.sku: 1})[0]
