"""
Pruebas de Carga — FermentAI (Locust)
Simula usuarios concurrentes interactuando con la plataforma.

Ejecución (modo headless):
    locust -f tests/08_carga/locustfile.py \
        --headless \
        --users 50 \
        --spawn-rate 5 \
        --run-time 60s \
        --host http://localhost:8000 \
        --html tests/reports/locust_report.html

Ejecución (modo UI web):
    locust -f tests/08_carga/locustfile.py --host http://localhost:8000
    Luego abrir: http://localhost:8089

Escenarios:
    - InvestigadorUser : 20% del tráfico — lee datasets y aprueba aportes
    - ColaboradorUser  : 60% del tráfico — sube aportes y consulta sus registros
    - PublicoUser      : 20% del tráfico — navega datasets aprobados
"""
import io
import zipfile
import random
from locust import HttpUser, task, between, events
from locust.runners import MasterRunner, LocalRunner

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"
COLABORADOR_EMAIL = "test.colaborador@example.com"
COLABORADOR_PASSWORD = "colaborador123"

VALID_CSV_HEADER = (
    "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
    "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "estado_fermentacion,intervalo_incertidumbre_min,validado_asesor,observaciones\n"
)


def _build_zip_bytes(ferm_code: str) -> bytes:
    """Construye un ZIP válido en memoria para la subida."""
    buf = io.BytesIO()
    csv_row = (
        f"{ferm_code}_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,"
        "0.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,semi_fermentado,5,true,carga\n"
    )
    img_data = b"\xff\xd8\xff" + b"\x00" * 200
    with zipfile.ZipFile(buf, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(f"{ferm_code}/imagenes/{ferm_code}_20240101_120000.jpg", img_data)
        zf.writestr(f"{ferm_code}/{ferm_code}_metadata.csv", VALID_CSV_HEADER + csv_row)
    return buf.getvalue()


class InvestigadorUser(HttpUser):
    """
    Simula un investigador que revisa aportes pendientes
    y consulta los datasets aprobados.
    Peso relativo: 20% del tráfico.
    """
    weight = 20
    wait_time = between(2, 5)
    token: str = None

    def on_start(self):
        r = self.client.post("/api/auth/login", json={
            "email": INVESTIGADOR_EMAIL,
            "password": INVESTIGADOR_PASSWORD,
        })
        if r.status_code == 200:
            self.token = r.json().get("access_token")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(3)
    def listar_fermentaciones(self):
        self.client.get("/api/fermentaciones", headers=self._headers(),
                        name="GET /api/fermentaciones")

    @task(2)
    def ver_aportes_pendientes(self):
        self.client.get("/api/revisar", headers=self._headers(),
                        name="GET /api/revisar")

    @task(1)
    def ver_notificaciones(self):
        self.client.get("/api/notificaciones", headers=self._headers(),
                        name="GET /api/notificaciones")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="GET /health")

    @task(1)
    def ver_perfil(self):
        self.client.get("/api/auth/me", headers=self._headers(),
                        name="GET /api/auth/me")


