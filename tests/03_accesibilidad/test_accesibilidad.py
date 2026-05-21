"""
Pruebas de Accesibilidad WCAG 2.1 — FermentAI
Usa Playwright + axe-core para detectar violaciones de accesibilidad.

Ejecución:
    pytest tests/03_accesibilidad/test_accesibilidad.py -v -m accesibilidad

Requisito: playwright install chromium
"""
import pytest
from playwright.sync_api import sync_playwright, Page

FRONTEND_URL = "http://localhost:3000"
INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"

AXE_CORE_CDN = "https://cdnjs.cloudflare.com/ajax/libs/axe-core/4.10.0/axe.min.js"

IMPACT_CRITICO = {"critical", "serious"}


def _inject_axe(page: Page):
    """Inyecta axe-core en la página actual."""
    page.add_script_tag(url=AXE_CORE_CDN)
    page.wait_for_function("typeof axe !== 'undefined'", timeout=10000)


def _run_axe(page: Page, context_selector: str = None) -> dict:
    """Ejecuta axe-core y retorna el resultado."""
    if context_selector:
        return page.evaluate(f"axe.run('{context_selector}')")
    return page.evaluate("axe.run()")


def _format_violations(violations: list) -> str:
    lines = []
    for v in violations:
        lines.append(f"\n  [{v.get('impact', '?').upper()}] {v.get('id')} — {v.get('description')}")
        for node in v.get("nodes", [])[:2]:
            lines.append(f"    → {node.get('html', '')[:120]}")
    return "\n".join(lines)


@pytest.fixture(scope="module")
def browser_context():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        yield context
        browser.close()


@pytest.fixture(scope="module")
def auth_cookies(browser_context):
    """Devuelve cookies de sesión de investigador."""
    page = browser_context.new_page()
    page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
    page.fill('input[type="email"]', INVESTIGADOR_EMAIL)
    page.fill('input[type="password"]', INVESTIGADOR_PASSWORD)
    page.click('button[type="submit"]')
    try:
        page.wait_for_url(f"{FRONTEND_URL}/dashboard**", timeout=10000)
    except Exception:
        pass
    cookies = browser_context.cookies()
    page.close()
    return cookies


@pytest.mark.accesibilidad
class TestAccesibilidadPaginasPublicas:
    """Pruebas WCAG en páginas accesibles sin login."""

    def test_login_sin_violaciones_criticas(self, browser_context):
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        _inject_axe(page)
        result = _run_axe(page)
        criticas = [v for v in result.get("violations", []) if v.get("impact") in IMPACT_CRITICO]
        page.close()
        assert len(criticas) == 0, (
            f"Violaciones críticas/serias en /login:{_format_violations(criticas)}"
        )

    def test_registro_sin_violaciones_criticas(self, browser_context):
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/registro", wait_until="networkidle")
        _inject_axe(page)
        result = _run_axe(page)
        criticas = [v for v in result.get("violations", []) if v.get("impact") in IMPACT_CRITICO]
        page.close()
        assert len(criticas) == 0, (
            f"Violaciones críticas/serias en /registro:{_format_violations(criticas)}"
        )

    def test_login_tiene_labels_en_inputs(self, browser_context):
        """Todos los inputs del formulario deben tener label asociado."""
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        inputs_sin_label = page.eval_on_selector_all(
            "input:not([aria-label]):not([aria-labelledby])",
            "els => els.filter(el => !document.querySelector(`label[for='${el.id}']`)).map(el => el.outerHTML)"
        )
        page.close()
        assert len(inputs_sin_label) == 0, (
            f"Inputs sin label: {inputs_sin_label}"
        )

    def test_contraste_de_color(self, browser_context):
        """No debe haber violaciones de contraste (WCAG AA)."""
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        _inject_axe(page)
        result = _run_axe(page)
        contraste = [v for v in result.get("violations", []) if "color-contrast" in v.get("id", "")]
        page.close()
        assert len(contraste) == 0, (
            f"Problemas de contraste de color:{_format_violations(contraste)}"
        )

    def test_navegacion_por_teclado_login(self, browser_context):
        """El formulario de login debe ser navegable por teclado (Tab)."""
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        page.keyboard.press("Tab")
        focused1 = page.evaluate("document.activeElement.tagName")
        page.keyboard.press("Tab")
        focused2 = page.evaluate("document.activeElement.tagName")
        page.close()
        assert focused1 in ("INPUT", "BUTTON", "A"), f"Primer foco inesperado: {focused1}"
        assert focused2 in ("INPUT", "BUTTON", "A"), f"Segundo foco inesperado: {focused2}"

    def test_titulo_de_pagina_presente(self, browser_context):
        """Cada página debe tener un <title> descriptivo."""
        for path in ["/login", "/registro"]:
            page = browser_context.new_page()
            page.goto(f"{FRONTEND_URL}{path}", wait_until="networkidle")
            title = page.title()
            page.close()
            assert title and len(title) > 3, f"Título ausente o muy corto en {path}: '{title}'"

    def test_botones_tienen_texto_accesible(self, browser_context):
        """Todos los botones deben tener texto o aria-label."""
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/login", wait_until="networkidle")
        botones_sin_texto = page.eval_on_selector_all(
            "button",
            """els => els.filter(el =>
                !el.textContent.trim() &&
                !el.getAttribute('aria-label') &&
                !el.getAttribute('aria-labelledby') &&
                !el.querySelector('title')
            ).map(el => el.outerHTML)"""
        )
        page.close()
        assert len(botones_sin_texto) == 0, (
            f"Botones sin texto accesible: {botones_sin_texto}"
        )


@pytest.mark.accesibilidad
class TestAccesibilidadDashboard:
    """Pruebas WCAG en páginas del dashboard (requieren login)."""

    def test_dashboard_sin_violaciones_criticas(self, browser_context, auth_cookies):
        browser_context.add_cookies(auth_cookies)
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/dashboard", wait_until="networkidle")
        _inject_axe(page)
        result = _run_axe(page)
        criticas = [v for v in result.get("violations", []) if v.get("impact") in IMPACT_CRITICO]
        page.close()
        assert len(criticas) == 0, (
            f"Violaciones críticas en /dashboard:{_format_violations(criticas)}"
        )

    def test_datasets_sin_violaciones_criticas(self, browser_context, auth_cookies):
        browser_context.add_cookies(auth_cookies)
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/dashboard/datasets", wait_until="networkidle")
        _inject_axe(page)
        result = _run_axe(page)
        criticas = [v for v in result.get("violations", []) if v.get("impact") in IMPACT_CRITICO]
        page.close()
        assert len(criticas) == 0, (
            f"Violaciones críticas en /dashboard/datasets:{_format_violations(criticas)}"
        )

    def test_landmarks_presentes(self, browser_context, auth_cookies):
        """La página debe tener landmarks de navegación (main, nav)."""
        browser_context.add_cookies(auth_cookies)
        page = browser_context.new_page()
        page.goto(f"{FRONTEND_URL}/dashboard", wait_until="networkidle")
        tiene_main = page.locator("main, [role='main']").count() > 0
        page.close()
        assert tiene_main, "Falta elemento <main> o role='main' en el dashboard"
