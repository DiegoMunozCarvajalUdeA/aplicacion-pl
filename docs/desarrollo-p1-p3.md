# Informe de desarrollo P1–P3

Fecha: 2026-11-10, comprobada con el reloj UTC. Python 3.12.13 mediante uv.
Rama: `feat/p1-p3`, creada desde `main`. Se leyó el PDF completo antes de editar;
se conservaron el enunciado y ambos prompts. Alcance terminado: P1, P2 y P3.

## Verificación por paquete

Los seis criterios corresponden a la sección 8 de `PROMPT-desarrollo.md`.
Los comandos de calidad se ejecutaron mediante `rtk proxy`.

| Criterio | P1 | P2 | P3 |
|---|---|---|---|
| 1. `make lint` | Sin hallazgos; formato correcto | Sin hallazgos; formato correcto | Sin hallazgos; 42 archivos con formato correcto |
| 2. `make test` | 165 pasan, 36 xfail, 0 XPASS | 204 pasan, 22 xfail, 0 XPASS | 237 pasan, 22 xfail, 0 XPASS |
| 3. `make verify FILE=…` | Los 13 fixtures verificados por SciPy; los solvers aún eran stubs | Gran M coincide con SciPy en los 13 fixtures | Los 13 siguen coincidiendo con SciPy |
| 4. Arranque y parada | `/_stcore/health`: `ok`; detenido | `ok`; detenido | `ok`; detenido, sin escucha residual en 8501 |
| 5. Revisión de la app contra cálculo manual | Formas estándar de ejemplos 1 y 2 inspeccionadas con AppTest | Ejemplo 2: x = (2/5, 9/5), Z = 17/5 | Tablas de ejemplos 1, 2 y 6 contrastadas con las trazas manuales |
| 6. Sustentación | Sección P1 escrita antes de P2 | Sección P2 y traza completa del ejemplo 2 escritas antes de P3 | Sección P3, formato, visor y preguntas escritas |

Las 22 marcas xfail finales pertenecen exclusivamente a gráfico, sensibilidad,
simplex revisado y PDF. Las pruebas de MValue, forma estándar y Gran M ya no
tienen esa marca. No se debilitó la prueba AST de imports prohibidos.

La verificación de fixtures se ejecutó en cada paquete con:

```bash
rtk proxy sh -c 'for file in tests/fixtures/problems/*.json; do make verify FILE="$file" || exit; done'
```

Cada ejecución termina con código 0. A partir de P2, los 13 archivos muestran
`Gran M: coincide con SciPy`; el revisado informa que sigue pendiente.
Hypothesis también compara Gran M con SciPy en 40 problemas generados de
2–4 variables y 1–4 restricciones, con signos y sentidos variados.

El arranque real se hizo con:

```bash
STREAMLIT_SERVER_HEADLESS=true STREAMLIT_SERVER_ADDRESS=127.0.0.1 STREAMLIT_BROWSER_GATHER_USAGE_STATS=false make run
rtk proxy curl --fail --silent http://localhost:8501/_stcore/health
```

En P2 y P3, un proceso de control con Python/uv inició `make run`, consultó el
mismo endpoint, inspeccionó los datos de AppTest y detuvo el grupo de procesos
en un bloque `finally`. El log no contiene traceback; `lsof` confirmó que no
quedó escucha en el puerto. La revisión de contenido fue mediante AppTest y
cálculo exacto manual; no se hizo inspección visual en navegador ni capturas.
Playwright no está instalado en el proyecto; las capturas del manual quedan
para P8.

## Evidencia de cálculo y presentación

- Ejemplo 1: dos pivotes (x2 entra/s2 sale, x1 entra/s1 sale), con Z = 0,
  2400 y 3380. La segunda razón mínima excluye un coeficiente negativo.
- Ejemplo 2: bases (a1, a2, s3), (x1, a2, s3), (x1, x2, s3) y
  (x1, x2, e2); Z = 9M, 4 + 2M, 18/5 y 17/5.
- Ejemplos 4 y 5: mensajes de infactibilidad y no acotación, respectivamente.
  Otro caso prueba infactibilidad antes de una posible mejora real no acotada.
- Ejemplo 6: Z = 10 en el segmento entre (0, 5/2) y (3, 1); el punto alterno
  se obtiene por pivote, sin consultar los resultados esperados del fixture.
- Ejemplo 7: Z = 18, con x1 básica en cero; no se confunde un pivote
  degenerado con una segunda solución.
