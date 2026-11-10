"""Comprobar la app real y capturar su presentación con Chromium."""

import argparse
import json
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import Locator, Page, expect, sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/problems"


@contextmanager
def app_server(url: str, serve: bool, timeout: float = 40):
    """Administrar el servidor propio y detenerlo incluso si falla una comprobación."""
    if not serve:
        yield url
        return
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    local_url = f"http://127.0.0.1:{port}"
    with tempfile.TemporaryFile(mode="w+") as log:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app/streamlit_app.py",
                "--server.headless",
                "true",
                "--server.address",
                "127.0.0.1",
                "--server.port",
                str(port),
                "--browser.gatherUsageStats",
                "false",
            ],
            cwd=ROOT,
            stdout=log,
            stderr=subprocess.STDOUT,
        )
        try:
            deadline = time.monotonic() + timeout
            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        "Streamlit terminó antes de responder a la comprobación de salud."
                    )
                try:
                    with urlopen(local_url + "/_stcore/health", timeout=1) as response:
                        if response.read() == b"ok":
                            break
                except (URLError, TimeoutError):
                    pass
                time.sleep(0.1)
            else:
                raise TimeoutError("Streamlit no respondió a tiempo a la comprobación de salud.")
            print("Salud: ok")
            yield local_url
        finally:
            process.terminate()
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


def select(page: Page, label: str, value: str) -> None:
    """Elegir una opción por su texto para no depender del orden del selector."""
    page.get_by_role("combobox", name=label, exact=True).click()
    page.get_by_role("option", name=value, exact=True).click()
    expect(page.get_by_role("combobox", name=label, exact=True)).to_have_value(value)
    wait_ready(page)


def wait_ready(page: Page) -> None:
    """Esperar el rerun de Streamlit antes de usar sus URL temporales de descarga."""
    page.wait_for_timeout(150)
    expect(page.locator('[data-testid="stApp"]')).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=30000
    )


def load_example(page: Page, filename: str) -> None:
    """Cargar un ejemplo y esperar su rerun antes del siguiente clic.

    Si se pulsa Resolver mientras el rerun de la carga sigue en curso, el
    navegador todavía envía el sentido anterior y la app lo aplica al nuevo
    problema. Por eso se comprueba el resumen con el dato de entrada «sentido»
    del archivo; nunca se lee el bloque de resultados esperados.
    """
    select(page, "Ejemplo", filename)
    page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
    wait_ready(page)
    sense = json.loads((FIXTURES / filename).read_text(encoding="utf-8"))["sentido"]
    summary = page.locator('[data-testid="stExpander"]').first
    expect(summary).to_contain_text(f"{sense.upper()} Z")


def solve(page: Page) -> None:
    """Pulsar Resolver y esperar a que la app termine de presentar el resultado."""
    page.get_by_role("button", name="Resolver", exact=True).click()
    wait_ready(page)


def capture_region(page: Page, first: Locator, last: Locator, path: Path) -> None:
    """Recortar desde un elemento hasta otro para conservar el contexto de la captura."""
    first.scroll_into_view_if_needed()
    viewport = page.viewport_size
    bottom = last.bounding_box()
    if viewport and bottom and bottom["y"] + bottom["height"] > viewport["height"]:
        # Llevar el primer elemento cerca del borde superior, debajo de la cabecera fija.
        first.evaluate(
            """element => {
                element.scrollIntoView({block: "start"});
                let node = element.parentElement;
                while (node && !["auto", "scroll"].includes(getComputedStyle(node).overflowY)) {
                    node = node.parentElement;
                }
                if (node) node.scrollTop -= 90;
            }"""
        )
        page.wait_for_timeout(200)
    top, bottom = first.bounding_box(), last.bounding_box()
    assert top and bottom, f"{path.name}: elementos no visibles"
    assert viewport and bottom["y"] + bottom["height"] <= viewport["height"], (
        f"{path.name}: la región no cabe en la ventana; aumente su altura."
    )
    left = min(top["x"], bottom["x"]) - 8
    right = max(top["x"] + top["width"], bottom["x"] + bottom["width"]) + 8
    clip = {
        "x": max(left, 0),
        "y": max(top["y"] - 8, 0),
        "width": right - max(left, 0),
        "height": bottom["y"] + bottom["height"] - top["y"] + 16,
    }
    page.screenshot(path=str(path), clip=clip)


def check_no_errors(page: Page) -> None:
    """Fallar si la app mostró un traceback o un aviso de error inesperado."""
    assert not page.locator('[data-testid="stException"]').count()
    assert not page.locator('[data-testid="stAlertContentError"]').count()


