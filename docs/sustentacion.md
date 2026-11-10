# Guía de sustentación

Esta guía acompaña los paquetes implementados. El equipo debe recorrer las
pruebas y practicar las modificaciones; comprender esta guía no reemplaza leer
el código. El estado de los paquetes está en `docs/plan.md`; los problemas de
ensayo, el simulacro y el banco de modificaciones probadas están en
`docs/ensayo-sustentacion.md`.

## Índice por módulo

Cada integrante debe poder explicar cualquier fila en dos minutos y hacer su
ejercicio en vivo. «Mod. n» remite al banco de `docs/ensayo-sustentacion.md`,
donde cada cambio se probó en una copia temporal y se anotaron las pruebas que fallan.

| Archivo | Qué explicar en dos minutos | Sección | Preguntas probables | Ejercicio |
|---|---|---|---|---|
| `src/plapp/__init__.py` | Solo marca el paquete `plapp` del layout `src/`; no importa ni ejecuta nada. | Índice | ¿Por qué `uv run` encuentra el paquete? | Importar `plapp.model` desde `uv run python`. |
| `src/plapp/mvalue.py` | a + bM con dos Fraction; el orden compara primero b. | P1: M simbólica | ¿Por qué no M = 10⁶? ¿Por qué no se permite M·M? | Comprobar que −M + 10¹⁰⁰ < 0. |
| `src/plapp/linalg.py` | Identidad, productos e inversa por Gauss-Jordan con intercambio de filas. | P1: Álgebra lineal | ¿Cuándo se declara B singular? | Invertir una B cuyo primer pivote es cero. |
| `src/plapp/model.py` | `parse_number` acepta 2, −3, 2,5, 2.5 y 2/5; `validate` acumula errores por celda. | Modelo y JSON | ¿Por qué Fraction y no float? ¿Por qué acumular errores? | Rechazar `1e3` (hoy se acepta). |
| `src/plapp/io_json.py` | Números como texto exacto; carga y guardado con errores en español. | Modelo y JSON | ¿Por qué `"2/5"` entre comillas? ¿La app lee `esperado`? | Guardar, editar y volver a cargar un JSON. |
| `src/plapp/result.py` | Contratos inmutables que comparten métodos, UI, PDF y sensibilidad. | Contratos | ¿Por qué el estado anterior al pivote? ¿Por qué multiplicidad no es un estado? | Agregar un campo con valor por defecto. |
| `src/plapp/standard_form.py` | b ≥ 0, holguras, excesos y artificiales; `row_signs` recuerda filas negadas. | P1: Forma estándar | ¿Por qué ≥ pasa a ≤ al negar? | Variable llamada s1 y nombre s1_1. |
| `src/plapp/simplex_rules.py` | Entrada, razón mínima, salida, Bland, infactibilidad, no acotación y alternativas. | P2; P6, paso 1 | ¿Por qué Bland también al entrar? ¿Cómo se prueba la infactibilidad? | Mod. 1 (Bland siempre) y Mod. 2 (desempate). |
| `src/plapp/big_m.py` | Tablero completo con costos simbólicos; ciclo con límite de 1000 estados. | P2 | ¿Por qué canonizar la fila Z? | Seguir a mano el ejemplo 2. |
| `src/plapp/revised_simplex.py` | B⁻¹ actualizada con E; solo calcula d = B⁻¹aⱼ de la entrante. | P6, pasos 2–3 | ¿Por qué no invertir B en cada pivote? | Reconstruir E del segundo pivote del ejemplo 2. |
| `src/plapp/sensitivity.py` | Reconstruye B desde `final_basis`; precios, costos reducidos, rangos y textos. | P5; R | ¿Por qué un dato a la vez? ¿Por qué SciPy da otros precios en degeneración? | Mod. 6 (columna «Valor actual»). |
| `src/plapp/graphical.py` | Vértices exactos, conos de recesión y caja solo de dibujo. | P4; V | ¿Región no acotada implica Z no acotada? | Mod. 4 (margen de la caja). |
| `src/plapp/formatting.py` | Fracciones, decimales y a + bM; expresiones sin ceros ni unos. | Formato | ¿Cambiar el formato recalcula? | Escribir siempre `1·x1`. |
| `src/plapp/export_pdf.py` | PDF A4 horizontal desde la solución ya calculada, con DejaVu Sans. | P7 | ¿Exportar vuelve a resolver? | Cuatro columnas de datos por bloque. |
| `app/streamlit_app.py` | Estado de sesión, edición, pestañas y errores contenidos en mensajes. | P3; P6; V | ¿Qué pasa al editar un dato? ¿Por qué nunca hay traceback? | Mod. 3, Mod. 5 y Mod. 7. |
| `scripts/verify.py` | Oráculo SciPy/HiGHS fuera de la app; compara estado, Z y factibilidad. | Oráculo y estrés | ¿Por qué repetir sin presolve? | `make verify` con un ensayo modificado. |
| `scripts/stress.py` | Miles de problemas aleatorios con filas repetidas y lados derechos nulos. | Oráculo y estrés | ¿Qué cuenta como diferencia? | Cambiar la probabilidad de lado derecho 0. |
| `scripts/check_ui.py` | Chromium real: salud, gráficos, modos, formatos, PDF y capturas del manual. | R; V | ¿Qué agrega frente a AppTest? | Agregar un ejemplo a la lista de gráficos. |
| `scripts/build_manual.py` | Markdown del manual a PDF A4 con Chromium; falla con más de 5 páginas. | Oráculo y estrés | ¿Por qué no se edita el PDF a mano? | Cambiar el ancho de una captura. |

## P1: núcleo exacto

### M simbólica

`src/plapp/mvalue.py:8` representa a + bM con dos Fraction. Sumar y restar opera
por componente; multiplicar o dividir solo admite un escalar entero o Fraction.
El orden compara primero b: −M + 10¹⁰⁰ sigue siendo negativo. No se multiplica
M por M porque el resultado no cabe en esta representación. Cuando b = 0,
la igualdad y el hash coinciden con los del escalar a.

### Álgebra lineal

`src/plapp/linalg.py:16` contiene identidad; `matvec` en
`src/plapp/linalg.py:30`, `vecmat` en `src/plapp/linalg.py:40` y `matmul` en
`src/plapp/linalg.py:51`, productos;
`src/plapp/linalg.py:65`, inversa por Gauss-Jordan.
Para invertir se reduce [B | I]; si el pivote es cero, se intercambian filas.
Si toda la columna restante es cero, B es singular. Las pruebas verifican
B·B⁻¹ = B⁻¹·B = I con fracciones y con intercambio de filas.

