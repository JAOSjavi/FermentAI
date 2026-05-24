"""
Pruebas Funcionales — Aportes (subida y gestión de datasets ZIP)
Cubre: POST /api/aportes/subir, GET /api/aportes/me, GET /api/aportes/{id}

Ejecución:
    pytest tests/09_funcionales/test_aportes.py -v -m funcional
"""
import io
import zipfile
import pytest
import httpx

API_URL = "http://localhost:8000"
INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"
COLABORADOR_EMAIL = "test.colaborador.aportes@example.com"
COLABORADOR_PASSWORD = "colaborador_aportes_123"

VALID_CSV_HEADER = (
    "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
    "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "intervalo_incertidumbre_min,validado_asesor,observaciones\n"
)


def _make_zip(ferm_code: str = "FERM98") -> bytes:
    buf = io.BytesIO()
    csv_row = (
        f"{ferm_code}_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,"
        "0.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,semi_fermentado,5,true,\n"
    )
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{ferm_code}/imagenes/{ferm_code}_20240101_120000.jpg",
                    b"\xff\xd8\xff" + b"\x00" * 200)
        zf.writestr(f"{ferm_code}/{ferm_code}_metadata.csv", VALID_CSV_HEADER + csv_row)
    return buf.getvalue()


@pytest.fixture(scope="module")
def client():
    with httpx.Client(base_url=API_URL, timeout=30) as c:
        yield c


@pytest.fixture(scope="module")
def investigador_headers(client):
    r = client.post("/api/auth/login", json={
        "email": INVESTIGADOR_EMAIL,
        "password": INVESTIGADOR_PASSWORD,
    })
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def colaborador_headers(client):
    client.post("/api/auth/register", json={
        "nombre": "Colaborador Aportes",
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    r = client.post("/api/auth/login", json={
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.funcional
class TestSubirAporte:
    """Pruebas de la subida de ZIPs."""

    def test_subir_zip_valido_colaborador(self, client, colaborador_headers):
        """Un colaborador puede subir un ZIP válido."""
        zip_bytes = _make_zip("FERM95")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM95.zip", zip_bytes, "application/zip")},
            headers=colaborador_headers,
        )
        assert r.status_code in (201, 429), (
            f"Respuesta inesperada: {r.status_code} — {r.text[:300]}"
        )
        if r.status_code == 201:
            body = r.json()
            assert "id" in body
            assert body["estado"] == "pendiente_revision"

    def test_subir_zip_valido_investigador_aprueba_directo(self, client, investigador_headers):
        """Un investigador que sube un ZIP debe quedar aprobado directamente."""
        zip_bytes = _make_zip("FERM94")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM94.zip", zip_bytes, "application/zip")},
            headers=investigador_headers,
        )
        assert r.status_code in (201, 429)
        if r.status_code == 201:
            assert r.json()["estado"] == "aprobado"

    def test_subir_archivo_no_zip(self, client, colaborador_headers):
        """Subir un archivo que no es ZIP debe retornar 400."""
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("datos.txt", b"no soy un zip", "text/plain")},
            headers=colaborador_headers,
        )
        assert r.status_code == 400

    def test_subir_zip_estructura_invalida(self, client, colaborador_headers):
        """ZIP sin estructura FERM## debe retornar 400."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("archivo_suelto.txt", "hola")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("malo.zip", buf.getvalue(), "application/zip")},
            headers=colaborador_headers,
        )
        assert r.status_code == 400

    def test_subir_zip_sin_csv(self, client, colaborador_headers):
        """ZIP sin CSV de metadatos debe retornar 400."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("FERM93/imagenes/FERM93_20240101_120000.jpg",
                        b"\xff\xd8\xff" + b"\x00" * 100)
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM93.zip", buf.getvalue(), "application/zip")},
            headers=colaborador_headers,
        )
        assert r.status_code == 400

    def test_subir_zip_csv_columnas_faltantes(self, client, colaborador_headers):
        """ZIP con CSV incompleto debe retornar 400."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("FERM92/imagenes/FERM92_20240101_120000.jpg",
                        b"\xff\xd8\xff" + b"\x00" * 100)
            zf.writestr("FERM92/FERM92_metadata.csv",
                        "imagen,timestamp\nFERM92_20240101_120000.jpg,2024-01-01T12:00:00\n")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM92.zip", buf.getvalue(), "application/zip")},
            headers=colaborador_headers,
        )
        assert r.status_code == 400

    def test_subir_sin_token_retorna_401(self, client):
        """Subir sin autenticación debe retornar 401."""
        zip_bytes = _make_zip("FERM91")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM91.zip", zip_bytes, "application/zip")},
        )
        assert r.status_code == 401

    def test_subir_sin_archivo(self, client, colaborador_headers):
        """Request sin archivo debe retornar 422."""
        r = client.post("/api/aportes/subir", headers=colaborador_headers)
        assert r.status_code == 422


@pytest.mark.funcional
class TestMisAportes:
    """Pruebas de GET /api/aportes/me."""

    def test_mis_aportes_retorna_lista(self, client, colaborador_headers):
        r = client.get("/api/aportes/me", headers=colaborador_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_mis_aportes_sin_token_retorna_401(self, client):
        r = client.get("/api/aportes/me")
        assert r.status_code == 401

    def test_estructura_aporte_en_lista(self, client, investigador_headers):
        r = client.get("/api/aportes/me", headers=investigador_headers)
        assert r.status_code == 200
        data = r.json()
        if not data:
            pytest.skip("No hay aportes del investigador para verificar estructura")
        for a in data:
            assert "id" in a
            assert "estado" in a
            assert "fecha_subida" in a
            assert a["estado"] in ("pendiente_revision", "aprobado", "rechazado")


@pytest.mark.funcional
class TestDetalleAporte:
    """Pruebas de GET /api/aportes/{id}."""

    def test_aporte_propio_accesible(self, client, investigador_headers):
        """Un investigador puede ver el detalle de sus propios aportes."""
        lista = client.get("/api/aportes/me", headers=investigador_headers).json()
        if not lista:
            pytest.skip("No hay aportes para verificar detalle")

        aporte_id = lista[0]["id"]
        r = client.get(f"/api/aportes/{aporte_id}", headers=investigador_headers)
        assert r.status_code == 200
        body = r.json()
        assert body["id"] == aporte_id
        assert "metadatos" in body

    def test_aporte_inexistente_retorna_404(self, client, investigador_headers):
        r = client.get("/api/aportes/999999", headers=investigador_headers)
        assert r.status_code == 404

    def test_aporte_ajeno_sin_permiso_retorna_403(self, client, colaborador_headers, investigador_headers):
        """Un colaborador no puede ver aportes de otros colaboradores."""
        lista = client.get("/api/aportes/me", headers=investigador_headers).json()
        if not lista:
            pytest.skip("No hay aportes del investigador para verificar")

        aporte_id = lista[0]["id"]
        r = client.get(f"/api/aportes/{aporte_id}", headers=colaborador_headers)
        assert r.status_code in (403, 404)
