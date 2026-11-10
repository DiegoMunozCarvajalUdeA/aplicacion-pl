# Prompt: preparar el entorno del proyecto "Aplicación de Programación Lineal"

## 1. Rol y objetivo

Eres un ingeniero de software. Vas a preparar el repositorio y el entorno de desarrollo de un proyecto universitario de Optimización (Universidad de Antioquia, Ingeniería de Sistemas, noviembre de 2026).

- Directorio de trabajo: `/Users/diegocarvajal/dev/20-areas/udea/optimizacion/aplicacion-pl`
- Enunciado completo: `taller-optimi.pdf` en la raíz. Léelo antes de empezar. Este prompt lo resume; si hay diferencias, manda el PDF.
- Máquina: macOS (Apple Silicon), Homebrew, `uv` instalado en `/opt/homebrew/bin/uv`. El Python del sistema es 3.14; no lo uses.

Tu trabajo NO es resolver el proyecto. Es dejar listo todo lo que el equipo necesita para desarrollarlo: entorno reproducible, estructura del código, contratos de cada módulo, datos de prueba con resultados esperados, pruebas automáticas, verificación externa con scipy, interfaz base navegable, CI y documentación inicial. Trabaja hasta cumplir todos los criterios de aceptación de la sección 9 y verifícalos ejecutando los comandos.

## 2. Resumen del enunciado

Aplicación con interfaz gráfica (escritorio o web; una app solo de consola no se califica) que resuelve problemas de programación lineal por el método de la Gran M o por el simplex revisado, con un método implementado por el equipo. Las librerías de optimización (scipy, PuLP, OR-Tools, Solver de Excel) solo se permiten para verificar resultados, nunca para producirlos.

Requisitos funcionales:

1. Entrada: Max o Min, n variables, m restricciones con ≤, ≥ o =, lados derechos de cualquier signo. Todas las variables son x ≥ 0. Validar campos vacíos, valores no numéricos y dimensiones inconsistentes, con mensajes claros.
2. Método propio: Gran M o simplex revisado.
3. Dos modos que el usuario elige: solución directa o paso a paso. El paso a paso muestra la forma estándar (holguras, excesos, artificiales) y, en cada iteración, la variable que entra y por qué, la prueba de la razón mínima, la variable que sale y por qué, el pivote y el tablero (o B⁻¹, las variables básicas y los costos reducidos en el simplex revisado). Números en fracciones o decimales legibles.
4. Solución óptima: valor de cada variable, valor de Z, holgura o exceso de cada restricción.
5. Método gráfico cuando n = 2: región factible sombreada, restricciones rotuladas, vértices con su Z, recta de Z en el óptimo (isoutilidad), escala adecuada, regiones no acotadas o vacías bien mostradas. Si n > 2, avisar que el método gráfico no aplica.
6. Análisis de sensibilidad: precios sombra, costos reducidos, rango de cada coeficiente de la función objetivo y rango de cada lado derecho, con interpretación en texto.
7. Casos sin solución única: infactible, no acotado, óptimos múltiples, degenerado. Siempre con un mensaje claro, nunca con una excepción o traceback.
8. Interfaz: agregar o quitar variables y restricciones, editar y volver a resolver sin reiniciar; resultados en secciones (paso a paso, gráfico, sensibilidad); mensajes de error comprensibles.

Rúbrica de la entrega 1 (pesos): entrada y validación 10 %, implementación del método 15 %, paso a paso 25 %, método gráfico 20 %, sensibilidad 15 %, interfaz y usabilidad 15 %.

Bonificaciones (máximo +0.5): implementar los dos métodos y comparar sus iteraciones (+0.2); fracciones exactas en todo el paso a paso (+0.1); exportar el paso a paso a PDF (+0.1); cargar y guardar problemas en JSON o CSV (+0.1).

