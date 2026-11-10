# Reglas del proyecto

El objetivo es desarrollar una aplicación verificable y explicable. El enunciado
`taller-optimi.pdf` tiene prioridad sobre `PROMPT-entorno.md`. No mover, renombrar ni
borrar ninguno de esos archivos.

1. No importar librerías de optimización en `src/` ni `app/`: SciPy, PuLP,
   OR-Tools, CVXPY, Pyomo ni equivalentes. SciPy pertenece solo al grupo `dev`
   y se usa únicamente en `tests/` y `scripts/` como verificación independiente.
   Conservar la prueba de imports con AST.
2. La fase de preparación terminó. Implementar los algoritmos por paquetes según
   `PROMPT-desarrollo.md`, con firmas tipadas, código explicable y docstrings en
   español. Mantener `docs/sustentacion.md` al día; conservar como stubs los
   módulos fuera del alcance de la sesión.
3. Sí implementar modelo de datos, lectura y validación, JSON, formato,
   interfaz base, pruebas, oráculo externo, CI y documentación.
4. Interfaz, mensajes, comentarios y docstrings en español; identificadores en inglés.
5. Mantener código simple, funciones legibles y sin metaprogramación. Cada
   integrante debe poder explicar y modificar cualquier parte en la sustentación.
6. La interfaz nunca debe mostrar un traceback. Capturar `NotImplementedError`
   por módulo y mostrar un aviso; los errores inesperados llevan un mensaje
   comprensible en español. No usar resultados esperados de fixtures en la UI.
7. Usar Python 3.12 mediante uv, layout `src/`, paquete `plapp`, Fraction en el
   modelo y los algoritmos y M simbólica `a + b·M`; no usar Python del sistema.
8. Mantener `uv.lock` y exportar `requirements.txt` sin dependencias dev mediante
   `make requirements`. Ejecutar `make lint` y `make test` antes de finalizar.
9. Solo las pruebas de algoritmos pendientes usan
   `xfail(raises=NotImplementedError, strict=False)`. Quitar la marca al implementar
   el módulo. No ocultar errores de aserción ni marcar infraestructura como xfail.
10. Preservar cambios ajenos. Hacer commits locales pequeños con Conventional
    Commits, asunto menor de 50 caracteres. No crear remotos ni hacer push.
    No versionar `.venv`, cachés, `.env` ni secretos.

