# Ensayo de sustentación

Cinco problemas nuevos para practicar con la aplicación, un simulacro de 15
minutos y un banco de modificaciones en vivo ya probadas. Los problemas están en
`tests/fixtures/problems/ensayo_1.json` a `ensayo_5.json`: aparecen solos en
el selector **Ejemplo** de la barra lateral y en todas las pruebas
parametrizadas. Su campo `esperado` viene de SciPy (`"fuente": "scipy"`) y solo
lo leen las pruebas; la aplicación nunca lo consulta.

| Problema | Caso | Variables | Resultado | Verificación |
|---|---|---|---|---|
| Ensayo 1 | Infactible | 2 | Sin solución factible | `make verify` y gráfico |
| Ensayo 2 | No acotado | 2 | Z → −∞ por (0, 3) + t·(1, 1) | `make verify` y gráfico |
| Ensayo 3 | Óptimos múltiples | 2 | Z = 8 en el segmento (1, 3)–(3, 1) | `make verify`, SciPy y gráfico |
| Ensayo 4 | Degenerado | 3 | x = (3, 3, 0), Z = 15 | `make verify` |
| Ensayo 5 | =, ≥ y lado derecho negativo | 4 | x = (5/2, 3, 9/2, 0), Z = 37/2 | `make verify` |

En los cinco, `make verify FILE=tests/fixtures/problems/ensayo_n.json` imprime
«Gran M: coincide con SciPy» y «Simplex revisado: coincide con SciPy». En la
interfaz, AppTest resuelve cada uno con «Comparar ambos», en fracciones y en
decimales, y genera sus tres PDF (`tests/test_app.py`). Las capturas de los
tres gráficos se obtienen con `make ui-check` en `/tmp/plapp-ui`. Las cifras
de las iteraciones de este documento son las que muestra la pestaña Paso a paso
con Gran M; la numeración empieza en 0.

## Ensayo 1: infactible

```text
Min Z = 3x₁ + 2x₂
s. a.   x₁ + 2x₂ ≤ 4
        3x₁ + x₂ ≥ 15
        x₁, x₂ ≥ 0
```

**Solución verificada.** `make verify` informa «Estado: infactible» y ambos
métodos coinciden. El gráfico dice «El problema no tiene solución factible: la
región está vacía.» y dibuja R1 y R2 sin región sombreada.

**Qué mostrar.** Paso a paso: R1 recibe la holgura s1; R2, el exceso e2 y la
artificial a2 con costo +M. En la iteración 0 entra x1 (costo reducido
3 − 3M), las razones son 4 y 5, sale s1 y el pivote es 1. En la iteración 1
ninguna columna no artificial mejora la parte M y a2 sigue en 3: Z = 12 + 3M.
Mensaje: «El problema no tiene solución factible: no hay mejora en la parte M y
siguen positivas las artificiales a2.» Luego la pestaña Método gráfico.

**Preguntas probables.**

1. ¿Por qué una artificial positiva al final prueba infactibilidad? La parte M
   ya no puede bajar: a2 = 3 es lo menos posible. En el gráfico, el mayor valor
   de 3x₁ + x₂ con R1 es 12, en (4, 0), y R2 pide 15.
2. ¿Qué cambio mínimo lo vuelve factible? Bajar el lado derecho de R2 a 12:
   queda solo el punto (4, 0) con Z = 12 (comprobado con ambos métodos y SciPy).
3. ¿El gráfico decide la infactibilidad con la caja de dibujo? No: ninguna
   intersección de rectas y ejes cumple todas las restricciones, y en x ≥ 0 una
   región no vacía siempre tiene un vértice (`src/plapp/graphical.py:100`).

## Ensayo 2: no acotado

```text
Min Z = x₁ − 2x₂
s. a.   x₁ + x₂ ≥ 2
        −x₁ + x₂ ≤ 3
        x₁, x₂ ≥ 0
```

**Solución verificada.** `make verify` informa «Estado: no_acotado» y ambos
métodos coinciden. El gráfico muestra los vértices (0, 2) con Z = −4, (2, 0)
con Z = 2 y (0, 3) con Z = −6, la flecha «Mejora ilimitada: (1, 1)» y los avisos
de las direcciones (1, 0) y (1, 1).