Entregables: repositorio GitHub o GitLab con commits de todos los integrantes; README con requisitos, instalación y ejecución (ejecutable o URL); manual de usuario de máximo 5 páginas con capturas de dos problemas resueltos; video de máximo 5 minutos. En la sustentación cada integrante explica una parte del código elegida por el docente y el equipo resuelve en vivo un problema desconocido. Se permite usar IA como apoyo, pero el código que un integrante no pueda explicar cuenta como no implementado. Copiar de otro equipo o de un repositorio público sin citarlo descalifica.

Problemas de ejemplo (todos con x ≥ 0). El docente evaluará con problemas distintos de igual o mayor dificultad que cubren los mismos casos:

| # | Problema | Caso | Resultado esperado |
|---|---|---|---|
| 1 | Max Z = 50x₁ + 80x₂; 2x₁ + x₂ ≤ 100; x₁ + 3x₂ ≤ 90; x₂ ≤ 40 | Forma estándar, restricción redundante, gráfico | x₁ = 42, x₂ = 16, Z = 3380 |
| 2 | Min Z = 4x₁ + x₂; 3x₁ + x₂ = 3; 4x₁ + 3x₂ ≥ 6; −x₁ − 2x₂ ≥ −4 | Min, =, ≥, lado derecho negativo, artificiales | x₁ = 2/5, x₂ = 9/5, Z = 17/5 |
| 3 | Max Z = 3x₁ + 2x₂ + 5x₃; x₁ + 2x₂ + x₃ ≤ 430; 3x₁ + 2x₃ ≤ 460; x₁ + 4x₂ ≤ 420 | Tres variables (gráfico no aplica) | x₁ = 0, x₂ = 100, x₃ = 230, Z = 1350 |
| 4 | Max Z = x₁ + x₂; x₁ + x₂ ≤ 2; x₁ + x₂ ≥ 5 | Infactible | Mensaje: no tiene solución factible |
| 5 | Max Z = x₁ + x₂; x₁ − x₂ ≤ 1; −x₁ + x₂ ≤ 2 | No acotado | Mensaje: solución no acotada |
| 6 | Max Z = 2x₁ + 4x₂; x₁ + 2x₂ ≤ 5; x₁ + x₂ ≤ 4 | Óptimos múltiples | Z = 10 en todo el segmento entre (0, 5/2) y (3, 1) |
| 7 | Max Z = 3x₁ + 9x₂; x₁ + 4x₂ ≤ 8; x₁ + 2x₂ ≤ 4 | Degeneración | x₁ = 0, x₂ = 2, Z = 18, con una variable básica en 0 |

## 3. Stack (decidido)

- Python 3.12 gestionado con `uv` (`uv python pin 3.12`), layout `src/`, paquete `plapp`.
- Interfaz web con Streamlit (corre local en la sustentación y se puede desplegar en Streamlit Community Cloud para tener URL).
- Gráficos con Plotly. Exportación a PDF con fpdf2.
- Aritmética exacta con `fractions.Fraction` de la biblioteca estándar en todo el modelo y el paso a paso (bono de fracciones exactas). Los decimales son solo un formato de presentación.
- Gran M simbólica: no usar un número grande para M. Cada coeficiente del tablero es `a + b·M` con `a` y `b` de tipo `Fraction` (clase `MValue`). La comparación es lexicográfica: primero `b`, luego `a`. Así el tablero muestra `3 − 2M` y no `-1999997`.
- Método principal: Gran M. Segundo método: simplex revisado (bono). Ambos devuelven la misma estructura de resultado para poder compararlos iteración por iteración.
- Herramientas de desarrollo (grupo `dev` de uv): pytest, pytest-cov, hypothesis, ruff, scipy (solo como oráculo de verificación).

Consulta la documentación oficial vigente de Streamlit, Plotly, fpdf2 y uv antes de usar sus APIs; no supongas firmas de funciones. Si encuentras una razón técnica concreta para cambiar una decisión de esta sección, detente y explícala en vez de cambiarla por tu cuenta.

## 4. Reglas obligatorias

