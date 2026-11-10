# Informe de desarrollo R, P6 y P7

Fecha: 2026-11-10, comprobada con reloj UTC. Python 3.12.13 mediante uv.
Rama: `feat/r-p6-p7`, creada desde `main` en `6a4f379`.
Alcance terminado: R, P6 y P7, en ese orden. P8 queda para la siguiente sesión.
Se leyeron el enunciado completo, los prompts y los módulos y pruebas antes de
editar. Se preservaron los tres prompts sin seguimiento, `PROMPT-entorno.md`,
el PDF y los resultados esperados de los 14 fixtures.

## Verificación por paquete

Se aplicaron los seis criterios de la sección 8 de `PROMPT-desarrollo.md`.
Los comandos habituales se ejecutaron mediante `rtk` o `rtk proxy`; los
servidores y procesos largos se ejecutaron directamente con uv.

| Criterio | R | P6 | P7 |
|---|---|---|---|
| `make lint` | Sin hallazgos | Sin hallazgos, también antes del commit de refactor | Sin hallazgos; 52 archivos con formato correcto |
| `make test` | 332 pasan, 17 xfail | Refactor: 332 pasan, 17 xfail; implementación: 385 pasan, 1 xfail | 449 pasan; 0 xfail, 0 XPASS, 0 fallos |
| `make verify FILE=…` en cada fixture | 14 coincidencias de Gran M | 14 coincidencias de cada método; también se verificó Gran M antes de implementar el revisado | 14 coincidencias de cada método |
| Servidor real | Salud `ok`, capturas y parada | Salud `ok`, 12 recorridos de comparación y parada | Salud `ok`, 36 descargas y parada; sin escucha residual en 8501 |
| Revisión contra cálculo manual | Rótulos y certificados gráficos de ejemplos 1, 5–7 y extras 1 y 3 | Ejemplo 2: cuatro bases, Z = 9M, 4+2M, 18/5 y 17/5; ejemplo 6: bases y Z idénticos en la comparación | Ejemplo 2 en PDF: pivote 5/3, x=(2/5,9/5), Z=17/5; decimales 0.4, 1.8 y 3.4 |
| Sustentación | Sección R, tres preguntas y ejercicio | Reglas, E, revisado y comparación; preguntas y ejercicios | Exportación, fuentes y tablas; cinco preguntas y ejercicio |

El conteo de R ya incluye las 21 pruebas de trazas guardadas como preparación
del refactor. Los xfail se retiraron al implementar revisado y PDF; no quedan
algoritmos pendientes en la suite. La última ejecución completa duró 59.60 s,
con el navegador y las comprobaciones de PDF ejecutándose simultáneamente.
No se modificó `tests/test_forbidden_imports.py`.

Comandos de calidad, repetidos al cerrar cada paquete:

```bash
rtk proxy make lint
rtk proxy make test
rtk proxy sh -c 'for file in tests/fixtures/problems/*.json; do make verify FILE="$file" || exit; done'
rtk proxy make requirements
rtk proxy uv sync --locked
```

`make requirements` excluye Playwright, pypdf, SciPy y las demás herramientas
dev. FontTools ya era dependencia transitiva de fpdf2; ahora figura también
como dependencia directa y así lo refleja el comentario de `requirements.txt`.
El lockfile se sincroniza sin cambios pendientes.

## R: sensibilidad y capturas

Se eliminó la interpretación duplicada de cada RHS bajo precios sombra.
Ahora aparece una vez, debajo de su tabla de rangos. Todas las restricciones
originales tienen fila; una redundante muestra «No disponible (fila redundante)»
en ambos extremos. AppTest comprueba el conteo de interpretaciones y las
igualdades duplicadas, en ambos formatos.

Se revisaron estas seis capturas reales de Chromium, guardadas en el repositorio:

- `docs/capturas/r/ejemplo_1.png`.
- `docs/capturas/r/ejemplo_5.png`.
- `docs/capturas/r/ejemplo_6.png`.
- `docs/capturas/r/ejemplo_7.png`.
- `docs/capturas/r/extra_1.png`.
- `docs/capturas/r/extra_3.png`.

La primera inspección mostró rótulos sobre el óptimo y coordenadas cortadas
junto al eje vertical. Se ubicaron los rótulos en tramos alejados de vértices
y etiquetas anteriores, con anclas hacia dentro cerca de los bordes. Se hizo
explícito el contraste del texto, se colocó la leyenda debajo y se reforzó la
flecha de mejora del ejemplo 5, terminándola dentro del recorte. Se revisaron
las seis capturas finales: coordenadas, escalas, rectas, segmento, vacío y flecha
legibles. No cambió la geometría, la caja ni los certificados exactos.

Playwright se agregó exclusivamente a dev para esta verificación solicitada.
Las capturas del manual y la revisión visual general de P8 siguen pendientes.

## P6: preservación de trazas y revisado

