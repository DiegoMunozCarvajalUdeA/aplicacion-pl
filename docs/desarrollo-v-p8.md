# Informe de desarrollo V y P8

Fecha: 2026-11-10. Python 3.12.13 mediante uv.
Rama: `feat/v-p8`, creada desde `feat/r-p6-p7` (`8429870`) porque `main` todavía
no contenía ese commit. Alcance terminado: V (ajustes de presentación) y P8
(entregables y preparación de la sustentación), en ese orden.

No se hizo merge a `main` ni push, y no se crearon remotos. No se desplegó, no se
grabó y no se llenaron nombres. No se modificaron `PROMPT-entorno.md`,
`taller-optimi.pdf`, los resultados esperados de los 14 fixtures existentes ni
`tests/fixtures/big_m_traces.json`. Los `PROMPT-*.md` sin seguimiento siguen
fuera del control de versiones.

## Verificación final

Ejecutada sobre `01f01db`. Después solo cambió documentación: este informe y
el conteo de trazas de la Mod. 1 en `docs/ensayo-sustentacion.md`, que se
corrigió al repetir esa modificación.

| Comprobación | Resultado |
|---|---|
| `make lint` | Sin hallazgos; 61 archivos con formato correcto |
| `make test` | 556 pasan; 0 fallos, 0 xfail, 0 XPASS (72,6 s) |
| `uv run python scripts/stress.py --method both --seed 20261110 --count 3000` | Gran M: 3000 revisados, 0 errores, 0 diferencias, 0 inconcluyentes. Simplex revisado: 3000 revisados, 0 errores, 0 diferencias, 0 inconcluyentes |
| `make verify FILE=…` en los 19 fixtures | 19 de 19; 38 líneas «coincide con SciPy» (dos métodos por fixture) |
| `tests/test_simplex_traces.py` | 21 trazas pasan; `big_m_traces.json` y la prueba no cambian desde `8429870` |
| Resultados esperados de `ejemplo_*` y `extra_*` | Sin cambios desde `8429870` |
| `make ui-check` | Código de salida 0: 9 gráficos, ejemplos 2, 5 y 6 en ambos modos y formatos, 36 PDF descargados, sin avisos de error de la app |
| `make manual-captures` | 10 capturas. Nueve quedan idénticas byte a byte. `ejemplo_6_resultado.png` difiere en 57 de 5,4 millones de bytes de imagen, sin cambio visible, y se restauró la versionada |
| `make manual` | 5 páginas según pypdf. Mismo texto que el PDF versionado; solo cambian metadatos, así que se restauró el versionado. Se revisaron las 5 páginas renderizadas |
| PDF del paso a paso del ejemplo 2 | Fracciones y decimales, 7 páginas cada uno. Contienen `MIN Z = 4·x1 + x2` y `R3: -x1 - 2·x2 ≥ -4`. `Z = 17/5` aparece en fracciones y `Z = 3.4` en decimales. «Notas del documento» con la fuente es la última sección, después de «Resultado final» |
| Ensayo de despliegue desde un clon limpio | Ver «Ensayo de despliegue» |
| `git status` | Limpio salvo los cuatro `PROMPT-*.md` sin seguimiento |
| `git grep -n` de rutas personales de macOS (prefijo de usuario) | `docs/desarrollo-r-p6-p7.md:164` (informe histórico) y `PROMPT-entorno.md:7`. Este último es anterior a la sesión y no se puede modificar |

Se abrieron y revisaron todas las imágenes:

- Los 9 gráficos de `make ui-check` y su tabla de comparación.
- Las 10 capturas del manual.
- Las 5 páginas del manual.
- Las 14 páginas de los dos PDF del ejemplo 2.

## Verificación por paquete

Se aplicaron los seis criterios de la sección 8 de `PROMPT-desarrollo.md`.