**Qué mostrar.** Iteración 0: entra x2 (−2 − M), razones 2 y 3, sale a1,
pivote 1. Iteración 1: entra e1 (−2); la fila R1 se excluye porque su
coeficiente es negativo y sale s2 con razón 1. Iteración 2: entra x1 (−1) y
ningún coeficiente de su columna es positivo. Mensaje: «… Z decrece sin límite
a lo largo de (x1, x2) = (0, 3) + t·(1, 1), t ≥ 0.»

**Preguntas probables.**

1. ¿Cómo se comprueba la dirección (1, 1)? En R1, 1 + 1 = 2 ≥ 0; en R2,
   −1 + 1 = 0 ≤ 0; d ≥ 0. Además c·d = 1 − 2 = −1 < 0: Z baja en Min.
2. ¿Una región no acotada implica Z no acotada? No. (1, 0) también es una
   dirección de la región, pero c·d = 1 > 0 empeora Z en Min. Ver el ensayo 3.
3. ¿Qué cambio lo vuelve acotado? Con c₂ = −1, c·(1, 1) = 0 y la app informa
   «Z = -3 en todo el rayo desde (0, 3), con dirección (1, 1); el parámetro es
   no negativo.». Agregando
   x₂ ≤ 5, el óptimo es (2, 5) con Z = −8. Ambos casos coinciden con SciPy.

## Ensayo 3: óptimos múltiples

```text
Min Z = 2x₁ + 2x₂
s. a.   x₁ + x₂ ≥ 4
        x₁ + 3x₂ ≥ 6
        3x₁ + x₂ ≥ 6
        x₁, x₂ ≥ 0
```

**Solución verificada.** SciPy da (1, 3) y Z = 8, y ambos métodos coinciden.
Para los extremos del segmento se resolvió con SciPy el mínimo y el máximo de
x₁ sujeto además a 2x₁ + 2x₂ ≤ 8: resultan (1, 3) y (3, 1). El gráfico resalta
ese segmento, marca (0, 6) y (6, 0) con Z = 12, dibuja la isoutilidad Z = 8
sobre R1 y avisa las direcciones (0, 1) y (1, 0).

**Qué mostrar.** Tres artificiales. Iteración 0: x1 y x2 empatan en 2 − 5M y
entra x1 por menor índice; razones 4, 6 y 2, sale a3, pivote 3. Iteración 1:
entra x2 (4/3 − 10/3M), razones 3, 3/2 y 6, sale a2, pivote 8/3. Iteración 2:
entra e2 (1/2 − 1/4M), razones 4, excluida y 12, sale a1, pivote 1/4. Estado 3:
óptimo (1, 3) y e3, no básica, tiene cⱼ − zⱼ = 0. Resultado: «Se encontró una
solución óptima. Z = 8 en todo el segmento entre (1, 3) y (3, 1).», con la
solución alterna (3, 1). Sensibilidad: precio sombra de R1 = 2 y rango de c1
entre 2 y 6.

**Preguntas probables.**

1. ¿Cómo detecta el simplex el segundo óptimo? e3 no básica con costo reducido
   0; al pivotar sobre ella se llega a (3, 1) con el mismo Z
   (`src/plapp/simplex_rules.py:215`).
2. ¿Por qué Z es finito si la región no es acotada? Las direcciones (1, 0) y
   (0, 1) tienen c·d = 2 > 0: empeoran Z en Min.
3. ¿Por qué el rango de c₁ empieza justo en 2? Con c₁ < 2 el único óptimo pasa
   a (3, 1); en c₁ = 2 empatan. Con c = (2, 3) la app da (3, 1) y Z = 9.

## Ensayo 4: degenerado

```text
Max Z = 2x₁ + 3x₂ + x₃
s. a.   x₁ + x₂ + x₃ ≤ 6
        x₁ − x₂ ≥ 0
        2x₂ + x₃ ≤ 6
        x₁, x₂, x₃ ≥ 0
```

