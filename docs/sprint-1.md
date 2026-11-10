# Preparación del sprint 1 (semana 1: propuesta)

## 1. Qué se evalúa

El cronograma del enunciado (`taller-optimi.pdf`, sección 6) pide para la
semana 1 una propuesta con cuatro elementos:

1. lenguaje;
2. método elegido;
3. integrantes;
4. boceto de la interfaz.

El enunciado añade: «Las dudas sobre el enunciado se resuelven en clase antes
de la entrega de la propuesta. La comprensión de los requisitos hace parte de la
evaluación.» Por eso esta guía incluye las preguntas que conviene llevar a clase
(sección 5) y un mapa de requisitos (sección 6).

La propuesta está en `docs/propuesta.md`. La aplicación ya funciona, así que
conviene mostrarla en ejecución y explicar con honestidad qué está hecho y qué
falta. El uso de herramientas de IA se declara en la sección «Uso de herramientas
de IA» del README; el enunciado lo permite como apoyo, siempre que cada
integrante explique y modifique cualquier parte del código.

## 2. Lista de comprobación antes de la clase

- [ ] Completar en `docs/propuesta.md` y en el README los nombres, documentos y
      cuentas Git, y acordar quién lidera cada parte.
- [ ] Cada integrante instala y ejecuta la app en su computador: `make setup` y
      luego `make run`. Después resuelve los ejemplos 1, 2 y 6 (sección 7).
- [ ] Llevar al menos un portátil con la app ya instalada y probada, sin
      depender de la red (`docs/entrega.md`, sección 6).
- [ ] Si el docente pide el repositorio desde ya, crearlo y darle acceso según
      `docs/entrega.md`, secciones 2 y 3. No reescribir el historial.
- [ ] Repasar las preguntas de la sección 4 y llevar impresas las de la sección 5.
- [ ] Si se entrega en PDF, exportar `docs/propuesta.md` (por ejemplo, desde el
      visor de Markdown del editor) y revisar que el boceto se vea en monoespacio.

## 3. Guion de presentación (unos 4 minutos)

| Tiempo | Quién | Qué se dice o se muestra |
|---|---|---|
| 0:00–0:30 | [Integrante 1] | Equipo y objetivo: una app con interfaz gráfica que resuelve programación lineal con un método propio y muestra el proceso completo. |
| 0:30–1:15 | [Integrante 2] | Lenguaje: Python 3.12 con Streamlit, aritmética exacta con `Fraction`, SciPy solo para verificar. |
| 1:15–2:15 | [Integrante 3] | Método: Gran M con M simbólica `a + b·M`; cómo se tratan ≥, = y lados derechos negativos; reglas de entrada y salida; casos especiales. Segundo método: simplex revisado (bonificación). |
| 2:15–3:30 | [Integrante 1] | Boceto y app en vivo: cargar el ejemplo 2, Paso a paso, mostrar la forma estándar y una iteración; luego el gráfico del ejemplo 6. |
| 3:30–4:00 | [Integrante 2] | Plan por sprints y riesgos (tablas finales de `docs/propuesta.md`) y dudas para el docente. |

## 4. Preguntas probables del docente

**¿Por qué Gran M y no dos fases?** Con M simbólica se resuelve en una sola fase
y un solo tablero. Las artificiales reciben costo −M en Max y +M en Min, y la
fila de costos reducidos muestra expresiones como `4 - 7M`. Con dos fases habría
que explicar dos funciones objetivo y el paso entre ellas.

**¿Qué valor tiene M?** Ninguno. Cada costo se guarda como `a + b·M` y se compara
primero por b, la parte en M, y después por a. Así M domina a cualquier número
sin elegir un valor grande, y no hay errores de redondeo.

**¿Cómo tratan un lado derecho negativo?** Se multiplica la fila por −1 y se
invierte el signo. En el ejemplo 2, R3: −x1 − 2·x2 ≥ −4 pasa a x1 + 2·x2 ≤ 4 y
recibe la holgura s3.

**¿Qué variable entra y cuál sale?** En Max entra la de mayor costo reducido
cⱼ − zⱼ positivo; en Min, la del más negativo. Sale la básica con menor razón
x_B / d entre las filas con d > 0, y un empate se rompe por el menor índice. Si
una base se repite, se aplica la regla de Bland para no ciclar.

**¿Cómo demuestran que el método es propio?** `tests/test_forbidden_imports.py`
analiza el código y falla si `src/` o `app/` importan SciPy, PuLP, OR-Tools u
otra librería de optimización. SciPy solo aparece en `tests/` y `scripts/`, para
comparar resultados.

**¿Cómo validan la entrada?** Celda por celda: vacías, textos no numéricos,
denominador cero, filas sin coeficientes y JSON con dimensiones inconsistentes.
El mensaje indica fila y columna, y no se resuelve nada hasta corregir.

**¿Cómo detectan los casos especiales?**

- Infactible: al terminar queda una artificial con valor positivo.
- No acotado: la entrante no tiene coeficientes positivos en su columna.
- Óptimos múltiples: una no básica con costo reducido cero lleva a otro punto
  óptimo distinto.