| Criterio | V | P8 |
|---|---|---|
| `make lint` | Sin hallazgos | Sin hallazgos |
| `make test` | Pruebas nuevas de formato, caja, aviso, costos reducidos, nota del PDF y servidor; sin xfail | 556 pasan al final, incluidas las 10 de AppTest de ensayo y las 10 de referencias |
| `make verify` | 14 fixtures con ambos métodos; ningún cálculo cambió | 19 fixtures con ambos métodos, incluidos los cinco de ensayo |
| Servidor real | `make ui-check` inicia y detiene su propio servidor, y no queda nada escuchando después de un fallo simulado (`test_check_ui`) | Clon limpio con salud `ok` y parada; el servidor externo del puerto 8501 no se tocó |
| Revisión contra cálculo manual | Ver la nota bajo la tabla | Cada problema de ensayo se resolvió con ambos métodos, SciPy, el gráfico y AppTest; sus respuestas están en `docs/ensayo-sustentacion.md` |
| Sustentación | Sección «V: presentación verificable» | Índice por módulo y secciones de modelo, contratos, formato y oráculo; `test_docs_refs` comprueba que cada `ruta:línea` exista |

Revisión manual de V:

- **Ejemplo 2:** el resumen muestra `MIN Z = 4·x1 + x2` y
  `R3: -x1 - 2·x2 ≥ -4`. En sensibilidad, x1 y x2 aparecen como básicas.
- **Ejemplo 5:** la caja calculada a mano es (6, 36/5). Referencia actual:
  (0,0), (1,0) y (0,2), con s = 2 y dirección (1, 1); los puntos v + 4·(1,1)
  llevan el máximo a (5, 6), que por 6/5 da (6, 36/5).

## Cambios de contrato y de comportamiento visible

Ningún cambio altera estados, vértices, óptimos, valores de sensibilidad ni
trazas. Las 21 trazas congeladas y el estrés lo confirman.

| Cambio | Antes | Ahora | Motivo |
|---|---|---|---|
| `format_expression` (`formatting.py`) | Todos los coeficientes: `4·x1 + 1·x2`, `0·x1 + 1·x2` | Omite ceros; 1 y −1 se escriben `x2` y `-x2`, decidido sobre el `Fraction` y no sobre el texto; el signo del primer término va pegado; todo cero da `0` | Legibilidad en el resumen, los rótulos del gráfico y el PDF. Las tablas siguen mostrando todos los coeficientes |
| Caja del gráfico (`graphical.py`) | Solo vértices e interceptos, por 6/5 | Si hay direcciones de recesión, se agrega v + 2s·d para cada vértice v y dirección d, con s = max(1, mayor coordenada); luego se aplica el 6/5. Las regiones acotadas no cambian | Las regiones no acotadas se veían como polígonos cerrados. Ejemplo 5: de (6/5, 12/5) a (6, 36/5) |
| Dibujo de regiones no acotadas (`render_graph`) | Borde sólido en la caja | Los lados sobre la caja van punteados en gris. Aviso «La región factible continúa sin límite en la dirección (d₁, d₂); el recuadro solo limita el dibujo», uno por dirección | El recuadro no debe parecer una restricción |
| Escala de ejes | Independiente | Igual en ambos ejes (`scaleanchor`, `scaleratio`) si la razón de la caja está entre 1/4 y 4; si no, la nota «Los ejes tienen escalas distintas: direcciones y pendientes se ven deformadas» | Las pendientes y flechas se ven reales |
| Rótulos del gráfico (`space_graph_labels`) | Podían taparse | Se desplazan en píxeles aproximados y conservan una guía gris. La isoutilidad de una región no acotada se separa del óptimo | Los rótulos no se tapan en las capturas |
| `sensitivity_interpretations` | `(problem, report, mode, decimals)`; un texto genérico para r | Nuevo parámetro posicional `solution` y tres casos: básica; no básica con r ≠ 0; no básica con r = 0 (óptimo alterno, o pivotes de paso cero sin otro punto certificado) | La base final distingue los casos sin volver a resolver |
| PDF | Nota de la fuente al inicio | Sección final «Notas del documento» | El documento empieza por el problema |
| `scripts/check_ui.py` | Solo `--url`, `--output`, `--solutions` y `--downloads` | `--serve` inicia `streamlit run` headless en un puerto libre, espera `/_stcore/health` = `ok` y lo detiene en un `finally`. `--manual` guarda las 10 capturas del manual. Se dibujan 9 gráficos, con `ensayo_1`–`3` | Verificación visual reproducible sin servidor manual |
| `Makefile` | — | `ui-check` (con `OUT ?= /tmp/plapp-ui`), `manual-captures` y `manual` | La documentación nueva solo cita objetivos de `make` |
| `tests/test_manual.py` | Exigía que quedara al menos un `[por completar]` | Permite cero marcadores | Cuando el equipo llenara sus datos, CI fallaba |
| Fixtures `ensayo_1`–`5` | — | Infactible, no acotado, óptimos múltiples, degenerado y 4×4 con un precio sombra negativo | Ensayo de la sustentación. Las pruebas de óptimos múltiples aceptan cualquier punto del segmento esperado |

