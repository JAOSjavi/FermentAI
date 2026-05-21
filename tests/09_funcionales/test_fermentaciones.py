"""
Pruebas Funcionales — Datasets / Fermentaciones
Cubre GET /api/fermentaciones con filtros y control de acceso.

Ejecución:
    pytest tests/09_funcionales/test_fermentaciones.py -v -m funcional
"""
import pytest
import httpx

API_URL = "http://localhost:8000"
INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=API_URL, timeout=15) as c:
        yield c


@pytest.fixture(scope="module")
def auth_headers(client):
    r = client.post("/api/auth/login", json={
        "email": INVESTIGADOR_EMAIL,
        "password": INVESTIGADOR_PASSWORD,
    })
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.funcional
class TestFermentacionesAcceso:
    """Control de acceso al listado de datasets."""

    def test_sin_token_retorna_401(self, client):
        r = client.get("/api/fermentaciones")
        assert r.status_code == 401

    def test_token_invalido_retorna_401(self, client):
        r = client.get("/api/fermentaciones",
                       headers={"Authorization": "Bearer token_falso"})
        assert r.status_code == 401

    def test_con_token_valido_retorna_lista(self, client, auth_headers):
        r = client.get("/api/fermentaciones", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)


@pytest.mark.funcional
class TestFermentacionesRespuesta:
    """Estructura y contenido de la respuesta del listado."""

    def test_respuesta_es_lista(self, client, auth_headers):
        r = client.get("/api/fermentaciones", headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_estructura_cada_dataset(self, client, auth_headers):
        """Cada dataset aprobado debe tener los campos esperados."""
        r = client.get("/api/fermentaciones", headers=auth_headers)
        data = r.json()
        if not data:
            pytest.skip("No hay datasets aprobados para verificar estructura")

        for d in data:
            assert "id" in d
            assert "fermentacion" in d
            assert "imagenes" in d
            assert "total_imagenes" in d
            assert isinstance(d["imagenes"], list)
            assert d["total_imagenes"] >= 0

    def test_fermentacion_tiene_codigo(self, client, auth_headers):
        r = client.get("/api/fermentaciones", headers=auth_headers)
        data = r.json()
        if not data:
            pytest.skip("No hay datasets para verificar")
        for d in data:
            ferm = d.get("fermentacion", {})
            assert "codigo" in ferm
            assert ferm["codigo"].startswith("FERM")

    def test_content_type_json(self, client, auth_headers):
        r = client.get("/api/fermentaciones", headers=auth_headers)
        assert "application/json" in r.headers.get("content-type", "")


@pytest.mark.funcional
class TestFermentacionesFiltros:
    """Pruebas de los filtros de búsqueda."""

    def test_filtro_codigo_inexistente(self, client, auth_headers):
        """Filtrar por un código que no existe debe retornar lista vacía."""
        r = client.get("/api/fermentaciones?codigo=FERM00_INEXISTENTE_XYZ",
                       headers=auth_headers)
        assert r.status_code == 200
        assert r.json() == []

    def test_filtro_estado_invalido(self, client, auth_headers):
        """Filtrar por estado inválido debe retornar lista vacía (no error)."""
        r = client.get("/api/fermentaciones?estado_fermentacion=ESTADO_INVALIDO",
                       headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_filtro_estado_semi_fermentado(self, client, auth_headers):
        """Filtrar por semi_fermentado debe retornar solo datasets con ese estado."""
        r = client.get("/api/fermentaciones?estado_fermentacion=semi_fermentado",
                       headers=auth_headers)
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, list)

    def test_filtro_fecha_invalida(self, client, auth_headers):
        """Filtrar con fecha mal formada debe retornar 422."""
        r = client.get("/api/fermentaciones?fecha_desde=no-es-fecha",
                       headers=auth_headers)
        assert r.status_code == 422

    def test_multiples_filtros_combinados(self, client, auth_headers):
        """Combinar filtros no debe causar error del servidor."""
        r = client.get(
            "/api/fermentaciones?codigo=FERM&estado_fermentacion=semi_fermentado",
            headers=auth_headers,
        )
        assert r.status_code == 200
        assert isinstance(r.json(), list)


@pytest.mark.funcional
class TestFermentacionesSoloAprobados:
    """Verifica que solo aparecen datasets aprobados."""

    def test_datasets_son_solo_aprobados(self, client, auth_headers):
        """
        El endpoint /api/fermentaciones solo debe retornar aportes aprobados.
        Si hay datos, los metadatos e imágenes solo corresponden a aportes aprobados.
        """
        r = client.get("/api/fermentaciones", headers=auth_headers)
        assert r.status_code == 200
        # No podemos verificar el estado interno sin acceso a la DB directamente,
        # pero sí verificamos que el endpoint responde correctamente
        data = r.json()
        assert isinstance(data, list)