class ColaboradorUser(HttpUser):
    """
    Simula un colaborador que sube aportes y consulta su historial.
    Peso relativo: 60% del tráfico.
    """
    weight = 60
    wait_time = between(3, 8)
    token: str = None
    counter: int = 0

    def on_start(self):
        # Intentar registrar (puede fallar si ya existe)
        self.client.post("/api/auth/register", json={
            "nombre": "Colaborador Carga",
            "email": COLABORADOR_EMAIL,
            "password": COLABORADOR_PASSWORD,
        })
        r = self.client.post("/api/auth/login", json={
            "email": COLABORADOR_EMAIL,
            "password": COLABORADOR_PASSWORD,
        })
        if r.status_code == 200:
            self.token = r.json().get("access_token")

    def _headers(self):
        return {"Authorization": f"Bearer {self.token}"} if self.token else {}

    @task(4)
    def ver_mis_aportes(self):
        self.client.get("/api/aportes/me", headers=self._headers(),
                        name="GET /api/aportes/me")

    @task(2)
    def ver_datasets(self):
        self.client.get("/api/fermentaciones", headers=self._headers(),
                        name="GET /api/fermentaciones")

    @task(1)
    def ver_notificaciones(self):
        self.client.get("/api/notificaciones", headers=self._headers(),
                        name="GET /api/notificaciones")

    @task(1)
    def health_check(self):
        self.client.get("/health", name="GET /health")

    @task(2)
    def subir_aporte(self):
        """Sube un ZIP de prueba (tarea de alta carga)."""
        if not self.token:
            return
        ferm_num = random.randint(50, 99)
        ferm_code = f"FERM{ferm_num:02d}"
        zip_bytes = _build_zip_bytes(ferm_code)
        with self.client.post(
            "/api/aportes/subir",
            files={"file": (f"{ferm_code}.zip", zip_bytes, "application/zip")},
            headers=self._headers(),
            catch_response=True,
            name="POST /api/aportes/subir",
        ) as response:
            if response.status_code in (201, 400, 429):
                response.success()
            else:
                response.failure(f"Status inesperado: {response.status_code}")


class PublicoUser(HttpUser):
    """
    Simula tráfico anónimo (antes de autenticarse).
    Peso relativo: 20% del tráfico.
    """
    weight = 20
    wait_time = between(1, 3)

    @task(3)
    def health_check(self):
        self.client.get("/health", name="GET /health")

    @task(2)
    def intentar_login_invalido(self):
        """Simula intentos de login con credenciales incorrectas."""
        with self.client.post(
            "/api/auth/login",
            json={"email": "noexiste@test.com", "password": "wrong"},
            catch_response=True,
            name="POST /api/auth/login [invalid]",
        ) as r:
            if r.status_code == 401:
                r.success()
            else:
                r.failure(f"Esperaba 401, recibió {r.status_code}")

    @task(1)
    def ver_openapi(self):
        self.client.get("/openapi.json", name="GET /openapi.json")

    @task(1)
    def intentar_sin_token(self):
        """Simula acceso sin token — debe retornar 401."""
        with self.client.get(
            "/api/fermentaciones",
            catch_response=True,
            name="GET /api/fermentaciones [sin token]",
        ) as r:
            if r.status_code == 401:
                r.success()
            else:
                r.failure(f"Esperaba 401, recibió {r.status_code}")


# ──────────────────────────────────────────────────────────────
# Métricas personalizadas al finalizar el test
# ──────────────────────────────────────────────────────────────
@events.quitting.add_listener
def on_quitting(environment, **kwargs):
    stats = environment.stats
    total = stats.total
    if total.num_requests > 0:
        print("\n" + "="*60)
        print("  RESUMEN FINAL DE CARGA — FermentAI")
        print("="*60)
        print(f"  Total requests  : {total.num_requests}")
        print(f"  Fallos          : {total.num_failures}")
        print(f"  Tasa de fallos  : {total.fail_ratio*100:.2f}%")
        print(f"  RPS promedio    : {total.current_rps:.2f}")
        print(f"  Latencia media  : {total.avg_response_time:.1f} ms")
        print(f"  P95             : {total.get_response_time_percentile(0.95):.1f} ms")
        print(f"  P99             : {total.get_response_time_percentile(0.99):.1f} ms")
        print("="*60)

        # Criterios de aceptación de la prueba de carga
        if total.fail_ratio > 0.05:
            print(f"  [FAIL] Tasa de error {total.fail_ratio*100:.2f}% supera el 5%")
            environment.process_exit_code = 1
        if total.get_response_time_percentile(0.95) > 2000:
            print("  [FAIL] P95 supera los 2000ms bajo carga")
            environment.process_exit_code = 1