## Dependencias

- `markdown-it-py>=4,<5`, en el grupo `dev`, es la única dependencia nueva.
  `scripts/build_manual.py` convierte `docs/manual/README.md` en HTML para que
  Chromium lo imprima en A4. Así el Markdown es la única fuente del manual.
  Playwright y pypdf ya eran dependencias dev desde R–P7.
- `uv.lock` se actualizó. `requirements.txt` no cambia, porque no hay
  dependencias de ejecución nuevas.

## Archivos binarios versionados

| Archivo | Bytes |
|---|---:|
| `docs/capturas/v/ejemplo_1.png` | 41 017 |
| `docs/capturas/v/ejemplo_5.png` | 35 813 |
| `docs/capturas/v/ejemplo_6.png` | 40 011 |
| `docs/capturas/v/ejemplo_7.png` | 36 740 |
| `docs/capturas/v/extra_1.png` | 48 355 |
| `docs/capturas/v/extra_3.png` | 19 411 |
| `docs/manual/capturas/entrada.png` | 202 818 |
| `docs/manual/capturas/validacion.png` | 64 565 |
| `docs/manual/capturas/ejemplo_2_estandar.png` | 126 940 |
| `docs/manual/capturas/ejemplo_2_pivote.png` | 121 725 |
| `docs/manual/capturas/ejemplo_2_resultado.png` | 43 521 |
| `docs/manual/capturas/ejemplo_2_sensibilidad.png` | 15 155 |
| `docs/manual/capturas/ejemplo_2_rangos.png` | 95 431 |
| `docs/manual/capturas/ejemplo_6_resultado.png` | 73 651 |
| `docs/manual/capturas/ejemplo_6_grafico.png` | 94 104 |
| `docs/manual/capturas/comparacion.png` | 58 895 |
| `docs/manual/manual.pdf` | 813 714 |

`docs/capturas/r/` se conserva sin cambios.

## Ensayo de despliegue

Cada ensayo usó `git clone` de `01f01db` en un directorio temporal, que se
borró al terminar. Los pasos y su lectura para el equipo están en
`docs/entrega.md`.

1. **Solo `requirements.txt`.** Comandos: `uv venv --python 3.12` y
   `uv pip install -r requirements.txt`.
   - Se instalan 37 paquetes con Python 3.12.13.
   - SciPy, pytest, Playwright, pypdf, Hypothesis, Ruff y markdown-it-py no se
     pueden importar.
   - `plapp` queda en `site-packages` con `assets/fonts` (las dos DejaVu y la
     licencia).
   - Salud `ok`. `scripts/check_ui.py --url … --solutions --downloads`, desde
     el entorno dev: 9 gráficos, 12 recorridos, 36 PDF y código de salida 0.
   - El registro del servidor no tiene errores.
2. **Ruta de `uv.lock`, como simulación de Community Cloud.**
   `uv sync --locked` instala 52 paquetes (640 MB), con SciPy y Playwright.
   `uv sync --locked --no-dev` instala 37 (375 MB); la app responde `ok` y
   `check_ui.py` dibuja 9 gráficos con código de salida 0.
3. **Plan B sin red.** Con `uv sync --locked` ya hecho, la red externa se
   bloqueó con `sandbox-exec` de macOS y sin variables de proxy. Funcionaron sin
   red: `make lint`, `uv run streamlit run …` y
   `check_ui.py --solutions` con Chromium (9 gráficos, 12 recorridos, código de
   salida 0).