1. Ningún archivo bajo `src/` ni `app/` puede importar `scipy`, `pulp`, `ortools`, `cvxpy`, `pyomo` ni otra librería de optimización. scipy va solo en el grupo `dev` y solo se usa en `tests/` y `scripts/`. Agrega una prueba que lo verifique recorriendo los imports con `ast`.
2. No implementes los algoritmos centrales: conversión a forma estándar, `MValue`, Gran M, simplex revisado, cálculo del método gráfico, análisis de sensibilidad y exportación a PDF. Déjalos como stubs con firma tipada, un docstring en español que describa el algoritmo paso a paso (ver sección 6) y `raise NotImplementedError`. El equipo los implementará y debe poder explicarlos.
3. Sí implementa por completo la infraestructura: modelo de datos, lectura de números, validación, carga y guardado JSON, formato de números, interfaz base, pruebas, script de verificación con scipy, CI y documentación.
4. Interfaz, mensajes, comentarios y docstrings en español. Identificadores de código en inglés.
5. Código simple y legible: funciones cortas, sin metaprogramación ni abstracciones innecesarias. Cada integrante debe poder explicarlo en la sustentación.
6. La interfaz nunca muestra un traceback. Captura `NotImplementedError` (y cualquier error inesperado) y muestra un aviso en español.
7. No muevas, renombres ni borres `taller-optimi.pdf` ni este archivo.
8. Git: inicializa el repositorio y haz commits locales pequeños con Conventional Commits. No crees remotos ni hagas push.

## 5. Estructura objetivo

```
aplicacion-pl/
├── pyproject.toml
├── uv.lock
├── .python-version
├── .gitignore
├── Makefile
├── requirements.txt            # exportado con uv, para el despliegue
├── README.md
├── AGENTS.md                   # reglas para futuras sesiones con IA (sección 4)
├── .github/workflows/ci.yml
├── .streamlit/config.toml
├── src/plapp/
│   ├── __init__.py
│   ├── model.py                # LPProblem, Constraint, parse_number, validate  (implementar)
│   ├── io_json.py              # load_problem, save_problem                     (implementar)
│   ├── formatting.py           # Fraction y MValue a texto, modo fracción/decimal (implementar)
│   ├── result.py               # dataclasses de resultados y Status             (implementar)
│   ├── mvalue.py               # MValue = a + b·M                               (stub)
│   ├── standard_form.py        # to_standard_form                               (stub)
│   ├── big_m.py                # solve_big_m                                    (stub)
│   ├── revised_simplex.py      # solve_revised                                  (stub)
│   ├── graphical.py            # graphical_method                               (stub)
│   ├── sensitivity.py          # sensitivity_analysis                           (stub)
│   └── export_pdf.py           # export_steps_pdf                               (stub)
├── app/
│   └── streamlit_app.py
├── scripts/
│   └── verify.py               # oráculo scipy para un JSON
├── tests/
│   ├── conftest.py
│   ├── fixtures/problems/      # ejemplo_1.json … ejemplo_7.json y extras
│   ├── test_model.py
│   ├── test_io_json.py
│   ├── test_formatting.py
│   ├── test_forbidden_imports.py
│   ├── test_examples.py
│   ├── test_oracle_scipy.py
│   ├── test_graphical.py
│   └── test_sensitivity.py
└── docs/
    ├── propuesta.md
    ├── plan.md
    ├── teoria.md
    └── manual/README.md
```

## 6. Contratos de los módulos

Puedes ajustar nombres si lo justificas, pero conserva la idea.

