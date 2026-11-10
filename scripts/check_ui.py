"""Comprobar la app real y capturar su presentación con Chromium."""

import argparse
import socket
import subprocess
import sys
import tempfile
import time
from contextlib import contextmanager
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

from playwright.sync_api import Page, expect, sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]


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


def capture_graphs(page: Page, output: Path) -> None:
    """Guardar los seis casos exigidos, incluidos vacío y mejora ilimitada."""
    for name in ("ejemplo_1", "ejemplo_5", "ejemplo_6", "ejemplo_7", "extra_1", "extra_3"):
        select(page, "Ejemplo", name + ".json")
        page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
        page.get_by_role("tab", name="Método gráfico", exact=True).click()
        chart = page.locator('[data-testid="stPlotlyChart"]')
        expect(chart.locator(".js-plotly-plot")).to_be_visible()
        page.wait_for_function(
            "name => document.querySelector('[data-testid=stExpander]')?.innerText.includes(name)",
            arg="MIN Z" if name == "extra_1" else "MAX Z",
        )
        # Plotly termina el dibujo después del rerun del servidor.
        page.wait_for_timeout(400)
        page.get_by_role("tabpanel").filter(visible=True).screenshot(
            path=str(output / f"{name}.png")
        )
        assert not page.locator('[data-testid="stException"]').count()
        assert not page.locator('[data-testid="stAlertContentError"]').count()
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
        select(page, "Ejemplo", f"ejemplo_{example}.json")
        page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
        for mode in ("Directo", "Paso a paso"):
            page.locator('[data-testid="stSidebar"]').get_by_text(mode, exact=True).click()
            wait_ready(page)
            for number_format in ("Fracciones", "Decimales"):
                select(page, "Formato numérico", number_format)
                page.get_by_role("button", name="Resolver", exact=True).click()
                page.get_by_role("tab", name="Comparar métodos", exact=True).click()
                summary = "Mismo estado: Sí" if example == 5 else "Misma solución: Sí. Mismo Z: Sí."
                expect(page.get_by_text(summary, exact=False)).to_be_visible()
                expect(page.get_by_text("Base coincide", exact=True)).to_be_visible()
                wait_ready(page)
                assert not page.locator('[data-testid="stException"]').count()
                assert not page.locator('[data-testid="stAlertContentError"]').count()
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
    """Capturar entradas, validación y dos problemas resueltos, sin datos esperados."""
    output.mkdir(parents=True, exist_ok=True)
    select(page, "Ejemplo", "ejemplo_2.json")
    page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
    wait_ready(page)
    page.screenshot(path=str(output / "entrada.png"))
    # Editar la celda real del canvas, igual que el usuario en la interfaz.
    grid = page.locator('[data-testid="stDataFrame"]').first.locator(".dvn-scroller")
    grid.dblclick(position={"x": 65, "y": 55})
    editor = page.locator(".dvn-scroller input, .gdg-input")
    expect(editor).to_be_visible()
    editor.fill("abc")
    editor.press("Enter")
    wait_ready(page)
    page.get_by_role("button", name="Resolver", exact=True).click()
    error = page.locator('[data-testid="stAlertContentError"]')
    expect(error).to_contain_text("objetivo, x1")
    error.screenshot(path=str(output / "validacion.png"))
    page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
    select(page, "Método", "Gran M")
    page.locator('[data-testid="stSidebar"]').get_by_text("Paso a paso", exact=True).click()
    wait_ready(page)
    page.get_by_role("button", name="Resolver", exact=True).click()
    wait_ready(page)
    page.get_by_role("tab", name="Resultado", exact=True).click()
    page.get_by_role("tabpanel").filter(visible=True).screenshot(
        path=str(output / "ejemplo_2_resultado.png")
    )
    page.get_by_role("tab", name="Paso a paso", exact=True).click()
    panel = page.get_by_role("tabpanel").filter(visible=True)
    panel.locator('[data-testid="stExpander"]').filter(
        has=page.get_by_text("Iteración 1", exact=True)
    ).screenshot(path=str(output / "ejemplo_2_pivote.png"))
    for summary in panel.locator('[data-testid="stExpander"] summary').all():
        summary.click()
    panel.screenshot(path=str(output / "ejemplo_2_estandar.png"))
    page.get_by_role("tab", name="Sensibilidad", exact=True).click()
    panel = page.get_by_role("tabpanel").filter(visible=True)
    panel.locator('[data-testid="stTable"]').first.screenshot(
        path=str(output / "ejemplo_2_sensibilidad.png")
    )
    panel.locator('[data-testid="stTable"]').last.screenshot(
        path=str(output / "ejemplo_2_rangos.png")
    )
    select(page, "Método", "Comparar ambos")
    page.get_by_role("button", name="Resolver", exact=True).click()
    page.get_by_role("tab", name="Comparar métodos", exact=True).click()
    page.get_by_role("tabpanel").filter(visible=True).locator(
        '[data-testid="stTable"]'
    ).first.screenshot(path=str(output / "comparacion.png"))
    select(page, "Ejemplo", "ejemplo_6.json")
    page.get_by_role("button", name="Cargar ejemplo", exact=True).click()
    page.get_by_role("button", name="Resolver", exact=True).click()
    page.get_by_role("tab", name="Método gráfico", exact=True).click()
    wait_ready(page)
    page.wait_for_timeout(400)
    page.get_by_role("tabpanel").filter(visible=True).screenshot(
        path=str(output / "ejemplo_6_grafico.png")
    )
    assert not page.locator('[data-testid="stException"]').count()
    assert not page.locator('[data-testid="stAlertContentError"]').count()
    print("Manual: nueve capturas reales guardadas")


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
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
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
