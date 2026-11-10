# Guía de sustentación

Esta guía acompaña los paquetes implementados. El equipo debe recorrer las
pruebas y practicar las modificaciones; comprender esta guía no reemplaza leer
el código. El estado de los paquetes está en `docs/plan.md`.

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

Ejercicio: cambiar la selección de entrada para usar Bland siempre. Explicar
qué secuencias de pivotes cambian y por qué se conservan Z y factibilidad.

## P3: presentación de resultados y paso a paso

`app/streamlit_app.py:116` centraliza el formato numérico elegido. El estado
de sesión conserva el modelo exacto y sus soluciones: cambiar a decimales no
vuelve a resolver ni cambia Fraction por float. La función de formato está en
`src/plapp/formatting.py:12` y usa Decimal solo para presentar.

`app/streamlit_app.py:158` muestra variables, Z, y por restricción su tipo
original: holgura, exceso o igualdad. Aunque R3 se normalice a ≤ en el ejemplo 2,
en el resultado sigue siendo un exceso de la restricción original ≥.
`app/streamlit_app.py:134` presenta una solución alterna y el segmento o rayo
certificado; construye las coordenadas con el formato elegido. Las notas del
solver identifican las variables básicas nulas.

`app/streamlit_app.py:281` devuelve inmediatamente en modo Directo; Paso a paso
presenta forma estándar, costos simbólicos, transformaciones y base inicial.
`app/streamlit_app.py:243` presenta cada estado y sus razones y justificaciones.
`app/streamlit_app.py:187` construye el tablero rotulado por variables básicas,
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
vértices e interceptos no negativos, con 20 % de margen. Se interseca la región
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
mejora; los ejes no fuerzan escala 1:1. `render_graph` recibe el problema para
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
`scripts/check_ui.py` reproduce las seis capturas de `docs/capturas/r/` con
Chromium y comprueba la salud del servidor. Playwright solo pertenece a dev.

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

`simplex_rules.py` recibe costos reducidos, base, tipos de columna, x_B y d.
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

`app/streamlit_app.py:206` presenta B⁻¹, x_B, y y costos reducidos.
`app/streamlit_app.py:285` muestra d con razones, exclusiones y pivote resaltado,
incluido el retiro sin razón mínima. `app/streamlit_app.py:554` compara cada
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