Documentación oficial consultada:

- La página de dependencias de Streamlit Community Cloud:
  - busca en la carpeta del archivo de entrada y luego en la raíz;
  - usa el primero de `uv.lock`, `Pipfile`, `environment.yml`,
    `requirements.txt` y `pyproject.toml`;
  - advierte usar un solo archivo.
- Python se elige en «Advanced settings» y solo se cambia borrando y volviendo
  a desplegar.
- Streamlit no dice qué comando de uv ejecuta. uv incluye el grupo `dev` por
  defecto en `uv sync`.

Conclusión: Cloud usará `uv.lock` y probablemente instalará también el grupo dev.
La app funciona en ambos casos.

## Banco de modificaciones en vivo

Las siete modificaciones de `docs/ensayo-sustentacion.md` se probaron en
worktrees temporales con su propio `uv sync`; los worktrees se borraron.

| Modificación | Resultado de la suite |
|---|---|
| Mod. 1: usar siempre Bland | Fallan 30: 19 de las 21 trazas, 3 de `test_big_m` y 8 de AppTest (repetida al cerrar) |
| Mod. 2: desempatar la razón por el mayor índice | Fallan 18 |
| Mod. 3: dos decimales por defecto | Fallan 2 |
| Mod. 4: margen de la caja del gráfico | Fallan 2; la caja del ejemplo 5 pasa a (15/2, 9) |
| Mod. 5: mensaje con el número de pivotes | No falla ninguna; 547 pasan |
| Mod. 6: columna «Valor actual» en sensibilidad | No falla ninguna. No tiene cobertura; la guía sugiere una prueba |
| Mod. 7: resaltar el pivote en verde | Fallan 20 |

## Decisiones que el equipo debe conocer

- **Caja grande en regiones no acotadas.** La regla de V2 la exige. En
  `ensayo_3` la caja es (108/5, 108/5) y los vértices quedan en una esquina.
  Para explicarlo, usar el zoom de Plotly o el aviso de recesión.
- **Precios sombra en problemas degenerados.** Pueden no ser únicos. En
  `ensayo_4` la app advierte: «Degeneración: los precios sombra pueden no ser
  únicos y un extremo del rango puede coincidir con el valor actual».
- **Costo reducido cero en una no básica.** Solo se afirma un óptimo alterno si
  el solver lo certificó. Si no, el texto habla de pivotes de paso cero.
- **Archivo de dependencias en Cloud.** El repositorio conserva `uv.lock` y
  `requirements.txt`, aunque Cloud recomienda uno solo; `requirements.txt` se
  exige en el proyecto y sirve para instalar sin dev. Si la instalación en Cloud
  pesa demasiado, se puede agregar `[tool.uv] default-groups = []`, con el costo
  descrito en `docs/entrega.md`.
- **Fusión.** `main` es ancestro de `feat/v-p8`, así que
  `git merge --ff-only feat/v-p8` no crea commits nuevos. Decidirlo es tarea del
  equipo.
- **Autoría.** Todos los commits tienen el mismo autor. El taller 6a exige
  commits de cada integrante, sin reescribir el historial.
- **Pie del manual.** «Página n de 5» aparece en una fuente serif, porque la
  plantilla de pie de Chromium no usa la fuente de la página. Es solo estético.
- **Rótulos.** En `ensayo_2` la flecha de mejora cruza el rótulo de R2, que
  sigue legible. En `ejemplo_6` el segmento verde pasa bajo el rótulo de R1.

## Lo que no se pudo verificar

- El despliegue real en Streamlit Community Cloud, qué comando de uv ejecuta y
  si instala el grupo dev. Las instrucciones prohíben desplegar y la
  documentación oficial no lo dice. Hay que revisar el registro en «Manage
  app».
- CI en un remoto: no hay remoto. Localmente se ejecutaron los mismos pasos
  (`uv sync --locked`, Ruff, pytest).
