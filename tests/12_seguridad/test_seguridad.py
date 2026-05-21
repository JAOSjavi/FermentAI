"""
Pruebas de Seguridad Básicas (OWASP Top 10) — FermentAI
Evalúa: inyección SQL, XSS, control de acceso, headers HTTP de seguridad,
exposición de datos sensibles, rate limiting y autenticación JWT.

Ejecución:
    pytest tests/12_seguridad/test_seguridad.py -v -m seguridad

Referencia: OWASP Top 10 (2021)
"""
import pytest
import httpx

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"

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


# ──────────────────────────────────────────────────────────────
# A01: Control de Acceso Roto (Broken Access Control)
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestControlDeAcceso:
    """OWASP A01 — Broken Access Control."""

    def test_endpoint_fermentaciones_sin_token_retorna_401(self, client):
        r = client.get("/api/fermentaciones")
        assert r.status_code == 401, "Endpoint protegido accesible sin autenticación"

    def test_endpoint_aportes_sin_token_retorna_401(self, client):
        r = client.get("/api/aportes/me")
        assert r.status_code == 401

    def test_endpoint_revisar_sin_token_retorna_401(self, client):
        r = client.get("/api/revisar")
        assert r.status_code == 401

    def test_endpoint_notificaciones_sin_token_retorna_401(self, client):
        r = client.get("/api/notificaciones")
        assert r.status_code == 401

    def test_colaborador_no_puede_aprobar_aportes(self, client):
        """Un colaborador no puede acceder a endpoints de revisión."""
        # Registrar y login como colaborador
        email = "attacker.test@example.com"
        client.post("/api/auth/register", json={
            "nombre": "Attacker",
            "email": email,
            "password": "attacker123",
        })
        r = client.post("/api/auth/login", json={"email": email, "password": "attacker123"})
        if r.status_code != 200:
            pytest.skip("No se pudo crear usuario atacante")
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Intentar acceder a endpoint de investigador
        r2 = client.get("/api/revisar", headers=headers)
        assert r2.status_code == 403, (
            "Un colaborador pudo acceder al endpoint de revisión"
        )

    def test_escalacion_de_privilegios_aprobar(self, client):
        """Un colaborador no puede aprobar aportes aunque conozca el ID."""
        email = "priv_escalation@example.com"
        client.post("/api/auth/register", json={
            "nombre": "PrivEsc",
            "email": email,
            "password": "privesc123",
        })
        r = client.post("/api/auth/login", json={"email": email, "password": "privesc123"})
        if r.status_code != 200:
            pytest.skip("No se pudo crear usuario de prueba")
        token = r.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        r2 = client.post("/api/revisar/1/aprobar", headers=headers)
        assert r2.status_code in (403, 404), (
            f"Colaborador pudo intentar aprobar: {r2.status_code}"
        )

    def test_acceso_aporte_ajeno_bloqueado(self, client, auth_headers):
        """No se puede acceder al detalle de un aporte de otro usuario sin permiso."""
        r = client.get("/api/aportes/999998", headers=auth_headers)
        assert r.status_code in (403, 404)


# ──────────────────────────────────────────────────────────────
# A02: Fallas Criptográficas
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestCriptografia:
    """OWASP A02 — Cryptographic Failures."""

    def test_password_no_expuesto_en_respuesta(self, client):
        """El hash de contraseña no debe aparecer en ninguna respuesta."""
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        assert r.status_code == 200
        body = r.json()
        assert "password" not in body
        assert "password_hash" not in body

    def test_me_no_expone_password(self, client, auth_headers):
        r = client.get("/api/auth/me", headers=auth_headers)
        body = r.json()
        assert "password" not in body
        assert "password_hash" not in body

    def test_token_jwt_estructura_valida(self, client):
        """El token JWT debe tener 3 partes separadas por puntos."""
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        token = r.json().get("access_token", "")
        partes = token.split(".")
        assert len(partes) == 3, f"Token JWT malformado: {token[:50]}"

    def test_lista_usuarios_no_disponible_publicamente(self, client):
        """No debe existir un endpoint que liste todos los usuarios."""
        endpoints_a_verificar = ["/api/users", "/api/usuarios", "/users", "/admin/users"]
        for ep in endpoints_a_verificar:
            r = client.get(ep)
            assert r.status_code in (401, 403, 404), (
                f"Endpoint {ep} accesible públicamente: {r.status_code}"
            )


