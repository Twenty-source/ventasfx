"""
modelos.py — Tipos de datos del sistema (Tema 2.1: El tipo de datos).

Aquí se definen las estructuras con las que trabaja toda la aplicación.
Todas son INMUTABLES: una vez creadas no cambian. Para "modificarlas"
se produce un valor nuevo a partir del anterior.

Tipos de Python que aparecen en este módulo:
    int    -> cantidad, stock
    float  -> precio, costo, descuento
    bool   -> activo
    str    -> sku, nombre, categoria, vendedor
    tuple  -> CATALOGO, VENDEDORES, TABLA_COMISIONES (colecciones inmutables)
    set    -> CATEGORIAS_RAIZ (valores únicos)
    dict   -> INDICE_PRODUCTOS (búsqueda rápida por clave)
    list   -> se usa en la interfaz para selecciones del usuario
"""

from dataclasses import dataclass
from datetime import date
from typing import NamedTuple


# ---------------------------------------------------------------------------
# Producto: dataclass congelada (frozen=True) -> no se puede modificar.
# ---------------------------------------------------------------------------
@dataclass(frozen=True)
class Producto:
    sku: str
    nombre: str
    categoria: str      # Ruta jerárquica: "Electrónica/Cómputo/Laptops"
    precio: float
    costo: float
    stock: int
    activo: bool = True


# ---------------------------------------------------------------------------
# Venta: NamedTuple -> es una tupla, por lo tanto inmutable.
# Para "cambiarla" se usa venta._replace(campo=nuevo_valor), que devuelve
# una venta NUEVA y deja la original intacta.
# ---------------------------------------------------------------------------
class Venta(NamedTuple):
    folio: str
    fecha: date
    sku: str
    producto: str
    categoria: str
    precio: float
    costo: float
    cantidad: int
    descuento: float    # Porcentaje como fracción: 0.10 = 10 %
    vendedor: str


TASA_IVA: float = 0.16

VENDEDORES: tuple = (
    "Ana Torres", "Carlos Ruiz", "Diana López", "Emilio Vargas",
    "Fernanda Gil", "Gustavo Peña", "Hilda Navarro", "Iván Castillo",
)

# Comisión escalonada MENSUAL: (monto mínimo vendido en el mes sin IVA, porcentaje)
TABLA_COMISIONES: tuple = (
    (0, 0.02),
    (1_000_000, 0.03),
    (1_750_000, 0.04),
    (2_500_000, 0.05),
)