`model.py`
- `Sense = Literal["max", "min"]`, `Relation = Literal["<=", ">=", "="]`.
- `@dataclass(frozen=True) class Constraint`: `coefficients: tuple[Fraction, ...]`, `relation: Relation`, `rhs: Fraction`, `name: str` (por defecto `R1`, `R2`, …).
- `@dataclass(frozen=True) class LPProblem`: `name`, `sense`, `variable_names: tuple[str, ...]` (por defecto `x1`, `x2`, …), `objective: tuple[Fraction, ...]`, `constraints: tuple[Constraint, ...]`.
- `parse_number(text) -> Fraction`: acepta enteros, decimales con punto o coma (`2,5`), fracciones (`2/5`), signo negativo y espacios. Lanza `ValueError` con mensaje en español.
- `validate(raw) -> tuple[LPProblem | None, list[ValidationIssue]]`: recibe los datos crudos de la interfaz o del JSON. `ValidationIssue` indica ubicación (`objetivo`, `restricción 2, x3`, `lado derecho de R1`) y mensaje. Detecta campos vacíos, valores no numéricos, signos inválidos, filas con distinto número de coeficientes, n < 1, m < 1 y restricciones con todos los coeficientes en 0.

`result.py`
- `Status(Enum)`: `OPTIMAL`, `INFEASIBLE`, `UNBOUNDED`. Además, banderas `multiple_optima: bool` y `degenerate: bool` en la solución.
- `StandardForm`: nombres de columnas, tipo de cada columna (`original`, `holgura`, `exceso`, `artificial`), matriz A, vector b, costos c como `MValue`, base inicial y lista de transformaciones en texto (por ejemplo: "R3 multiplicada por −1 porque su lado derecho era negativo; ≥ pasa a ≤").
- `RatioRow`: fila, variable básica, lado derecho, coeficiente de la columna entrante, razón o `None` con el motivo de exclusión (coeficiente ≤ 0).
- `Iteration`: número, base, tablero (o B⁻¹ y costos reducidos en el simplex revisado), variable entrante con justificación, filas de la razón mínima, variable saliente con justificación (incluye empates), pivote (fila, columna, valor).
- `Solution`: método, estado, mensaje en español, valores de las variables, Z, holgura o exceso por restricción, forma estándar, iteraciones, base final, B⁻¹ final, banderas y soluciones alternativas si hay óptimos múltiples.
- `SensitivityReport`: precios sombra, costos reducidos, rango de cada cⱼ y de cada bᵢ como `(inferior, superior)` con `None` para ±∞, e interpretación en texto por cada fila.
- `GraphicalResult`: `applicable`, motivo si no aplica, rectas de las restricciones, polígono factible, vértices con su Z, si la región es acotada o vacía, punto(s) óptimo(s) y recta de isoutilidad.

Stubs (firma tipada, docstring con el algoritmo en pasos, `raise NotImplementedError`):
- `mvalue.py`: `MValue` con suma, resta, multiplicación y división por escalar `Fraction`, comparación lexicográfica y `__str__`.
- `standard_form.py`: `to_standard_form(problem) -> StandardForm`. Pasos: lado derecho negativo se multiplica por −1 y se invierte el signo; ≤ agrega holgura; ≥ agrega exceso y artificial; = agrega artificial; las artificiales tienen costo −M en Max o +M en Min.
- `big_m.py`: `solve_big_m(problem) -> Solution`. Entrante: costo reducido más favorable según Max o Min. Razón mínima solo con coeficientes > 0. Usar la regla de Bland ante empates o ciclos. Infactible si al terminar hay una artificial básica con valor > 0. No acotado si la columna entrante no tiene coeficientes > 0. Óptimos múltiples si una no básica tiene costo reducido 0 en el tablero final. Degenerado si una básica vale 0 o hubo empate en la razón mínima.
- `revised_simplex.py`: `solve_revised(problem) -> Solution` con B⁻¹, c_B B⁻¹ y costos reducidos por iteración.
- `graphical.py`: `graphical_method(problem) -> GraphicalResult`. Pasos: si n ≠ 2, `applicable=False`; intersecar cada par de rectas (restricciones y ejes); conservar los puntos factibles; ordenarlos por ángulo alrededor del centroide; si la región no es acotada, recortarla con una caja que supere el vértice más lejano en un margen; evaluar Z en cada vértice; trazar la isoutilidad por el óptimo.
- `sensitivity.py`: `sensitivity_analysis(problem, solution) -> SensitivityReport` a partir de la base óptima: y = c_B B⁻¹; rango de cⱼ básica y no básica; rango de bᵢ con B⁻¹(b + Δeᵢ) ≥ 0.
- `export_pdf.py`: `export_steps_pdf(solution, path) -> None`.

