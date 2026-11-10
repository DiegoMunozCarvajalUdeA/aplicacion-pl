# Verificación del entorno

Fecha: 2026-11-10. Equipo: macOS Apple Silicon. Python gestionado por uv:
3.12.13; `.python-version`: `3.12`. Se leyó completo `taller-optimi.pdf` antes
de implementar. El PDF y `PROMPT-entorno.md` se conservaron sin cambios.

## Criterios de aceptación

| N.º | Comando o comprobación ejecutada | Resultado |
|---:|---|---|
| 1 | `uv python pin 3.12`, `uv sync`, `uv sync --locked` | Correcto; entorno instalado, pin 3.12 y uv.lock existente |
| 2 | `uv run ruff check .`, `uv run ruff format --check .` | Sin hallazgos; formato verificado |
| 3 | `uv run pytest` | 119 pruebas pasan, 49 xfail esperados, cero fallos |
| 4 | `uv run streamlit run app/streamlit_app.py --server.headless true --server.address 127.0.0.1`; `curl http://localhost:8501/_stcore/health` | `ok`; log sin errores; servidor detenido con salida 0 |
| 5 | `uv run pytest tests/test_forbidden_imports.py -q`; `grep -rE 'import (scipy\|pulp\|ortools)\|from (scipy\|pulp\|ortools)' src app` | 9 pruebas pasan; búsqueda sin coincidencias, código 1 esperado de grep |
| 6 | `uv run python scripts/verify.py tests/fixtures/problems/ejemplo_1.json` y ejecución del mismo script sobre los otros seis ejemplos | x1 = 42, x2 = 16, Z = 3380; los siete coinciden con el enunciado |
| 7 | Script sobre los seis extras; `uv run pytest tests/test_oracle_scipy.py -q` | Estados, x, Z, holguras y precios de extras contrastados con SciPy; fuente registrada |
| 8 | `git log --oneline`, `git ls-files`, `git status --short`, `git remote` | Commits locales por área; árbol limpio, sin remotos, secretos ni cachés versionadas |

Para el criterio 5, el patrón literal ejecutado fue:

```bash
grep -rE "import (scipy|pulp|ortools)|from (scipy|pulp|ortools)" src app
```

Las pruebas AST también prohíben CVXPY, Pyomo y otros solvers, e incluyen casos
de detección. Se comprobó que SciPy pertenece solo a `dependency-groups.dev`
y que `requirements.txt` no contiene SciPy, pytest, Ruff ni Hypothesis.
Se verificaron las opciones de `uv export --help` y se ejecutó:

```bash
uv export --locked --no-dev --no-hashes --no-editable --output-file requirements.txt
```

La acción oficial de Astral se consultó en su documentación vigente y se fijó
por SHA, versión v9.0.0. Los mismos comandos de calidad de CI se ejecutaron
localmente; el workflow remoto no se ejecutó porque no se publicó el repositorio.
Las referencias oficiales consultadas están en `README.md`.

## Resultados del oráculo

| Archivo | Estado | x de referencia | Z |
|---|---|---|---|
| ejemplo_1.json | Óptimo | (42, 16) | 3380 |
| ejemplo_2.json | Óptimo | (2/5, 9/5) | 17/5 |
| ejemplo_3.json | Óptimo | (0, 100, 230) | 1350 |
| ejemplo_4.json | Infactible | — | — |
| ejemplo_5.json | No acotado | — | — |
| ejemplo_6.json | Óptimos múltiples | Segmento (0, 5/2) a (3, 1) | 10 |
| ejemplo_7.json | Óptimo degenerado | (0, 2) | 18 |
| extra_1.json | Óptimo; región no acotada | (2, 1) | 4 |
| extra_2.json | Óptimo; solo igualdades | (2, 1, 1) | 8 |
| extra_3.json | Infactible; región vacía | — | — |
| extra_4.json | Óptimo; n=4, m=3 mixto | (7, 3, 0, 0) | 27 |
| extra_5.json | Óptimo; Max con RHS negativo en ≤ | (4, 0) | 12 |
| extra_6.json | Óptimo degenerado; empate de razón mínima | (2, 0) | 6 |

Los valores de los extras se calcularon usando `verify_with_scipy` de
`scripts/verify.py`, se guardaron como texto racional y se revalidaron mediante
la CLI del mismo script y pruebas independientes de factibilidad. HiGHS no
informa directamente las banderas de degeneración o multiplicidad: estas
propiedades vienen del enunciado y de la construcción de los casos. En el
extra 6, x1 entra con razones 2 en R1 y R3; en el óptimo quedan restricciones
activas redundantes con la no negatividad de x2.

Para el ejemplo 1, el verificador informa holguras (0, 0, 24) y precios sombra
(14, 22, 0). Las pruebas de signos contrastan marginales con perturbaciones
del RHS en el sentido original. La guardia para comparar sensibilidad en los
problemas generados exige óptimo único y no degenerado.

## Interfaz