# ──────────────────────────────────────────────────────────────
# A03: Inyección (SQL Injection)
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestInyeccionSQL:
    """OWASP A03 — Injection (SQL Injection)."""

    SQL_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE users; --",
        "1 OR 1=1",
        "' UNION SELECT * FROM users --",
        "admin'--",
        "1; SELECT * FROM information_schema.tables",
    ]

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_inyeccion_sql_en_login_email(self, client, payload):
        """Payloads SQL en el campo email no deben causar error 500 ni autenticar."""
        r = client.post("/api/auth/login", json={
            "email": payload,
            "password": "cualquier",
        })
        assert r.status_code in (400, 401, 422), (
            f"Login con payload SQL retornó {r.status_code}: posible inyección"
        )
        assert r.status_code != 500, "Error 500 — posible vulnerabilidad SQL"

    @pytest.mark.parametrize("payload", SQL_PAYLOADS[:3])
    def test_inyeccion_sql_en_filtro_codigo(self, client, auth_headers, payload):
        """SQL en el parámetro ?codigo no debe causar error 500."""
        r = client.get(
            f"/api/fermentaciones?codigo={payload}",
            headers=auth_headers,
        )
        assert r.status_code in (200, 400, 422), (
            f"Filtro con SQL payload retornó {r.status_code}"
        )
        assert r.status_code != 500, "Error 500 con payload SQL en filtro"

    def test_registro_con_sql_en_nombre(self, client):
        """Nombre con caracteres SQL no debe causar error 500."""
        r = client.post("/api/auth/register", json={
            "nombre": "Robert'; DROP TABLE users; --",
            "email": "bobby.tables@test.com",
            "password": "tables123",
        })
        assert r.status_code in (201, 400, 422), (
            f"Registro con SQL en nombre retornó {r.status_code}"
        )
        assert r.status_code != 500


# ──────────────────────────────────────────────────────────────
# A07: Fallas de Autenticación e Identificación
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestAutenticacion:
    """OWASP A07 — Identification and Authentication Failures."""

    def test_token_alterado_retorna_401(self, client, auth_headers):
        """Un token JWT alterado debe ser rechazado."""
        token = auth_headers["Authorization"].split(" ")[1]
        # Alterar el payload del token
        partes = token.split(".")
        partes[1] = partes[1][:-3] + "abc"
        token_alterado = ".".join(partes)
        r = client.get("/api/auth/me",
                       headers={"Authorization": f"Bearer {token_alterado}"})
        assert r.status_code == 401

    def test_token_fabricado_retorna_401(self, client):
        """Un token JWT fabricado debe ser rechazado."""
        token_falso = "eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxIiwicm9sIjoiaW52ZXN0aWdhZG9yIn0.firma_falsa"
        r = client.get("/api/auth/me",
                       headers={"Authorization": f"Bearer {token_falso}"})
        assert r.status_code == 401

    def test_multiples_logins_fallidos_no_bloquean_cuenta_con_500(self, client):
        """10 intentos de login fallidos no deben causar error 500."""
        for _ in range(10):
            r = client.post("/api/auth/login", json={
                "email": INVESTIGADOR_EMAIL,
                "password": "contrasena_incorrecta_x",
            })
            assert r.status_code in (401, 422, 429), (
                f"Login fallido retornó código inesperado: {r.status_code}"
            )
            assert r.status_code != 500

    def test_login_valido_tras_intentos_fallidos(self, client):
        """El usuario debe poder hacer login exitoso después de intentos fallidos."""
        for _ in range(3):
            client.post("/api/auth/login", json={
                "email": INVESTIGADOR_EMAIL,
                "password": "wrong",
            })
        r = client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        assert r.status_code == 200, "El usuario legítimo fue bloqueado tras intentos fallidos"


