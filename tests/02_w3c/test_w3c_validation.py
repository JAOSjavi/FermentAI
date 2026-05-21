"""
Pruebas de validación W3C — FermentAI
Valida el HTML generado por el frontend contra el validador oficial nu.validator.w3.org.

Ejecución:
    pytest tests/02_w3c/test_w3c_validation.py -v -m w3c

Requisito: el frontend debe estar corriendo en FERMENTAI_FRONTEND_URL (default: http://localhost:3000)
"""
import time
import pytest
import requests
from playwright.sync_api import sync_playwright

FRONTEND_URL = "http://localhost:3000"
W3C_VALIDATOR_URL = "https://validator.w3.org/nu/"

PAGINAS_PUBLICAS = [
    ("/login", "Página de Login"),
    ("/registro", "Página de Registro"),
]

PAGINAS_PROTEGIDAS = [
    ("/dashboard", "Dashboard Principal"),
    ("/dashboard/datasets", "Datasets Aprobados"),
    ("/dashboard/mis-aportes", "Mis Aportes"),
    ("/dashboard/notificaciones", "Notificaciones"),
]

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"


def _get_html_with_playwright(url: str, cookies: list = None) -> str:
    """Obtiene el HTML renderizado de una página mediante Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=15000)
        html = page.content()
        browser.close()
    return html


def _validate_with_w3c(html: str, page_label: str) -> dict:
    """Envía HTML al validador W3C y retorna el resultado."""
    time.sleep(1)  # respetar rate limit del servicio público
    try:
        response = requests.post(
            W3C_VALIDATOR_URL,
            params={"out": "json"},
            data=html.encode("utf-8"),
            headers={"Content-Type": "text/html; charset=utf-8"},
            timeout=30,
        )
        response.raise_for_status()
        data = response.json()
        messages = data.get("messages", [])
        errors = [m for m in messages if m.get("type") == "error"]
        warnings = [m for m in messages if m.get("type") == "info" and m.get("subType") == "warning"]
        return {
            "page": page_label,
            "errors": errors,
            "warnings": warnings,
            "total_errors": len(errors),
            "total_warnings": len(warnings),
        }
    except requests.RequestException as e:
        pytest.skip(f"Validador W3C no disponible: {e}")


def _login_and_get_cookies() -> list:
    """Hace login en el frontend y retorna las cookies de sesión."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        page.fill('input[type="email"]', INVESTIGADOR_EMAIL)
        page.fill('input[type="password"]', INVESTIGADOR_PASSWORD)
        page.click('button[type="submit"]')
        page.wait_for_url(f"{FRONTEND_URL}/dashboard**", timeout=10000)
        cookies = page.context.cookies()
        browser.close()
    return cookies


@pytest.mark.w3c
class TestW3CValidacion:
    """Validación W3C de páginas públicas del frontend Next.js."""

    @pytest.mark.parametrize("path,label", PAGINAS_PUBLICAS)
    def test_pagina_publica_sin_errores_w3c(self, path, label):
        """Las páginas públicas no deben tener errores de validación W3C."""
        url = f"{FRONTEND_URL}{path}"
        html = _get_html_with_playwright(url)
        result = _validate_with_w3c(html, label)

        errores_criticos = [
            e for e in result["errors"]
            if "doctype" not in e.get("message", "").lower()
        ]
        assert len(errores_criticos) == 0, (
            f"{label} tiene {len(errores_criticos)} error(es) W3C:\n"
            + "\n".join(f"  Línea {e.get('lastLine','?')}: {e.get('message','')}" for e in errores_criticos[:5])
        )

    @pytest.mark.parametrize("path,label", PAGINAS_PUBLICAS)
    def test_pagina_publica_advertencias_w3c(self, path, label):
        """Reporta advertencias W3C (no falla el test, solo registra)."""
        url = f"{FRONTEND_URL}{path}"
        html = _get_html_with_playwright(url)
        result = _validate_with_w3c(html, label)

        if result["total_warnings"] > 0:
            msgs = "\n".join(
                f"  Línea {w.get('lastLine','?')}: {w.get('message','')}"
                for w in result["warnings"][:5]
            )
            print(f"\nAdvertencias W3C en {label} ({result['total_warnings']} total):\n{msgs}")

    def test_html_tiene_doctype(self):
        """El HTML debe declarar DOCTYPE html5."""
        html = _get_html_with_playwright(f"{FRONTEND_URL}/login")
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html.lower(), \
            "La página no declara DOCTYPE html5"

    def test_html_tiene_lang(self):
        """El elemento <html> debe tener atributo lang."""
        html = _get_html_with_playwright(f"{FRONTEND_URL}/login")
        assert 'lang="' in html or "lang='" in html, \
            "El elemento <html> no tiene atributo lang (requerido por W3C/accesibilidad)"

    def test_html_tiene_charset(self):
        """El HTML debe declarar charset UTF-8."""
        html = _get_html_with_playwright(f"{FRONTEND_URL}/login")
        assert "utf-8" in html.lower() or "UTF-8" in html, \
            "El HTML no declara charset UTF-8"

    def test_html_tiene_viewport_meta(self):
        """El HTML debe incluir meta viewport para responsividad."""
        html = _get_html_with_playwright(f"{FRONTEND_URL}/login")
        assert 'name="viewport"' in html, \
            "Meta tag viewport ausente — requerido por W3C para dispositivos móviles"

    def test_imagenes_tienen_alt(self):
        """Todas las imágenes deben tener atributo alt."""
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
            imagenes_sin_alt = page.eval_on_selector_all(
                "img:not([alt])",
                "els => els.map(el => el.src)"
            )
            browser.close()

        assert len(imagenes_sin_alt) == 0, (
            f"Imágenes sin atributo alt: {imagenes_sin_alt}"
        )
