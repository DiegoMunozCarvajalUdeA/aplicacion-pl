# Guía de sustentación

Esta guía acompaña los paquetes implementados. El equipo debe recorrer las
pruebas y practicar las modificaciones; comprender esta guía no reemplaza leer
el código. Los módulos de gráfico, sensibilidad, revisado y PDF siguen pendientes.

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

`src/plapp/big_m.py:17` canoniza cⱼ − zⱼ con los costos de la base actual;
`src/plapp/big_m.py:28` guarda el estado anterior al pivote y Z = c_B·b.
`src/plapp/big_m.py:44` hace el pivote con Fraction,
`src/plapp/big_m.py:64` calcula las razones y explica exclusiones, y
`src/plapp/big_m.py:89` decide
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

`src/plapp/big_m.py:111` busca un punto óptimo distinto, recorriendo bases
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
La prueba simula ese contrato con una base calculada por Gran M; no implementa
ni reemplaza el solver revisado en la aplicación.

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

Una artificial que sale de la base nunca vuelve a entrar. Las candidatas
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