# Catálogo base. Es una tupla de Productos: el catálogo completo es inmutable.
CATALOGO: tuple = (
    # Electrónica
    Producto("EL-LAP-01", "Laptop Pro 14", "Electrónica/Cómputo/Laptops", 24999.0, 18500.0, 40),
    Producto("EL-LAP-02", "Laptop Air 13", "Electrónica/Cómputo/Laptops", 17999.0, 13200.0, 55),
    Producto("EL-LAP-03", "Laptop Gamer 16", "Electrónica/Cómputo/Laptops", 32999.0, 25900.0, 25),
    Producto("EL-ESC-01", "PC Escritorio Office", "Electrónica/Cómputo/Escritorio", 12999.0, 9300.0, 30),
    Producto("EL-ESC-02", "PC Workstation", "Electrónica/Cómputo/Escritorio", 38999.0, 30100.0, 12),
    Producto("EL-PER-01", "Mouse inalámbrico", "Electrónica/Cómputo/Periféricos", 399.0, 180.0, 300),
    Producto("EL-PER-02", "Teclado mecánico", "Electrónica/Cómputo/Periféricos", 1499.0, 820.0, 150),
    Producto("EL-PER-03", "Monitor 27\"", "Electrónica/Cómputo/Periféricos", 5499.0, 3900.0, 70),
    Producto("EL-CEL-01", "Smartphone A5", "Electrónica/Telefonía/Celulares", 5999.0, 4300.0, 120),
    Producto("EL-CEL-02", "Smartphone X Pro", "Electrónica/Telefonía/Celulares", 21999.0, 17100.0, 45),
    Producto("EL-ACC-01", "Audífonos BT", "Electrónica/Telefonía/Accesorios", 899.0, 450.0, 260),
    Producto("EL-ACC-02", "Cargador rápido", "Electrónica/Telefonía/Accesorios", 449.0, 190.0, 400),
    # Hogar
    Producto("HO-COC-01", "Licuadora 10 vel.", "Hogar/Cocina/Electrodomésticos", 1299.0, 780.0, 90),
    Producto("HO-COC-02", "Freidora de aire", "Hogar/Cocina/Electrodomésticos", 2199.0, 1400.0, 80),
    Producto("HO-COC-03", "Cafetera espresso", "Hogar/Cocina/Electrodomésticos", 4599.0, 3100.0, 35),
    Producto("HO-UTE-01", "Juego de sartenes", "Hogar/Cocina/Utensilios", 1199.0, 640.0, 110),
    Producto("HO-UTE-02", "Set de cuchillos", "Hogar/Cocina/Utensilios", 899.0, 420.0, 95),
    Producto("HO-MUE-01", "Silla ergonómica", "Hogar/Muebles/Oficina", 3499.0, 2300.0, 60),
    Producto("HO-MUE-02", "Escritorio en L", "Hogar/Muebles/Oficina", 4299.0, 2900.0, 28),
    Producto("HO-MUE-03", "Sofá 3 plazas", "Hogar/Muebles/Sala", 11999.0, 8200.0, 15),
    Producto("HO-MUE-04", "Mesa de centro", "Hogar/Muebles/Sala", 2499.0, 1500.0, 40),
    # Deportes
    Producto("DE-FIT-01", "Mancuernas 10 kg", "Deportes/Fitness/Pesas", 899.0, 520.0, 140),
    Producto("DE-FIT-02", "Banco de ejercicio", "Deportes/Fitness/Pesas", 2899.0, 1900.0, 35),
    Producto("DE-FIT-03", "Caminadora plegable", "Deportes/Fitness/Cardio", 9999.0, 7100.0, 18),
    Producto("DE-FIT-04", "Bicicleta fija", "Deportes/Fitness/Cardio", 6499.0, 4500.0, 22),
    Producto("DE-EXT-01", "Casa de campaña 4p", "Deportes/Exterior/Campismo", 2599.0, 1600.0, 50),
    Producto("DE-EXT-02", "Bicicleta de montaña", "Deportes/Exterior/Ciclismo", 8999.0, 6300.0, 26),
    Producto("DE-EXT-03", "Casco ciclismo", "Deportes/Exterior/Ciclismo", 799.0, 380.0, 120),
    # Papelería
    Producto("PA-ESC-01", "Cuaderno profesional", "Papelería/Escolar/Cuadernos", 59.0, 24.0, 2000),
    Producto("PA-ESC-02", "Paquete de plumas", "Papelería/Escolar/Escritura", 89.0, 35.0, 1500),
    Producto("PA-ESC-03", "Mochila escolar", "Papelería/Escolar/Mochilas", 699.0, 360.0, 210),
    Producto("PA-OFI-01", "Paquete hojas carta", "Papelería/Oficina/Consumibles", 119.0, 70.0, 900),
    Producto("PA-OFI-02", "Tóner láser", "Papelería/Oficina/Consumibles", 1599.0, 980.0, 75),
    Producto("PA-OFI-03", "Impresora láser", "Papelería/Oficina/Equipo", 3999.0, 2800.0, 33),
)

# dict comprehension: índice sku -> Producto (búsqueda O(1))
INDICE_PRODUCTOS: dict = {p.sku: p for p in CATALOGO}

# set comprehension: categorías raíz únicas
CATEGORIAS_RAIZ: set = {p.categoria.split("/")[0] for p in CATALOGO}