Antes de extraer reglas se guardó `tests/fixtures/big_m_traces.json`, con 21
casos: 14 fixtures, cinco regresiones C1, retiro artificial con pivote negativo
y Beale. `tests/test_simplex_traces.py` compara todos los campos preexistentes
de cada iteración: tablero, base, costos, entrante, saliente, pivote, Z, razones,
justificaciones y notas. También compara estado, mensaje y notas finales.
Las 21 trazas quedaron idénticas después del refactor; no se regeneraron.
El refactor tiene un commit propio, anterior a la implementación del revisado.

`simplex_rules.py` concentra candidatas sin artificiales, Bland, entrante,
razón mínima, saliente, infactibilidad, retiro de artificiales, terminación,
direcciones, búsqueda de alternativas y armado final de `Solution`.
Las funciones reciben los datos que necesitan, independientemente de cómo
se calcularon. Gran M conserva el tablero y delega las decisiones.

El revisado calcula x_B=B⁻¹b, y=c_B B⁻¹ con MValue, r=c−yA y d=B⁻¹a_j.
Mantiene la inversa y aplica la matriz elemental E mediante operaciones de
filas O(m²). Solo reconstruye B⁻¹A completo para retiro y posproceso; cada
iteración deja `tableau=None`. Las pruebas:

- Invierten B con Gauss-Jordan en cada estado de los 21 casos y comprueban
  B⁻¹, x_B, y, d y el pivote con igualdad exacta.
- Construyen E explícita y comparan E·B⁻¹, también con pivote negativo.
- Comparan todas las decisiones y las secuencias completas de bases con Gran M.
- Exigen el mismo resultado, notas, certificados y sensibilidad en los óptimos.
- Comprueban que B⁻¹A no se construye en los pivotes normales del revisado.
- Comprueban el límite de iteraciones y el rechazo de un pivote cero.

No hubo diferencias de secuencia que explicar: coinciden también en Beale,
incluido el cambio a Bland después de repetir una base. La comparación de la
UI muestra una fila por estado y conserva estados ausentes como discrepancias;
una prueba introduce deliberadamente una secuencia desigual y exige «No».

Estrés reproducible:

```bash
uv run python scripts/stress.py --method both --seed 20261110 --count 3000
```

| Método | Generados | Verificados con SciPy | Errores | Diferencias | Oráculos inconcluyentes excluidos |
|---|---:|---:|---:|---:|---:|
| `big_m` | 3000 | 3000 | 0 | 0 | 0 |
| `revised` | 3000 | 3000 | 0 | 0 | 0 |

El script acepta también `--method big_m` y `--method revised`; el valor por
defecto es `both`. Cada corrida usa la misma semilla para ambos métodos y
cuenta por separado errores propios, diferencias y oráculos no concluyentes.
Solo estos últimos se excluyen; en esta ejecución no hubo ninguno.

## P7: PDF y recorrido real

`tests/test_export_pdf.py` aprobó 62 pruebas: 56 documentos de los 14 fixtures
con ambos métodos y formatos; cuatro combinaciones del problema ancho de ocho
variables y seis restricciones; y dos pruebas de certificados, formato,
redundancia, glifos e entradas inválidas. Pypdf abre cada documento y exige
contenido real. La prueba ancha inspecciona las coordenadas de las celdas en
el PDF serializado y comprueba que permanezcan dentro de la página.

El PDF incluye modelo original, transformaciones, forma estándar, todos los
estados con tablero o B⁻¹/x_B/y, costos, razón mínima y exclusiones, decisiones,
pivote resaltado, justificaciones y notas. El resultado incluye holguras o
excesos, solución alterna, segmento o rayo óptimo, o dirección no acotada.
La sensibilidad incluye advertencias, precios, costos, rangos e interpretaciones
y recibe la misma solución ya calculada. El exportador no llama a solvers.

Las páginas A4 horizontales dividen tablas de más de ocho columnas de datos
en bloques que repiten la primera columna. Los encabezados se repiten al
cambiar de página y las celdas ajustan el texto sin cortarlo. Se incluyen
DejaVu Sans 2.37 regular y negrita, sin modificar, junto con la licencia.
Se comprobó el SHA-256 oficial del archivo de distribución y los glifos de
todos los símbolos utilizados. Para caracteres del usuario fuera de la fuente
se escribe explícitamente `[U+XXXX]`. No hizo falta sustituir los símbolos
matemáticos por ASCII.

Pypdf se agregó solo a dev para verificar estructura y texto con un lector
independiente. FontTools se declara directamente porque el exportador comprueba
cada carácter antes de escribirlo; ya estaba instalado por fpdf2. El wheel
incluye las fuentes y la licencia. Se verificó además la exportación desde su
contenido extraído, fuera de `src/`:

```bash
rtk proxy uv build --wheel --out-dir /tmp/plapp-build
```

AppTest verifica botones con URL y habilitados, ausencia de generación sin
solución y contención de fallos del exportador. Las descargas reales se
comprobaron con el siguiente comando; el ayudante inicia y detiene el servidor:

