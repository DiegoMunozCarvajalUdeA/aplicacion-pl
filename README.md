# Aplicación de Programación Lineal

Entorno de desarrollo para el proyecto de Optimización de Ingeniería de Sistemas,
Universidad de Antioquia. El enunciado oficial está en `taller-optimi.pdf`.

La aplicación resuelve problemas con Gran M simbólica y Fraction, en modo directo
o paso a paso. P1–P5 y las correcciones de redundancia están implementados; simplex
revisado y PDF siguen pendientes según `docs/plan.md`. SciPy se usa únicamente como
oráculo de pruebas, nunca en la aplicación.

## Requisitos e instalación

- Python **3.12**, descargado y gestionado por [uv](https://docs.astral.sh/uv/).
- En macOS con Homebrew: `brew install uv`. No usar Python 3.14 del sistema.
- Git para el historial de contribuciones del equipo.

Desde la raíz del repositorio:

```bash
uv python pin 3.12
uv sync --locked
uv run streamlit run app/streamlit_app.py
```

Abrir `http://localhost:8501`. Detener con Ctrl-C. También están disponibles
`make setup` y `make run`. El entorno se instala en `.venv/`, excluido de Git.

## Uso

La app permite editar Max/Min, agregar o quitar variables y restricciones sin
perder las celdas restantes, cargar los 14 ejemplos y cargar/descargar JSON.
Admite números como `-3`, `2.5`, `2,5` y `2/5`; todas las variables cumplen x ≥ 0.
Al pulsar Resolver, los errores indican la celda afectada. El resumen del modelo
validado funciona; cada algoritmo pendiente muestra un aviso en su sección.

Seleccione Gran M y pulse Resolver. Directo muestra variables, Z y holguras o
excesos originales. Paso a paso añade normalización, forma estándar y todas las
iteraciones: base con nombres, tablero rotulado, costos reducidos, Z, pivote
resaltado, razones y justificaciones. Fracciones y decimales cambian únicamente
la presentación; los cálculos permanecen exactos. Se informan infactibilidad,
no acotación, segmentos o rayos óptimos y variables básicas nulas.

El método gráfico resuelve de forma independiente los problemas de dos variables:
región sombreada, rectas rotuladas, vértices con Z, isoutilidad, segmentos y
rayos óptimos. Informa regiones vacías y objetivos no acotados; la caja sirve
solo para dibujar. La sensibilidad presenta precios sombra originales, costos
reducidos y rangos de un dato a la vez, con interpretación y advertencias de
degeneración o redundancia. Una fila redundante recibe un representante dual
cero y no se ofrece un rango para su RHS.

Los contratos compartidos están en `src/plapp/result.py`. Los índices internos
empiezan en cero; la interfaz muestra filas desde uno y columnas por nombre.
Ambos métodos comparten el contrato `Solution` en el sentido original de Z,
aunque el revisado continúa pendiente. Los costos reducidos usan
r = c − c_B B⁻¹ A. MValue opera con las partes racional y simbólica exactas.
La guía `docs/sustentacion.md` explica los módulos y la traza del ejemplo 2.

## Pruebas y calidad

```bash
make lint
make test
uv run pytest --cov=plapp --cov-report=term-missing
make fmt
make requirements
```

`make fmt` aplica formato y correcciones automáticas de Ruff. La configuración
usa 100 columnas y reglas E, F, I, UP, B. CI ejecuta sincronización bloqueada,
Ruff y pytest. Las pruebas de infraestructura deben pasar; las de algoritmos
pendientes aparecen como `xfail` mientras lancen NotImplementedError. Las marcas
se retiran al implementar cada módulo; MValue, forma estándar y Gran M ya se
prueban sin xfail. Una aserción fallida sigue siendo un fallo real.

## Oráculo SciPy

```bash
uv run python scripts/verify.py tests/fixtures/problems/ejemplo_1.json
make verify FILE=tests/fixtures/problems/ejemplo_2.json
uv run python scripts/verify.py tests/fixtures/problems/extra_1.json --json
uv run pytest tests/test_oracle_scipy.py -q
```

El script informa estado, x, Z, holguras/excesos y precios sombra. También intenta
ambos métodos propios: informa que están pendientes o compara estado, Z y
factibilidad, sin exigir el mismo vértice si hay óptimos múltiples. Devuelve
código distinto de cero si hay discrepancias o errores de verificación.

`linprog` minimiza: para Max se transforma c en −c. Cada restricción ≥ se
transforma en −a·x ≤ −b. El precio reportado es **∂Z*/∂b original**:
signo del objetivo × signo de transformación de fila × marginal de HiGHS.
En Max el signo del objetivo es −1; en Min, +1. El signo de fila es −1 solo
para ≥. Una igualdad conserva su signo. SciPy calcula en coma flotante; las
fracciones del informe son reconstrucciones legibles, no aritmética exacta.
Los precios pueden no ser únicos con degeneración o soluciones múltiples.

Los siete ejemplos conservan los resultados del enunciado. Los primeros seis extras
tienen `fuente: "scipy"` y cubren región no acotada con óptimo finito,
igualdades, región vacía, cuatro variables, RHS negativo y empate degenerado.
El oráculo contrasta todos los fixtures sin xfail. Hypothesis genera problemas
de 2–4 variables y 1–6 restricciones, incluidas copias y filas escaladas; la comparación de precios sombra se limita
a óptimos únicos no degenerados mediante una guardia conservadora.

El extra 7 cubre una no acotación que presolve clasifica como infactible; su
fuente es «scipy sin presolve y Gran M». El oráculo repite sin presolve los
estados 2, 3 y 4 y exige confirmación si cambia el estado. Si no concluye,
las pruebas generativas descartan ese caso y el estrés lo cuenta por separado.

```bash
uv run python scripts/stress.py --seed 20261110 --count 3000
```

La última corrida terminó con 3000 verificados, 0 errores, 0 diferencias y
0 inconcluyentes. La suite tarda unos 18 segundos en este equipo. El informe
`docs/desarrollo-c-p4-p5.md` conserva el conteo previo de 72 errores, la prueba
de regresión temporal y las verificaciones por paquete. No se agregaron
dependencias; Playwright y las capturas del manual quedan para P8.

## Despliegue en Streamlit Community Cloud

1. Completar los algoritmos y comprobar `make lint`, `make test` y los ejemplos.
2. Ejecutar `make requirements` para exportar el lockfile sin herramientas dev.
   La exportación incluye `.` para instalar el paquete local `src/plapp`.
3. Cuando el equipo decida publicar, subir el repositorio a su cuenta y crear
   la app en Streamlit Community Cloud con `app/streamlit_app.py` como entrada.
4. Seleccionar Python **3.12** en la configuración avanzada. Community Cloud
   también puede detectar `uv.lock`; mantenerlo coherente con `requirements.txt`.
5. Verificar carga de JSON, ejemplos y reejecución; registrar la URL real abajo.

Esta preparación no crea remotos ni publica la app. La ejecución local sigue
disponible para la sustentación sin conexión a un servicio de despliegue.

## Estructura

```text
src/plapp/       Modelo, Gran M, álgebra exacta, contratos y módulos pendientes
app/            Interfaz Streamlit y presentación Plotly
scripts/        Verificador externo con SciPy
tests/          Infraestructura, contratos, AppTest y 14 fixtures JSON
docs/           Propuesta, plan, teoría, manual y verificación del entorno
.github/        CI de Ruff y pytest
.streamlit/     Configuración local y manejo de errores
```

Ver `docs/plan.md` para el orden de implementación y el reparto sugerido.

## Equipo y entregables

| Integrante | Identificador | Área | Cuenta Git |
|---|---|---|---|
| [Nombre 1] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 2] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 3] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 4, si aplica] | [Documento/código] | [Área] | [Usuario] |