### Forma estándar y ejemplo 2

`src/plapp/standard_form.py:19` mantiene el sentido original de Z y el orden:
originales, holguras/excesos por fila, artificiales por fila. La base inicial
es identidad. `StandardForm.row_signs[i]` conserva el signo aplicado a Ri
para recuperar después los precios sombra originales.

El ejemplo 2 queda, con columnas (x1, x2, e2, s3, a1, a2):

1. R1: 3x1 + x2 + a1 = 3.
2. R2: 4x1 + 3x2 − e2 + a2 = 6.
3. R3: −x1 − 2x2 ≥ −4 se multiplica por −1; x1 + 2x2 + s3 = 4.
4. Base inicial (a1, a2, s3); valores (3, 6, 4).
5. Min Z = 4x1 + x2 + M·a1 + M·a2; signos de fila (1, 1, −1).

Los nombres auxiliares reciben sufijo si coinciden con nombres del usuario.

Preguntas para practicar:

1. ¿Por qué no escoger M = 10⁶? Podría no dominar los datos; el orden simbólico
   garantiza esa dominancia sin redondear.
2. ¿Por qué invertir ≥ al negar una fila? Multiplicar una desigualdad por un
   número negativo cambia su sentido.
3. ¿Por qué el exceso no forma la base inicial? Su coeficiente es −1; la
   artificial aporta +1 y una básica inicialmente no negativa.
4. ¿Por qué guardar el signo de fila? La sensibilidad debe derivar respecto
   al lado derecho original, no al normalizado.
5. ¿Qué demuestra el producto con la inversa? Que la reducción exacta conserva
   las ecuaciones y permite recuperar x_B = B⁻¹b.

Ejercicio: cargar una variable llamada s1 y comprobar el nombre s1_1 de la
holgura; después cambiar una restricción ≥ con b negativo y explicar su base.

## P2: método de la Gran M

`src/plapp/simplex_rules.py:124` canoniza cⱼ − zⱼ con los costos de la base actual;
`src/plapp/big_m.py:14` guarda el estado anterior al pivote y Z = c_B·b.
`src/plapp/simplex_rules.py:135` hace el pivote con Fraction,
`src/plapp/simplex_rules.py:155` calcula las razones y explica exclusiones, y
`src/plapp/simplex_rules.py:182` decide
la salida. La entrada usa el mayor costo positivo en Max o el menor negativo
en Min, con desempate por índice. El ciclo principal guarda bases visitadas:
al repetir una, cambia permanentemente a Bland, incluida la entrada.

La condición de infactibilidad se comprueba antes de buscar una columna sin
saliente: si ninguna parte M permite mejorar y aún hay una artificial positiva,
la suma de artificiales ya no puede bajar a cero. Esto evita llamar no acotado
a un modelo infactible que además tenga una dirección favorable en Z real.

### Continuación de la traza del ejemplo 2

Las columnas siguen siendo (x1, x2, e2, s3, a1, a2).

| Estado antes del pivote | Base | Valores básicos | Z | Decisión |
|---|---|---|---|---|
| 0 | a1, a2, s3 | 3, 6, 4 | 9M | Entra x1, sale a1, pivote 3 |
| 1 | x1, a2, s3 | 1, 2, 3 | 4 + 2M | Entra x2, sale a2, pivote 5/3 |
| 2 | x1, x2, s3 | 3/5, 6/5, 1 | 18/5 | Entra e2, sale s3, pivote 1 |
| 3 | x1, x2, e2 | 2/5, 9/5, 1 | 17/5 | Todos los costos reducidos son ≥ 0: termina |

En el estado 0, r = (4 − 7M, 1 − 4M, M, 0, 0, 0): se restan M veces
R1 y R2 de la fila c − z. Las razones de x1 son (1, 3/2, 4).
En el estado 1, x2 tiene r = −1/3 − 5M/3; sus razones son (3, 6/5, 9/5).
Ya sin artificiales positivas, e2 tiene costo reducido −1/5 y razones
(3, excluida por coeficiente −3/5, 1). Su entrada reduce Z de 18/5 a 17/5.
R2 original queda con exceso 1; R1 y R3 son activas. La fila Z final coincide
con 4·(2/5) + 9/5 = 17/5.

Para el ejemplo 1, las entradas/salidas son (x2, s2) y (x1, s1), con Z en
cada estado 0, 2400 y 3380. El ejemplo 7 termina con x1 básica en cero.

### Casos especiales y contratos

`src/plapp/simplex_rules.py:215` busca un punto óptimo distinto, recorriendo bases
adyacentes de paso cero si el primer pivote es degenerado. Sin coeficientes
positivos, un costo reducido cero certifica un rayo óptimo. Se guarda un
segundo punto en `alternative_solutions` y, para rayos, la dirección en
`alternative_rays`. El segmento certificado no pretende enumerar toda una
cara óptima de dimensión mayor que uno.

Una artificial nula sale con una columna no artificial de coeficiente no cero,
incluso negativo: el paso cero conserva la factibilidad. Si no existe esa
columna, la fila transformada es redundante. Se conserva la artificial nula
como testigo de redundancia para mantener B cuadrada e invertir las columnas
de la forma estándar original; esto queda avisado en las notas. P5 deberá
tratar esa redundancia antes de interpretar su precio sombra.

`Iteration.objective_value` contiene Z simbólica y `Iteration.notes` explica
canonización, Bland y limpieza. `Solution.notes` informa degeneración y
redundancia; todos son campos opcionales con valor por defecto. La última
iteración óptima o infactible tiene `entering_variable=None` y explica la
terminación. En no acotación, el último estado conserva la columna candidata,
sus exclusiones y el mensaje, sin duplicar el tablero.

La protección limita a 1000 los estados del solver y a 1000 las bases de
búsqueda de alternativas. Alcanzar el límite produce un error comprensible;
nunca se presenta como óptimo único un análisis de multiplicidad incompleto.

Preguntas para practicar:

1. ¿Por qué canonizar Z? La base actual ya aporta costos; c sin restar c_B·A
   no mide el cambio marginal al introducir una no básica.
