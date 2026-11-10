# Guion del video de demostración

Duración máxima según el taller (6d): 5:00. Objetivo: 4:45, para dejar 15 s de
margen. Grabar y publicar el video es tarea del equipo; cuando esté publicado,
registrar su URL en `README.md` ([por completar]).

Antes de grabar, abrir la app en la URL desplegada o con `make run`. Usar
siempre los ejemplos incluidos: así lo que se dice coincide con lo que la app
muestra. Los textos entre comillas son los mensajes reales de la interfaz.

| Tramo | Inicio–fin | En pantalla | Qué se dice | Quién habla |
|---|---|---|---|---|
| 1. Presentación | 0:00–0:20 | Pantalla inicial con la barra lateral visible. | «Esta es nuestra aplicación de programación lineal. Resuelve con Gran M y con simplex revisado, implementados por nosotros con fracciones exactas, y muestra el proceso completo.» | [Integrante 1] |
| 2. Entrada y validación | 0:20–0:55 | Elegir MIN; pulsar Agregar variable y luego Quitar variable; cargar `ejemplo_2.json`; escribir `abc` en x1 de la función objetivo; Resolver; corregir con `4`. | «Se elige Max o Min, se agregan o quitan variables y restricciones sin perder datos. Se aceptan enteros, decimales con punto o coma y fracciones. Si una celda no es un número, la app indica la fila y la columna: “objetivo, x1: Número inválido…”.» | [Integrante 1] |
| 3. Ejemplo 2 paso a paso | 0:55–1:55 | Método Gran M, modo Paso a paso, Resolver. Pestaña Paso a paso: forma estándar, transformación de R3, iteración 1 con el pivote 5/3 resaltado y la tabla de razones; luego pestaña Resultado. | «R3 tiene lado derecho negativo: se multiplica por −1 y ≥ pasa a ≤. Se agregan exceso, holgura y dos artificiales con costo +M simbólico. En la iteración 1 entra x2 por el menor costo reducido; las razones son 3, 6/5 y 9/5, sale a2 y el pivote es 5/3. El óptimo es x1 = 2/5, x2 = 9/5, Z = 17/5, con R2 en exceso 1.» | [Integrante 2] |
| 4. Sensibilidad | 1:55–2:35 | Pestaña Sensibilidad: precios sombra, costos reducidos, rangos e interpretaciones. | «El precio sombra de R1 es 7/5: cada unidad adicional aumenta Z en 7/5 mientras su lado derecho esté entre 2 y 12. La app muestra también los costos reducidos y el rango de cada coeficiente de Z, siempre variando un solo dato.» | [Integrante 2] |
| 5. Ejemplo 6 y método gráfico | 2:35–3:20 | Cargar `ejemplo_6.json`, Resolver. Pestaña Resultado: mensaje del segmento. Pestaña Método gráfico: región, vértices con Z, isoutilidad y segmento verde. | «Este problema tiene óptimos múltiples: “Z = 10 en todo el segmento entre (0, 5/2) y (3, 1)”. El gráfico, calculado de forma independiente al simplex, sombrea la región, rotula restricciones y vértices con su Z y muestra la isoutilidad sobre el segmento óptimo.» | [Integrante 3] |
| 6. Caso especial | 3:20–3:50 | Cargar `ejemplo_5.json`, Resolver. Resultado y Método gráfico con la flecha de mejora y el aviso de región no acotada. | «Aquí el problema es no acotado: la app da la dirección (1, 0) + t·(1, 1) en la que Z crece sin límite. Ningún caso especial produce un error del programa; los infactibles y degenerados también tienen su mensaje.» | [Integrante 3] |
| 7. Comparación, JSON y PDF | 3:50–4:25 | Volver a `ejemplo_2.json`, Método «Comparar ambos», Resolver; pestaña Comparar métodos. Pulsar «Exportar paso a paso a PDF» y abrir el archivo. Pulsar Guardar JSON. | «Con Comparar ambos se ven las iteraciones de los dos métodos lado a lado: las bases coinciden en todos los estados. El paso a paso se exporta a PDF con fracciones o decimales, y el problema se guarda y se carga en JSON.» | [Integrante 4] (o [Integrante 1] si son tres) |
| 8. Cierre | 4:25–4:45 | README del repositorio o pestaña Resultado. | «SciPy solo se usa en las pruebas para verificar resultados, nunca en la app. El código, el manual y las instrucciones están en el repositorio. Gracias.» | [Integrante 1] |

## Lista de comprobación de grabación

- [ ] Resolución de pantalla 1920 × 1080 y zoom del navegador entre 110 % y
  125 %, de modo que las tablas y los rótulos del gráfico se lean en el video.
- [ ] Ventana privada, sin marcadores, notificaciones ni datos personales a la
  vista. Cerrar otras pestañas y aplicaciones que puedan mostrar avisos.
- [ ] La app arranca antes de grabar y responde en la URL o en `localhost`.
- [ ] Micrófono probado; cada integrante dice su parte con su propia voz.
- [ ] Ensayo completo con cronómetro, al menos dos veces. Si un tramo se pasa,
  recortar el texto, no acelerar la voz.
- [ ] Medir la duración del archivo final en el reproductor (o con `ffprobe`)
  y confirmar que es de 5:00 o menos antes de publicarlo.
- [ ] Publicar el video con acceso para el docente y probar el enlace en una
  ventana privada. Registrar la URL en `README.md` y en `docs/manual/README.md`.
