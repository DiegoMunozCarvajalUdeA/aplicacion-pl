# Propuesta — semana 1

## Alcance

Aplicación web local en Python 3.12 y Streamlit para formular y resolver problemas
de programación lineal con variables no negativas. Método principal: Gran M
simbólica con Fraction. Segundo método propuesto: simplex revisado para comparar
iteraciones. Plotly presenta la geometría; fpdf2 permitirá exportar el proceso.
SciPy se reserva exclusivamente para verificar resultados en pruebas y scripts.

El equipo implementará los algoritmos. La infraestructura inicial incluye sus
contratos y pruebas, sin resolver el proyecto por los integrantes.

## Integrantes

| Nombre | Cuenta Git | Responsabilidad acordada |
|---|---|---|
| [Integrante 1] | [Cuenta] | [Por acordar] |
| [Integrante 2] | [Cuenta] | [Por acordar] |
| [Integrante 3] | [Cuenta] | [Por acordar] |
| [Integrante 4, si aplica] | [Cuenta] | [Por acordar] |

## Boceto

```text
+----------------------+----------------------------------------------+
| Sentido: Max / Min    | Aplicación de Programación Lineal             |
| Método               | [+ variable] [- variable] [+ fila] [- fila]  |
| Directo / Paso a paso| Función objetivo: [x1] [x2] ...               |
| Fracción / Decimal   | Restricciones:                               |
| Decimales            | R1 [x1] [x2] ... [<= / >= / =] [rhs]          |
| Ejemplo [Cargar]     | R2 [x1] [x2] ... [<= / >= / =] [rhs]          |
| [Subir JSON]         | [Resolver]                                   |
| [Guardar JSON]       | Resumen del problema validado                 |
|                      | Resultado | Paso a paso | Gráfico             |
|                      | Sensibilidad | Comparar métodos               |
|                      | Forma estándar, razones y pivotes             |
|                      | [Exportar paso a paso a PDF]                  |
+----------------------+----------------------------------------------+
```

La interfaz debe conservar las celdas al cambiar dimensiones, señalar errores
por ubicación y permitir editar y volver a resolver sin reiniciar.