- `check_ui.py` contra la URL de Cloud: no existe todavía.
- La instalación en Windows y en el portátil de la sustentación.
- El video, su duración y los nombres, que son tarea del equipo.
- El plan B sin red se probó en macOS con `sandbox-exec`, no con la red
  realmente desconectada.

## Tareas pendientes del equipo

En orden:

1. Completar nombres, identificadores, áreas y cuentas: `README.md`,
   `docs/propuesta.md`, `docs/manual/README.md`, la columna Responsable de
   `docs/plan.md` y «Quién habla» de `docs/video.md` (`docs/entrega.md`,
   sección 1).
2. Decidir la fusión a `main`, crear el remoto en GitHub, subir y confirmar CI
   en verde (`docs/entrega.md`, sección 2).
3. Hacer commits propios de cada integrante, sin reescribir el historial
   (`docs/entrega.md`, sección 3).
4. Desplegar en Community Cloud con `app/streamlit_app.py` y Python 3.12;
   revisar el registro de dependencias y verificar la URL en una ventana
   privada con los ejemplos 2 y 6 (`docs/entrega.md`, sección 4).
5. Grabar y publicar el video de 5:00 o menos (`docs/video.md`).
6. Registrar las URL de repositorio, app y video en `README.md` y
   `docs/manual/README.md`; regenerar con `make manual` y revisar las páginas
   (`docs/entrega.md`, secciones 1 y 4).
7. Completar «Uso de herramientas de IA» (`README.md`).
8. Ensayar 15 minutos por integrante, con al menos una modificación en vivo
   (`docs/ensayo-sustentacion.md`, `docs/sustentacion.md`).
9. Instalar y probar el plan B en el portátil de la sustentación días antes
   (`docs/entrega.md`, sección 6).
10. Recorrer la lista de comprobación final (`docs/entrega.md`, sección 8).

## Commits locales

V:

- `b90ed9a` — `fix: simplify linear expression labels`.
- `1e77291` — `fix: show unbounded graph regions`.
- `cd2e757` — `fix: explain basic reduced costs`.
- `fc611fb` — `fix: move font note to PDF end`.
- `669ad8f` — `feat: start server from UI check`.
- `3517e11` — `fix: separate unbounded isoutility label`.

P8:

- `1b3c770` — `docs: add user manual`.
- `a4d4941` — `docs: add video script`.
- `7984681` — `test: add rehearsal problems`.
- `1c98235` — `docs: add rehearsal guide`.
- `a132753` — `docs: index sustentacion by module`.
- `64a2df7` — `test: drop stale PDF report count`.
- `525619a` — `docs: finalize readme and plan`.
- `9cea42a` — `test: allow filled manual placeholders`.
- `01f01db` — `docs: add delivery guide`.
- `4f071db` — `docs: correct Mod. 1 trace count`.
- Este informe — `docs: record V P8 verification`.

## Revisión posterior (2026-11-10)

Una revisión independiente del gráfico encontró cuatro detalles de presentación,
corregidos sin cambiar cálculos (vértices, óptimos y certificados siguen iguales):

1. Los lados del polígono sobre los ejes x1 = 0 o x2 = 0 se dibujaban grises y
   punteados como borde del recorte, aunque son fronteras reales (x ≥ 0). Ahora
   solo los lados sobre x = ancho o y = alto de la caja son punteados.
2. La ampliación v + 2s·d hacía demasiado grande la caja cuando la región sigue
   los ejes (extra 1: 18 × 78/5). Ahora se usa v + s·d: el ejemplo 5 queda en
   (18/5, 24/5) y el extra 1 en (12, 48/5).
3. En el ensayo 3, el rótulo de la isoutilidad no encontraba hueco y quedaba
   tapado por el del vértice (0, 6). `space_graph_labels` ahora prueba subidas de
   20 en 20 px hasta el borde; su docstring y la guía explican la heurística.
4. Los ternarios encadenados del rótulo de las rectas pasaron a `if`/`elif`, y
   se agregó una coma faltante en las referencias del README.

Se regeneraron `docs/capturas/v/ejemplo_5.png` y `extra_1.png`; las otras cuatro
capturas son idénticas píxel a píxel. El manual no cambia porque usa el
ejemplo 6, que es acotado.
