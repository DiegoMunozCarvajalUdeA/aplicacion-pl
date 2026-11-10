# Guía breve para la sustentación

Todas las variables originales satisfacen x ≥ 0. La aritmética del método será
exacta con Fraction; convertir a decimal solo al presentar.

## Gran M y forma estándar

Si b_i < 0, multiplicar toda la fila por −1 e invertir ≤ y ≥. A una fila ≤
se suma holgura; a una ≥ se resta exceso y se agrega artificial; a una igualdad
se agrega artificial. Las artificiales permiten construir la base inicial, pero
no pertenecen al problema original. Su costo es −M en Max y +M en Min.

M es simbólica: a + bM se guarda como dos fracciones. Comparar primero b y luego
a representa una penalización dominante sin elegir un número grande arbitrario.
Antes de pivotear hay que canonizar los costos respecto a la base inicial.

## Costos reducidos y razón mínima

Con B formada por columnas básicas, x_B = B⁻¹b, y = c_B B⁻¹ y
r = c − yA. En Max, una no básica con r_j > 0 permite mejorar; la base es
óptima si todos los r_j ≤ 0. En Min se invierten estas condiciones: mejora con
r_j < 0 y optimalidad con r_j ≥ 0. Estas convenciones corresponden a c − yA;
si se usa yA − c en un tablero, también cambian los signos del criterio.

La columna de dirección es d = B⁻¹a_j. Solo participan en la razón mínima
las filas con d_i > 0: θ = min(x_Bi / d_i). La saliente alcanza cero y preserva
la factibilidad de las otras básicas. Registrar exclusiones, empates y el
pivote; no basta con mostrar el cociente ganador.

La regla de Bland elige la variable elegible de menor índice como entrante y,
entre las filas empatadas en razón mínima, la variable básica de menor índice
como saliente. Usarla consistentemente evita ciclos; no confundir índice de
variable con posición de fila.

## Casos especiales

- Infactible: al finalizar la eliminación de artificiales, una artificial básica
  conserva valor positivo. Mensaje: «no tiene solución factible».
- No acotado: existe una entrante favorable y su dirección no tiene componentes
  positivos; puede mejorarse Z indefinidamente. Mensaje: «solución no acotada».
- Óptimos múltiples: un costo reducido cero en una no básica puede producir un
  punto óptimo alterno. Confirmar desplazamiento factible no nulo; un pivote
  degenerado o una artificial excluida no bastan para probar puntos distintos.
- Degeneración: una básica vale cero o hay empate en la razón mínima. Puede
  haber iteraciones sin cambio de Z. Es una bandera, no otro estado terminal.

Una artificial básica nula puede requerir un pivote para retirarla; si su fila
es redundante, se elimina esa fila. No usar artificiales en la base final del
análisis de sensibilidad.

## Método gráfico

Para dos variables se intersectan restricciones y ejes, se filtran puntos con
el modelo original y se evalúa Z. Incluir no negatividad, igualdades, rectas
paralelas y regiones que sean solo un punto o segmento. La región puede ser
vacía o no acotada. Una región no acotada puede tener óptimo finito, por ejemplo
en minimización. La caja usada para dibujar no agrega restricciones al modelo;
sus esquinas no son vértices reales. La isoutilidad satisface c₁x₁+c₂x₂=Z*.

## Sensibilidad de una base óptima

Precios sombra: y = c_B B⁻¹. Deshacer el cambio de signo de cualquier fila
normalizada para reportar ∂Z*/∂b_i original. Si se transformó Max a Min también
hay que deshacer el signo de la función objetivo. Los costos reducidos de las
variables originales son r_j = c_j − y a_j.

Para una no básica, c_j + Δ cambia solo su costo reducido: r_j + Δ. Exigir
≤ 0 en Max o ≥ 0 en Min. Para una básica en posición k, variar c_B en Δe_k
cambia los costos no básicos en r_N − Δe_kᵀB⁻¹A_N. Intersectar las desigualdades
correspondientes. Luego trasladar los límites de Δ a valores del coeficiente.

Para b_i + Δ, exigir x_B + ΔB⁻¹e_i ≥ 0. Si d_k = (B⁻¹e_i)_k > 0,
Δ ≥ −x_Bk/d_k; si d_k < 0, Δ ≤ −x_Bk/d_k; si d_k = 0 no aporta límite.
Intersectar límites y trasladarlos a valores de b_i; representar infinitos
con None. Si la fila se multiplicó por −1, transformar también la perturbación.

Se varía un solo dato a la vez. Los rangos preservan una base óptima y los
precios valen dentro de su rango; no garantizan que el óptimo siga siendo único
en los extremos. Con degeneración los precios pueden no ser únicos.

Referencias de requisitos y APIs: sección Referencias de `README.md`. Antes de
presentar, agregar las fuentes académicas que el equipo realmente consulte.