## 7. Datos de prueba, pruebas y verificación

Fixtures JSON en `tests/fixtures/problems/`. Los números van como texto para conservar fracciones exactas:

```json
{
  "nombre": "Ejemplo 2",
  "caso": "Min, =, ≥, lado derecho negativo, artificiales",
  "sentido": "min",
  "variables": ["x1", "x2"],
  "objetivo": ["4", "1"],
  "restricciones": [
    {"coeficientes": ["3", "1"], "signo": "=", "rhs": "3"},
    {"coeficientes": ["4", "3"], "signo": ">=", "rhs": "6"},
    {"coeficientes": ["-1", "-2"], "signo": ">=", "rhs": "-4"}
  ],
  "esperado": {
    "estado": "optimo",
    "x": {"x1": "2/5", "x2": "9/5"},
    "z": "17/5",
    "multiples": false,
    "degenerado": false,
    "fuente": "enunciado"
  }
}
```

- Crea `ejemplo_1.json` a `ejemplo_7.json` con los datos de la tabla de la sección 2.
- Agrega al menos 6 problemas extra que cubran lo que el docente puede variar: Min con solo ≥ y región no acotada pero óptimo finito (para el gráfico), solo restricciones =, región gráfica vacía, n = 4 y m = 3 mixto, Max con lado derecho negativo en una ≤, y un caso degenerado con empate en la razón mínima. Calcula sus resultados esperados con `scripts/verify.py` y marca `"fuente": "scipy"`.
- `test_examples.py`: parametrizado sobre todos los fixtures y sobre ambos métodos. Para el ejemplo 6, acepta cualquier punto del segmento con Z = 10 y exige `multiple_optima`. Para el 7, exige `degenerate`. Para el 4 y el 5, verifica el estado y que el mensaje contenga "no tiene solución factible" y "no acotada".
- `test_oracle_scipy.py`: con hypothesis, genera PL pequeños (n de 2 a 4, m de 1 a 4, coeficientes enteros entre −9 y 9, los tres signos, lados derechos de cualquier signo) y compara estado y Z con `scipy.optimize.linprog(method="highs")`. Compara precios sombra solo cuando la solución es única y no degenerada.
- `test_graphical.py` y `test_sensitivity.py`: vértices y Z del ejemplo 1 (incluye que x₂ ≤ 40 es redundante), aviso de no aplica para el ejemplo 3, precios sombra del ejemplo 1 comparados con scipy.
- Las pruebas de los stubs se marcan `@pytest.mark.xfail(raises=NotImplementedError, strict=False)` para que pasen a verde cuando el equipo implemente cada módulo, sin cambiar la prueba.
- `scripts/verify.py <archivo.json>`: imprime estado, x, Z, holguras y precios sombra según scipy. Documenta la convención de signos: linprog minimiza, así que en Max se niega c, y las restricciones ≥ se pasan como −a·x ≤ −b, lo que invierte el signo del multiplicador. El precio sombra que se reporta es ∂Z*/∂bᵢ en el sentido original del problema. Si el solver propio ya está implementado, compara ambos resultados e indica las diferencias.

## 8. Interfaz base (`app/streamlit_app.py`)

- Barra lateral: sentido (Max o Min), método (Gran M, Simplex revisado, Comparar ambos), modo (Directo o Paso a paso), formato numérico (Fracciones o Decimales con número de decimales), cargar un ejemplo (lista con los fixtures), cargar JSON (subir archivo), guardar JSON (descarga).
- Panel principal: botones "Agregar variable", "Quitar variable", "Agregar restricción" y "Quitar restricción". Tabla editable de la función objetivo y tabla editable de restricciones (columnas x1…xn, signo como lista desplegable, lado derecho). El estado vive en `st.session_state`; al agregar o quitar filas o columnas no se pierden los valores existentes.
- Botón "Resolver": valida y muestra los problemas encontrados señalando la celda; si todo es válido, intenta resolver.
- Pestañas: "Resultado", "Paso a paso", "Método gráfico", "Sensibilidad", "Comparar métodos". Mientras un módulo sea stub, la pestaña muestra "Pendiente de implementar: <módulo>". La pestaña de forma estándar y el resumen del problema validado sí deben funcionar desde ya.
- Botón "Exportar paso a paso a PDF" visible, deshabilitado o con aviso mientras sea stub.

