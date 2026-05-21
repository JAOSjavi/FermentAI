"""
Pruebas Funcionales — Revisión de Aportes (rol investigador)
Cubre: GET /api/revisar, POST /api/revisar/{id}/aprobar, POST /api/revisar/{id}/rechazar

Ejecución:
    pytest tests/09_funcionales/test_revisar.py -v -m funcional
"""
import io
import zipfile
import pytest
import httpx

API_URL = "http://localhost:8000"
INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"
COLABORADOR_EMAIL = "test.revisar.colaborador@example.com"
COLABORADOR_PASSWORD = "test_revisar_pass_123"

VALID_CSV_HEADER = (
    "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
    "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "estado_fermentacion,intervalo_incertidumbre_min,validado_asesor,observaciones\n"
)


def _make_zip(ferm_code: str) -> bytes:
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
        "nombre": "Colaborador Revisar",
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    r = client.post("/api/auth/login", json={
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.fixture(scope="module")
def aporte_pendiente_id(client, colaborador_headers):
    """Crea un aporte pendiente y retorna su ID."""
    zip_bytes = _make_zip("FERM89")
    r = client.post(
        "/api/aportes/subir",
        files={"file": ("FERM89.zip", zip_bytes, "application/zip")},
        headers=colaborador_headers,
    )
    if r.status_code == 429:
        pytest.skip("Rate limit alcanzado — esperar antes de re-ejecutar")
    if r.status_code != 201:
        pytest.skip(f"No se pudo crear aporte de prueba: {r.status_code} {r.text[:200]}")
    return r.json()["id"]


@pytest.mark.funcional
class TestListadoRevisiones:
    """Pruebas del listado de aportes pendientes."""

    def test_investigador_puede_ver_pendientes(self, client, investigador_headers):
        r = client.get("/api/revisar", headers=investigador_headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)

    def test_colaborador_no_puede_ver_pendientes(self, client, colaborador_headers):
        """Un colaborador no debe poder ver la cola de revisión."""
        r = client.get("/api/revisar", headers=colaborador_headers)
        assert r.status_code == 403

    def test_sin_token_retorna_401(self, client):
        r = client.get("/api/revisar")
        assert r.status_code == 401


@pytest.mark.funcional
class TestAprobarAporte:
    """Pruebas del endpoint de aprobación."""

    def test_investigador_puede_aprobar(self, client, investigador_headers, aporte_pendiente_id):
        r = client.post(
            f"/api/revisar/{aporte_pendiente_id}/aprobar",
            headers=investigador_headers,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["estado"] == "aprobado"
        assert body["id"] == aporte_pendiente_id

    def test_colaborador_no_puede_aprobar(self, client, colaborador_headers, aporte_pendiente_id):
        r = client.post(
            f"/api/revisar/{aporte_pendiente_id}/aprobar",
            headers=colaborador_headers,
        )
        assert r.status_code == 403

    def test_aprobar_aporte_inexistente_retorna_404(self, client, investigador_headers):
        r = client.post("/api/revisar/999999/aprobar", headers=investigador_headers)
        assert r.status_code == 404

    def test_aprobar_sin_token_retorna_401(self, client):
        r = client.post("/api/revisar/1/aprobar")
        assert r.status_code == 401


@pytest.mark.funcional
class TestRechazarAporte:
    """Pruebas del endpoint de rechazo."""

    @pytest.fixture(scope="class")
    def aporte_para_rechazar(self, client, colaborador_headers):
        zip_bytes = _make_zip("FERM88")
        r = client.post(
            "/api/aportes/subir",
            files={"file": ("FERM88.zip", zip_bytes, "application/zip")},
            headers=colaborador_headers,
        )
        if r.status_code in (429, 400, 500):
            pytest.skip(f"No se pudo crear aporte para rechazar: {r.status_code}")
        return r.json()["id"]

    def test_investigador_puede_rechazar_con_observaciones(
        self, client, investigador_headers, aporte_para_rechazar
    ):
        r = client.post(
            f"/api/revisar/{aporte_para_rechazar}/rechazar",
            json={"observaciones": "Imágenes de baja calidad, re-subir con mejor resolución."},
            headers=investigador_headers,
        )
        assert r.status_code == 200
        body = r.json()
        assert body["estado"] == "rechazado"

    def test_rechazar_sin_observaciones_retorna_error(
        self, client, investigador_headers, aporte_para_rechazar
    ):
        """El rechazo requiere observaciones — sin ellas debe fallar."""
        r = client.post(
            f"/api/revisar/{aporte_para_rechazar}/rechazar",
            json={},
            headers=investigador_headers,
        )
        assert r.status_code in (400, 422)

    def test_colaborador_no_puede_rechazar(
        self, client, colaborador_headers, aporte_para_rechazar
    ):
        r = client.post(
            f"/api/revisar/{aporte_para_rechazar}/rechazar",
            json={"observaciones": "test"},
            headers=colaborador_headers,
        )
        assert r.status_code == 403
