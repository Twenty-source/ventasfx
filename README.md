# VentasFx

**Sistema administrativo de ventas e inventario construido con el paradigma de programación funcional en Python.**

| | |
|---|---|
| **Alumno** | Alan Rodríguez · No. de control 23940396 |
| **Grupo** | 7 AS · Ingeniería en Sistemas Computacionales |
| **Materia** | Programación Lógica y Funcional |
| **Unidad** | 2 · Modelo de Programación Funcional (proyecto integrador) |
| **Docente** | Torres Rangel José Ángel |
| **Institución** | Instituto Tecnológico de Tlajomulco (TecNM) |

### ▶ [Abrir la aplicación en línea](https://ventasfx-alan.streamlit.app) · [Repositorio](https://github.com/Twenty-source/ventasfx)

La aplicación en línea no requiere instalar nada. Si estuvo varios días sin uso, Streamlit la pone en
pausa: basta con presionar el botón para reactivarla y esperar unos segundos.

---

## Descripción

VentasFx administra las ventas, el catálogo y el inventario de una tienda con 34 productos,
8 vendedores y alrededor de 60 000 ventas simuladas de dos años. Su objetivo es aplicar cada tema
de la Unidad 2 a un caso real y no a ejemplos aislados.

Toda la lógica de negocio está escrita como **funciones puras** que transforman **datos
inmutables**. La interfaz (Streamlit) es una capa imperativa delgada que solo muestra resultados y
recibe acciones del usuario. Todo el sistema sigue el mismo flujo:

```
datos → filtrar (filter) → transformar (map) → agregar (reduce) → resultado
```

Cada pantalla incluye un panel ** Concepto aplicado** que explica el tema y muestra el código
fuente real que se está ejecutando.

---

## Sugerencia Personal

Este es un recorrido que sugiero yo, profesor, en la aplicación en línea. Cada paso indica dónde hacer clic y qué tema de la
unidad se comprueba.

| # | Dónde | Qué hacer | Qué se comprueba |
|---|---|---|---|
| 1 | **Inicio** | Revisar el diagrama de arquitectura y la tabla de temas. | Organización del proyecto: núcleo funcional y capa de interfaz. |
| 2 | **Laboratorio → Imperativo vs funcional** | Elegir *Suma de cuadrados de pares* y presionar **Ejecutar ambas**. | Cambio de paradigma: misma respuesta (220) con dos enfoques, con tiempos. |
| 3 | **Laboratorio → Pureza** | Presionar **agregar(5)** dos veces y revisar la sección de inmutabilidad. | Funciones puras vs impuras; lista vs tupla; objetos que no se pueden modificar. |
| 4 | **Laboratorio → Tipos** | Revisar la tabla. | 2.1 Tipos de datos y su uso dentro del sistema. |
| 5 | **Laboratorio → Constructor de flujos** | Cambiar el `range`, el predicado, la transformación y el reductor. | 2.2 Funciones como valores, 2.3 `range`, map/filter/reduce y su equivalente en comprensión. |
| 6 | **Dashboard** | Quitar una categoría del filtro. | 2.5 Los 5 indicadores se calculan con un solo `reduce`; predicados combinados. |
| 7 | **Ventas → Explorar (pipeline)** | Cambiar la regla `campo operador valor` y activar **Negar reglas (NOT)**. | 2.4 Operadores (`operator.gt`, `operator.eq`…) y predicados; funciones de orden superior; pipeline paso a paso. |
| 8 | **Ventas → Registrar venta** | Registrar una venta y presionar **Deshacer última acción**. | Inmutabilidad: cada acción crea un estado nuevo; ver también *Historial de versiones*. |
| 9 | **Laboratorio → Recursividad** | Mover los controles de factorial y Fibonacci. | Recursividad con caso base; memoización posible gracias a la pureza. |
| 10 | **Catálogo e inventario** | Explorar *Árbol de categorías* y *Árbol de búsqueda por precio* (cambiar entre *Insertando* y *Balanceado*). | 2.6 Árboles con tuplas `(valor, izquierda, derecha)`, recorridos y búsqueda por rango. |
| 11 | **Reportes** | Cambiar el nivel y la métrica en *Por categoría*; abrir *Comparativo anual*. | Funciones que fabrican funciones; periodos generados con `range`. |
| 12 | **Carga masiva** | Presionar **Generar archivo**, luego **Comparar**; activar **Transmitir en vivo**. | 2.7 Evaluación perezosa: memoria ansiosa vs perezosa, `islice`, secuencia infinita con generadores. |

---

## Marcas en el código

Los comentarios que empiezan con **`[PF`** señalan dónde se aplica cada tema. Para recorrerlos,
buscar `[PF` en todo el proyecto (en GitHub: tecla `.` para abrir el editor web y luego
`Ctrl + Shift + F`). Para un tema específico, buscar la marca completa, por ejemplo `[PF 2.5 reduce]`.

