# Informe de desarrollo C, P4 y P5

Fecha: 2026-11-10, comprobada con el reloj UTC. Python 3.12.13 mediante uv.
Rama: `feat/c-p4-p5`, creada desde `feat/p1-p3` porque esa rama todavía no
estaba fusionada en `main`. Alcance terminado: C, P4 y P5, en ese orden.
P6, P7 y P8 permanecen pendientes. No se hizo merge ni push ni se crearon remotos.

## Verificación por paquete

| Criterio | C | P4 | P5 |
|---|---|---|---|
| `make lint` | Sin hallazgos | Sin hallazgos | Sin hallazgos; 45 archivos con formato correcto |
| `make test` | 251 pasan, 23 xfail | 285 pasan, 19 xfail | 311 pasan, 17 xfail; menos de 20 segundos |
| `make verify FILE=…` | 14 fixtures coinciden con SciPy | Los mismos 14 coinciden | Los mismos 14 coinciden |
| Arranque real y parada | `/_stcore/health`: `ok`; detenido | `ok`; detenido | `ok`; detenido; sin escucha residual en 8501 |
| Revisión de aplicación y cálculo manual | Ejemplo 2: traza y Z; ejemplo 5: un único estado terminal y rayo (1,0)+t·(1,1) | Ejemplos 1, 4–7: rótulos, vacío, flecha, segmento, vértices e isoutilidad | Ejemplo 2: precios y rangos exactos; redundancia y degeneración visibles |
| Guía de sustentación | Sección C escrita antes de P4 | Sección P4 escrita antes de P5 | Sección P5 con derivación completa del ejemplo 2 |

No hay fallos ni XPASS finales. Los 17 xfail son exclusivamente los 14 fixtures
del simplex revisado, sus dos propiedades generativas y la exportación PDF.
Las marcas de gráfico y sensibilidad se retiraron. La prueba AST de imports
prohibidos se conserva intacta. No se modificó ningún resultado esperado
preexistente: solo se agregó el fixture `extra_7.json`.

Los comandos se ejecutaron mediante `rtk proxy` cuando correspondía:

```bash
make lint
make test
make requirements
uv run python scripts/stress.py --seed 20261110 --count 3000
```

Para cada paquete se recorrieron los fixtures así:

```bash
for file in tests/fixtures/problems/*.json; do
    make verify FILE="$file" || exit
done
```

En cada recorrido aparecieron 14 mensajes `Gran M: coincide con SciPy` y el
aviso de simplex revisado pendiente. `make requirements` exportó sin dev;
`requirements.txt` y `uv.lock` permanecen sin cambios. No se añadieron dependencias.

Para el arranque se lanzó `make run` con `STREAMLIT_SERVER_HEADLESS=true`,
`STREAMLIT_SERVER_ADDRESS=127.0.0.1` y estadísticas desactivadas; se consultó
`http://127.0.0.1:8501/_stcore/health`. Un bloque `finally` detuvo el grupo de
procesos y esperó su salida. El log no contiene traceback; `lsof` confirmó
que no quedó escucha en 8501.

La revisión de contenido se hizo con AppTest y comparación exacta de sus datos,
sin inspección visual en navegador ni capturas. Los ejemplos 2, 5 y 6 se
resolvieron en Directo y Paso a paso, con Fracciones y Decimales. La matriz
existente también revisa los demás ejemplos. Las pruebas nuevas inspeccionan
el gráfico Plotly serializado y las tablas y advertencias de sensibilidad.
Playwright y las capturas del manual permanecen para P8.

## Estrés y regresión temporal de C1

Misma semilla `20261110`, 3000 modelos de 2–4 variables y 1–6 filas. El generador
copia o escala filas por 1, 2 y −1, invirtiendo desigualdades cuando corresponde,
y elige frecuentemente RHS cero. El oráculo ya incluía C2 en las tres corridas:

| Estado de Gran M | Verificados | Errores | Diferencias | Oráculos inconcluyentes excluidos |
|---|---:|---:|---:|---:|
| Antes de C1 | 3000 | 72 | 0 | 0 |
| Solo exclusión de artificiales de C1 | 3000 | 1 | 0 | 0 |
| C completo, incluida deduplicación de bases alternativas | 3000 | 0 | 0 | 0 |

La corrida intermedia descubrió un defecto adicional: las permutaciones de
filas de una misma base agotaban el límite de búsqueda de alternativas. Se
cuentan conjuntos de columnas básicas, manteniendo el límite de 1000 bases
realmente distintas. Una regresión con seis filas activas protege esta corrección.

`small_problems` ahora genera copias y escalados y RHS cero frecuentes.
`test_own_solver_against_scipy[solve_big_m]` usa 200 ejemplos deterministas.
Al retirar temporalmente la exclusión de artificiales, esa misma propiedad
falló con `Se alcanzó el límite de 1000 iteraciones de Gran M`; después se
restauró el archivo en `finally`. Se interrumpió la reducción automática del
contraejemplo después de detectar el fallo; el informe de pytest conservó
el fallo y el modelo generado. Con la corrección, la propiedad pasa.
Los cuatro problemas explícitos de C1 también se verifican con SciPy.