2. ¿Por qué excluir coeficientes negativos? La básica aumenta al crecer la
   entrante y no limita su paso.
3. ¿Por qué usar Bland también al entrar? Desempatar solo la salida no impide
   el ciclo de Beale; su prueba repite la base tras seis pivotes.
4. ¿Basta un costo reducido cero para multiplicidad? No: exigir un segundo
   punto distinto o una dirección factible no nula en las variables originales.
5. ¿Cómo se comprueba la inversa final? Las pruebas verifican B·B⁻¹ = I,
   B⁻¹b igual al lado derecho final y B⁻¹A igual al tablero final.

Ejercicio: cambiar la selección de entrada para usar Bland siempre (Mod. 1 del
ensayo). Explicar qué secuencias de pivotes cambian y por qué se conservan Z y
factibilidad.

## P3: presentación de resultados y paso a paso

`app/streamlit_app.py:121` centraliza el formato numérico elegido. El estado
de sesión conserva el modelo exacto y sus soluciones: cambiar a decimales no
vuelve a resolver ni cambia Fraction por float. La función de formato está en
`src/plapp/formatting.py:12` y usa Decimal solo para presentar.

`app/streamlit_app.py:164` muestra variables, Z, y por restricción su tipo
original: holgura, exceso o igualdad. Aunque R3 se normalice a ≤ en el ejemplo 2,
en el resultado sigue siendo un exceso de la restricción original ≥.
`app/streamlit_app.py:140` presenta una solución alterna y el segmento o rayo
certificado; construye las coordenadas con el formato elegido. Las notas del
solver identifican las variables básicas nulas.

`app/streamlit_app.py:350` devuelve inmediatamente en modo Directo; Paso a paso
presenta forma estándar, costos simbólicos, transformaciones y base inicial.
`app/streamlit_app.py:288` presenta cada estado y sus razones y justificaciones.
`app/streamlit_app.py:209` construye el tablero rotulado por variables básicas,
con fila cⱼ − zⱼ y Z. Pandas Styler resalta solo la celda cuya posición ya
calculó el solver. El visor no decide entradas, salidas ni pivotes.

Para simplex revisado, el mismo visor recibe B⁻¹, rotula sus filas por básicas
y columnas por restricciones originales, y muestra costos reducidos y Z.
Las pruebas verifican también x_B, y y la columna d del método revisado real,
en ambos modos y formatos, con los ejemplos 2, 5 y 6.

Al cargar el ejemplo 2, escoger Paso a paso y Resolver, comprobar las cuatro
bases de la tabla de P2. En el estado 1, la fila x1 tiene lado derecho 1 y la
fila a2, 2; la celda de entrada x2/salida a2 vale 5/3 y está resaltada. En el
estado final se muestran x1 = 2/5, x2 = 9/5, exceso de R2 = 1 y Z = 17/5.
Con un máximo de cuatro decimales deben verse 0.4, 1.8, 1 y 3.4.

Preguntas para practicar:

1. ¿Dónde se decide qué celda resaltar? En `Iteration.pivot`; el visor solo
   aplica el estilo a esa fila y columna, con índices internos desde cero.
2. ¿Por qué el resultado de R3 se llama exceso? Se reporta la restricción
   original; la holgura s3 pertenece únicamente a su forma normalizada.
3. ¿Qué ocurre al cambiar el formato? Se reutilizan las mismas fracciones y
   se redondea únicamente el texto presentado.
4. ¿Qué ocurre al editar el problema? `invalidate` descarta resultados para
   evitar mostrar una solución de datos anteriores.
5. ¿Cómo se verifican los casos especiales sin navegador? AppTest carga y
   resuelve los ejemplos en ambos modos y formatos; comprueba mensajes,
   encabezados, base, Z y el estilo enviado para el pivote.

Ejercicio: cambiar el número de decimales y demostrar que `Solution.values`
sigue conteniendo Fraction; después comparar el segmento óptimo del ejemplo 6.

