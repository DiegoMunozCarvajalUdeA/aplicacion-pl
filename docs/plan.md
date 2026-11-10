# Plan de implementación y verificación

## Rúbrica de la aplicación

| Criterio | Peso | Módulos | Pruebas | Responsable | Estado inicial |
|---|---:|---|---|---|---|
| Entrada y validación | 10 % | model, io_json | test_model, test_io_json | [Integrante] | Infraestructura implementada |
| Método propio | 15 % | mvalue, standard_form, big_m | test_contracts, test_examples, test_oracle_scipy | [Integrante] | Stubs |
| Paso a paso | 25 % | result, formatting, standard_form, big_m, revised_simplex, UI | test_contracts, test_examples, test_app | [Integrante] | Contratos y presentación base; cálculo pendiente |
| Método gráfico | 20 % | graphical, presentación Plotly | test_graphical, test_app | [Integrante] | Cálculo pendiente |
| Sensibilidad | 15 % | sensitivity, base final del solver | test_sensitivity, test_oracle_scipy | [Integrante] | Stub |
| Interfaz y usabilidad | 15 % | streamlit_app | test_app | [Integrante] | Navegación, edición y avisos implementados |

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
