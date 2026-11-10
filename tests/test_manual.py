"""El manual impreso debe cumplir el límite del taller y reflejar su Markdown."""

import re
from pathlib import Path

from pypdf import PdfReader

MANUAL = Path(__file__).resolve().parents[1] / "docs/manual"


def test_manual_pdf_has_at_most_five_pages():
    """El taller 6c limita el manual a cinco páginas."""
    assert 1 <= len(PdfReader(MANUAL / "manual.pdf").pages) <= 5


def test_manual_images_are_real_captures():
    """Cada imagen citada existe en capturas/, que solo llena `make manual-captures`."""
    text = (MANUAL / "README.md").read_text(encoding="utf-8")
    images = re.findall(r"!\[[^\]]*\]\(([^) ]+)", text)
    assert len(images) >= 8
    assert all(name.startswith("capturas/") and (MANUAL / name).is_file() for name in images)


def test_manual_only_team_placeholders_remain():
    """Solo pueden quedar marcadores [por completar] para datos que aporta el equipo.

    Cuando el equipo complete nombres y URL, la lista queda vacía y la prueba
    sigue pasando.
    """
    text = (MANUAL / "README.md").read_text(encoding="utf-8")
    # Corchetes que no forman un enlace ni una imagen de Markdown.
    markers = re.findall(r"(?<!!)\[([^\]]*)\](?!\()", text)
    assert set(markers) <= {"por completar"}


def test_manual_pdf_matches_markdown_sections():
    """El PDF versionado debe regenerarse con `make manual` al cambiar las secciones."""
    text = (MANUAL / "README.md").read_text(encoding="utf-8")
    headings = re.findall(r"^## (.+)$", text, flags=re.MULTILINE)
    pdf = " ".join(page.extract_text() for page in PdfReader(MANUAL / "manual.pdf").pages)
    pdf = " ".join(pdf.split())
    assert headings and all(heading in pdf for heading in headings)
