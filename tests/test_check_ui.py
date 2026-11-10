"""El servidor temporal debe detenerse también si falla el recorrido del navegador."""

from urllib.error import URLError
from urllib.request import urlopen

import pytest

from scripts.check_ui import app_server


def test_server_stops_after_check_failure():
    """Provocar una falla tras salud ok y comprobar que no queda una escucha viva."""
    with pytest.raises(RuntimeError, match="Fallo simulado"):
        with app_server("", True) as url:
            with urlopen(url + "/_stcore/health", timeout=2) as response:
                assert response.read() == b"ok"
            raise RuntimeError("Fallo simulado")
    with pytest.raises(URLError):
        urlopen(url + "/_stcore/health", timeout=1)


def test_external_server_url_is_preserved():
    """Sin --serve la URL se reutiliza sin iniciar ni detener procesos ajenos."""
    with app_server("http://127.0.0.1:12345", False) as url:
        assert url == "http://127.0.0.1:12345"
