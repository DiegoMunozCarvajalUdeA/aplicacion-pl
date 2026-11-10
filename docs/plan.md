# Plan de implementación y verificación: estado final

Estado al 2026-11-10, rama `feat/v-p8`. Todos los paquetes de desarrollo están
implementados y verificados. La suite tiene 555 pruebas aprobadas, sin xfail,
XPASS ni fallos. Lo que falta depende del equipo: nombres, remoto, despliegue,
video y ensayo (sección «Pendiente del equipo»).

Los comandos, conteos intermedios y decisiones de cada sesión están en los
informes históricos, que no se reescriben:

- `docs/desarrollo-p1-p3.md`: P1, P2 y P3.
- `docs/desarrollo-c-p4-p5.md`: C, P4 y P5.
- `docs/desarrollo-r-p6-p7.md`: R, P6 y P7.
- `docs/desarrollo-v-p8.md`: V y P8.

## Paquetes

| Paquete | Alcance | Evidencia | Informe |
|---|---|---|---|
| P1: núcleo exacto | `MValue` (a + b·M), álgebra lineal con `Fraction`, forma estándar, modelo, validación y JSON | `test_mvalue`, `test_contracts`, `test_linalg`, `test_standard_form`, `test_model`, `test_io_json`; arranque real con `/_stcore/health` = `ok` | `desarrollo-p1-p3.md` |
| P2: Gran M | Base inicial, costos reducidos, razones, Bland, casos especiales, óptimos alternos | `test_big_m` (traza manual del ejemplo 1, certificados del tablero, Beale con Bland, redundancia); `test_simplex_traces` fija 21 trazas | `desarrollo-p1-p3.md` |
| P3: paso a paso | Tablero, pivote resaltado, razones y justificación de cada decisión en la interfaz | `test_app::test_solved_examples_in_both_modes_and_formats` en ambos modos y formatos | `desarrollo-p1-p3.md` |
| C: correcciones | Estados ambiguos de SciPy, reingreso de artificiales y ciclos, formato del tablero; fixture `extra_7` | `test_verifier`, `test_big_m::test_redundant_zero_rows_never_reenter_artificials`; 3000 problemas generados sin diferencias | `desarrollo-c-p4-p5.md` |
| P4: método gráfico | Vértices por Cramer, recesión, recorte, segmento y rayo óptimos, isoutilidad; sin llamar al simplex | `test_graphical` (incluye la propiedad `test_graphical_against_big_m`), `test_app::test_graph_presentation` | `desarrollo-c-p4-p5.md` |
| P5: sensibilidad | Precios sombra, costos reducidos y rangos derivados de A y la base final, con signos originales | `test_sensitivity` (derivación del ejemplo 2, perturbaciones resueltas con SciPy, certificado dual de cada fixture óptimo) | `desarrollo-c-p4-p5.md` |
| R: revisión menor | Interpretaciones únicas, filas redundantes visibles, capturas de gráficos | `test_app::test_sensitivity_redundant_warning_and_unavailable_range`; capturas en `docs/capturas/r/` | `desarrollo-r-p6-p7.md` |
| P6: simplex revisado | Reglas compartidas en `simplex_rules.py`, B⁻¹ por producto de matrices elementales, comparación por estado | `test_revised_simplex` (mismo camino y certificado de B⁻¹ en cada estado), `test_app::test_comparison_and_revised_evidence`, 3000 problemas por método | `desarrollo-r-p6-p7.md` |
| P7: PDF | Paso a paso, resultado y sensibilidad en PDF Unicode, fracciones o decimales | `test_export_pdf` (19 fixtures en ambos formatos, tablas anchas dentro de la página, nota final de la fuente) | `desarrollo-r-p6-p7.md` |
| V: presentación | Expresiones legibles, caja y aviso de regiones no acotadas, escala igual de ejes, costo reducido por caso, nota de fuente al final del PDF, `make ui-check` | `test_formatting::test_readable_expressions`, `test_graphical::test_unbounded_objective` (caja (6, 36/5)), `test_app::test_unbounded_graph_notice`, `test_sensitivity::test_reduced_cost_interpretations`, `test_check_ui`; capturas en `docs/capturas/v/` | `desarrollo-v-p8.md` |
| P8: entregables | Manual, guion del video, cinco problemas de ensayo, guía por módulo, README, este plan y guía de entrega | `test_manual` (5 páginas o menos, capturas reales), `test_app::test_rehearsal_problems_in_app`, `test_docs_refs`; `docs/manual/`, `docs/video.md`, `docs/ensayo-sustentacion.md`, `docs/entrega.md` | `desarrollo-v-p8.md` |

Comprobaciones transversales:

- Los 19 fixtures (`ejemplo_1`–`7`, `extra_1`–`7`, `ensayo_1`–`5`) coinciden
  con SciPy/HiGHS con ambos métodos (`make verify`, `test_oracle_scipy`).
- `scripts/stress.py --method both --seed 20261110 --count 3000` termina con
  0 errores, 0 diferencias y 0 inconcluyentes en cada método.
- `test_forbidden_imports` comprueba con AST que `src/` y `app/` no importan
  librerías de optimización.
- CI (`.github/workflows/ci.yml`) ejecuta `uv sync --locked`, Ruff y pytest con
  Python 3.12. Aún no corre en un remoto: ver `docs/entrega.md`.

## Rúbrica de la aplicación

Los porcentajes son los pesos del enunciado, no notas obtenidas. El estado
indica lo que la aplicación hace y la prueba que lo respalda; la calificación
la decide el docente.

