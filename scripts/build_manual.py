"""Generar el manual en PDF desde su Markdown, con Chromium y CSS de impresión.

El Markdown de `docs/manual/README.md` es la fuente única: se convierte a HTML
con markdown-it-py y Chromium lo imprime en A4. El título de cada imagen indica
su ancho impreso (por ejemplo "72%") y, si agrega «derecha», la imagen flota a
la derecha del texto que la sigue. Las imágenes y la fuente DejaVu Sans se incrustan
como datos para que el resultado no dependa de las fuentes de cada equipo.
"""

import argparse
import base64
from pathlib import Path

from markdown_it import MarkdownIt
from playwright.sync_api import sync_playwright
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
MANUAL = ROOT / "docs/manual"
FONTS = ROOT / "assets/fonts"
MAX_PAGES = 5

CSS = """
@font-face { font-family: "DejaVu Sans"; src: url("{regular}"); }
@font-face { font-family: "DejaVu Sans"; font-weight: bold; src: url("{bold}"); }
@page { size: A4; margin: 14mm 15mm 16mm 15mm; }
body { font-family: "DejaVu Sans"; font-size: 9pt; line-height: 1.4; color: #111827; }
h1 { font-size: 15pt; margin: 0 0 4pt; }
h2 { font-size: 11.5pt; margin: 9pt 0 3pt; border-bottom: 1px solid #d1d5db; }
p, ul, ol { margin: 3pt 0; }
li { margin: 1pt 0; }
code { font-size: 8pt; background: #f3f4f6; padding: 0 2pt; }
p:has(> img) { text-align: center; clear: both; }
h2 { clear: both; break-after: avoid; }
img { display: inline-block; vertical-align: top; margin: 3pt 0.5%; border: 1px solid #d1d5db; }
table { border-collapse: collapse; width: 100%; margin: 4pt 0; font-size: 8pt; }
th, td { border: 1px solid #d1d5db; padding: 2pt 4pt; text-align: left; vertical-align: top; }
th { background: #f3f4f6; }
"""

FOOTER = (
    '<div style="width: 100%; font-size: 8px; text-align: center; color: #6b7280;">'
    'Página <span class="pageNumber"></span> de <span class="totalPages"></span></div>'
)


def data_uri(path: Path, mime: str) -> str:
    """Incrustar un archivo para que Chromium no necesite leer rutas locales."""
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode("ascii")


def render_html(markdown: str) -> str:
    """Convertir el Markdown a HTML con imágenes incrustadas y su ancho impreso."""
    parser = MarkdownIt("commonmark", {"html": True}).enable("table")
    tokens = parser.parse(markdown)
    for token in tokens:
        for child in token.children or []:
            if child.type != "image":
                continue
            source = MANUAL / str(child.attrGet("src"))
            if not source.is_file():
                raise FileNotFoundError(f"Falta la captura {source.relative_to(ROOT)}.")
            child.attrSet("src", data_uri(source, "image/png"))
            # El título indica el ancho y, opcionalmente, «derecha» para que el
            # texto siguiente rodee la imagen; no se muestra como texto emergente.
            width, *side = str(child.attrGet("title") or "100%").split()
            style = f"width: {width}"
            if side == ["derecha"]:
                style += "; float: right; margin: 0 0 4pt 8pt"
            child.attrSet("style", style)
            del child.attrs["title"]
    css = CSS.replace("{regular}", data_uri(FONTS / "DejaVuSans.ttf", "font/ttf")).replace(
        "{bold}", data_uri(FONTS / "DejaVuSans-Bold.ttf", "font/ttf")
    )
    body = parser.renderer.render(tokens, parser.options, {})
    head = '<!doctype html><html lang="es"><meta charset="utf-8"><title>Manual de usuario</title>'
    return f"{head}<style>{css}</style>{body}"


def build(source: Path, output: Path) -> int:
    """Imprimir el HTML en A4 y fallar si el manual supera el límite del taller."""
    html = render_html(source.read_text(encoding="utf-8"))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.pdf(
                path=str(output),
                format="A4",
                print_background=True,
                prefer_css_page_size=True,
                display_header_footer=True,
                header_template="<div></div>",
                footer_template=FOOTER,
            )
        finally:
            browser.close()
    pages = len(PdfReader(output).pages)
    if pages > MAX_PAGES:
        raise SystemExit(f"El manual tiene {pages} páginas; el taller permite {MAX_PAGES}.")
    return pages


def main() -> None:
    """Generar `docs/manual/manual.pdf` e informar su número de páginas."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=MANUAL / "README.md")
    parser.add_argument("--output", type=Path, default=MANUAL / "manual.pdf")
    args = parser.parse_args()
    pages = build(args.source, args.output)
    print(f"Manual: {args.output.relative_to(ROOT)}, {pages} páginas")


if __name__ == "__main__":
    main()