**Solución verificada.** `make verify` da x = (3, 3, 0) y Z = 15, y ambos métodos
coinciden. Tiene tres variables: el gráfico no aplica.

**Qué mostrar.** Forma estándar: s1, e2 con a2 (costo −M por ser Max) y s3;
la base inicial s1, a2, s3 vale (6, 0, 6). Iteración 0: entra x1 (2 + M),
razones 6, 0 y excluida; sale a2 con razón 0. Es un pivote degenerado: el punto
no cambia y Z sigue en 0. Iteración 1: entra x2 (5), razones 3, excluida y 3;
empatan s1 y s3 y sale s1 por menor índice. Estado 2: óptimo con s3 básica en 0.
Notas: «Degeneración: hubo empate en la razón mínima; se aplicó Bland para la
salida.» y «Degeneración: variables básicas en 0: s3.». Resultado: «Se detectó
degeneración.». Sensibilidad: aviso «Degeneración: los precios sombra pueden no
ser únicos y un extremo del rango puede coincidir con el valor actual.», precios
5/2, −1/2 y 0, y rango de R1 entre 0 y 6.

**Preguntas probables.**

1. ¿Qué significa la razón 0? a2 ya vale 0: x1 entra con valor 0, la base
   cambia y el punto no.
2. ¿Por qué `make verify` muestra otros precios sombra (2, 0, 1/2)? Con una base
   degenerada hay varios duales óptimos; ambos cumplen b·y = 15. Son derivadas
   por lados distintos: bajar R1 de 6 a 5 reduce Z en 5/2, hasta 25/2 (precio
   de la app, rango hasta 6); subirlo a 7 solo aumenta Z en 2, hasta 17 (precio
   de SciPy). Ambos valores se comprobaron resolviendo los problemas modificados.
3. ¿Puede ciclar? `src/plapp/simplex_rules.py:27` activa Bland al repetirse una
   base y la salida siempre desempata por menor índice. La prueba del ejemplo
   de Beale lo demuestra.

## Ensayo 5: cuatro variables con =, ≥ y lado derecho negativo

```text
Min Z = 2x₁ + 3x₂ + x₃ + 4x₄
s. a.   x₁ + x₂ + x₃ + x₄ = 10
        x₁ − x₃ ≥ −2
        2x₂ + x₄ ≥ 5
        x₁ + x₃ ≤ 7
        x₁, x₂, x₃, x₄ ≥ 0
```

**Solución verificada.** `make verify` da x = (5/2, 3, 9/2, 0), Z = 37/2 y
precios sombra 3, 1/2, 0 y −3/2; ambos métodos coinciden. El gráfico informa
«El método gráfico no aplica: requiere exactamente dos variables.»

**Qué mostrar.** Forma estándar: «R2 tenía lado derecho negativo (-2): se
multiplicó por −1 y ≥ pasó a ≤.»; R1 recibe a1, R2 la holgura s2, R3 e3 y a3,
R4 la holgura s4. Base inicial a1, s2, a3, s4. Iteraciones: entra x2 y sale a3
(pivote 2); entra x3 y sale s2 (pivote 1); entra x1 y sale s4 (pivote 2); entra
e3 y sale a1 (pivote 1/2); el estado 4 es óptimo. En la iteración 1, x1 y x3
tienen la misma parte M (−M) y gana x3 por su parte real menor (1 − M frente a
2 − M). Resultado: R3 con exceso 1. Sensibilidad: R1 = 3 desde 19/2, R2 = 1/2
entre −7 y 7, R4 = −3/2 entre 2 y 15/2; x4 tiene costo reducido 1.

**Preguntas probables.**

1. ¿Cómo se lee el precio de R2 si su fila se multiplicó por −1? Respecto al
   lado derecho original: pasar de −2 a −1 sube Z en 1/2, de 37/2 a 19
   (comprobado). `row_signs` guarda ese signo (`src/plapp/standard_form.py:19`).
2. ¿Por qué R1 necesita artificial? Una igualdad no tiene holgura que sirva
   como básica inicial con coeficiente +1.