Documentación de presentación consultada para esta implementación:
[Streamlit, st.table](https://docs.streamlit.io/develop/api-reference/data/st.table),
[Streamlit, AppTest](https://docs.streamlit.io/develop/concepts/app-testing/cheat-sheet),
[pandas, Styler.apply](https://pandas.pydata.org/docs/reference/api/pandas.io.formats.style.Styler.apply.html).

## C: correcciones de redundancia y terminación

Una artificial que sale de la base nunca vuelve a entrar. La terminación también se refiere solo a columnas no artificiales. Las candidatas
no básicas excluyen siempre las columnas artificiales, tanto para la mejora
en M como para la mejora real. Equivale a descartar su columna en fase I.
La limpieza de una artificial nula puede usar un pivote negativo con paso cero;
sin esta exclusión, su antiguo costo reducido favorable permite reentrar y
repetir limpieza indefinidamente. Bland no corrige ese ciclo porque la limpieza
no es un pivote simplex elegido por costo. La primera iteración explica la regla.

En no acotación se conserva un solo estado con entrante y razones excluidas.
La dirección completa es d_entrante = 1, d_B = −columna_entrante y cero en las
demás no básicas; luego se proyecta sobre las variables originales. El origen
factible y la dirección exacta quedan en `Solution.unbounded_origin` y
`Solution.unbounded_direction`. En el ejemplo 5 se obtiene (1, 0) + t·(1, 1),
t ≥ 0; Z aumenta 2t. La columna entrante puede ser una holgura: la proyección
sigue dando una dirección verificable para las variables del usuario.

El tablero rotula «cⱼ − zⱼ (Z en lado derecho)»: esa celda contiene Z, no −Z.
El formato decimal elimina ceros finales y normaliza −0 a 0; la precisión
seleccionada es un máximo, no un número obligatorio de cifras.

El oráculo repite sin presolve los estados 2, 3 y 4. Si cambia el estado,
exige que una segunda corrida sin presolve lo confirme; si estas dos corridas
no concuerdan o no alcanzan un estado verificable, lanza
`OracleInconclusiveError` («Oráculo no concluyente»). Se acepta así el cambio
2 a 3 del extra 7 sin escoger arbitrariamente entre estados persistentes.
Solo las pruebas y scripts usan SciPy; jamás decide un estado de la aplicación.

Para repetir el estrés: `uv run python -m scripts.stress --seed 20261110 --count 3000`.
La generación incluye filas duplicadas o escaladas por 1, 2 y −1 y lados
derechos frecuentemente nulos. El signo de la desigualdad se invierte al negar
una fila. Se cuentan por separado errores, diferencias y oráculos excluidos.

Preguntas: ¿por qué una artificial no reentra?, ¿por qué Bland no evitaba la
limpieza cíclica?, ¿cómo verificar a·d y c·d en un rayo?, ¿por qué la caja del
gráfico no puede certificar no acotación?, ¿cuándo descartar un oráculo numérico?

El estrés también descubrió que las permutaciones de filas de una misma base
agotaban las 1000 bases de búsqueda de alternativas. Se deduplican por conjunto
de columnas básicas: representan el mismo punto y los mismos vecinos, con
independencia del orden del tablero. Se mantiene el límite de 1000 bases
realmente distintas y una regresión con seis filas activas redundantes.

## P4: método gráfico exacto e independiente

`graphical_method` no llama a Gran M, forma estándar ni SciPy. Interseca las
rectas originales y los ejes con Cramer. Un determinante cero indica paralelas
o coincidentes: no hay punto aislado que agregar. Filtra todas las
intersecciones con las restricciones originales y x ≥ 0, deduplica fracciones
y ordena el contorno mediante productos cruzados exactos. Las igualdades pueden
dejar un segmento o un punto. En el cuadrante no negativo toda región no vacía
contiene un vértice; por eso la ausencia de intersecciones factibles prueba vacío.

Para certificar recesión se prueban (1, 0), (0, 1) y ambas perpendiculares a
cada restricción. Se exige d ≥ 0, d ≠ 0 y a·d ≤ 0, ≥ 0 o = 0 según la fila.
Se normaliza cada dirección por su componente máxima. Si no hay direcciones,
la región es acotada. Si alguna mejora c·d en el sentido de Z, el objetivo es
no acotado. De lo contrario se evalúa Z en los vértices; dos empates certifican
un segmento y una dirección con c·d = 0 certifica un rayo óptimo.

La caja tiene límites separados por eje: máximo entre 1, coordenadas de
vértices e interceptos no negativos, con 20 % de margen; desde V, una región no
acotada amplía esa referencia con sus rayos (sección V). Se interseca la región
con esa caja solo para sombrear; sus esquinas nunca se agregan a los vértices
reales. También se recortan rectas verticales, isoutilidad y rayos. Los ejes
participan en la geometría; `lines` contiene las restricciones rotuladas.
Una región vacía conserva rectas para que la interfaz pueda explicarla.

Ejemplo 1: vértices (0, 0), (50, 0), (42, 16), (0, 30), con Z = 0, 2500,
3380, 2400. R3: x2 ≤ 40 se dibuja sin crear un vértice. Ejemplo 5: d = (1, 1)
es factible y c·d = 2; la flecha termina en el borde del recorte, sin afirmar
que allí acaba la región. Ejemplo 6: Z = 10 en el segmento (0, 5/2)–(3, 1).
Ejemplo 7: un único vértice óptimo (0, 2), aunque la base sea degenerada.
El extra 1 tiene región no acotada y mínimo finito Z = 4 en (2, 1).

`GraphicalResult` agrega estado, Z, direcciones de recesión, direcciones
óptimas y de mejora, límites de dibujo y segmentos de rayos ya recortados.
Todos tienen valores por defecto. La UI solo dibuja esos datos: rótulos sobre
rectas, coordenadas y Z, segmento óptimo, isoutilidad punteada y flecha de
mejora; desde V los ejes usan la misma escala cuando la razón entre los lados
de la caja está entre 1/4 y 4. `render_graph` recibe el problema para
rotular nombres, sentidos y números con el formato escogido sin analizar texto.

Preguntas para practicar:

1. ¿Por qué una esquina de la caja no demuestra un óptimo?
2. ¿Cómo distinguir región no acotada de Z no acotada?
3. ¿Qué pasa si dos rectas coinciden o son verticales?
4. ¿Qué demuestra c·d = 0 en una dirección de recesión?
5. ¿Por qué el gráfico sirve como segundo oráculo exacto de Gran M?

Ejercicio: cambiar el objetivo del ejemplo 5 a Min Z = x1 + x2. La región
sigue no acotada, pero el origen pasa a ser óptimo con Z = 0.

APIs consultadas: [Plotly, rellenos](https://plotly.com/python/shapes/),
[Plotly, anotaciones](https://plotly.com/python/text-and-annotations/) y
[Streamlit, Plotly](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart).

## P5: sensibilidad de la base óptima

`sensitivity_analysis` reconstruye B con `standard_form.a` y `final_basis` e
invierte con Gauss-Jordan de `linalg`. No consulta el tablero, las iteraciones
ni `final_b_inverse`: sirve también para el futuro simplex revisado. Calcula
x_B = B⁻¹b, y = c_B B⁻¹ y r = c − yA con fracciones. Los costos de artificiales
no intervienen en el problema original. Cada precio se multiplica por
`row_signs[i]` para reportar el modelo original, sin cambiar el sentido de Z.

Los rangos preservan esta base variando un único dato. Para RHS se exige
x_B + Δ·signo_fila·B⁻¹e_i ≥ 0. Para un costo no básico solo cambia su r_j;
para uno básico en posición k cambian todos los r_N por −Δ·(B⁻¹A)_kN.
Se intersectan desigualdades lineales manteniendo r_N ≤ 0 en Max o ≥ 0 en Min;
las columnas artificiales retiradas se excluyen. Se trasladan los límites de
Δ al valor original; `None` significa infinito. Los extremos pueden tener
otra base óptima; degeneración puede dejar un extremo en el valor actual.

### Derivación exacta del ejemplo 2

Base final (x1, x2, e2), con b normalizado (3, 6, 4):

```text
B     = [(3, 1,  0), (4, 3, -1), (1, 2, 0)]
B⁻¹   = [(2/5, 0, -1/5), (-1/5, 0, 3/5), (1, -1, 1)]
x_B   = (2/5, 9/5, 1)
c_B   = (4, 1, 0)
y_std = (7/5, 0, -1/5)
y     = (7/5, 0, 1/5)
```

R3 se negó al estandarizar: el precio original es +1/5. Solo queda s3 no
básica no artificial, con r_s3 = 1/5. Variar c1 en Δ exige (1+Δ)/5 ≥ 0;
variar c2 exige (1−3Δ)/5 ≥ 0. Para RHS, las tres fórmulas son
x1 = (2b1−b3)/5, x2 = (−b1+3b3)/5 y e2 = b1−b2+b3.

| Dato | Rango que conserva la base |
|---|---|
| c1 | [3, +∞) |
| c2 | (−∞, 4/3] |
| b1 original | [2, 12] |
| b2 original | (−∞, 7] |
| b3 original | [−6, −3] |

Z* = 17/5. Si b3 sube de −4 a −7/2, Δ = 1/2 y Z* sube 1/10, hasta 7/2;
el punto pasa a (1/2, 3/2). Las pruebas escriben la derivación en un comentario,
contrastan los precios con SciPy y perturban dentro y fuera de cada rango de
los ejemplos 1 y 2. Dentro se conserva la predicción lineal; fuera de un
extremo finito cambia la predicción o desaparece la factibilidad.

### Redundancia y degeneración

Una artificial básica en cero que no pudo retirarse identifica una fila
redundante. Su columna es el vector unitario de su fila original; esa fila
puede ocupar otra posición en el tablero. Se elimina la fila original y la
artificial para invertir una base reducida, y se extiende el dual poniendo
su precio en cero. Se avisa «precio sombra no único: fila redundante» y se
omite su rango de RHS. No se interpreta ese representante como una derivada
para perturbaciones aisladas que destruyen las dependencias.

Las filas conservadas siguen sujetas a las igualdades omitidas: en la base
completa sus artificiales deben permanecer exactamente en cero. Por eso una
perturbación de una fila conservada puede tener intervalo [b_i, b_i]. Con
x1+x2=4 repetida, Max Z=x1+2x2, se reporta y=(2,0), no hay rango para R2 y
el de R1 es [4,4]. Cambiar solo R1 a 5 vuelve el sistema infactible; reportar
un intervalo amplio después de omitir R2 sería incorrecto.

`SensitivityReport.warnings` contiene advertencias de redundancia y
degeneración. Las interpretaciones usan claves `b:nombre`, `c:nombre` y
`r:nombre`, evitando colisiones si una variable se llama como una restricción.
`sensitivity_interpretations` aplica el formato elegido sin cambiar fracciones.
La pestaña muestra precios, costos reducidos y ambos rangos, con encabezados,
interpretación debajo de cada tabla y advertencias visibles.

Preguntas para practicar:

1. ¿Por qué el precio de R3 del ejemplo 2 es positivo si y_std es negativo?
2. ¿Por qué un rango de una básica usa todos los costos no básicos?
3. ¿Por qué los rangos son de una base y de un dato a la vez?
4. ¿Por qué y_i=0 en una redundante es una elección dual y no una promesa de
   factibilidad al mover solo ese RHS?
5. ¿Cómo demostrar que sensibilidad no depende del tablero de Gran M?

Ejercicio: quitar `final_b_inverse` y las iteraciones de una solución óptima;
la sensibilidad debe permanecer idéntica. Después perturbar b3 del ejemplo 2
hasta −3: e2 llega a cero y se alcanza un extremo degenerado del rango.

## R: lectura de sensibilidad y revisión visual

La interpretación de cada lado derecho se muestra una sola vez, debajo de los
rangos. La tabla enumera todas las restricciones originales; una redundante
indica «No disponible (fila redundante)» en ambos límites, sin inventar un rango.
Las advertencias siguen explicando el representante dual y la degeneración.

Los rótulos del gráfico se ubican en tramos alejados de vértices y rótulos
anteriores. Se anclan hacia dentro cerca de los bordes; las coordenadas tienen
fondo claro y contraste explícito. La flecha de mejora termina dentro del
recorte para que su cabeza sea visible. No cambian la geometría ni las escalas.
`scripts/check_ui.py` reproduce con Chromium las seis capturas de
`docs/capturas/r/` (rehechas en `docs/capturas/v/`) y las de los tres ensayos de
dos variables, y comprueba la salud del servidor. Playwright solo pertenece a dev.

Preguntas para practicar:

1. ¿Por qué no usar infinito en el rango de una redundante? Su perturbación
   aislada puede romper una igualdad dependiente; no hay rango informado.
2. ¿La flecha termina donde acaba la región? No: termina dentro de la caja
   de dibujo; la dirección exacta certifica la mejora ilimitada.
3. ¿Qué demuestra AppTest y qué exige una captura? AppTest verifica datos y
   textos; el navegador permite observar superposiciones y recortes.

Ejercicio: duplicar R1 como igualdad y comprobar que aparece la segunda fila
sin rango, con una sola interpretación debajo de la tabla.

## P6, paso 1: reglas compartidas de simplex

`src/plapp/simplex_rules.py:36` excluye candidatas artificiales;
`src/plapp/simplex_rules.py:41` prueba infactibilidad y
`src/plapp/simplex_rules.py:64` elige entrante. El módulo recibe costos
reducidos, base, tipos de columna, x_B y d.
No calcula esas entradas desde un almacenamiento particular. Gran M conserva
su tablero en `big_m.py`; la razón mínima, la elección por costo o Bland y el
certificado de infactibilidad se deciden en funciones compartidas. Solo el
posproceso de retiro y alternativas necesita filas transformadas completas.

El armado final verifica Z contra el objetivo original, calcula holguras,
certifica puntos o rayos alternos y conserva B⁻¹. Se mantiene la artificial
nula de una redundante y el límite de 1000 bases alternativas.
`tests/fixtures/big_m_traces.json` se guardó antes de modificar el solver:
21 casos, incluidos los 14 fixtures, C1, retiro negativo y Beale. Se comparan
todos los estados, tableros, razones, costos, decisiones, Z y notas, además
del estado y mensaje finales. No se regeneran al cambiar el código.

Preguntas para practicar:

1. ¿Por qué compartir decisiones? Con los mismos x_B, r y d, ambos métodos
   deben elegir la misma base siguiente; su almacenamiento no cambia la regla.
2. ¿Por qué comparar notas además de Z? El paso a paso es parte observable
   del contrato; un refactor también debe preservar sus explicaciones.
3. ¿Puede una columna artificial de costo favorable entrar? No: se excluye
   antes de elegir entrante y antes de comprobar mejora en la parte M.

Ejercicio: usar Bland desde el inicio en `choose_entering`; identificar qué
trazas congeladas fallan y explicar por qué la prueba detecta un cambio real.

## P6, pasos 2–3: revisado y comparación

`src/plapp/revised_simplex.py:38` calcula x_B=B⁻¹b, y=c_B B⁻¹ con MValue y
r=c−yA. Para la entrante se calcula solo d=B⁻¹a_j. Cada `Iteration` guarda
`b_inverse`, `basic_values` y `multipliers`, con `tableau=None`. Los dos campos
nuevos tienen tupla vacía por defecto para conservar el contrato de Gran M.
`src/plapp/revised_simplex.py:65` coordina las mismas reglas compartidas.

### Actualización elemental

`src/plapp/revised_simplex.py:16` aplica E·B⁻¹. Si sale la básica de posición p,
E es identidad excepto en su columna p: E_pp=1/d_p y E_ip=−d_i/d_p para i≠p.
Así E·d=e_p, y E·(B⁻¹B_nueva)=I. El producto se aplica normalizando la fila p
de la inversa y restando d_i veces esa fila a las demás, en O(m²), sin calcular
una nueva inversión. También funciona con d_p<0 en un retiro artificial de
paso cero. Las pruebas construyen E explícita y comparan el producto; además
invierten B con Gauss-Jordan en cada estado de los 21 casos.

En el ejemplo 2, el primer d=(3,4,1) y p=0. E tiene filas (1/3,0,0),
(−4/3,1,0) y (−1/3,0,1). Como B⁻¹ inicial es I, esa E es la nueva inversa;
x_B=(1,2,3), Z=4+2M. Las bases y Z siguen exactamente la tabla de P2.

Solo al retirar artificiales o certificar alternativas se calcula B⁻¹A completo.
Las pruebas cuentan estos productos para impedir que el revisado mantenga un
tablero durante los pivotes normales. Las artificiales redundantes conservan
su testigo nulo; la sensibilidad sigue reconstruyendo la base por su cuenta.

`app/streamlit_app.py:209` presenta B⁻¹, x_B, y y costos reducidos.
`app/streamlit_app.py:288` muestra d con razones, exclusiones y pivote resaltado,
incluido el retiro sin razón mínima. `app/streamlit_app.py:647` compara cada
base, entrante, saliente y Z; si falta un estado, muestra «No» en la coincidencia.
El resumen distingue estados registrados de pivotes. La referencia de trabajo
m×(n+m+1) del tablero supone filas ≤; artificiales y excesos aumentan su ancho.
El revisado mantiene m×m pero aún calcula yA y busca alternativas al terminar.

Los 14 fixtures y las regresiones C1 y Beale tienen secuencias idénticas,
sensibilidad idéntica en óptimos y el mismo resultado exacto. El estrés con
semilla 20261110 y `--method both --count 3000` verificó 3000 por método,
con 0 errores, 0 diferencias y 0 oráculos inconcluyentes en ambos.

Preguntas para practicar:

1. ¿Por qué y contiene M? Mientras haya artificiales básicas, c_B contiene
   penalizaciones simbólicas y debe conservarse su efecto dominante.
2. ¿Por qué E no depende de b? E convierte la columna d en e_p; b solo aporta
   x_B para la razón mínima y la factibilidad.
3. ¿Por qué no invertir B en cada pivote? La actualización elemental preserva
   la inversa con operaciones de filas O(m²); Gauss-Jordan queda como verificación.
4. ¿Se compara solo el resultado? También cada estado; una misma Z final no
   demuestra que ambos métodos apliquen las mismas decisiones.
5. ¿Por qué no mostrar el gráfico para n>2? Ambos métodos aceptan n variables;
   la geometría dibujada es exclusivamente bidimensional.

Ejercicio: reconstruir a mano E del segundo pivote del ejemplo 2 y verificar
que E·B⁻¹ produce x_B=(3/5,6/5,1). Luego activar Bland desde el inicio.

## P7: exportación del paso a paso a PDF

`src/plapp/export_pdf.py:378` recibe problema y solución existentes y devuelve
bytes. `mode="fraction"` y `decimals=4` son valores por defecto; el exportador
valida ambos con el mismo formateador de la UI. No importa ni llama solvers.
`src/plapp/export_pdf.py:109` escribe el modelo original y la forma estándar;
`src/plapp/export_pdf.py:172`, cada estado anterior al pivote con su evidencia;
`src/plapp/export_pdf.py:277`, el resultado y los certificados especiales.
Si hay óptimo, `src/plapp/export_pdf.py:327` llama a `sensitivity_analysis` con
la misma solución, sin recalcular el método, e incluye tablas e interpretaciones.

La clase de presentación `src/plapp/export_pdf.py:22` carga DejaVu Sans 2.37,
regular y negrita, desde `assets/fonts/`; el wheel lleva copias y licencia en
`plapp/assets/fonts/`. FontTools comprueba cada carácter contra la intersección
de los mapas de glifos de ambas fuentes. ≤, ≥, −, ⁻¹, ⱼ, ∂, ∞ y Δ tienen glifo;
un carácter del usuario ajeno a la fuente se sustituye explícitamente por su
código `[U+XXXX]`. No se omiten caracteres silenciosamente ni se usa M numérica.
La descarga oficial se verificó con el SHA-256 publicado; README cita origen
y licencia. FontTools ya era transitivo de fpdf2 y ahora es dependencia directa.

Las páginas son A4 horizontales. Cada tabla tiene como máximo ocho columnas
de datos además de su primera columna, que se repite en todos los bloques.
Los encabezados se repiten al cambiar de página, los textos numéricos largos
se ajustan por caracteres y el pivote mantiene su fila y columna originales.
`src/plapp/export_pdf.py:240` escribe d y las razones del revisado; un retiro
artificial conserva su aviso de paso cero y no inventa cocientes de razón mínima.

`app/streamlit_app.py:697` ofrece `st.download_button` con bytes, MIME
`application/pdf` y el formato elegido, solo cuando existe solución. Paso a
paso ofrece el primer método seleccionado; Comparar métodos ofrece un PDF por
método, incluso en modo Directo. Los fallos quedan contenidos en un mensaje
comprensible, sin traceback. Pypdf, solo dev, lee y valida los documentos reales
en pruebas; Playwright descarga desde el navegador y espera que termine el rerun.

Preguntas para practicar:

1. ¿Por qué recibir también el problema? La solución conserva la forma estándar;
   el informe debe mostrar además el modelo original y las holguras originales.
2. ¿Exportar vuelve a ejecutar simplex? No. Recorre `Solution.iterations` y, si
   hay óptimo, reconstruye sensibilidad desde la base ya calculada.
3. ¿Por qué dividir columnas y repetir la primera? Así cada valor conserva su
   básica o restricción identificada y ninguna celda queda fuera de la página.
4. ¿Qué cambia al pedir decimales? Solo el texto; Fraction y MValue se conservan
   en el objeto original, incluidos costos, razones y certificados.
5. ¿Cómo detectar un PDF vacío que empieza por `%PDF-`? Leerlo con un lector
   independiente y exigir modelo, estados, resultado y sensibilidad aplicable.

Ejercicio: reducir a cuatro las columnas de datos por bloque; comprobar con el
caso de ocho variables que no se pierde ninguna columna ni el pivote resaltado.

## V: presentación verificable

`format_expression` omite coeficientes cero y el módulo de los unitarios exactos;
las tablas siguen completas. El gráfico amplía la referencia con v + 2s·d para
cada vértice y dirección normalizada, antes de aplicar el margen 6/5. Solo cambia
el recorte: no cambia ningún vértice ni certificado de los métodos. El ejemplo 5
usa (6, 36/5). Los bordes de caja son grises punteados; el aviso enumera los rayos.
Se anclan los ejes con razón 1 cuando el cociente de lados está entre 1/4 y 4;
fuera se informa la deformación. Los rótulos desplazados conservan una guía.

Sensibilidad usa los nombres de las columnas de `final_basis` para distinguir
básicas y no básicas. Un costo reducido cero solo anuncia otro óptimo cuando
el solver ya lo certificó; un punto aislado degenerado puede tener costos cero.
La nota de fuente está en «Notas del documento», al final del PDF.

`make ui-check` inicia un servidor en puerto libre, espera salud `ok`, recorre
modos y formatos y descarga PDF; el `finally` detiene el proceso propio, incluso
si falla Chromium. `make manual-captures` toma capturas de interacciones reales.
Sin `--serve`, el verificador reutiliza `--url` y no administra el servidor ajeno.

Preguntas: ¿por qué el recorte no modifica el modelo?, ¿por qué comparar Fraction
antes de omitir el uno?, ¿por qué costo cero no siempre implica otro punto?

Ejercicio: quitar temporalmente `scaleanchor` y observar la flecha (1, 1), luego
reponerlo y ejecutar las pruebas de presentación del gráfico.

## Modelo y JSON: `model.py` e `io_json.py`

`src/plapp/model.py:52` lee cada celda: quita espacios, cambia la coma decimal
por punto y construye `Fraction(texto)`. Así `2`, `-3`, `2.5`, `2,5` y `2/5`
quedan exactos; `0.1` es 1/10, no un binario aproximado. Una celda vacía produce
«El campo está vacío; ingrese un número.»; `abc` o `1/0`, «Número inválido;
use 2, -3, 2,5 o 2/5, con denominador no nulo.». `Fraction` también acepta
`1e3` y `1_000`; la interfaz no los anuncia, pero los lee como 1000.

`src/plapp/model.py:83` valida el esquema JSON en español: `nombre`, `sentido`
(`max` o `min`), `variables`, `objetivo` y `restricciones`, cada una con
`nombre`, `coeficientes`, `signo` (`<=`, `>=`, `=`) y `rhs`; `n` y `m` son
opcionales y deben coincidir con los datos. No se detiene en el primer error:
`src/plapp/model.py:72` acumula un `ValidationIssue` (`src/plapp/model.py:13`)
por celda con su ubicación, por ejemplo «objetivo, x1», «restricción 2, x1»,
«restricción 2, signo» o «lado derecho de R2». También rechaza filas con todos
los coeficientes en cero, nombres vacíos o repetidos y dimensiones distintas.
Solo con cero errores crea `LPProblem` (`src/plapp/model.py:31`), que asigna
x1, x2… y R1, R2… cuando faltan nombres. Todas las variables son no negativas.

`src/plapp/io_json.py:9` escribe cada número con `str(Fraction)`, por ejemplo
`"2/5"`, y nunca escribe `esperado`. `src/plapp/io_json.py:28` acepta una ruta,
texto o bytes; un archivo roto produce «No se pudo leer el archivo: use un JSON
válido con codificación UTF-8.» y los errores de validación se unen con «; ».
`src/plapp/io_json.py:44` devuelve el texto que descarga «Guardar JSON». La
validación no lee `esperado`: ese campo de los fixtures solo lo usan las pruebas.

Preguntas para practicar:

1. ¿Por qué los números van entre comillas en el JSON? Un número JSON se lee
   como float; el texto `"2/5"` o `"0.1"` se convierte en una fracción exacta.
2. ¿Por qué acumular errores en lugar de detenerse en el primero? El usuario
   corrige todas las celdas de una vez y cada mensaje dice dónde está el dato.
3. ¿La aplicación usa los resultados esperados de los fixtures? No: `validate`
   ignora `esperado` y `problem_to_dict` no lo escribe.

Ejercicio: rechazar la notación científica. En `src/plapp/model.py:52`, si el
texto contiene `e` o `E`, lanzar el mismo `ValueError`; agregar en
`tests/test_model.py` un caso con `1e3` y comprobar que el resto sigue pasando.

## Contratos: `result.py`

`src/plapp/result.py:1` fija las convenciones: índices de base y pivote desde
cero y costos reducidos r = c − c_B B⁻¹A en el sentido original de Z. Todas las
clases son `dataclass(frozen=True)`: un resultado no se modifica después de
calcularse y cambiar el formato no lo toca.

- `Status` (`src/plapp/result.py:21`): solo estados terminales, óptimo,
  infactible y no acotado. Multiplicidad y degeneración son banderas aparte.
- `StandardForm` (`src/plapp/result.py:30`): nombres y tipos de columna, A, b,
  costos `MValue`, base inicial, transformaciones y `row_signs`.
- `RatioRow` (`src/plapp/result.py:44`): una razón `None` exige `exclusion_reason`.
- `Iteration` (`src/plapp/result.py:65`): el estado **antes** del pivote, con
  tablero (Gran M) o B⁻¹, x_B y multiplicadores (revisado). La última iteración
  no tiene entrante y explica la terminación.
- `Solution` (`src/plapp/result.py:86`): estado, mensaje, valores y holguras en
  el modelo original, iteraciones, base final, alternativas, rayos y notas.
- `SensitivityReport` (`src/plapp/result.py:109`) y `GraphicalResult`
  (`src/plapp/result.py:139`): `None` en un límite significa infinito.

Los dos métodos devuelven el mismo `Solution`; por eso la UI, el PDF, la
sensibilidad y la comparación no dependen de cuál lo produjo. Los campos que se
agregaron en paquetes posteriores tienen valor por defecto y no rompen a quien
construía el contrato antes.

Preguntas para practicar:

1. ¿Por qué `Iteration` guarda el estado anterior al pivote? Para mostrar cada
   decisión con los datos con que se tomó; el estado siguiente es otra iteración.
2. ¿Por qué multiplicidad y degeneración no son estados? Un óptimo puede ser
   múltiple y degenerado a la vez; `Status` solo dice cómo terminó el método.
3. ¿Qué pasa si un campo nuevo no tiene valor por defecto? Fallan todos los
   constructores existentes, incluidos los de las pruebas.

Ejercicio: agregar `pivot_count: int = 0` a `Solution`, llenarlo en
`src/plapp/big_m.py:30` y `src/plapp/revised_simplex.py:65`, y comprobar en
`tests/test_examples.py` que ambos métodos cuentan lo mismo en los 19 fixtures.

## Formato: `formatting.py`

`src/plapp/formatting.py:12` convierte un valor exacto en texto. En fracciones
usa `str(Fraction)`. En decimales divide con `Decimal` y precisión suficiente,
redondea al máximo de cifras pedido (0 a 12), quita ceros finales y escribe
`0` en lugar de `-0`. Un `MValue` se muestra como `a + bM`, con `M` sin
coeficiente cuando |b| = 1 y solo `a` cuando b = 0. La UI, el PDF, el gráfico y
las interpretaciones de sensibilidad usan esta misma función.

`src/plapp/formatting.py:42` (V1) arma expresiones lineales legibles: omite los
coeficientes cero, no escribe el módulo de los unitarios, pega el signo al
primer término y une los demás con ` + ` o ` - `. Si todos son cero devuelve
`0`. El ejemplo 2 se lee `MIN Z = 4·x1 + x2` y `R3: -x1 - 2·x2 ≥ -4`. La
comparación con 1 en `src/plapp/formatting.py:54` se hace sobre la Fraction:
con dos decimales 9999/10000 se ve «1», pero se escribe `1·x1` porque no es uno.
Las tablas siguen mostrando todos los coeficientes, incluidos ceros y unos.

Preguntas para practicar:

1. ¿Cambiar a decimales vuelve a resolver? No: se formatean las mismas
   Fraction guardadas en la sesión.
2. ¿Por qué comparar la fracción y no el texto con 1? El texto redondeado puede
   ocultar un coeficiente distinto de uno.
3. ¿Por qué la cantidad de decimales es un máximo? Se quitan los ceros finales:
   1/2 se ve 0.5 aunque se pidan cuatro decimales.

Ejercicio: escribir siempre el coeficiente (`1·x1`) quitando el caso
`magnitude == 1` de `src/plapp/formatting.py:54`; identificar qué pruebas de
`tests/test_formatting.py` y `tests/test_app.py` esperan la forma simplificada.

## Oráculo y estrés: `scripts/verify.py` y `scripts/stress.py`

`scripts/verify.py:39` traduce el modelo a `linprog`: en Max niega c, una fila
≥ se multiplica por −1 y una igualdad va a `A_eq`. `scripts/verify.py:61`
resuelve con HiGHS. Si el estado es 2, 3 o 4 (infactible, no acotado o
problema numérico), repite sin presolve: el presolve puede clasificar mal una
no acotación, como en el extra 7. Si el estado cambia, una segunda corrida sin
presolve debe confirmarlo; si no coinciden o el estado no es verificable, lanza
`OracleInconclusiveError` y el caso se cuenta como excluido. Los precios sombra
se pasan al modelo original con signo_objetivo · signo_fila · marginal.

`scripts/verify.py:110` compara: mismo estado; en un óptimo, Z con tolerancia
1e-7, punto propio factible con Fraction exacta y c·x igual a Z. No exige el
mismo punto porque con óptimos múltiples HiGHS puede elegir otro vértice.
`scripts/verify.py:146` es `make verify FILE=…`: imprime el resultado de SciPy
y si cada método propio coincide.

`scripts/stress.py:20` genera problemas de 2 a 4 variables y 1 a 6 filas. El
35 % de las filas copia una anterior escalada por 1, 2 o −1 (al negar invierte
el signo) y `scripts/stress.py:47` deja el lado derecho en 0 con probabilidad
0,6. Así aparecen muchas filas redundantes y bases degeneradas.
`scripts/stress.py:57` cuenta por separado verificados, errores propios,
diferencias y oráculos excluidos, y `scripts/stress.py:80` falla si hay errores
o diferencias. Los conteos de la última corrida (semilla 20261110, 3000 por
método) están en `docs/desarrollo-v-p8.md`.

`scripts/check_ui.py:23` inicia un servidor propio con `--serve`;
`scripts/check_ui.py:158` captura los gráficos y `scripts/check_ui.py:236`, las
del manual. `scripts/build_manual.py:52` convierte el Markdown del manual a HTML
con capturas incrustadas y `scripts/build_manual.py:80` lo imprime en A4 y
falla si pasa de cinco páginas.

Preguntas para practicar:

1. ¿Por qué SciPy no está en la aplicación? El taller exige métodos propios; el
   oráculo usa otro algoritmo y otra aritmética, así que un error no se repite
   igual. Una prueba con AST impide importarlo en `src/` y `app/`.
2. ¿Por qué repetir sin presolve? Para distinguir infactible de no acotado
   cuando el presolve no concluye o clasifica distinto.
3. ¿Qué cuenta como diferencia? Otro estado, otro Z, un punto propio infactible
   o un Z que no es c·x. Un caso excluido no cuenta como acierto ni como fallo.

Ejercicio: cambiar 0.6 por 0.1 en `scripts/stress.py:47`, ejecutar
`uv run python scripts/stress.py --count 300` y comparar los conteos con los
de 0.6; explicar por qué los lados derechos nulos generan bases degeneradas.
