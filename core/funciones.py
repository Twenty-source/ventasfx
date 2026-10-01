"""
funciones.py — Reglas de negocio como FUNCIONES PURAS.

Una función pura:
    1. Con la misma entrada siempre devuelve la misma salida.
    2. No modifica nada fuera de ella (no hay efectos secundarios).

Por eso todas estas funciones se pueden probar con pytest de forma
trivial (ver tests/test_funciones.py) y se pueden componer entre sí.
"""

from dataclasses import replace
from datetime import date

from core.modelos import TABLA_COMISIONES, TASA_IVA, Producto, Venta


# ---------------------------------------------------------------------------
# Cálculos sobre una venta
# ---------------------------------------------------------------------------
def redondear(monto: float) -> float:
    """Redondea a 2 decimales (centavos)."""
    return round(monto, 2)


def importe_bruto(venta: Venta) -> float:
    """precio × cantidad (el 'importe' del proyecto integrador)."""
    return venta.precio * venta.cantidad


def monto_descuento(venta: Venta) -> float:
    return importe_bruto(venta) * venta.descuento


def subtotal(venta: Venta) -> float:
    """Importe después de descuento, antes de IVA."""
    return importe_bruto(venta) - monto_descuento(venta)


def calcular_iva(monto: float, tasa: float = TASA_IVA) -> float:
    return monto * tasa


def total_venta(venta: Venta) -> float:
    """Total cobrado al cliente: subtotal + IVA."""
    return redondear(subtotal(venta) + calcular_iva(subtotal(venta)))


def utilidad(venta: Venta) -> float:
    """Ganancia de la venta: subtotal - costo de la mercancía."""
    return redondear(subtotal(venta) - venta.costo * venta.cantidad)


def margen(venta: Venta) -> float:
    """Utilidad como proporción del subtotal (0..1)."""
    s = subtotal(venta)
    return utilidad(venta) / s if s else 0.0


# ---------------------------------------------------------------------------
# Comisiones escalonadas
# ---------------------------------------------------------------------------
def tasa_comision(monto_vendido: float, tabla: tuple = TABLA_COMISIONES) -> float:
    """
    Devuelve el porcentaje de comisión que corresponde a un monto.
    Se queda con el último escalón cuyo mínimo se alcanzó.
    (Generator expression + max: sin ciclos ni variables mutables.)
    """
    return max((tasa for minimo, tasa in tabla if monto_vendido >= minimo), default=0.0)


def comision(monto_vendido: float, tabla: tuple = TABLA_COMISIONES) -> float:
    return redondear(monto_vendido * tasa_comision(monto_vendido, tabla))


# ---------------------------------------------------------------------------
# Transformaciones que PRODUCEN NUEVOS VALORES (inmutabilidad)
# ---------------------------------------------------------------------------
def con_descuento(venta: Venta, descuento: float) -> Venta:
    """Devuelve una venta NUEVA con otro descuento. La original no cambia."""
    return venta._replace(descuento=descuento)


def ajustar_precio(producto: Producto, porcentaje: float) -> Producto:
    """Devuelve un producto NUEVO con el precio ajustado (+0.10 = +10 %)."""
    return replace(producto, precio=redondear(producto.precio * (1 + porcentaje)))


def actualizar_stock(inventario: dict, sku: str, delta: int) -> dict:
    """
    Devuelve un inventario NUEVO con el stock de `sku` modificado.
    {**inventario, ...} copia el diccionario: el original queda intacto.
    """
    return {**inventario, sku: inventario.get(sku, 0) + delta}


def crear_venta(folio: str, fecha: date, producto: Producto, cantidad: int,
                descuento: float, vendedor: str) -> Venta:
    """Construye una venta a partir de un producto del catálogo."""
    return Venta(
        folio=folio, fecha=fecha, sku=producto.sku, producto=producto.nombre,
        categoria=producto.categoria, precio=producto.precio, costo=producto.costo,
        cantidad=cantidad, descuento=descuento, vendedor=vendedor,
    )


def validar_venta(venta: Venta, inventario: dict) -> tuple:
    """
    Regresa una tupla de mensajes de error (vacía si todo está bien).
    Se construye con una comprensión sobre (condición, mensaje):
    no hay if/append encadenados.
    """
    reglas = (
        (venta.cantidad <= 0, "La cantidad debe ser mayor que cero."),
        (not 0 <= venta.descuento <= 0.5, "El descuento debe estar entre 0 % y 50 %."),
        (inventario.get(venta.sku, 0) < venta.cantidad, "No hay stock suficiente."),
    )
    return tuple(mensaje for falla, mensaje in reglas if falla)