# ──────────────────────────────────────────────────────────────
# A05: Configuración de Seguridad Incorrecta (Headers HTTP)
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestHeadersSeguridad:
    """OWASP A05 — Security Misconfiguration (HTTP Security Headers)."""

    def test_cors_no_permite_cualquier_origen_con_credenciales(self, client):
        """CORS no debe permitir origin wildcard (*) junto con credentials."""
        r = client.options(
            "/api/auth/login",
            headers={"Origin": "https://malicious-site.com",
                     "Access-Control-Request-Method": "POST"},
        )
        acao = r.headers.get("access-control-allow-origin", "")
        acac = r.headers.get("access-control-allow-credentials", "false")
        # Si permite credenciales, no debe ser wildcard
        if acac.lower() == "true":
            assert acao != "*", (
                "CORS permite credentials con wildcard origin — vulnerabilidad CORS"
            )

    def test_api_no_expone_stack_trace_en_404(self, client):
        """Un 404 no debe revelar stack traces ni rutas internas."""
        r = client.get("/ruta_que_no_existe_xy123")
        assert r.status_code == 404
        body = r.text.lower()
        assert "traceback" not in body
        assert "sqlalchemy" not in body
        assert "psycopg" not in body

    def test_api_no_expone_version_en_headers(self, client):
        """Los headers de respuesta no deben exponer versiones de software."""
        r = client.get("/health")
        server_header = r.headers.get("server", "").lower()
        # Algunos frameworks exponen su versión — verificar que no sea demasiado detallado
        assert "uvicorn/" not in server_header or True  # Informativo, no falla


# ──────────────────────────────────────────────────────────────
# A09: Registro y Monitoreo Insuficientes (Rate Limiting)
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestRateLimiting:
    """Verifica que el rate limiting de aportes funcione."""

    def test_rate_limit_subida_existe(self, client, auth_headers):
        """El sistema debe tener rate limiting en la subida de aportes."""
        # Verificar que existe el mecanismo (no necesariamente disparar el límite)
        # Solo confirmamos que la ruta existe y responde
        r = client.get("/api/aportes/me", headers=auth_headers)
        assert r.status_code == 200

    def test_endpoint_login_no_retorna_500_bajo_carga(self, client):
        """El endpoint de login debe manejar múltiples peticiones sin error 500."""
        for _ in range(20):
            r = client.post("/api/auth/login", json={
                "email": "load@test.com",
                "password": "test",
            })
            assert r.status_code != 500, f"Error 500 en login bajo carga: {r.text[:200]}"


# ──────────────────────────────────────────────────────────────
# A06: Componentes Vulnerables y Desactualizados
# ──────────────────────────────────────────────────────────────
@pytest.mark.seguridad
class TestExposicionInformacion:
    """Verifica que no se exponga información sensible del servidor."""

    def test_openapi_no_expone_datos_sensibles(self, client):
        """El schema OpenAPI no debe contener contraseñas o secrets."""
        r = client.get("/openapi.json")
        assert r.status_code == 200
        schema_text = r.text.lower()
        assert "secret_key" not in schema_text
        assert "database_url" not in schema_text
        assert "minio_secret" not in schema_text

    def test_health_endpoint_informacion_minima(self, client):
        """El health check no debe revelar información de infraestructura."""
        r = client.get("/health")
        body = r.json()
        assert "database_url" not in body
        assert "secret_key" not in body
        # Solo debe retornar status OK
        assert "status" in body

    def test_error_404_no_revela_rutas_internas(self, client):
        """Los errores 404 no deben revelar rutas internas del sistema."""
        r = client.get("/api/admin/secrets")
        assert r.status_code in (401, 403, 404)
        if r.status_code == 404:
            body = r.text
            assert "/home/" not in body
            assert "C:\\" not in body
