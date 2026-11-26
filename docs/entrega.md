# Guía de entrega

Pasos para que el equipo publique el repositorio, despliegue la app, grabe el
video y llegue a la sustentación con un plan B. Ninguno de estos pasos se ha
ejecutado todavía: no hay remoto, despliegue ni video. Los nombres ya están;
faltan documentos, cuentas Git y responsables. Lo que sí se ensayó localmente está en «Ensayos locales hechos» y en
`docs/desarrollo-v-p8.md`.

Documentación oficial consultada el 2026-11-10:

- Streamlit Community Cloud:
  [dependencias](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/app-dependencies),
  [despliegue](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy),
  [versión de Python](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/upgrade-python),
  [cuenta de GitHub](https://docs.streamlit.io/deploy/streamlit-community-cloud/get-started/connect-your-github-account)
  y [administración de la app](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app).
- uv: [dependencias y grupos](https://docs.astral.sh/uv/concepts/projects/dependencies/).

## 1. Completar los datos del equipo

Cada integrante completa sus propios datos y los registra en un commit propio
(sección 3):

| Dato | Archivo |
|---|---|
| Nombre, identificador, área y cuenta Git | Tabla «Equipo y entregables» de `README.md`; tabla «Integrantes» de `docs/propuesta.md` |
| Equipo, URL de la app, repositorio, video y contacto | Marcadores `[por completar]` de `docs/manual/README.md` |
| Responsable de cada criterio | Columna «Responsable» de `docs/plan.md` |
| Quién dice cada tramo | Columna «Quién habla» de `docs/video.md` |
| Herramientas de IA usadas por cada integrante | Sección «Uso de herramientas de IA» de `README.md` |
| URL del repositorio, despliegue y video | Lista «Equipo y entregables» de `README.md` |

Después de cambiar `docs/manual/README.md`, regenerar el PDF y comprobarlo:

```bash
make manual        # imprime «Manual: docs/manual/manual.pdf, N páginas»; falla si N > 5
uv run pytest tests/test_manual.py
```

`make manual` necesita Chromium de Playwright: la primera vez, ejecutar
`uv run playwright install chromium`. Abrir el PDF y revisar cada página.

## 2. Crear el remoto y subir la rama principal

Community Cloud pide una cuenta de GitHub («You must have a GitHub account») y
su documentación solo describe repositorios de GitHub. Por eso conviene crear el
remoto en GitHub aunque el curso acepte GitLab. Un repositorio privado necesita
dar a Community Cloud permisos adicionales.

`main` es ancestro de `feat/v-p8`, y las ramas `feat/p1-p3`, `feat/c-p4-p5` y
`feat/r-p6-p7` ya están contenidas en ella. Fusionar es decisión del equipo; con
avance rápido no se crea ningún commit nuevo ni se reescribe el historial:

```bash
git status                      # los PROMPT-*.md locales no se versionan
git switch main
git merge --ff-only feat/v-p8
make lint && make test
git remote add origin https://github.com/<cuenta>/<repositorio>.git
git push -u origin main
```

Al subir, GitHub Actions ejecuta `.github/workflows/ci.yml`: `uv sync --locked`,
Ruff y pytest con Python 3.12. Abrir la pestaña «Actions» del repositorio y
confirmar que la ejecución termina en verde. Las pruebas no necesitan Chromium.

## 3. Commits de cada integrante (taller 6a)

El taller exige un repositorio con commits de todos los integrantes. Hoy todos
los commits tienen el mismo autor. Cada integrante debe aportar commits propios con
trabajo real:

```bash
git config user.name "Nombre Apellido"
git config user.email "correo@udea.edu.co"
git switch -c docs/datos-nombre       # o trabajar en main si el equipo lo acuerda
# ... editar ...
make lint && make test
git add <archivos>
git commit -m "docs: add member data"
git push -u origin docs/datos-nombre  # y abrir un pull request, o fusionar en main
```

Ejemplos de trabajo propio: completar sus datos, ajustar el guion de su tramo,
agregar la prueba sugerida en la modificación M6 de `docs/ensayo-sustentacion.md`,
corregir lo que encuentre al ensayar su módulo o completar su parte de «Uso de
herramientas de IA».

No reescribir el historial: nada de `git commit --amend` ni `git rebase` sobre
commits ya subidos, y nada de `git push --force` en `main`. No usar `--author`
con el nombre de otra persona ni atribuirse trabajo ajeno. Varios commits
existentes llevan la línea `Co-Authored-By` de un asistente de IA; declarar en
«Uso de herramientas de IA» cómo se usaron estas herramientas.

## 4. Desplegar en Streamlit Community Cloud

1. Entrar a <https://share.streamlit.io> con la cuenta de GitHub y pulsar
   «Create app» y luego «Yup, I have an app».
2. Repositorio: el del paso 2. Rama: `main`. Archivo principal:
   `app/streamlit_app.py`. Opcional: un subdominio en «App URL».
3. En «Advanced settings», elegir **Python 3.12**. La página de despliegue dice
   que Community Cloud usa 3.12 por defecto, pero el valor por defecto cambia
   con las versiones nuevas: confirmarlo en el menú. `pyproject.toml` exige
   `>=3.12,<3.13`. No hace falta configurar secretos. Pulsar «Save».
4. Esperar la instalación y revisar el registro en «Manage app», esquina
   inferior derecha. Solo lo ven quienes tienen permiso de escritura en el
   repositorio.

La versión de Python no se puede cambiar después: «After you have deployed an
app, you must delete it and redeploy it to change the version of Python it
uses».

### Qué archivo de dependencias usará

Según la página de dependencias:

- Community Cloud busca primero en la carpeta del archivo de entrada (`app/`) y
  después en la raíz del repositorio.
- Reconoce, en este orden, `uv.lock`, `Pipfile`, `environment.yml`,
  `requirements.txt` y `pyproject.toml`, y usa el primero que encuentra («will
  use the first dependency file it finds»).
- Advierte: «You should only use one dependency file for your app».

`app/` no tiene archivos de dependencias, y en la raíz están `uv.lock`,
`requirements.txt` y `pyproject.toml`. Por lo tanto Community Cloud instalará
desde **`uv.lock`** e ignorará `requirements.txt`. Ambos describen las mismas
versiones de ejecución, porque `requirements.txt` se genera desde el lockfile con
`make requirements` (`uv export --locked --no-dev`). El proyecto conserva los dos
archivos: `requirements.txt` sirve para instalar sin el grupo dev.

**Incluye o no el grupo `dev`.** La documentación de Streamlit no dice qué
comando de uv ejecuta con `uv.lock` ni menciona grupos de dependencias. La de uv
dice: «By default, uv includes the `dev` dependency group in the environment
(e.g., during `uv run` or `uv sync`)». Si Community Cloud ejecuta `uv sync` sin
opciones, instalará también el grupo dev: pytest, Hypothesis, Ruff, SciPy, el
paquete de Playwright (sin navegador), pypdf y markdown-it-py. Esto no se pudo
confirmar sin desplegar. En el registro de instalación se ve qué paquetes
instala.

En cualquiera de los dos casos la app funciona: sus dependencias de ejecución
(Streamlit, Plotly, fpdf2 y FontTools) están en `[project.dependencies]`, y la
app nunca importa SciPy. El ensayo local midió ambos casos (sección 7):
`uv sync --locked` instala 52 paquetes (640 MB) y `uv sync --locked --no-dev`
instala 37 (375 MB).

Si la instalación con dev falla o tarda demasiado, el equipo puede decidir
agregar `default-groups = []` en una sección `[tool.uv]` de `pyproject.toml`.
Ese cambio obliga a usar `uv sync --group dev` en CI, en `make setup` y en cada
equipo de trabajo. No se hizo porque no es necesario para que la app funcione.

### Verificar la URL

- Abrir la URL en una ventana privada, sin sesión iniciada.
- Ejemplo 2, Gran M, Paso a paso: pivote 5/3 y Z = 17/5. Descargar «Exportar
  paso a paso a PDF» y abrirlo.
- Ejemplo 6: el mensaje «Z = 10 en todo el segmento entre (0, 5/2) y (3, 1)» y
  el gráfico con el segmento verde.
- Registrar la URL en `README.md` y en `docs/manual/README.md` (sección 1).

Community Cloud duerme las apps sin tráfico: «All apps without traffic for 12
hours go to sleep». Abrir la URL antes de la sustentación; si está dormida,
pulsar «Yes, get this app back up!» y esperar a que arranque.

## 5. Grabar el video

Seguir `docs/video.md`: tramos, textos y lista de comprobación. Duración máxima
5:00. Publicarlo con acceso para el docente, probar el enlace en una ventana
privada y registrar la URL en `README.md` y `docs/manual/README.md`. Luego
regenerar el manual (sección 1).

## 6. Plan B: la app en el portátil de la sustentación (condición 2b)

La condición 2b exige que la app funcione en la sustentación, en el equipo del
estudiante o en la URL. Instalar y probar en el portátil **días antes**, con red:

```bash
# Instalar uv según https://docs.astral.sh/uv/
git clone https://github.com/<cuenta>/<repositorio>.git plapp
cd plapp
uv python install 3.12
uv sync --locked
uv run playwright install chromium     # para make ui-check y make manual
make lint && make test                 # en Windows sin make: uv run ruff check . y uv run pytest
uv run streamlit run app/streamlit_app.py --browser.gatherUsageStats false
```

Abrir <http://localhost:8501>, resolver los ejemplos 2 y 6, descargar el PDF y
detener con Ctrl-C. Si el portátil tiene `make`, `make ui-check` hace la misma
revisión con el navegador.

El día de la sustentación no se necesita red. Desde la carpeta `plapp`:

```bash
uv run streamlit run app/streamlit_app.py --browser.gatherUsageStats false
```

Si uv intenta conectarse, usar `uv run --offline streamlit run ...` con las
mismas opciones. Llevar además el portátil cargado, el cargador y una copia del
repositorio en una memoria USB, con `docs/manual/manual.pdf`.

## 7. Ensayos locales hechos

Ensayos del 2026-11-10 sobre la rama `feat/v-p8`, cada uno en un clon limpio
(`git clone`) dentro de un directorio temporal que se borró al terminar. Los
commits exactos están en `docs/desarrollo-v-p8.md`.

1. **Solo `requirements.txt`.** `uv venv --python 3.12` y
   `uv pip install -r requirements.txt`, sin `uv sync` ni grupo dev:
   - Python 3.12.13; SciPy, pytest, Playwright, pypdf, Hypothesis, Ruff y
     markdown-it-py no se pueden importar.
   - `plapp` queda instalado en `site-packages`, con DejaVu Sans y su licencia
     en `plapp/assets/fonts`. Así se comprueba que `.` en `requirements.txt`
     instala el paquete con sus fuentes.
   - El servidor headless responde `ok` en `/_stcore/health`.
   - `scripts/check_ui.py --url … --solutions --downloads`, ejecutado desde el
     entorno dev, dibujó 9 gráficos, resolvió los ejemplos 2, 5 y 6 en ambos
     modos y formatos y descargó 36 PDF. El paso a paso del ejemplo 2 contiene
     `MIN Z = 4·x1 + x2`, `Z = 17/5` y la nota de la fuente después de
     «Resultado final».
   - El registro del servidor no tiene errores.
2. **Ruta de `uv.lock`.** `uv sync --locked` instaló 52 paquetes, entre ellos
   SciPy y Playwright. `uv sync --locked --no-dev` instaló 37. Con el segundo,
   la app respondió `ok` y `check_ui.py` dibujó los 9 gráficos.
3. **Plan B sin red.** Después de `uv sync --locked`, la red externa se
   bloqueó con `sandbox-exec` de macOS. `make lint`, el servidor
   (`uv run streamlit run …`) y `check_ui.py --solutions` con Chromium
   funcionaron sin red, con los ejemplos 2, 5 y 6 resueltos.

No se probó el despliegue real en Community Cloud ni la instalación en Windows.

## 8. Lista de comprobación final

- [ ] CI en verde en el remoto, sobre el último commit de `main`.
- [ ] URL de la app abierta en una ventana privada.
- [ ] Ejemplos 2 y 6 resueltos en la URL, con el PDF del ejemplo 2 descargado.
- [ ] Manual regenerado con `make manual`, de 5 páginas o menos, revisado
      página por página.
- [ ] Video de 5:00 o menos, publicado y con el enlace probado.
- [ ] Nombres completos en `README.md`, `docs/propuesta.md`, el manual y el
      plan; sin `[por completar]` ni `[Integrante]`.
- [ ] «Uso de herramientas de IA» completo en `README.md`.
- [ ] Commits propios de cada integrante en el remoto.
- [ ] Ensayo de 15 minutos de cada integrante con `docs/ensayo-sustentacion.md`,
      incluida al menos una modificación en vivo.
- [ ] Plan B probado en el portátil de la sustentación (sección 6).