3. ¿Qué pasa si R4 sube a 8? Sale del rango [2, 15/2] y la predicción lineal,
   37/2 − 3/2 = 17, ya no vale: la app da 71/4, igual que con 15/2.

## Simulacro de 15 minutos

Practicar con un problema que el equipo no conozca: uno de estos cinco escrito
a mano, sin cargar el JSON, o uno inventado por otro integrante. Quien explica
no maneja el computador. Cada integrante debe pasar por todos los papeles.

| Tiempo | Actividad | Qué comprobar |
|---|---|---|
| 0:00–1:30 | Leer el enunciado en voz alta: sentido, n, m, signos y lados derechos negativos. | Todos coinciden en el modelo antes de escribir. |
| 1:30–4:00 | Escribirlo: Sentido, Agregar o Quitar, coeficientes, Signo y Lado derecho. | El «Resumen del problema validado» coincide con el enunciado. |
| 4:00–4:30 | Pulsar Resolver; si hay un error, leer su ubicación y corregir. | No queda ningún mensaje de error. |
| 4:30–8:30 | Paso a paso con Gran M: transformaciones, base inicial y cada iteración. | Entrante y por qué, razones y exclusiones, saliente y pivote. |
| 8:30–10:00 | Pestaña Resultado. | Estado, valores, Z, holguras o excesos y notas. |
| 10:00–12:00 | Pestaña Sensibilidad. | Un precio sombra con su rango, un costo reducido y qué pasa fuera del rango. |
| 12:00–13:30 | Gráfico si hay dos variables; si no, Comparar ambos. | Región, vértices e isoutilidad, o bases coincidentes. |
| 13:30–15:00 | Contrastar y responder. | Comparar ambos o `make verify` con el JSON guardado. |

Si algo no se entiende, se explica con la tabla en pantalla, no con «la app lo
hace». Al terminar, anotar las preguntas que no se respondieron y repasarlas en
`docs/sustentacion.md`.

## Banco de modificaciones en vivo

Cada cambio se aplicó en una copia temporal y se ejecutó la suite completa
(546 pruebas en la base). Procedimiento usado, que también sirve para ensayar:

```bash
git worktree add --detach /tmp/plapp-mod HEAD
cd /tmp/plapp-mod && uv sync --locked
# editar el archivo indicado
uv run pytest -q
cd - && git worktree remove --force /tmp/plapp-mod
```

Los cambios no quedaron en la rama. Las líneas citadas corresponden al código
actual. Entre paréntesis, el número de pruebas que fallan sobre 546.

### Mod. 1: usar siempre Bland

- **Dónde:** `src/plapp/simplex_rules.py:75`.
- **Cambio:** `if bland:` por `if True:` para que la entrante sea siempre el
  menor índice con costo reducido favorable.
- **Resultado real (30 fallan):** 19 de las 21 trazas congeladas de
  `tests/test_simplex_traces.py`, tres pruebas de `tests/test_big_m.py`
  (traza del ejemplo 1, segmento y básica nula de los ejemplos 6 y 7, y Beale)
  y ocho de AppTest de
  los ejemplos 6 y 7. Z no cambia en ningún fixture. El ejemplo 6 termina en
  (3, 1) y el mensaje dice «entre (3, 1) y (0, 5/2)»; en el ejemplo 7 la
  básica nula pasa a ser s1. En el ejemplo 2 la secuencia es la misma, pero la
  justificación de la entrada cambia de texto.
- **Qué ajustar:** las trazas se regeneran solo si el cambio es intencional;
  las pruebas de los ejemplos 6 y 7 deben aceptar el otro extremo.

### Mod. 2: desempatar la razón mínima por el mayor índice

- **Dónde:** `src/plapp/simplex_rules.py:191`.
- **Cambio:** `min(tied, key=lambda i: basis[i])` por `max(...)`. Actualizar
  también el texto de `src/plapp/simplex_rules.py:194`, que menciona Bland.