```bash
uv run python /Users/diegocarvajal/.codex/skills/webapp-testing/scripts/with_server.py \
  --server 'uv run streamlit run app/streamlit_app.py --server.headless true --server.address 127.0.0.1 --browser.gatherUsageStats false' \
  --port 8501 -- uv run python scripts/check_ui.py --downloads --output /tmp/plapp-p7-final
```

Resultado: seis gráficos capturados, 12 recorridos de los ejemplos 2, 5 y 6
en «Comparar ambos», en ambos modos y formatos, y 36 PDF descargados. Son dos
PDF en Comparar métodos y otro en Paso a paso por combinación. Los bytes se
validan y se leen con pypdf; el ejemplo 2 comprueba además el formato numérico.
El script espera el final de cada rerun antes de usar las URL de descarga.
Todos los recorridos terminaron sin excepciones ni avisos de error de la app.
La salud respondió `ok`; el servidor quedó detenido y `lsof` no encontró
escucha residual en 8501.

Se abrieron mediante renderización completa con Poppler dos PDF descargados:
ejemplo 2 de Gran M en fracciones y ejemplo 2 revisado en decimales. Se
inspeccionaron páginas con iteraciones, pivote, resultado y sensibilidad:
tablas, glifos, números y justificaciones legibles, sin celdas cortadas.
Ambos documentos finales tienen siete páginas. Este límite no corresponde
al manual de P8, que sí deberá tener cinco páginas o menos. Los PDF y sus
renderizaciones de prueba permanecen en `/tmp/`; el repositorio conserva el
script reproducible y las seis capturas exigidas en R.

## Contratos y firmas

| Contrato | Cambio | Motivo |
|---|---|---|
| `Iteration.basic_values` | `tuple[Fraction, ...] = ()` | Guardar x_B del revisado sin exigir un tablero |
| `Iteration.multipliers` | `tuple[MValue, ...] = ()` | Guardar y=c_B B⁻¹ con la penalización simbólica |
| `solve_revised(problem)` | Firma conservada; implementación propia | Compartir reglas y resultado con Gran M, manteniendo B⁻¹ |
| `export_steps_pdf` | `(problem, solution, mode="fraction", decimals=4) -> bytes` | Incluir modelo original y formato elegido; entregar bytes a Streamlit |
| `run_stress` | `method="big_m"` opcional; CLI `big_m|revised|both` | Repetir los mismos casos y contar resultados por método |

Los nuevos campos de `Iteration` tienen valores por defecto y Gran M mantiene
su contrato anterior. Las firmas de los algoritmos existentes, la sensibilidad
y el gráfico se conservan. La interfaz revisada muestra y en filas normalizadas;
la sensibilidad continúa devolviendo precios respecto al problema original.

## Rama y commits locales

- `9d7473a` — `fix: clarify sensitivity and graph labels`.
- `4d5f576` — `refactor: share simplex rules and postprocess`.
- `16d6b1e` — `feat: solve and compare with revised simplex`.
- `c3acfce` — `feat: export exact solution steps to PDF`.

Este informe se guarda en un commit posterior de documentación. No se hizo
merge a `main`, no se crearon remotos y no se hizo push.

## Decisiones para el equipo y próxima sesión

1. Ambos métodos comparten decisiones y certificados. No asignar un número a M
   ni permitir que una artificial retirada vuelva a entrar.
2. E normaliza la columna d; el revisado aplica E·B⁻¹ mediante filas y las
   pruebas invierten B independientemente para verificarlo.
3. Una artificial básica nula sin pivote de retiro identifica redundancia:
   conserva B cuadrada; sensibilidad informa y=0 como representante, sin rango
   para esa fila. La UI y el PDF conservan su fila visible.
4. Los dos contadores de comparación distinguen estados registrados de pivotes.
   El costo m×(n+m+1) del tablero es una referencia para filas ≤; los excesos y
   artificiales pueden aumentar su ancho.
5. Fracciones y MValue siguen exactos; formato decimal, gráfico y PDF solo
   cambian la presentación. Exportar no vuelve a resolver.
6. Se conservan los límites de 1000 estados y 1000 bases alternativas. Los
   rangos de sensibilidad varían un único dato y preservan la base actual.

No quedan fallos conocidos de R, P6 o P7 en las verificaciones solicitadas.
Se pudieron tomar las capturas y abrir los PDF; no hay comprobaciones de esos
paquetes aplazadas por falta de herramientas. No se ejecutó despliegue ni CI
remota porque no se publicó el repositorio.

Siguiente sesión recomendada: **P8**. Faltan manual de máximo cinco páginas con
sus capturas y PDF, guion de hasta cinco minutos, cinco problemas nuevos de
ensayo verificados y sus fixtures, revisión global de referencias y cierre de
README y plan. Nombres del equipo, remoto, despliegue y video siguen a cargo
del equipo. No se adelantaron esos entregables en esta sesión.
