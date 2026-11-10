# Propuesta — semana 1

Entregable del sprint 1 según el cronograma del enunciado (`taller-optimi.pdf`,
sección 6): lenguaje, método elegido, integrantes y boceto de la interfaz. La
guía para preparar y presentar esta propuesta está en `docs/sprint-1.md`.

## Lenguaje y herramientas

- **Python 3.12**, instalado y gestionado con uv, para que todos los integrantes
  tengan el mismo entorno (`uv.lock`).
- **Streamlit** para la interfaz web: se ejecuta en el computador del estudiante
  (`make run`) y se puede publicar en Streamlit Community Cloud. El enunciado
  exige interfaz gráfica; una solución solo de consola no se califica.
- **`fractions.Fraction`** de la biblioteca estándar para la aritmética exacta.
- **Plotly** para el método gráfico y **fpdf2** para exportar el paso a paso.
- **SciPy** solo en pruebas y scripts, como verificador externo. Nunca produce
  resultados en la aplicación (condición 1a del enunciado).

## Método elegido

- **Método principal: Gran M.** Acepta ≤, ≥, = y lados derechos negativos sin
  una segunda fase: las filas con lado derecho negativo se multiplican por −1, y
  las filas ≥ o = reciben una artificial con costo ±M.
- **M simbólica.** Cada costo se guarda como `a + b·M` y se compara primero por
  la parte en M. Así no hay que elegir un número grande ni aparecen errores de
  redondeo.
- **Segundo método: simplex revisado**, con B⁻¹ y las mismas reglas de decisión,
  para comparar iteraciones (bonificación de +0.2).
- **Reglas:** entra la variable con el costo reducido más favorable y, si una
  base se repite, se cambia a la regla de Bland para evitar ciclos. En la razón
  mínima, el empate se rompe por el menor índice.
- **Casos especiales:** infactible (una artificial positiva al terminar), no
  acotado (columna sin coeficientes positivos), óptimos múltiples (costo
  reducido cero en una no básica) y degenerado (básica en cero). Cada uno se
  informa con un mensaje, nunca con un error del programa.

## Integrantes

| Nombre | Documento | Cuenta Git | Parte que explica en la sustentación |
|---|---|---|---|
| [Integrante 1] | [Documento] | [Cuenta] | [Por acordar] |
| [Integrante 2] | [Documento] | [Cuenta] | [Por acordar] |
| [Integrante 3] | [Documento] | [Cuenta] | [Por acordar] |
| [Integrante 4, si aplica] | [Documento] | [Cuenta] | [Por acordar] |

El docente elige qué parte explica cada integrante, así que todos deben poder
explicar y modificar cualquier módulo. El reparto solo indica quién lidera cada
parte. `docs/sustentacion.md` tiene un índice por módulo.

## Boceto de la interfaz

```text
+----------------------+----------------------------------------------+
| Sentido: Max / Min   | Aplicación de Programación Lineal            |
| Método               | [+ variable] [- variable] [+ fila] [- fila]  |
| Directo / Paso a paso| Función objetivo: [x1] [x2] ...              |
| Fracción / Decimal   | Restricciones:                               |
| Decimales            | R1 [x1] [x2] ... [<= / >= / =] [rhs]         |
| Ejemplo [Cargar]     | R2 [x1] [x2] ... [<= / >= / =] [rhs]         |
| [Subir JSON]         | [Resolver]                                   |
| [Guardar JSON]       | Resumen del problema validado                |
|                      | Resultado | Paso a paso | Método gráfico     |
|                      | Sensibilidad | Comparar métodos              |
|                      | [Exportar paso a paso a PDF]                 |
+----------------------+----------------------------------------------+
```

La interfaz conserva las celdas al cambiar las dimensiones, señala cada error
con su fila y columna, y permite editar y volver a resolver sin reiniciar. La
pantalla real correspondiente está en `docs/manual/capturas/entrada.png`.

## Plan por sprints

| Sprint | Qué se muestra | Estado al 2026-11-10 |
|---|---|---|
| Semana 1: propuesta | Este documento y la app en ejecución | Falta completar integrantes y reparto |
| Semana 3: avance | Entrada del problema y método resolviendo los ejemplos 1 y 3 | Implementado: ejemplo 1 da x = (42, 16), Z = 3380; ejemplo 3 da x = (0, 100, 230), Z = 1350 |
| Semana 5: entrega final | App, manual, video, repositorio y sustentación | App, manual y guion listos; faltan remoto, despliegue, video y nombres (`docs/entrega.md`) |

## Riesgos y cómo se controlan

- **Errores en el método:** 19 problemas de referencia y miles de problemas
  aleatorios se comparan contra SciPy (`make test`, `scripts/stress.py`).
- **La app no arranca el día de la sustentación (condición 2b):** instalación
  probada en el portátil días antes, sin depender de la red
  (`docs/entrega.md`, sección 6).
- **Un integrante no puede explicar una parte:** esa parte cuenta como no
  implementada. Para evitarlo hay ensayos con el banco de modificaciones en vivo
  de `docs/ensayo-sustentacion.md`.