- **Resultado real (18 fallan):** ocho trazas congeladas (ejemplo 7, extras 6
  y 7, los cuatro casos C1 y Beale), cuatro AppTest del ejemplo 7, el aviso de
  fila redundante en la UI, dos de redundancia en `tests/test_sensitivity.py`,
  el PDF decimal de certificados especiales y dos de `tests/test_big_m.py`.
  Con esta regla el ejemplo de Beale termina en 3 estados sin repetir base.
- **Qué explicar:** cualquier fila empatada es válida para un pivote, pero el
  teorema de Bland exige menor índice en la entrada y en la salida; con `max`
  se pierde la garantía contra ciclos.

### Mod. 3: dos decimales por defecto

- **Dónde:** `app/streamlit_app.py:860`.
- **Cambio:** `value=4` por `value=2` en «Número de decimales».
- **Resultado real (2 fallan):** `test_decimal_transformation_and_fractional_result`
  (espera `Z = 0.1667`, ahora `0.17`) y `test_pdf_requires_solution_and_reports_failure`
  (espera que el PDF reciba 4 decimales).
- **Qué ajustar:** esos dos valores esperados en `tests/test_app.py`.

### Mod. 4: margen de la caja del gráfico

- **Dónde:** `src/plapp/graphical.py:127` (y el comentario de la línea 116).
- **Cambio:** margen `Fraction(6, 5)` por `Fraction(3, 2)`.
- **Resultado real (2 fallan):** `test_example_one_vertices` y
  `test_unbounded_objective` de `tests/test_graphical.py`, que fijan la caja
  exacta de los ejemplos 1 y 5. Vértices, Z y certificados no cambian.
- **Qué ajustar:** las cajas esperadas, por ejemplo (18/5, 24/5) del ejemplo 5
  pasa a (9/2, 6).

### Mod. 5: agregar un mensaje con el número de pivotes

- **Dónde:** `app/streamlit_app.py:183`, al final del `else` que escribe el
  mensaje del método, dentro de `render_solution`.
- **Cambio:** agregar
  `pivots = sum(1 for state in solution.iterations if state.pivot is not None)`
  y `st.write(f"Pivotes realizados: {pivots}")`, más una prueba en
  `tests/test_app.py` que cargue el ejemplo 2 y espere «Pivotes realizados: 3».
- **Resultado real (0 fallan):** 547 pasan, incluida la prueba nueva. Ninguna
  prueba existente compara la lista completa de textos del resultado.
- **Qué explicar:** el estado final no tiene pivote; por eso se cuentan las
  iteraciones con `pivot` y no `len(solution.iterations)`.

### Mod. 6: columna «Valor actual» en sensibilidad

- **Dónde:** `app/streamlit_app.py:776`, el diccionario de cada fila de las
  tablas de precios sombra y costos reducidos.
- **Cambio:** agregar
  `"Valor actual": number(solution.slacks[name] if prefix == "b" else solution.values[name])`.
  En precios sombra muestra la holgura o el exceso; en costos reducidos, el
  valor de la variable. Así se ve la holgura complementaria: precio no nulo con
  holgura 0, costo reducido no nulo con variable en 0.
- **Resultado real (0 fallan):** 546 pasan. Ninguna prueba fija las columnas de
  esas dos tablas, así que el cambio queda sin cobertura.
- **Qué ajustar:** agregar una prueba en `tests/test_app.py` que, con el
  ejemplo 2, busque la tabla «Precio sombra ∂Z*/∂b» y espere en «Valor actual»
  0, 1 y 0 (R1 igualdad, R2 exceso 1, R3 activa).

### Mod. 7: resaltar el pivote en verde

- **Dónde:** `app/streamlit_app.py:236` y `app/streamlit_app.py:284`.
- **Cambio:** `background-color: #fef08a` por `background-color: #bbf7d0`.
- **Resultado real (20 fallan):** las 14 pruebas de AppTest en modo Paso a paso
  de los ejemplos 1 a 7 y 6 de `test_comparison_and_revised_evidence`; todas
  comprueban el estilo `background-color: #fef08a` de la celda pivote.
- **Qué ajustar:** el color esperado en `tests/test_app.py`. Conviene definirlo
  una sola vez en una constante para que el cambio sea de una línea.