| Criterio | Peso | Estado | Módulos | Pruebas que lo respaldan | Responsable |
|---|---:|---|---|---|---|
| Entrada y validación | 10 % | Cumplido: Max/Min, variables y restricciones dinámicas, ≤ ≥ =, enteros, decimales y fracciones; error con fila y columna | `model`, `io_json`, `app/streamlit_app.py` | `test_model::test_all_cell_errors`, `test_app::test_validation_locations`, `test_app::test_resize_preserves_cells`, `test_app::test_invalid_upload_preserves_problem` | [Integrante] |
| Implementación del método | 15 % | Cumplido: Gran M con M simbólica y simplex revisado, casos especiales | `mvalue`, `standard_form`, `simplex_rules`, `big_m`, `revised_simplex` | `test_examples`, `test_oracle_scipy::test_own_solver_against_scipy`, `test_big_m`, `test_revised_simplex`, `test_simplex_traces` | [Integrante] |
| Solución paso a paso | 25 % | Cumplido: forma estándar, tablero o B⁻¹, pivote, razones, justificación y solución final | `result`, `formatting`, `big_m`, `revised_simplex`, interfaz | `test_app::test_solved_examples_in_both_modes_and_formats`, `test_app::test_decimal_transformation_and_fractional_result`, `test_big_m::test_example_one_manual_trace` | [Integrante] |
| Método gráfico | 20 % | Cumplido para dos variables: región, rótulos, vértices con Z, isoutilidad, segmento, rayo y aviso de región no acotada | `graphical`, `render_graph` | `test_graphical::test_graphical_against_big_m`, `test_graphical::test_optimal_segment`, `test_app::test_graph_presentation`, `test_app::test_unbounded_graph_notice` | [Integrante] |
| Análisis de sensibilidad | 15 % | Cumplido: precios sombra, costos reducidos, rangos de c y b con interpretación | `sensitivity` | `test_sensitivity::test_example_two_exact_derivation`, `test_sensitivity::test_ranges_by_scipy_perturbation`, `test_oracle_scipy::test_shadow_prices_against_scipy`, `test_app::test_sensitivity_presentation` | [Integrante] |
| Interfaz gráfica y usabilidad | 15 % | Cumplido: pestañas, mensajes en español, sin tracebacks, JSON y PDF | `app/streamlit_app.py` | `test_app::test_navigation_and_pending_modules`, `test_app::test_unexpected_solver_error`, `test_app::test_rehearsal_problems_in_app`, `make ui-check` | [Integrante] |

Los casos especiales exigidos (infactible, no acotado, óptimos múltiples y
degenerado) están en `ejemplo_4`–`7`, los extras y `ensayo_1`–`4`, y se prueban
en `test_examples`, `test_graphical` y `test_app`.

## Bonificaciones

El enunciado limita los bonos a +0,5 y solo los otorga si todos los requisitos
obligatorios funcionan. La evidencia no garantiza el bono: muestra que la
función existe y está probada.

| Bono | Valor | Evidencia |
|---|---:|---|
| Dos métodos y comparación de iteraciones | +0,2 | Gran M y simplex revisado propios; pestaña «Comparar métodos» con base y Z por estado. `test_app::test_comparison_and_revised_evidence`, `test_app::test_comparison_reports_missing_state`, `test_revised_simplex::test_same_path_and_inverse_certificates` |
| Fracciones exactas en todo el paso a paso | +0,1 | `Fraction` y `MValue` en modelo y algoritmos; el formato decimal solo cambia la presentación. `test_app::test_format_change_preserves_exact_solution`, `test_formatting` |
| Exportar el paso a paso a PDF | +0,1 | Botón «Exportar paso a paso a PDF» en ambos formatos. `test_export_pdf::test_all_fixtures_export_content`, `test_app::test_pdf_requires_solution_and_reports_failure` |
| Cargar y guardar en JSON | +0,1 | Botones de carga y guardado; CSV no está implementado. `test_io_json::test_round_trip`, `test_app::test_invalid_upload_preserves_problem` |

## Pendiente del equipo

En orden. Cada tarea indica el archivo que la documenta.

1. Completar nombres, documentos, áreas y usuarios en `README.md`,
   `docs/propuesta.md` y `docs/manual/README.md`; asignar responsables en la
   rúbrica de este plan y en los tramos de `docs/video.md`.
2. Crear el remoto, subir la rama principal y confirmar CI en verde
   (`docs/entrega.md`).
3. Que cada integrante haga sus propios commits, sin reescribir el historial
   (`docs/entrega.md`, taller 6a).
4. Desplegar en Streamlit Community Cloud con Python 3.12, revisar el registro
   de instalación y probar la URL en una ventana privada (`docs/entrega.md`).
5. Grabar y publicar el video de 5 minutos o menos (`docs/video.md`).
6. Registrar las URL de repositorio, despliegue y video en `README.md` y
   `docs/manual/README.md`; regenerar el manual con `make manual`
   (`docs/manual/README.md`).
7. Completar «Uso de herramientas de IA» en `README.md`.
8. Ensayar la sustentación de 15 minutos con cada integrante
   (`docs/ensayo-sustentacion.md`, `docs/sustentacion.md`).
9. Instalar y probar la app en el portátil de la sustentación días antes, como
   plan B sin red (`docs/entrega.md`).

Todos los integrantes deben poder explicar cualquier archivo que elija el
docente. El índice por módulo de `docs/sustentacion.md` reparte el estudio.
