# Aplicación de Programación Lineal

Proyecto de Optimización de Ingeniería de Sistemas, Universidad de Antioquia.
El enunciado oficial está en `taller-optimi.pdf`.

La aplicación resuelve problemas con Gran M simbólica y simplex revisado, con
Fraction, en modo directo o paso a paso, y agrega método gráfico, sensibilidad,
comparación de métodos, JSON y PDF. SciPy se usa únicamente como oráculo de
pruebas, nunca en la aplicación.

**Estado.** Implementados y verificados: P1–P7 (núcleo, Gran M, presentación,
gráfico, sensibilidad, simplex revisado y PDF), las correcciones C, R y V, y los
entregables de P8 (manual, guion del video, ensayo, guía y guía de entrega).
Falta lo que solo puede hacer el equipo: nombres, remoto, despliegue, video y
commits propios; la lista ordenada está en `docs/entrega.md` y el detalle por
paquete en `docs/plan.md`.

## Documentación

| Documento | Contenido |
|---|---|
| [Manual de usuario (PDF)](docs/manual/manual.pdf) | 5 páginas con capturas reales; fuente en [`docs/manual/README.md`](docs/manual/README.md). |
| [Guion del video](docs/video.md) | Tramos de 4:45 con pantalla, texto y responsable. Video: **[URL por completar]**. |
| [Guía de sustentación](docs/sustentacion.md) | Índice por módulo, preguntas y ejercicios de modificación. |
| [Ensayo de sustentación](docs/ensayo-sustentacion.md) | Cinco problemas nuevos, simulacro de 15 minutos y banco de modificaciones probadas. |
| [Entrega](docs/entrega.md) | Remoto, despliegue, video, plan B y lista de comprobación final. |
| [Plan y rúbrica](docs/plan.md) | Estado por paquete, rúbrica, bonificaciones y pendientes. |
| [Teoría](docs/teoria.md) | Resumen de Gran M, sensibilidad y método gráfico. |
| [Capturas V](docs/capturas/v/) | Gráficos revisados de los seis casos de referencia. |

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
perder las celdas restantes, cargar los 19 problemas incluidos y cargar o
descargar JSON.
Admite números como `-3`, `2.5`, `2,5` y `2/5`; todas las variables cumplen x ≥ 0.
Al pulsar Resolver, los errores indican la celda afectada. El resumen del modelo
validado presenta el problema original antes de resolverlo.

Seleccione un método y pulse Resolver. Directo muestra variables, Z y holguras o
excesos originales. Paso a paso añade normalización, forma estándar y todas las
iteraciones: base con nombres, tablero rotulado, costos reducidos, Z, pivote
resaltado, razones y justificaciones. Fracciones y decimales cambian únicamente
la presentación; los cálculos permanecen exactos. Se informan infactibilidad,
no acotación, segmentos o rayos óptimos y variables básicas nulas.

El revisado muestra B⁻¹, x_B, los multiplicadores simbólicos `y`, costos reducidos
y la columna d con la razón mínima y el pivote. «Comparar ambos» presenta una
fila por estado con las dos bases, entrantes, salientes y Z, y resume las
coincidencias. Ambos usan las mismas reglas simplex; mantienen representaciones
distintas. Las capturas revisadas del gráfico están en `docs/capturas/v/`
(las de la revisión anterior siguen en `docs/capturas/r/`).

«Exportar paso a paso a PDF» está disponible tras resolver, incluso en modo
Directo. El PDF contiene el problema, forma estándar, iteraciones, justificaciones,
resultado y sensibilidad cuando hay óptimo. Respeta el formato y los decimales
seleccionados; usa páginas horizontales, bloques de columnas y encabezados
repetidos. «Comparar métodos» ofrece además un PDF por método.

El método gráfico resuelve de forma independiente los problemas de dos variables:
región sombreada, rectas rotuladas, vértices con Z, isoutilidad, segmentos y
rayos óptimos. Informa regiones vacías y objetivos no acotados; la caja sirve
solo para dibujar. La sensibilidad presenta precios sombra originales, costos
reducidos y rangos de un dato a la vez, con interpretación y advertencias de
degeneración o redundancia. Una fila redundante recibe un representante dual
cero y su fila de RHS muestra «No disponible (fila redundante)».

Los contratos compartidos están en `src/plapp/result.py`. Los índices internos
empiezan en cero; la interfaz muestra filas desde uno y columnas por nombre.
Ambos métodos comparten el contrato `Solution` en el sentido original de Z,
con x_B y multiplicadores simbólicos explícitos en las iteraciones del revisado.
Los costos reducidos usan
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
Ruff y pytest. Todos los algoritmos se prueban sin xfail. Las trazas anteriores
al refactor se conservan en `tests/fixtures/big_m_traces.json` y no se regeneran
para aceptar cambios del método.

