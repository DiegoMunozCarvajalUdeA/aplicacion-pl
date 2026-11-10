# Plan de implementación y verificación

## Estado por paquete de desarrollo

| Paquete | Estado | Evidencia |
|---|---|---|
| P1: núcleo exacto | Implementado | MValue, linalg y forma estándar; 165 pruebas pasan, 36 xfail pendientes, sin XPASS |
| P2: Gran M | Implementado | 204 pruebas pasan, 22 xfail pendientes, sin XPASS; 13 fixtures coinciden con SciPy |
| C: correcciones | Implementado | 3000 casos: 0 errores y diferencias; 14 fixtures coinciden con SciPy |
| P3: paso a paso | Implementado | 237 pruebas pasan, 22 xfail pendientes, sin XPASS; 42 pruebas de interfaz |
| P4: gráfico | Implementado | 285 pruebas pasan, 19 xfail; 250 casos exactos contra Gran M |
| P5: sensibilidad | Implementado | Precios y rangos exactos; perturbaciones de ejemplos 1–2 y 150 casos generados |
| R: revisión menor | Implementado | Interpretaciones únicas, redundantes visibles y seis capturas Chromium revisadas |
| P6: revisado | Implementado | Reglas compartidas; 21 trazas idénticas; B⁻¹ comprobada en cada estado; 3000 casos por método sin errores ni diferencias |
| P7: PDF | Pendiente | Stub |
| P8: entregables | Pendiente | Guía de sustentación de P1–P5 escrita; manual, capturas y video pendientes |

P1: `make lint` y `make test` correctos. Los 13 fixtures pasan por el oráculo;
los solvers aún informan que están pendientes. AppTest muestra las formas
estándar de los ejemplos 1 y 2 sin excepciones, contrastadas con la traza manual
de `docs/sustentacion.md`.
El arranque real mediante `make run` en modo headless respondió `ok` en
`/_stcore/health`; el servidor se detuvo después de la comprobación.

P2: lint y pruebas correctos, incluidos certificados exactos del tablero,
traza manual del ejemplo 1, 40 problemas generados contra SciPy, redundancia,
rayos óptimos y Beale (14 estados, activa Bland al repetir base). Se repitió
el arranque y parada real; AppTest resolvió el ejemplo 2 con Z = 17/5.

P3: `make lint` y `make test` correctos. Los ejemplos 1–7 pasan en ambos modos
y formatos; AppTest comprueba encabezados, base, Z, estilo del pivote, razones,
alternativas, degeneración y ausencia de excepciones. Los 13 fixtures siguen
coincidiendo con SciPy. El arranque real respondió `ok`; se inspeccionaron los
datos de los ejemplos 1, 2 y 6 mediante AppTest y se detuvo el servidor.
Guía de P3 e informe de sesión en `docs/sustentacion.md` y
`docs/desarrollo-p1-p3.md`. En ese hito se recomendó continuar con P4 (gráfico).

## Rúbrica de la aplicación

| Criterio | Peso | Módulos | Pruebas | Responsable | Estado actual |
|---|---:|---|---|---|---|
| Entrada y validación | 10 % | model, io_json | test_model, test_io_json | [Integrante] | Infraestructura implementada |
| Método propio | 15 % | mvalue, standard_form, big_m | test_contracts, test_examples, test_oracle_scipy | [Integrante] | Gran M implementada |
| Paso a paso | 25 % | result, formatting, standard_form, big_m, revised_simplex, UI | test_contracts, test_examples, test_app | [Integrante] | Gran M completa; revisado pendiente |
| Método gráfico | 20 % | graphical, presentación Plotly | test_graphical, test_app | [Integrante] | Geometría exacta y presentación implementadas |
| Sensibilidad | 15 % | sensitivity, base final del solver | test_sensitivity, test_oracle_scipy | [Integrante] | Precios originales, rangos e interpretación implementados |
| Interfaz y usabilidad | 15 % | streamlit_app | test_app | [Integrante] | Gran M, gráfico y sensibilidad en ambos modos y formatos |

