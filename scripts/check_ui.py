"""Capturar gráficos en Chromium; ejecutar contra un servidor local ya iniciado."""

import argparse
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright
from pypdf import PdfReader


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
        chart.screenshot(path=str(output / f"{name}.png"))
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


def main() -> None:
    """Comprobar salud, tomar capturas y cerrar Chromium incluso ante fallos."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=Path("/tmp/plapp-ui"))
    parser.add_argument("--solutions", action="store_true")
    parser.add_argument("--downloads", action="store_true")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page(viewport={"width": 1440, "height": 1100})
            assert page.request.get(args.url + "/_stcore/health").text() == "ok"
            page.goto(args.url)
            page.wait_for_load_state("networkidle")
            page.get_by_role("tab", name="Método gráfico", exact=True).wait_for()
            capture_graphs(page, args.output)
            if args.solutions or args.downloads:
                check_solutions(page, args.output, args.downloads)
        finally:
            browser.close()


if __name__ == "__main__":
    main()