## Oráculo SciPy

```bash
uv run python scripts/verify.py tests/fixtures/problems/ejemplo_1.json
make verify FILE=tests/fixtures/problems/ejemplo_2.json
uv run python scripts/verify.py tests/fixtures/problems/extra_1.json --json
uv run pytest tests/test_oracle_scipy.py -q
```

El script informa estado, x, Z, holguras/excesos y precios sombra. También intenta
ambos métodos propios: compara estado, Z y
factibilidad, sin exigir el mismo vértice si hay óptimos múltiples. Devuelve
código distinto de cero si hay discrepancias o errores de verificación.

`linprog` minimiza: para Max se transforma c en −c. Cada restricción ≥ se
transforma en −a·x ≤ −b. El precio reportado es **∂Z*/∂b original**:
signo del objetivo × signo de transformación de fila × marginal de HiGHS.
En Max el signo del objetivo es −1; en Min, +1. El signo de fila es −1 solo
para ≥. Una igualdad conserva su signo. SciPy calcula en coma flotante; las
fracciones del informe son reconstrucciones legibles, no aritmética exacta.
Los precios pueden no ser únicos con degeneración o soluciones múltiples.

Los siete ejemplos conservan los resultados del enunciado. Los cinco ensayos
(`ensayo_1` a `ensayo_5`) tienen `fuente: "scipy"`: infactible, no acotado,
óptimos múltiples, degenerado y cuatro variables con =, ≥ y lado derecho
negativo. Los primeros seis extras
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
uv run python scripts/stress.py --method both --seed 20261110 --count 3000
```

La corrida de V–P8 (2026-11-10) verificó 3000 problemas por método con
0 errores, 0 diferencias y 0 inconcluyentes. También acepta `--method big_m`
o `revised`. `docs/desarrollo-v-p8.md` registra la verificación completa de la
última sesión; los informes anteriores `docs/desarrollo-*.md` conservan las suyas.

Playwright, pypdf y markdown-it-py son dependencias dev: capturas, descargas
e impresión del manual en Chromium; lectura independiente de los PDF; y
conversión del manual de Markdown a HTML, respectivamente. FontTools,
ya requerido por fpdf2, se declara también como dependencia directa para
comprobar todos los glifos antes de escribirlos. `requirements.txt` excluye dev.

Para repetir la verificación visual y el manual (la primera vez, instalar Chromium):

```bash
uv run playwright install chromium
make ui-check
make manual-captures
make manual
```

`make ui-check` comprueba salud, captura nueve gráficos (los seis casos de
referencia y los tres ensayos de dos variables) y descarga 36 PDF de los
ejemplos 2, 5 y 6 en ambos modos y formatos. Inicia y detiene su propio
servidor; `OUT=/tmp/plapp-ui` cambia el directorio de resultados.
`make manual-captures` reemplaza las diez capturas de `docs/manual/capturas/` y
`make manual` genera `docs/manual/manual.pdf` desde `docs/manual/README.md`;
falla si el PDF supera cinco páginas.

## Despliegue en Streamlit Community Cloud

Los pasos completos, con el ensayo local hecho desde un clon limpio, están en
`docs/entrega.md`. En resumen:

1. Comprobar `make lint` y `make test`, y ejecutar `make requirements` si cambió
   una dependencia de ejecución. `requirements.txt` excluye dev e incluye `.`
   para instalar el paquete local `src/plapp`.
2. Subir el repositorio a la cuenta del equipo y crear la app con
   `app/streamlit_app.py` como archivo de entrada.
3. Elegir Python **3.12** en «Advanced settings»; después del despliegue no se
   puede cambiar sin borrar y volver a desplegar la app.
4. Community Cloud usa el primer archivo de dependencias que encuentra y
   `uv.lock` va antes que `requirements.txt`: aquí instalará con uv desde
   `uv.lock`. Revisar en el registro de construcción qué comando ejecuta.
5. Abrir la URL en una ventana privada, resolver los ejemplos 2 y 6 y
   registrar la URL abajo.

Esta preparación no crea remotos ni publica la app. La ejecución local sigue
disponible para la sustentación sin conexión a un servicio de despliegue.

## Estructura

```text
src/plapp/       Modelo, métodos propios, reglas compartidas, gráfico, sensibilidad y PDF
app/            Interfaz Streamlit y presentación Plotly
assets/fonts/   DejaVu Sans 2.37 y licencia de redistribución
scripts/        Oráculo SciPy, estrés, verificación en Chromium y manual en PDF
tests/          Pruebas, AppTest, trazas congeladas y 19 fixtures JSON
docs/           Plan, guías, manual, video, ensayo, entrega, capturas e informes
.github/        CI de Ruff y pytest
.streamlit/     Configuración local y manejo de errores
```

Ver `docs/plan.md` para el estado por paquete y la rúbrica.

## Equipo y entregables

| Integrante | Identificador | Área | Cuenta Git |
|---|---|---|---|
| [Nombre 1] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 2] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 3] | [Documento/código] | [Área] | [Usuario] |
| [Nombre 4, si aplica] | [Documento/código] | [Área] | [Usuario] |

- Repositorio remoto: **[URL por completar]**.
- Despliegue: **[URL por completar]**.
- Manual: [`docs/manual/manual.pdf`](docs/manual/manual.pdf), 5 páginas.
- Video: máximo 5 minutos; **[URL por completar]**. Guion en `docs/video.md`.
- Sustentación: 15 minutos; todos deben explicar y modificar cualquier módulo.
- Registrar commits propios de cada integrante; los commits de preparación no
  reemplazan las contribuciones del equipo.

## Referencias

- Universidad de Antioquia. *Proyecto: Aplicación de Programación Lineal*,
  noviembre de 2026. Documento local `taller-optimi.pdf`; fuente de requisitos y
  de los siete primeros problemas.
- Streamlit: [tablas editables y estado](https://docs.streamlit.io/develop/concepts/design/dataframes),
  [st.table](https://docs.streamlit.io/develop/api-reference/data/st.table),
  [st.plotly_chart](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart),
  [st.download_button](https://docs.streamlit.io/develop/api-reference/widgets/st.download_button),
  [AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest)
  y [su guía rápida](https://docs.streamlit.io/develop/concepts/app-testing/cheat-sheet).
- Streamlit Community Cloud: [dependencias](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies),
  [despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy),
  [versión de Python](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python),
  [cuenta de GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account)
  y [administración y suspensión](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).
- [pandas: Styler.apply](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.apply.html).
- Plotly: [líneas](https://plotly.com/python/line-charts/),
  [rellenos y formas](https://plotly.com/python/shapes/),
  [anotaciones](https://plotly.com/python/text-and-annotations/) y
  [ejes con `scaleanchor`](https://plotly.com/python/axes/).
- fpdf2: [Unicode](https://py-pdf.github.io/fpdf2/Unicode.html) y
  [tablas](https://py-pdf.github.io/fpdf2/Tables.html);
  [FontTools: TTFont](https://fonttools.readthedocs.io/en/latest/ttLib/ttFont.html).
- [DejaVu Fonts 2.37](https://dejavu-fonts.github.io/Download.html): DejaVu Sans
  regular y negrita incluidas sin modificar en `assets/fonts/`. Licencia completa
  [Bitstream Vera y DejaVu](assets/fonts/LICENSE-DejaVu.txt). Archivo oficial
  `dejavu-fonts-ttf-2.37.tar.bz2`, SHA-256
  `fa9ca4d13871dd122f61258a80d01751d603b4d3ee14095d65453b4e846e17d7`.
- Oráculo de pruebas: [SciPy linprog y marginales](https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.linprog.html),
  que usa [HiGHS](https://highs.dev/).
- Herramientas de prueba: [Hypothesis](https://hypothesis.readthedocs.io/en/latest/),
  [Playwright para Python](https://playwright.dev/python/docs/intro)
  (incluido [`page.pdf`](https://playwright.dev/python/docs/api/class-page)),
  [pypdf: extracción de texto](https://pypdf.readthedocs.io/en/stable/user/extract-text.html)
  y [markdown-it-py](https://markdown-it-py.readthedocs.io/en/latest/) para el manual.
- uv: [sincronización y lockfile](https://docs.astral.sh/uv/concepts/projects/sync/),
  [grupos de dependencias](https://docs.astral.sh/uv/concepts/projects/dependencies/)
  y [acción oficial para GitHub](https://docs.astral.sh/uv/guides/integration/github/).
- [Python 3.12: Fraction](https://docs.python.org/3.12/library/fractions.html).

## Uso de herramientas de IA

El taller permite herramientas de IA como apoyo y exige que cada integrante
explique y modifique cualquier parte del código. Las sesiones de desarrollo con
asistentes de IA están registradas en `docs/desarrollo-*.md`; los métodos no
usan un solver ajeno y SciPy solo verifica en las pruebas.

**[Por completar por el equipo]:** qué herramientas usó cada integrante, para
qué tareas y cómo revisó, probó y comprendió cada cambio que presenta como propio.
