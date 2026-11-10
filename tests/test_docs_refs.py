"""Referencias `ruta:línea` de la documentación vigente.

Se revisan `README.md` y los Markdown de `docs/`. Se excluyen los informes
históricos `docs/desarrollo-*.md` y `docs/verificacion.md`: registran líneas
del código en el momento de cada sesión y no se reescriben después. La prueba
solo garantiza que el archivo exista y que la línea no supere su longitud; que
la línea citada sea la correcta se revisa a mano.
"""

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
HISTORICAL = {"verificacion.md"}
REFERENCE = re.compile(
    r"((?:src|app|scripts|tests|docs|assets)/[\w./-]+\.\w+|README\.md|Makefile|pyproject\.toml)"
    r":(\d+)(?:[-–](\d+))?"
)


def current_documents() -> list[Path]:
    """Documentos que deben seguir el código actual, sin informes históricos."""
    documents = [ROOT / "README.md", *sorted((ROOT / "docs").rglob("*.md"))]
    return [
        path
        for path in documents
        if path.name not in HISTORICAL and not path.name.startswith("desarrollo-")
    ]


def references(path: Path) -> list[tuple[str, int, int]]:
    """Extraer cada referencia como (ruta, primera línea, última línea)."""
    found = []
    for match in REFERENCE.finditer(path.read_text(encoding="utf-8")):
        first = int(match.group(2))
        found.append((match.group(1), first, int(match.group(3) or first)))
    return found


def test_guide_has_references():
    """La expresión regular debe encontrar las referencias de la guía."""
    assert len(references(ROOT / "docs/sustentacion.md")) >= 20


@pytest.mark.parametrize(
    "document", current_documents(), ids=lambda path: str(path.relative_to(ROOT))
)
def test_references_point_to_existing_lines(document):
    name = document.relative_to(ROOT)
    for target, first, last in references(document):
        path = ROOT / target
        assert path.is_file(), f"{name}: no existe {target}"
        length = len(path.read_text(encoding="utf-8").splitlines())
        assert 1 <= first <= last <= length, (
            f"{name}: {target}:{first}-{last} supera {length} líneas"
        )