`uv run pytest tests/test_app.py -q`: nueve pruebas pasan. Se comprobaron las
cinco pestañas, resumen validado, avisos de stubs, botón PDF deshabilitado,
conservación de datos al agregar/quitar dimensiones, mínimos de una variable
y una restricción, cambio de sentido al cargar, aviso gráfico para n=3,
comparación de métodos, formato decimal, errores por celda, fallo inesperado
del solver y carga inválida sin pérdida del modelo.

AppTest ejecutó la app sin excepciones. El arranque real respondió `ok` en
8501; el log mostró inicio de Uvicorn y parada normal, sin traceback ni errores.
El proceso de verificación se detuvo; no se dejó un servidor ejecutándose.

## Árbol de archivos creados

```text
.
├── .github/workflows/ci.yml
├── .gitignore
├── .python-version
├── .streamlit/config.toml
├── AGENTS.md
├── Makefile
├── README.md
├── pyproject.toml
├── requirements.txt
├── uv.lock
├── src/plapp/
│   ├── __init__.py
│   ├── model.py
│   ├── io_json.py
│   ├── formatting.py
│   ├── result.py
│   ├── mvalue.py
│   ├── standard_form.py
│   ├── big_m.py
│   ├── revised_simplex.py
│   ├── graphical.py
│   ├── sensitivity.py
│   └── export_pdf.py
├── app/streamlit_app.py
├── scripts/verify.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_app.py
│   ├── test_contracts.py
│   ├── test_examples.py
│   ├── test_forbidden_imports.py
│   ├── test_formatting.py
│   ├── test_graphical.py
│   ├── test_io_json.py
│   ├── test_model.py
│   ├── test_oracle_scipy.py
│   ├── test_sensitivity.py
│   ├── test_verifier.py
│   └── fixtures/problems/
│       ├── ejemplo_1.json
│       ├── ejemplo_2.json
│       ├── ejemplo_3.json
│       ├── ejemplo_4.json
│       ├── ejemplo_5.json
│       ├── ejemplo_6.json
│       ├── ejemplo_7.json
│       ├── extra_1.json
│       ├── extra_2.json
│       ├── extra_3.json
│       ├── extra_4.json
│       ├── extra_5.json
│       └── extra_6.json
└── docs/
    ├── propuesta.md
    ├── plan.md
    ├── teoria.md
    ├── verificacion.md
    └── manual/README.md
```

Preexistentes, conservados: `taller-optimi.pdf` y `PROMPT-entorno.md`.

## Decisiones y ajustes al prompt

- Existe una contradicción entre mantener la conversión a forma estándar como
  stub (§4 y §6) y mostrarla funcionando desde ahora (§8). Se respetó la regla
  obligatoria: el resumen validado funciona y la sección de forma estándar
  está conectada, pero muestra «Pendiente de implementar: forma estándar».
- La prohibición de implementar MValue se aplica a sus operaciones y `__str__`.
  Su dataclass solo almacena las dos fracciones para que funcionen contratos y
  formato de presentación sin implementar aritmética simbólica.
- Se agregaron `test_contracts.py`, `test_app.py`, `test_verifier.py`,
  `tests/__init__.py` y este informe para verificar las responsabilidades
  solicitadas. Se añadieron Pivot, GraphLine y GraphVertex como contratos
  explícitos; la UI dibuja puntos ya calculados y no realiza geometría.
- Las marcas xfail solo capturan NotImplementedError. Una aserción fallida no
  queda ocultada. Los resultados futuros satisfactorios aparecerán como XPASS
  mientras se conservan las marcas `strict=False` solicitadas.

No se cambió el stack ni se implementaron los algoritmos centrales.

## Stubs pendientes, en orden sugerido

| Orden | Módulo | Criterio que habilita |
|---:|---|---|
| 1 | mvalue.py | Método propio 15 %, paso a paso 25 %, bono fracciones exactas |
| 2 | standard_form.py | Método propio 15 %, forma estándar del paso a paso 25 % |
| 3 | big_m.py | Método propio 15 %, paso a paso 25 %, detección de casos especiales |
| 4 | graphical.py | Método gráfico 20 % |
| 5 | sensitivity.py | Análisis de sensibilidad 15 % |
| 6 | revised_simplex.py | Segundo método, paso a paso 25 %, bono comparación +0.2 |
| 7 | export_pdf.py | Exportación del paso a paso; bono PDF +0.1 |

Cada stub tiene firma tipada, docstring en español con pasos y
`raise NotImplementedError`. Implementar después con contribuciones del equipo.

## Historial local y datos por completar

- `a2d0151` — `chore: set up Python project and contracts`.
- `746c61f` — `test: add fixtures and SciPy verification`.
- `ec05b2d` — `feat: add editable Streamlit interface`.
- `5d3d03c` — `fix: format files before lint corrections`. Ajuste de `make fmt`: formatear antes de comprobar reglas para que Ruff pueda
  corregir primero las líneas largas que admiten formato automático.
- Commit de documentación y este informe, posterior a las verificaciones.

Completar nombres e identificadores de integrantes, cuentas Git y responsables,
URL real del repositorio remoto y URL real de despliegue. Para la entrega final,
agregar capturas auténticas de dos problemas resueltos y URL del video. Esta
preparación no crea remotos ni realiza push o despliegue.