Los porcentajes son de la rúbrica, no porcentajes ya obtenidos. Una base
navegable no satisface por sí sola la resolución y visualización requeridas.

## Orden sugerido

1. MValue: operaciones exactas y orden lexicográfico; luego forma estándar.
2. Gran M: base, costos reducidos, razones, Bland, pivotes y casos especiales.
3. Paso a paso: revisar que cada decisión tenga evidencia en Iteration y que el
   resultado final conserve B⁻¹ y la base necesaria para sensibilidad.
4. Geometría: intersecciones, vacío, recesión, segmentos, recorte e isoutilidad.
5. Sensibilidad: derivadas originales y rangos que mantienen la base.
6. Simplex revisado: mismo contrato, comparación de resultados e iteraciones.
7. PDF: exportar los objetos existentes sin volver a resolver el problema.

Las pruebas no implementan los métodos. Las marcas xfail solo toleran
NotImplementedError; cualquier otro defecto debe corregirse. Los contratos de
MValue y forma estándar tienen pruebas propias para trabajar antes del solver.

## Semanas

| Semana | Resultado observable | Verificación |
|---|---|---|
| 1 | Propuesta, integrantes, entorno y contratos entendidos | make setup, make lint, make test |
| 2 | M simbólica, forma estándar y primeros pivotes | test_contracts; revisión manual de signos y razones |
| 3 | Entrada y Gran M resuelven ejemplos 1 y 3 | test_examples, oráculo; demostrar ambos modos |
| 4 | Casos especiales, gráfico y sensibilidad | Todos los fixtures, Hypothesis, test_graphical y test_sensitivity |
| 5 | Entrega final, manual y video; bonos si lo obligatorio funciona | Suite sin algoritmos pendientes, ensayo local y sustentación |

Las fechas exactas de los sprints deben completarse con las acordadas en clase;
no se deducen fechas de entrega del mes del enunciado.

## Reparto sugerido

- [Integrante 1]: MValue, forma estándar y Gran M; explicar penalización y Bland.
- [Integrante 2]: simplex revisado y sensibilidad; explicar B⁻¹ y derivadas.
- [Integrante 3]: geometría e interfaz; explicar recesión, recorte y estado de UI.
- [Integrante 4, si aplica]: pruebas, persistencia, PDF y entregables; distribuir
  estas tareas entre los demás si el equipo tiene tres integrantes.

Cada integrante registra commits propios, prueba su área y revisa otra. Todos
deben poder explicar cualquier archivo elegido por el docente. No registrar
contribuciones con nombres ajenos ni reescribir el historial para simularlas.

## Entrega

Completar nombres, repositorio y URL. Preparar manual de máximo 5 páginas con
dos problemas realmente resueltos, video de máximo 5 minutos y ensayo de
sustentación de 15 minutos con un problema nuevo. Los bonos suman máximo +0.5:
dos métodos +0.2, fracciones exactas +0.1, PDF +0.1 y JSON/CSV +0.1, únicamente
cuando todos los requisitos obligatorios funcionen.

P4: `make lint` y `make test` correctos; 14 fixtures coinciden con SciPy.
AppTest comprueba rótulos, vacío, flecha, segmento e isoutilidad; el servidor
respondió `ok` y se detuvo. El cálculo usa Cramer, recesión y recorte exactos,
sin llamar a Gran M. La guía P4 está en `docs/sustentacion.md`.

P5: rangos y precios derivados de A y la base, sin consultar el tablero.
Se deshacen signos originales; las redundantes reciben precio dual cero sin
rango propio y las demás filas conservan las dependencias originales.
P6 implementado: refactor de reglas puras en commit separado y comparación real.
Siguiente paquete de esta sesión: P7 (PDF).
P8 permanece para la sesión final; `docs/desarrollo-c-p4-p5.md` registra
comandos, resultados y decisiones de C, P4 y P5.
