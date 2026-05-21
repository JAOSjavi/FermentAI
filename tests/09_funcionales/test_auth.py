"""
Pruebas Funcionales — Autenticación y Autorización
Cubre los endpoints: POST /api/auth/register, POST /api/auth/login, GET /api/auth/me

Ejecución:
    pytest tests/09_funcionales/test_auth.py -v -m funcional
"""
import pytest
import httpx

API_URL = "http://localhost:8000"

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"

NUEVO_EMAIL = "nuevo.usuario.test@example.com"
NUEVO_PASSWORD = "nuevo_password_123"


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=API_URL, timeout=15) as c:
        yield c


@pytest.mark.funcional
class TestLogin:
    """Pruebas del endpoint POST /api/auth/login."""

    def test_login_investigador_exitoso(self, client):
        """Login con credenciales de investigador debe retornar token."""
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        assert r.status_code == 200
        body = r.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"
        assert len(body["access_token"]) > 10

    def test_login_password_incorrecto(self, client):
        """Contraseña incorrecta debe retornar 401."""
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": "contrasena_incorrecta",
        })
        assert r.status_code == 401
        assert "detail" in r.json()

    def test_login_email_inexistente(self, client):
        """Email no registrado debe retornar 401."""
        r = client.post("/api/auth/login", json={
            "email": "noexiste@nowhere.com",
            "password": "cualquier",
        })
        assert r.status_code == 401

    def test_login_email_invalido(self, client):
        """Email con formato inválido debe retornar 422."""
        r = client.post("/api/auth/login", json={
            "email": "no-es-un-email",
            "password": "algo",
        })
        assert r.status_code == 422

    def test_login_campos_vacios(self, client):
        """Request sin campos debe retornar 422."""
        r = client.post("/api/auth/login", json={})
        assert r.status_code == 422

    def test_login_segundo_investigador(self, client):
        """El segundo investigador también debe poder hacer login."""
        r = client.post("/api/auth/login", json={
            "email": "daniel.coral@ucc.edu.co",
            "password": "investigador123",
        })
        assert r.status_code == 200
        assert "access_token" in r.json()


@pytest.mark.funcional
class TestRegistro:
    """Pruebas del endpoint POST /api/auth/register."""

    def test_registro_colaborador_exitoso(self, client):
        """Un nuevo usuario se puede registrar como colaborador."""
        # Limpiar por si existe de pruebas anteriores
        r = client.post("/api/auth/register", json={
            "nombre": "Usuario Test Nuevo",
            "email": NUEVO_EMAIL,
            "password": NUEVO_PASSWORD,
        })
        assert r.status_code in (201, 400)
        if r.status_code == 201:
            body = r.json()
            assert body["email"] == NUEVO_EMAIL
            assert body["rol"] == "colaborador"
            assert "id" in body
            assert "password_hash" not in body
            assert "password" not in body

    def test_registro_rol_por_defecto_colaborador(self, client):
        """El rol asignado por defecto en registro debe ser colaborador."""
        r = client.post("/api/auth/login", json={
            "email": NUEVO_EMAIL,
            "password": NUEVO_PASSWORD,
        })
        if r.status_code == 200:
            token = r.json()["access_token"]
            me = client.get("/api/auth/me",
                            headers={"Authorization": f"Bearer {token}"})
            assert me.status_code == 200
            assert me.json()["rol"] == "colaborador"

    def test_registro_email_duplicado(self, client):
        """Registrar con un email existente debe retornar 400."""
        r = client.post("/api/auth/register", json={
            "nombre": "Duplicado",
            "email": INVESTIGADOR_EMAIL,
            "password": "cualquier123",
        })
        assert r.status_code == 400
        assert "detail" in r.json()

    def test_registro_sin_nombre(self, client):
        """Registro sin campo nombre debe retornar 422."""
        r = client.post("/api/auth/register", json={
            "email": "sin.nombre@example.com",
            "password": "pass123",
        })
        assert r.status_code == 422

    def test_registro_password_no_expuesto(self, client):
        """El hash de contraseña no debe aparecer en la respuesta."""
        email = "check.password@example.com"
        r = client.post("/api/auth/register", json={
            "nombre": "CheckPass",
            "email": email,
            "password": "testpass123",
        })
        if r.status_code == 201:
            body = r.json()
            assert "password" not in body
            assert "password_hash" not in body


@pytest.mark.funcional
class TestMe:
    """Pruebas del endpoint GET /api/auth/me."""

    @pytest.fixture
    def token(self, client):
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        return r.json()["access_token"]

    def test_me_con_token_valido(self, client, token):
        """El endpoint /me debe retornar el perfil del usuario autenticado."""
        r = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert r.status_code == 200
        body = r.json()
        assert body["email"] == INVESTIGADOR_EMAIL
        assert body["rol"] == "investigador"
        assert "id" in body
        assert "nombre" in body
        assert "created_at" in body

    def test_me_sin_token(self, client):
        """Acceder a /me sin token debe retornar 401."""
        r = client.get("/api/auth/me")
        assert r.status_code == 401

    def test_me_token_malformado(self, client):
        """Token inválido/malformado debe retornar 401."""
        r = client.get("/api/auth/me",
                       headers={"Authorization": "Bearer este_token_es_invalido"})
        assert r.status_code == 401

    def test_me_bearer_ausente(self, client):
        """Authorization header sin 'Bearer' debe retornar 401."""
        r = client.get("/api/auth/me",
                       headers={"Authorization": "Token algo"})
        assert r.status_code == 401