| Marca | Significado |
|---|---|
| `[PF pura]` | Función pura: misma entrada, misma salida, sin efectos |
| `[PF inmutable]` | Se produce un valor nuevo en lugar de modificar el existente |
| `[PF 2.1 tipos]` | Tipos de datos y por qué se eligió cada uno |
| `[PF 2.2 primera clase]` | Funciones guardadas en variables, diccionarios o pasadas como valor |
| `[PF 2.2 orden superior]` | Funciones que reciben o devuelven funciones |
| `[PF 2.2 lambda]` | Funciones anónimas |
| `[PF 2.3 range]` | Intervalos con `range()` |
| `[PF 2.4 operator]` | Operadores tratados como funciones (`operator.gt`, `itemgetter`…) |
| `[PF 2.4 predicado]` | Funciones que devuelven True / False |
| `[PF 2.5 map]` · `[PF 2.5 filter]` · `[PF 2.5 reduce]` | Transformar · seleccionar · acumular |
| `[PF 2.5 comprensión]` | Comprensiones de listas, diccionarios y conjuntos |
| `[PF recursividad]` | Caso base y caso recursivo |
| `[PF 2.6 árbol]` | Árboles construidos con tuplas |
| `[PF 2.7 generador]` · `[PF 2.7 perezoso]` | `yield`, iteradores y evaluación diferida |
| `[PF efecto]` | Efectos secundarios aislados a propósito (archivos, reloj, estado de la interfaz) |

---

## Correspondencia con los temas de la Unidad 2

| Tema | Pantalla | Código |
|---|---|---|
| Imperativo vs. funcional | Laboratorio → *Imperativo vs funcional* (5 problemas) | `core/didactico.py` |
| Funciones puras | Todo el núcleo · Laboratorio → *Pureza* | `core/funciones.py`, `tests/` |
| Inmutabilidad | Ventas → *Registrar venta* e *Historial de versiones* · Catálogo → ajuste de precios | `core/modelos.py`, `ui/estado.py` |
| 2.1 Tipos de datos | Laboratorio → *Tipos* | `core/modelos.py` |
| 2.2 Funciones de primera clase | Diccionarios de funciones en Reportes y Laboratorio | `core/didactico.py`, `core/predicados.py` |
| Funciones de orden superior | `regla()`, `y_()`, `clave_categoria()`, `compose()`, decoradores | `core/predicados.py`, `core/pipeline.py` |
| lambda | Predicados, transformaciones y ordenamientos | `core/` |
| 2.3 Intervalos `range()` | Meses en Reportes, paginación en Ventas, Carga masiva, Laboratorio | `core/reportes.py` |
| 2.4 Operadores y predicados | Ventas → reglas con `operator.gt`, `operator.eq`… | `core/predicados.py` |
| 2.5 map / filter / reduce | Dashboard (un solo `reduce` para los indicadores), pipeline en Ventas | `core/reportes.py`, `core/pipeline.py` |
| Comprensiones de listas | Reportes, validaciones, diferencias entre versiones | varios |
| Recursividad | Laboratorio → factorial con traza, Fibonacci con y sin memoización | `core/didactico.py` |
| 2.6 Árboles | Catálogo → árbol de categorías y árbol binario por precio | `core/arbol.py` |
| 2.7 Evaluación perezosa | Carga masiva → memoria ansiosa vs perezosa, `islice`, lotes | `core/perezoso.py` |
| Generadores y `yield` | Lectura de CSV, recorridos de árboles, flujo infinito de ventas | `core/perezoso.py`, `core/arbol.py` |

---

## Ejecución local (opcional)

Requisitos: **Python 3.10 o superior**.

**1. Obtener el código.** En GitHub: botón **Code → Download ZIP** y descomprimir, o bien:

```
git clone https://github.com/Twenty-source/ventasfx.git
cd ventasfx
```

**2. Crear el entorno virtual e instalar dependencias** (desde la carpeta del proyecto):

```powershell
python -m venv .venv
.venv\Scripts\activate          # Windows (PowerShell)
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno, ejecutar una vez
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned` y volver a intentar.

**3. Abrir la aplicación** (se abre en el navegador):

```
streamlit run app.py
```

La primera ejecución genera `data/ventas.csv` con las ventas simuladas; tarda unos segundos.
Los datos se generan con una semilla fija, por lo que siempre son los mismos.

**4. Ejecutar las pruebas automáticas** (47 pruebas):

```
python -m pytest
```

---

## Estructura del proyecto

```
ventasfx/
├── app.py                  Punto de entrada y menú de navegación
├── core/                   NÚCLEO FUNCIONAL (no depende de Streamlit)
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
├── paginas/                Pantallas de la aplicación
├── data/generar_datos.py   Generador de datos simulados
└── tests/                  Pruebas automáticas con pytest
```

---

## Decisiones de diseño

- **Núcleo funcional, capa imperativa delgada.** `core/` no importa Streamlit: sus funciones se
  pueden probar y reutilizar en cualquier otro programa.
- **Estado como historial de valores.** Cada acción crea un `EstadoTienda` nuevo; deshacer
  consiste en volver al anterior. Ningún estado se sobrescribe.
- **Mutación local controlada.** En `reportes._sumar_en`, el acumulador del `reduce` es un
  diccionario recién creado que ninguna otra parte del programa ve. La función `agrupar` sigue
  siendo pura hacia afuera y evita copiar el diccionario en cada paso.
- **Python no es un lenguaje funcional puro.** El sistema aplica la disciplina funcional donde
  aporta (reglas de negocio, transformaciones, consultas) y deja los efectos (archivos, pantalla,
  reloj) en la orilla del sistema.
- **Versión en línea.** Se publica en Streamlit Community Cloud. Ahí la Carga masiva se limita a
  250 000 ventas para no rebasar la memoria del servidor; en ejecución local permite hasta
  1 000 000.
- **Datos no persistentes.** Las ventas registradas y los ajustes de precio viven solo durante la
  sesión del navegador; al recargar, la aplicación vuelve a su estado inicial.
