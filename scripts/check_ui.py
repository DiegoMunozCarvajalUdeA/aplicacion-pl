"""Capturar gráficos en Chromium; ejecutar contra un servidor local ya iniciado."""

import argparse
from pathlib import Path

from playwright.sync_api import Page, expect, sync_playwright


def select(page: Page, label: str, value: str) -> None:
    """Elegir una opción por su texto para no depender del orden del selector."""
    page.get_by_role("combobox", name=label, exact=True).click()
    page.get_by_role("option", name=value, exact=True).click()
    expect(page.get_by_role("combobox", name=label, exact=True)).to_have_value(value)


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


def main() -> None:
    """Comprobar salud, tomar capturas y cerrar Chromium incluso ante fallos."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8501")
    parser.add_argument("--output", type=Path, default=Path("/tmp/plapp-ui"))
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
        finally:
            browser.close()


if __name__ == "__main__":
    main()