El gráfico se contrasta con Gran M en los fixtures bidimensionales y en
250 modelos aleatorios exactos, incluidos multiplicidad, redundancia y RHS cero.
La sensibilidad se comprueba por dualidad y por resolución de perturbaciones
en otros 150 modelos. Una comprobación adicional de 1000 modelos del generador
de estrés produjo 391 óptimos, 84 con filas redundantes: todos tuvieron el
mismo valor primal y dual exacto. Los precios se comparan con SciPy solo en
óptimos únicos no degenerados; un oráculo inconcluyente descarta únicamente
ese ejemplo mediante `assume`, sin ocultar errores del método propio.

## Contratos y firmas

Todos los campos nuevos tienen valores por defecto.

| Contrato | Cambio y motivo |
|---|---|
| `Solution.unbounded_origin` | Diccionario exacto del punto factible desde el que mejora Z |
| `Solution.unbounded_direction` | Dirección exacta en variables originales; sirve para verificar el gráfico y el futuro PDF |
| `GraphicalResult.status`, `objective_value` | Comparar estado y Z del método independiente con Gran M |
| `GraphicalResult.recession_directions`, `optimal_rays`, `improving_direction` | Distinguir región no acotada, rayo óptimo y mejora ilimitada |
| `GraphicalResult.drawing_bounds`, `improvement_segment`, `optimal_ray_segments` | Dar a la UI una caja y rayos ya recortados; no agrega vértices reales |
| `SensitivityReport.warnings` | Advertir redundancia y degeneración en la interfaz |
| `SensitivityReport.interpretations` | Claves `b:nombre`, `c:nombre`, `r:nombre` para evitar colisiones entre nombres |
| `sensitivity_interpretations(problem, report, mode, decimals)` | Presentar explicaciones en el mismo formato numérico de las tablas |
| `render_graph(result, problem)` | Recibe el modelo en vez de solo nombres para rotular restricciones sin analizar texto |
| `OracleInconclusiveError` | Distingue una limitación numérica del oráculo de un fallo del solver propio |

Se conservan las firmas públicas de `solve_big_m`, `graphical_method`,
`sensitivity_analysis`, `to_standard_form` y los stubs de revisado y PDF.
`format_number` ahora usa los decimales seleccionados como máximo y elimina
ceros finales, incluido −0. El tablero identifica Z en su fila de costos.

## Decisiones para la sustentación

1. Una artificial que sale nunca reentra. La limpieza de una artificial nula
   no es un pivote simplex elegido por costos; Bland no evita por sí solo ese
   ciclo. La primera iteración y la terminación explican qué columnas se consideran.
2. En no acotación se guarda un solo tablero terminal con entrante y razones.
   Se proyecta d_entrante=1, d_B=−columna sobre las variables originales.
3. El gráfico certifica con Cramer y recesión, sin Gran M ni SciPy. La caja es
   solo dibujo; una región no acotada puede tener óptimo finito. R3 del ejemplo 1
   aparece dibujada sin crear vértices.
4. Sensibilidad reconstruye B desde A y la base, sin depender del tablero.
   `row_signs` devuelve los precios al modelo original. En el ejemplo 2 los
   precios son (7/5, 0, 1/5), c1∈[3,+∞), c2∈(−∞,4/3], b1∈[2,12],
   b2∈(−∞,7] y b3∈[−6,−3].
5. Una redundante recibe precio dual cero y ningún rango propio. Las filas
   conservadas también deben respetar las igualdades omitidas: en una igualdad
   duplicada el intervalo puede reducirse al dato actual. Degeneración advierte
   que el precio puede no ser único.
6. El oráculo repite sin presolve los estados 2, 3 y 4. Cuando cambia el estado,
   exige una segunda corrida sin presolve concordante; de persistir la
   discrepancia lanza un error no concluyente. No consulta Gran M para decidir.

## Commits locales

- `ce55dbb` — `fix: confirm ambiguous SciPy statuses`.
- `579b126` — `fix: prevent artificial reentry and cycles`.
- `22495f3` — `fix: clarify tableau and number formatting`.
- `b61dbfa` — `feat: implement exact graphical method`.
- `a68e5f8` — `feat: compute exact sensitivity ranges`.
- `3192c40` — `feat: present sensitivity and warnings`.
- `3ce2f46` — `fix: clarify eligible reduced costs`.

Este informe se registra en un commit posterior de documentación. Los prompts nuevos se conservaron sin seguimiento;
no se versionaron `PROMPT-continuacion.md` ni `PROMPT-desarrollo.md`.
Se preservaron el PDF y `PROMPT-entorno.md`.

## Problemas abiertos y próxima sesión

No quedan fallos conocidos de los paquetes C, P4 o P5 en las verificaciones
realizadas. Se mantienen los límites explícitos de 1000 iteraciones y
1000 bases alternativas; modelos mayores pueden alcanzar esas protecciones.
Los rangos varían un solo dato y preservan una base, sin garantizar unicidad
ni permitir interpretar un representante dual fuera de su dominio factible.

Siguiente sesión: P6 y después P7. Antes del revisado, extraer las decisiones
puras a `simplex_rules.py` en un commit separado, sin cambiar las trazas de Gran M;
comparar la secuencia de bases en los 14 fixtures y en las regresiones de C1.
Después implementar PDF con notas y rayos. P8 queda para manual, capturas,
video, nombres del equipo y URLs reales, con aprobación antes de publicar.