def capture_graphs(page: Page, output: Path) -> None:
    """Guardar los seis casos exigidos y los tres ensayos de dos variables."""
    # Los ensayos (infactible, no acotado y óptimos múltiples) se contrastan con el
    # gráfico en docs/ensayo-sustentacion.md.
    for name in (
        "ejemplo_1",
        "ejemplo_5",
        "ejemplo_6",
        "ejemplo_7",
        "extra_1",
        "extra_3",
        "ensayo_1",
        "ensayo_2",
        "ensayo_3",
    ):
        load_example(page, name + ".json")
        page.get_by_role("tab", name="Método gráfico", exact=True).click()
        chart = page.locator('[data-testid="stPlotlyChart"]')
        expect(chart.locator(".js-plotly-plot")).to_be_visible()
        # Plotly termina el dibujo después del rerun del servidor.
        page.wait_for_timeout(400)
        page.get_by_role("tabpanel").filter(visible=True).screenshot(
            path=str(output / f"{name}.png")
        )
        check_no_errors(page)
        print(f"Gráfico: {name}")


def download_pdf(page: Page, label: str, path: Path) -> None:
    """Descargar desde el navegador y comprobar que se recibió un archivo PDF real."""
    with page.expect_download() as received:
        page.get_by_role("button", name=label, exact=True).click()
    download = received.value
    failure = download.failure()
    assert failure is None, f"{label}: {failure}; {download.url}"
    download.save_as(path)
    assert path.read_bytes().startswith(b"%PDF-")
    text = "\n".join(page.extract_text() for page in PdfReader(path).pages)
    if path.name.startswith("ejemplo_2"):
        assert (
            "Z = 3.4" in text and "17/5" not in text
            if "Decimales" in path.name
            else "Z = 17/5" in text
        )


def check_solutions(page: Page, output: Path, downloads: bool = False) -> None:
    """Recorrer comparación en ambos modos y formatos con casos de la rúbrica."""
    select(page, "Método", "Comparar ambos")
    for example in (2, 5, 6):
        load_example(page, f"ejemplo_{example}.json")
        for mode in ("Directo", "Paso a paso"):
            page.locator('[data-testid="stSidebar"]').get_by_text(mode, exact=True).click()
            wait_ready(page)
            for number_format in ("Fracciones", "Decimales"):
                select(page, "Formato numérico", number_format)
                solve(page)
                page.get_by_role("tab", name="Comparar métodos", exact=True).click()
                summary = "Mismo estado: Sí" if example == 5 else "Misma solución: Sí. Mismo Z: Sí."
                expect(page.get_by_text(summary, exact=False)).to_be_visible()
                expect(page.get_by_text("Base coincide", exact=True)).to_be_visible()
                wait_ready(page)
                check_no_errors(page)
                if downloads:
                    stem = f"ejemplo_{example}_{mode.replace(' ', '_')}_{number_format}"
                    for label, method in (("Gran M", "big_m"), ("Simplex revisado", "revised")):
                        download_pdf(
                            page, f"Exportar PDF: {label}", output / f"{stem}_{method}.pdf"
                        )
                    page.get_by_role("tab", name="Paso a paso", exact=True).click()
                    download_pdf(page, "Exportar paso a paso a PDF", output / f"{stem}_pasos.pdf")
                    page.get_by_role("tab", name="Comparar métodos", exact=True).click()
                print(f"Solución: ejemplo {example}, {mode}, {number_format}")
    page.locator('[data-testid="stTable"]').filter(
        has=page.get_by_text("Base coincide", exact=True)
    ).screenshot(path=str(output / "comparacion.png"))


