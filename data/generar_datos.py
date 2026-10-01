"""
generar_datos.py — Crea el archivo de ventas simuladas.

La app lo ejecuta sola la primera vez, pero también se puede correr a mano:

    python data/generar_datos.py                   # 2 años (≈ 60 000 ventas)
    python data/generar_datos.py --dias 365 --salida data/otro.csv

Todo el proceso es PEREZOSO: el generador `simular_ventas` produce una
venta a la vez y `escribir_ventas` la escribe de inmediato, así que nunca
existe una lista con todas las ventas en memoria.
"""

import argparse
import sys
import time
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from core.perezoso import escribir_ventas, simular_ventas  # noqa: E402

RUTA_DEFAULT = RAIZ / "data" / "ventas.csv"
FECHA_INICIO = date(2024, 10, 1)
DIAS_DEFAULT = 730


def generar(ruta: Path = RUTA_DEFAULT, dias: int = DIAS_DEFAULT,
            ventas_por_dia: int = 60, semilla: int = 42) -> int:
    ruta.parent.mkdir(parents=True, exist_ok=True)
    flujo = simular_ventas(semilla=semilla, fecha_inicio=FECHA_INICIO,
                           dias=dias, ventas_por_dia=ventas_por_dia)
    return escribir_ventas(str(ruta), flujo)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Genera ventas simuladas en CSV.")
    parser.add_argument("--dias", type=int, default=DIAS_DEFAULT)
    parser.add_argument("--por-dia", type=int, default=60)
    parser.add_argument("--semilla", type=int, default=42)
    parser.add_argument("--salida", type=Path, default=RUTA_DEFAULT)
    args = parser.parse_args()

    inicio = time.perf_counter()
    filas = generar(args.salida, args.dias, args.por_dia, args.semilla)
    print(f"{filas:,} ventas escritas en {args.salida} "
          f"({time.perf_counter() - inicio:.1f} s)")
