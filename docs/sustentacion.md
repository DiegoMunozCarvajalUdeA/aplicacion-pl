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

`src/plapp/linalg.py:16` contiene identidad; `:30`, `:40` y `:51`, productos;
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
`:28` guarda el estado anterior al pivote y Z = c_B·b. `:44` hace el pivote
con Fraction, `:64` calcula las razones y explica exclusiones, y `:89` decide
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
iteración tiene `entering_variable=None` y explica por qué terminó. En no
acotación, el estado previo conserva la columna candidata y sus exclusiones.

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