- Repositorio remoto: **[URL por completar]**.
- Despliegue: **[URL por completar]**.
- Manual: máximo 5 páginas; esqueleto en `docs/manual/README.md`.
- Video: máximo 5 minutos; **[URL por completar]**.
- Sustentación: 15 minutos; todos deben explicar y modificar cualquier módulo.
- Registrar commits propios de cada integrante; los commits de preparación no
  reemplazan las contribuciones del equipo.

## Referencias

- Universidad de Antioquia. *Proyecto: Aplicación de Programación Lineal*,
  noviembre de 2026. Documento local `taller-optimi.pdf`; fuente de requisitos y
  de los siete primeros problemas.
- [Streamlit: tablas editables y estado](https://docs.streamlit.io/develop/concepts/design/dataframes).
- [Streamlit: AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).
- [Streamlit: tablas y Styler](https://docs.streamlit.io/develop/api-reference/data/st.table).
- [pandas: Styler.apply](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.apply.html).
- [Streamlit: dependencias de despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies).
- [Plotly: gráficos de líneas](https://plotly.com/python/line-charts/).
- [fpdf2: documentación y Unicode](https://py-pdf.github.io/fpdf2/Unicode.html).
- [uv: sincronización y lockfile](https://docs.astral.sh/uv/concepts/projects/sync/).
- [uv: acción oficial para GitHub](https://docs.astral.sh/uv/guides/integration/github/).
- [SciPy: linprog y marginales](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html).
- [Python 3.12: Fraction](https://docs.python.org/3.12/library/fractions.html).

La preparación se realizó con apoyo de Codex y consulta de documentación oficial.
No se incorporó un solver ajeno. El equipo debe registrar cualquier fuente
adicional y comprender cada cambio que presente.


