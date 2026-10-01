# VentasFx

**Sistema administrativo de ventas e inventario construido con programación funcional en Python.**

Proyecto integrador de la Unidad 2 · *Modelo de Programación Funcional*
Programación Lógica y Funcional · Ingeniería en Sistemas Computacionales

Toda la lógica de negocio está escrita como **funciones puras** que transforman **datos inmutables**.
La interfaz (Streamlit) es una capa imperativa delgada que solo muestra resultados y recibe acciones.

```
datos → filtrar (filter) → transformar (map) → agregar (reduce) → resultado
```

---

## Cómo ejecutarlo

Requisitos: Python 3.10 o superior.

```powershell
# 1. Entrar a la carpeta del proyecto
cd ventasfx

# 2. Activar el entorno virtual (Windows / PowerShell)
.venv\Scripts\activate
#    Mac / Linux:  source .venv/bin/activate

# 3. Instalar dependencias (solo la primera vez)
pip install -r requirements.txt

# 4. Abrir la app (se abre sola en el navegador)
streamlit run app.py
```

La primera vez, la app genera automáticamente `data/ventas.csv` con unas 60 000 ventas simuladas
de dos años. Tarda un par de segundos.

**Pruebas automáticas:**

```powershell
python -m pytest
```

**Publicarla en línea (Streamlit Community Cloud):** sube el proyecto a GitHub, entra a
share.streamlit.io con tu cuenta de GitHub, elige el repositorio, la rama `main` y el archivo
`app.py`, y en *Advanced settings* selecciona Python 3.10 o 3.11. La app detecta que corre en la
nube y limita la Carga masiva a 250 000 ventas para no rebasar la memoria del servidor.

---

## Estructura

```
ventasfx/
├── app.py                  Punto de entrada y menú de navegación
├── core/                   NÚCLEO FUNCIONAL (sin Streamlit)
│   ├── modelos.py          Tipos inmutables: Venta (NamedTuple), Producto (dataclass frozen)
│   ├── funciones.py        Reglas de negocio puras: importe, IVA, utilidad, comisiones
│   ├── predicados.py       Predicados, módulo operator, combinadores y_ / o_ / no_
│   ├── pipeline.py         compose, pipe, pipelines con pasos y decoradores
│   ├── reportes.py         Agregaciones con reduce, series con range, paginación
│   ├── arbol.py            Árbol binario con tuplas y árbol n-ario de categorías
│   ├── perezoso.py         Generadores, lectura perezosa de CSV, flujos infinitos
│   └── didactico.py        Ejemplos imperativo vs funcional, recursividad, laboratorio
├── ui/
│   ├── estado.py           Único lugar con estado: historial de versiones inmutables
│   └── componentes.py      Panel "Concepto aplicado", tarjetas de pipeline, formato
├── paginas/                Pantallas de la app
├── data/generar_datos.py   Generador de datos simulados
└── tests/                  47 pruebas con pytest
```

---

## Dónde está cada tema de la Unidad 2

| Tema | Pantalla | Código |
|---|---|---|
| Imperativo vs. funcional | Laboratorio → *Imperativo vs funcional* (5 problemas, con tiempos) | `core/didactico.py` |
| Funciones puras | Todo el núcleo · Laboratorio → *Pureza* | `core/funciones.py`, `tests/` |
| Inmutabilidad | Ventas → *Registrar* (con **deshacer**) y *Historial* · Catálogo → ajuste de precios | `core/modelos.py`, `ui/estado.py` |
| 2.1 Tipos de datos | Laboratorio → *Tipos* | `core/modelos.py` |
| 2.2 Funciones de primera clase | Diccionarios de funciones en Reportes y Laboratorio | `core/didactico.py`, `core/predicados.py` |
| Funciones de orden superior | `regla()`, `y_()`, `clave_categoria()`, `compose()`, decoradores | `core/predicados.py`, `core/pipeline.py` |
| lambda | Predicados, transformaciones y ordenamientos | todo `core/` |
| 2.3 Intervalos `range()` | Meses en Reportes, paginación en Ventas, Carga masiva, Laboratorio | `core/reportes.py` |
| 2.4 Operadores y predicados | Ventas → reglas `campo operador valor` con `operator.gt`, `operator.eq`… | `core/predicados.py` |
| 2.5 map / filter / reduce | Dashboard (un solo `reduce` para los KPIs), pipeline visible en Ventas | `core/reportes.py`, `core/pipeline.py` |
| Comprensiones de listas | Reportes, validaciones, diferencias entre versiones | varios |
| Recursividad | Laboratorio → factorial con traza, Fibonacci con y sin memoización | `core/didactico.py` |
| 2.6 Árboles | Catálogo → árbol de categorías (sunburst) y árbol binario por precio | `core/arbol.py` |
| 2.7 Evaluación perezosa | Carga masiva → memoria ansiosa vs perezosa, `islice`, lotes | `core/perezoso.py` |
| Generadores y `yield` | Lectura de CSV, recorridos de árboles, ticker de ventas infinito | `core/perezoso.py`, `core/arbol.py` |

Cada pantalla tiene un panel **🧠 Concepto aplicado** que explica el tema y muestra el código real
que se ejecuta (obtenido con `inspect.getsource`).

---

## Decisiones de diseño

- **Núcleo funcional, capa imperativa delgada.** `core/` no importa Streamlit: se puede probar y
  reutilizar en cualquier otro programa.
- **Estado como historial de valores.** Cada acción crea un `EstadoTienda` nuevo; deshacer es
  volver al anterior. Nada se sobrescribe.
- **Mutación local controlada.** En `reportes._sumar_en` el acumulador del `reduce` es un
  diccionario recién creado que nadie más ve. La función `agrupar` sigue siendo pura hacia afuera
  y evita copiar el diccionario en cada paso.
- **Python no es un lenguaje funcional puro.** La app usa la disciplina funcional donde aporta
  (reglas de negocio, transformaciones, consultas) y deja los efectos (archivos, pantalla, reloj)
  en la orilla del sistema.
