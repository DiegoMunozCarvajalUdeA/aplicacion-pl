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
