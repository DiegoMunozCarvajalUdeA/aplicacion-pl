# Aplicación de Programación Lineal

Entorno de desarrollo para el proyecto de Optimización de Ingeniería de Sistemas,
Universidad de Antioquia. El enunciado oficial está en `taller-optimi.pdf`.

La infraestructura funciona. El equipo implementará los algoritmos indicados en
`docs/plan.md`; la aplicación todavía no resuelve problemas. SciPy se usa únicamente
como oráculo de pruebas, nunca en la aplicación.

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

## Uso de la base

La app permite editar Max/Min, agregar o quitar variables y restricciones sin
perder las celdas restantes, cargar los 13 ejemplos y cargar/descargar JSON.
Admite números como `-3`, `2.5`, `2,5` y `2/5`; todas las variables cumplen x ≥ 0.
Al pulsar Resolver, los errores indican la celda afectada. El resumen del modelo
validado funciona; cada algoritmo pendiente muestra un aviso en su sección.

La forma estándar todavía es un stub. La sección que la presentará ya está
conectada y muestra el aviso correspondiente. No se presenta una conversión
inventada ni se usa SciPy para suplir el método del equipo.

Los contratos compartidos están en `src/plapp/result.py`. Los índices internos
empiezan en cero; la interfaz muestra filas y columnas desde uno. Los dos métodos
devuelven `Solution` y conservan el sentido original de Z. Los costos reducidos
usan r = c − c_B B⁻¹ A. Los números del modelo son Fraction; MValue almacena las
partes racional y simbólica, pero sus operaciones siguen pendientes.

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
aparecen como `xfail` mientras lancen NotImplementedError. Al implementarlos
pasarán como `XPASS`; una aserción fallida sigue siendo un fallo real. Quitar
las marcas cuando el equipo termine cada módulo.

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

Los siete ejemplos conservan los resultados del enunciado. Los seis extras
tienen `fuente: "scipy"` y cubren región no acotada con óptimo finito,
igualdades, región vacía, cuatro variables, RHS negativo y empate degenerado.
El oráculo contrasta todos los fixtures sin xfail. Hypothesis genera problemas
de 2–4 variables y 1–4 restricciones; la comparación de precios sombra se limita
a óptimos únicos no degenerados mediante una guardia conservadora.

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
src/plapp/       Modelo, persistencia, formato, contratos y stubs
app/            Interfaz Streamlit y presentación Plotly
scripts/        Verificador externo con SciPy
tests/          Infraestructura, contratos, AppTest y 13 fixtures JSON
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


