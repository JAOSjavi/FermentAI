"""Fixtures compartidos para toda la suite de pruebas de FermentAI."""
import io
import os
import zipfile
import tempfile
import pytest
import httpx

BASE_URL = os.getenv("FERMENTAI_API_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("FERMENTAI_FRONTEND_URL", "http://localhost:3000")

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"
COLABORADOR_EMAIL = "test.colaborador@example.com"
COLABORADOR_PASSWORD = "colaborador123"

VALID_CSV_HEADER = (
    "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
    "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "intervalo_incertidumbre_min,validado_asesor,observaciones\n"
)
VALID_CSV_ROW = (
    "FERM99_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,"
    "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5,true,prueba\n"
)


@pytest.fixture(scope="session")
def base_url():
    return BASE_URL


@pytest.fixture(scope="session")
def frontend_url():
    return FRONTEND_URL


@pytest.fixture(scope="session")
def api_client():
    with httpx.Client(base_url=BASE_URL, timeout=30.0) as client:
        yield client


@pytest.fixture(scope="session")
def investigador_token(api_client):
    r = api_client.post("/api/auth/login", json={
        "email": INVESTIGADOR_EMAIL,
        "password": INVESTIGADOR_PASSWORD,
    })
    assert r.status_code == 200, f"Login investigador falló: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def investigador_headers(investigador_token):
    return {"Authorization": f"Bearer {investigador_token}"}


@pytest.fixture(scope="session")
def colaborador_token(api_client):
    """Registra (si no existe) y hace login de un colaborador de prueba."""
    api_client.post("/api/auth/register", json={
        "nombre": "Test Colaborador",
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    r = api_client.post("/api/auth/login", json={
        "email": COLABORADOR_EMAIL,
        "password": COLABORADOR_PASSWORD,
    })
    assert r.status_code == 200, f"Login colaborador falló: {r.text}"
    return r.json()["access_token"]


@pytest.fixture(scope="session")
def colaborador_headers(colaborador_token):
    return {"Authorization": f"Bearer {colaborador_token}"}


@pytest.fixture
def zip_valido_bytes():
    """Genera un ZIP válido FERM99 en memoria."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        img_data = b"\xff\xd8\xff" + b"\x00" * 200
        zf.writestr("FERM99/imagenes/FERM99_20240101_120000.jpg", img_data)
        zf.writestr("FERM99/FERM99_metadata.csv", VALID_CSV_HEADER + VALID_CSV_ROW)
    buf.seek(0)
    return buf.read()