- Degenerado: una básica vale cero.

Cada caso muestra un mensaje en español, nunca un error del programa.

**¿Y si el problema tiene tres variables?** El método gráfico avisa «El método
gráfico no aplica: requiere exactamente dos variables»; el simplex sigue
funcionando.

**¿Qué bonificaciones buscan?** Las cuatro: dos métodos con comparación (+0.2),
fracciones exactas (+0.1), PDF (+0.1) y JSON (+0.1). El tope es +0.5 y solo
cuentan si todo lo obligatorio funciona.

## 5. Preguntas para el docente (llevar a clase)

1. ¿Acepta la M simbólica (`a + b·M`) en el paso a paso o espera un valor
   numérico de M?
2. Para la bonificación de fracciones, ¿basta con que todo el paso a paso sea
   exacto en fracciones y que los decimales sean una opción de presentación?
3. ¿El simplex revisado cuenta para la bonificación si comparte las reglas de
   decisión con la Gran M y solo cambia la representación (B⁻¹ en lugar del
   tablero)?
4. La condición 2b dice «en el equipo del estudiante o en la URL entregada».
   ¿La URL publicada es obligatoria o basta con el portátil?
5. ¿Cómo se entregan el manual y el video: archivo en el repositorio, enlace o
   plataforma del curso?
6. ¿El repositorio puede ser privado con acceso para el docente? ¿Qué usuario
   hay que invitar?
7. En la evaluación y en la sustentación, ¿los problemas se escriben en vivo o
   se entregan en un archivo? ¿Pueden traer coeficientes decimales o
   fraccionarios?
8. En problemas degenerados o con óptimos múltiples, ¿qué espera ver en la
   sensibilidad?
9. ¿Cómo quiere que se declare el uso de herramientas de IA?
10. ¿Cuáles son las fechas exactas de los sprints 3 y 5, y cuántos integrantes
    puede tener un equipo?

Anotar las respuestas aquí y ajustar la propuesta antes de entregarla.

## 6. Mapa de requisitos

| Requisito del enunciado | Dónde está en la app | Prueba que lo respalda |
|---|---|---|
| 1a. Max/Min, n variables, m restricciones ≤ ≥ =, lados derechos de cualquier signo, validación | Barra lateral y tablas editables; botones para agregar o quitar | `tests/test_model.py`, `tests/test_app.py` |
| Método propio (Gran M o revisado); librerías solo para verificar | `src/plapp/big_m.py`, `src/plapp/revised_simplex.py`, `src/plapp/simplex_rules.py` | `tests/test_forbidden_imports.py`, `tests/test_oracle_scipy.py` |
| 1b. Modo directo o paso a paso: forma estándar, entrante, razón mínima, saliente, pivote, tablero o B⁻¹ | Pestaña «Paso a paso» | `tests/test_app.py`, `tests/test_simplex_traces.py` |
| 1c. Valor de cada variable, Z, holgura o exceso | Pestaña «Resultado» | `tests/test_examples.py` |
| 1d. Gráfico con dos variables: región, vértices con Z, isoutilidad; aviso si n > 2 | Pestaña «Método gráfico» | `tests/test_graphical.py`, `tests/test_app.py` |
| 1e. Precios sombra, costos reducidos y rangos de c y b | Pestaña «Sensibilidad» | `tests/test_sensitivity.py` |
| 1f. Infactible, no acotado, múltiples y degenerado con mensaje claro | Pestaña «Resultado» y gráfico | `tests/test_examples.py`, `tests/test_big_m.py` |
| 1g. Interfaz gráfica obligatoria | Streamlit (`app/streamlit_app.py`) | `tests/test_app.py` |

Los pesos de la rúbrica de la entrega 1 son: entrada 10 %, método 15 %, paso a
paso 25 %, gráfico 20 %, sensibilidad 15 % e interfaz 15 %. El estado de cada
criterio está en `docs/plan.md`.

## 7. Preparación individual (unas 2 horas por integrante)

1. **Ejecutar (15 min).** `make setup` y `make run`. Abrir
   `http://localhost:8501` y resolver:
   - el ejemplo 1: x = (42, 16), Z = 3380;
   - el ejemplo 2 en modo Paso a paso: Z = 17/5;
   - el ejemplo 6: óptimos múltiples y segmento en el gráfico.
2. **Teoría (20 min).** Leer `docs/teoria.md`: Gran M, razón mínima, casos
   especiales, gráfico y sensibilidad.
3. **A mano (45 min).** Resolver el ejemplo 1 con tablero, en dos pivotes, y
   comparar cada iteración con la pestaña Paso a paso en fracciones. Repetir la
   primera iteración del ejemplo 2, que tiene artificiales.
4. **Código (40 min).** Leer el índice por módulo al inicio de
   `docs/sustentacion.md` y la sección del módulo que cada uno lidera. Ejecutar
   `make test` y abrir una prueba de ese módulo.