## 9. Calidad, CI y documentación

- ruff configurado en `pyproject.toml` (largo de línea 100; reglas E, F, I, UP, B).
- `Makefile` con objetivos `setup`, `run`, `test`, `lint`, `fmt`, `verify FILE=...` y `requirements` (exporta `requirements.txt` con `uv export` sin dependencias dev; verifica las opciones con `uv export --help`).
- `.github/workflows/ci.yml`: instala uv con la acción oficial de Astral (verifica la versión vigente), `uv sync --locked`, `ruff check`, `ruff format --check`, `pytest`.
- `README.md` en español: descripción, requisitos, instalación, ejecución, pruebas, despliegue en Streamlit Community Cloud, estructura del proyecto, tabla de integrantes (marcadores) y sección de referencias para citar cualquier fuente externa.
- `docs/propuesta.md` (semana 1): lenguaje, método elegido, integrantes (marcadores) y boceto ASCII de la interfaz.
- `docs/plan.md`: tabla criterio de la rúbrica → módulo → pruebas → responsable (marcador) → estado; plan por semanas (semana 3: entrada y método resolviendo los ejemplos 1 y 3; semana 5: entrega final); reparto sugerido para que cada integrante tenga un área propia y commits propios.
- `docs/teoria.md`: resumen corto de la Gran M, la prueba de la razón mínima, la regla de Bland, los criterios de optimalidad para Max y Min, la detección de los cuatro casos especiales y las fórmulas de sensibilidad. Sirve para preparar la sustentación.
- `docs/manual/README.md`: esqueleto del manual de usuario (máximo 5 páginas, capturas de dos problemas resueltos).
- `AGENTS.md`: las reglas de la sección 4 para futuras sesiones con IA.

## 10. Criterios de aceptación

Verifica cada uno ejecutando el comando y revisando la salida:

1. `uv sync` termina sin errores; `.python-version` dice 3.12; existe `uv.lock`.
2. `uv run ruff check .` y `uv run ruff format --check .` sin hallazgos.
3. `uv run pytest` termina sin fallos: las pruebas de infraestructura pasan y las de algoritmos aparecen como xfail.
4. La app arranca: `uv run streamlit run app/streamlit_app.py --server.headless true` en segundo plano, `curl http://localhost:8501/_stcore/health` responde `ok`; luego detén el proceso. Revisa que no haya errores en el log.
5. `test_forbidden_imports.py` pasa y `grep -rE "import (scipy|pulp|ortools)|from (scipy|pulp|ortools)" src app` no devuelve nada.
6. `uv run python scripts/verify.py tests/fixtures/problems/ejemplo_1.json` imprime x1 = 42, x2 = 16, Z = 3380, y los siete ejemplos coinciden con la tabla del enunciado (el 4 infactible y el 5 no acotado).
7. Todos los fixtures extra tienen resultados esperados verificados con scipy.
8. El repositorio git tiene commits atómicos con Conventional Commits y ningún archivo generado o secreto (`.venv`, `__pycache__`, `.pytest_cache`, `.env`).

## 11. Informe final

Al terminar, entrega:

- Árbol de archivos creados.
- Comandos ejecutados y resultado de cada criterio de aceptación.
- Cualquier desviación de este prompt y su motivo.
- Lista de stubs pendientes con el criterio de la rúbrica que cubre cada uno, en el orden sugerido de implementación.
- Datos que el equipo debe completar: nombres de los integrantes, URL del repositorio remoto y URL de despliegue.