def capture_manual(page: Page, output: Path) -> None:
    """Capturar entrada, validación y los ejemplos 2 y 6 resueltos por la app.

    Todas las cifras visibles provienen de la interfaz en ejecución; el script
    no consulta resultados esperados ni SciPy.
    """
    output.mkdir(parents=True, exist_ok=True)
    # Un ancho menor evita tablas casi vacías; el gráfico usa luego el ancho de R y V.
    page.set_viewport_size({"width": 1180, "height": 1700})
    sidebar = page.locator('[data-testid="stSidebar"]')
    select(page, "Método", "Gran M")
    sidebar.get_by_text("Paso a paso", exact=True).click()
    wait_ready(page)
    load_example(page, "ejemplo_2.json")
    capture_region(
        page,
        page.locator('[data-testid="stAppViewContainer"]'),
        page.locator('[data-testid="stExpander"]').first,
        output / "entrada.png",
    )
    # Editar la celda real del canvas, igual que el usuario en la interfaz.
    grid = page.locator('[data-testid="stDataFrame"]').first.locator(".dvn-scroller")
    grid.dblclick(position={"x": 65, "y": 55})
    editor = page.locator(".dvn-scroller input, .gdg-input")
    expect(editor).to_be_visible()
    editor.fill("abc")
    editor.press("Enter")
    wait_ready(page)
    solve(page)
    error = page.locator('[data-testid="stAlertContentError"]')
    expect(error).to_contain_text("objetivo, x1")
    capture_region(
        page,
        page.get_by_role("heading", name="Función objetivo"),
        error,
        output / "validacion.png",
    )
    load_example(page, "ejemplo_2.json")
    solve(page)
    check_no_errors(page)
    page.get_by_role("tab", name="Resultado", exact=True).click()
    page.get_by_role("tabpanel").filter(visible=True).screenshot(
        path=str(output / "ejemplo_2_resultado.png")
    )
    page.get_by_role("tab", name="Paso a paso", exact=True).click()
    panel = page.get_by_role("tabpanel").filter(visible=True)
    panel.locator('[data-testid="stExpander"]').filter(
        has=page.get_by_text("Iteración 1", exact=True)
    ).screenshot(path=str(output / "ejemplo_2_pivote.png"))
    capture_region(
        page,
        panel.get_by_role("heading", name="Forma estándar"),
        panel.locator('[data-testid="stMarkdown"]').filter(has_text="Base inicial").first,
        output / "ejemplo_2_estandar.png",
    )
    page.get_by_role("tab", name="Sensibilidad", exact=True).click()
    panel = page.get_by_role("tabpanel").filter(visible=True)
    panel.locator('[data-testid="stTable"]').first.screenshot(
        path=str(output / "ejemplo_2_sensibilidad.png")
    )
    capture_region(
        page,
        panel.get_by_text("Rangos de lados derechos", exact=True),
        panel.locator('[data-testid="stMarkdown"]').last,
        output / "ejemplo_2_rangos.png",
    )
    select(page, "Método", "Comparar ambos")
    solve(page)
    page.get_by_role("tab", name="Comparar métodos", exact=True).click()
    page.get_by_role("tabpanel").filter(visible=True).locator(
        '[data-testid="stTable"]'
    ).first.screenshot(path=str(output / "comparacion.png"))
    select(page, "Método", "Gran M")
    load_example(page, "ejemplo_6.json")
    solve(page)
    check_no_errors(page)
    page.get_by_role("tab", name="Resultado", exact=True).click()
    page.get_by_role("tabpanel").filter(visible=True).screenshot(
        path=str(output / "ejemplo_6_resultado.png")
    )
    page.set_viewport_size({"width": 1440, "height": 1100})
    page.get_by_role("tab", name="Método gráfico", exact=True).click()
    expect(page.locator('[data-testid="stPlotlyChart"] .js-plotly-plot')).to_be_visible()
    # Plotly vuelve a dibujar al cambiar el ancho de la ventana.
    page.wait_for_timeout(800)
    page.get_by_role("tabpanel").filter(visible=True).screenshot(
        path=str(output / "ejemplo_6_grafico.png")
    )
    check_no_errors(page)
    print("Manual: diez capturas reales guardadas")


def main() -> None:
    """Comprobar salud, tomar capturas y cerrar Chromium incluso ante fallos."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=Path("/tmp/plapp-ui"))
    parser.add_argument("--solutions", action="store_true")
    parser.add_argument("--downloads", action="store_true")
    parser.add_argument("--serve", action="store_true", help="Iniciar y detener un servidor propio")
    parser.add_argument(
        "--manual", action="store_true", help="Capturar el manual en docs/manual/capturas"
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with app_server(args.url, args.serve) as url, sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            # Las capturas del manual usan doble densidad para leerse al imprimirlas reducidas.
            page = browser.new_page(
                viewport={"width": 1440, "height": 1100},
                device_scale_factor=2 if args.manual else 1,
            )
            assert page.request.get(url + "/_stcore/health").text() == "ok"
            page.goto(url)
            page.wait_for_load_state("networkidle")
            page.get_by_role("tab", name="Método gráfico", exact=True).wait_for()
            if args.manual:
                capture_manual(page, ROOT / "docs/manual/capturas")
            else:
                capture_graphs(page, args.output)
                if args.solutions or args.downloads:
                    check_solutions(page, args.output, args.downloads)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