- Beale: 14 estados; repite la base tras seis pivotes, activa Bland y termina
  con x = (1, 0, 1, 0), Z = 1.
- También se prueban igualdades dependientes, retiro de artificial nula con
  pivote negativo, rayos óptimos y alternativas que requieren pasos degenerados.
- Para todos los óptimos de los fixtures se verifica exactamente B·B⁻¹ = I,
  B⁻¹b igual al lado derecho final y B⁻¹A igual al tablero final.
- Las 42 pruebas de interfaz incluyen los ejemplos 1–7 en ambos modos y
  formatos, los encabezados y filas básicas, Z, la coordenada y color del
  pivote, tipos originales de holgura/exceso, alternativas, degeneración,
  persistencia exacta al cambiar formato y errores sin traceback.

## Contratos y decisiones para sustentar

| Contrato | Cambio | Motivo |
|---|---|---|
| `StandardForm.row_signs` | `tuple[int, ...] = ()` | Signo aplicado a cada fila original; necesario para sensibilidad |
| `Iteration.objective_value` | `Fraction \| MValue \| None = None` | Mostrar Z del estado anterior al pivote |
| `Iteration.notes` | `tuple[str, ...] = ()` | Canonización, Bland y retiro de artificiales |
| `Solution.notes` | `tuple[str, ...] = ()` | Redundancia y nombres de básicas nulas |
| `Solution.alternative_rays` | `tuple[dict[str, Fraction], ...] = ()` | Conservar direcciones exactas y formatear rayos en la UI |
| `MValue` | Operaciones y comparaciones también con int/Fraction; operaciones reflejadas y negación | Sumas exactas, comparación con cero y hash compatible con escalares |
| `render_solution` | Recibe también `problem` | Rotular holgura/exceso según la restricción original |

Los campos nuevos tienen valores por defecto. Las firmas públicas de
`solve_big_m(problem)` y `to_standard_form(problem)` se conservan.

El solver mantiene el sentido original de Z y canoniza r = c − c_B·tablero
con M simbólica; nunca elige un valor grande numérico. Se guarda cada estado
antes de su pivote y un último estado sin entrante que explica la terminación.
Los costos reducidos de las básicas siempre son cero. La inversa final se calcula desde
las columnas básicas de la forma estándar, usando Gauss-Jordan.

Si una artificial básica nula no puede salir, su fila transformada es
redundante. Se conserva la artificial nula como testigo para mantener B
cuadrada en el sistema original y poder comprobar su inversa. P5 deberá tratar
esa redundancia antes de interpretar un precio sombra. Esta decisión y sus
notas son visibles en la prueba de igualdades dependientes.

La búsqueda de multiplicidad recorre bases de paso cero y exige otro punto
original o una dirección no nula. Un segmento certificado no pretende enumerar
toda una cara óptima de dimensión mayor que uno. Hay límites explícitos de
1000 estados del solver y 1000 bases al buscar alternativas; alcanzarlos
informa que el cálculo no concluyó, sin inventar un estado de optimalidad.

Pandas ya forma parte de Streamlit; no se agregaron dependencias. Se consultó
documentación oficial vigente de Streamlit y pandas, enlazada en README y en
la guía. No se usaron APIs nuevas de Plotly ni fpdf2 en estos paquetes.
`make requirements` reexportó las dependencias sin dev; `uv.lock` y
`requirements.txt` quedaron idénticos a `main`.

## Commits locales de implementación

1. `41f6014` — `feat: implement exact standard form core`.
2. `b9db467` — `feat: solve linear programs with symbolic big M`.
3. `57b72cd` — `feat: present big M steps and special cases`.

Este informe se guarda en un commit posterior de documentación. No se hizo
merge, no se crearon remotos y no se hizo push. `PROMPT-desarrollo.md` ya era
un archivo sin seguimiento al comenzar y se conserva en ese estado.

## Pendientes y siguiente paquete

P4 (gráfico) es el siguiente recomendado por su peso en la rúbrica y porque
puede implementarse de forma independiente. Continúan pendientes P5
(sensibilidad), P6 (revisado), P7 (PDF) y los entregables completos de P8.
Sus stubs se conservaron; la UI mantiene los avisos y el PDF deshabilitado.

No se cambiaron valores `esperado`, fixtures, la prueba de imports, el PDF ni
`PROMPT-entorno.md`. El avance de semana 3 queda cubierto: los ejemplos 1 y 3
se resuelven en ambos modos. La guía de sustentación de los paquetes terminados
está en `docs/sustentacion.md`.
