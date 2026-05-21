"""
Pruebas Funcionales — Notificaciones
Cubre GET /api/notificaciones y PATCH /api/notificaciones/{id}/leer

Ejecución:
    pytest tests/09_funcionales/test_notificaciones.py -v -m funcional
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
class TestNotificacionesListado:
    """Pruebas del listado de notificaciones."""

    def test_notificaciones_sin_token_retorna_401(self, client):
        r = client.get("/api/notificaciones")
        assert r.status_code == 401

    def test_notificaciones_con_token_retorna_lista(self, client, auth_headers):
        r = client.get("/api/notificaciones", headers=auth_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_estructura_notificacion(self, client, auth_headers):
        """Si hay notificaciones, cada una debe tener los campos esperados."""
        r = client.get("/api/notificaciones", headers=auth_headers)
        data = r.json()
        if not data:
            pytest.skip("No hay notificaciones para verificar estructura")
        for n in data:
            assert "id" in n
            assert "tipo" in n
            assert "mensaje" in n
            assert "leida" in n
            assert "created_at" in n
            assert isinstance(n["leida"], bool)

    def test_content_type_json(self, client, auth_headers):
        r = client.get("/api/notificaciones", headers=auth_headers)
        assert "application/json" in r.headers.get("content-type", "")


@pytest.mark.funcional
class TestNotificacionesMarcarLeida:
    """Pruebas de marcar notificaciones como leídas."""

    def test_marcar_notificacion_inexistente_retorna_404(self, client, auth_headers):
        r = client.patch("/api/notificaciones/999999/leer", headers=auth_headers)
        assert r.status_code == 404

    def test_marcar_leida_sin_token_retorna_401(self, client):
        r = client.patch("/api/notificaciones/1/leer")
        assert r.status_code == 401

    def test_marcar_notificacion_propia_como_leida(self, client, auth_headers):
        """Si hay una notificación no leída, marcarla como leída debe funcionar."""
        notifs = client.get("/api/notificaciones", headers=auth_headers).json()
        no_leidas = [n for n in notifs if not n.get("leida", True)]
        if not no_leidas:
            pytest.skip("No hay notificaciones no leídas para probar")

        notif_id = no_leidas[0]["id"]
        r = client.patch(f"/api/notificaciones/{notif_id}/leer", headers=auth_headers)
        assert r.status_code == 200

        # Verificar que está marcada como leída
        notifs_after = client.get("/api/notificaciones", headers=auth_headers).json()
        notif_after = next((n for n in notifs_after if n["id"] == notif_id), None)
        if notif_after:
            assert notif_after["leida"] is True
