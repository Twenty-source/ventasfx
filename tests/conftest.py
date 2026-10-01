"""Datos de prueba compartidos. Son tuplas: ninguna prueba puede alterarlos."""

from datetime import date

import pytest

from core.modelos import Venta


@pytest.fixture
def venta():
    return Venta("F-0000001", date(2026, 1, 15), "EL-PER-01", "Mouse inalámbrico",
                 "Electrónica/Cómputo/Periféricos", 400.0, 200.0, 3, 0.10, "Ana Torres")


@pytest.fixture
def ventas():
    return (
        Venta("F-1", date(2026, 1, 5), "A", "Mouse", "Electrónica/Cómputo/Periféricos",
              100.0, 50.0, 2, 0.0, "Ana Torres"),
        Venta("F-2", date(2026, 1, 20), "B", "Licuadora", "Hogar/Cocina/Electrodomésticos",
              1000.0, 600.0, 1, 0.10, "Carlos Ruiz"),
        Venta("F-3", date(2026, 3, 2), "C", "Laptop", "Electrónica/Cómputo/Laptops",
              20000.0, 15000.0, 1, 0.0, "Ana Torres"),
        Venta("F-4", date(2026, 3, 9), "D", "Cuaderno", "Papelería/Escolar/Cuadernos",
              50.0, 20.0, 10, 0.0, "Diana López"),
    )
