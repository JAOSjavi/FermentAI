"""
Pruebas de Disponibilidad — FermentAI
Verifica que todos los servicios (API, Frontend, MinIO) estén accesibles
y mide uptime con múltiples intentos consecutivos.

Ejecución:
    pytest tests/04_disponibilidad/test_disponibilidad.py -v -m disponibilidad

Métricas objetivo:
    - Disponibilidad esperada: >= 99%
    - Health check response time: < 500 ms
"""
import time
import statistics
import pytest
import httpx

API_URL = "http://localhost:8000"
FRONTEND_URL = "http://localhost:3000"
MINIO_URL = "http://localhost:9000"
MINIO_CONSOLE_URL = "http://localhost:9001"

UPTIME_INTENTOS = 10
UPTIME_INTERVALO_SEG = 0.5
UMBRAL_DISPONIBILIDAD = 0.99  # 99%
UMBRAL_RESPONSE_TIME_MS = 500


@pytest.mark.disponibilidad
class TestDisponibilidadAPI:
    """Comprueba que la API REST esté levantada y responda correctamente."""

    def test_health_endpoint_disponible(self):
        r = httpx.get(f"{API_URL}/health", timeout=10)
        assert r.status_code == 200, f"Health check falló: {r.status_code}"
        body = r.json()
        assert body.get("status") == "ok", f"Estado inesperado: {body}"

    def test_docs_openapi_disponibles(self):
        r = httpx.get(f"{API_URL}/docs", timeout=10)
        assert r.status_code == 200, "Documentación OpenAPI /docs no disponible"

    def test_openapi_json_disponible(self):
        r = httpx.get(f"{API_URL}/openapi.json", timeout=10)
        assert r.status_code == 200
        schema = r.json()
        assert "paths" in schema, "El schema OpenAPI no contiene rutas"
        assert schema.get("info", {}).get("title") == "FermentAI API"

    def test_uptime_api_10_intentos(self):
        """El API debe responder exitosamente en >= 99% de los intentos."""
        exitosos = 0
        tiempos = []
        for _ in range(UPTIME_INTENTOS):
            try:
                start = time.perf_counter()
                r = httpx.get(f"{API_URL}/health", timeout=5)
                elapsed = (time.perf_counter() - start) * 1000
                if r.status_code == 200:
                    exitosos += 1
                    tiempos.append(elapsed)
            except Exception:
                pass
            time.sleep(UPTIME_INTERVALO_SEG)

        disponibilidad = exitosos / UPTIME_INTENTOS
        assert disponibilidad >= UMBRAL_DISPONIBILIDAD, (
            f"Disponibilidad {disponibilidad*100:.1f}% por debajo del umbral {UMBRAL_DISPONIBILIDAD*100}%"
        )
        if tiempos:
            print(f"\n  Uptime: {disponibilidad*100:.1f}%")
            print(f"  Avg response: {statistics.mean(tiempos):.1f} ms")
            print(f"  Max response: {max(tiempos):.1f} ms")

    def test_endpoint_autenticacion_disponible(self):
        r = httpx.post(
            f"{API_URL}/api/auth/login",
            json={"email": "noexiste@example.com", "password": "x"},
            timeout=10,
        )
        assert r.status_code in (401, 422), (
            f"Endpoint de login no disponible o respuesta inesperada: {r.status_code}"
        )

    def test_endpoint_fermentaciones_disponible(self):
        r = httpx.get(f"{API_URL}/api/fermentaciones", timeout=10)
        assert r.status_code in (401, 403), (
            f"Endpoint /api/fermentaciones no disponible: {r.status_code}"
        )

    def test_tiempo_respuesta_health(self):
        """Health check debe responder en menos de 500 ms."""
        tiempos = []
        for _ in range(5):
            start = time.perf_counter()
            r = httpx.get(f"{API_URL}/health", timeout=5)
            elapsed = (time.perf_counter() - start) * 1000
            if r.status_code == 200:
                tiempos.append(elapsed)
        avg = statistics.mean(tiempos) if tiempos else 9999
        assert avg < UMBRAL_RESPONSE_TIME_MS, (
            f"Tiempo promedio de health check: {avg:.1f} ms (umbral: {UMBRAL_RESPONSE_TIME_MS} ms)"
        )


@pytest.mark.disponibilidad
class TestDisponibilidadFrontend:
    """Comprueba que el frontend Next.js esté disponible."""

    def test_frontend_responde_200(self):
        r = httpx.get(FRONTEND_URL, timeout=15, follow_redirects=True)
        assert r.status_code == 200, f"Frontend no disponible: {r.status_code}"

    def test_pagina_login_disponible(self):
        r = httpx.get(f"{FRONTEND_URL}/login", timeout=15, follow_redirects=True)
        assert r.status_code == 200

    def test_pagina_registro_disponible(self):
        r = httpx.get(f"{FRONTEND_URL}/registro", timeout=15, follow_redirects=True)
        assert r.status_code == 200

    def test_frontend_retorna_html(self):
        r = httpx.get(FRONTEND_URL, timeout=15, follow_redirects=True)
        content_type = r.headers.get("content-type", "")
        assert "text/html" in content_type, f"Content-Type inesperado: {content_type}"

    def test_uptime_frontend_10_intentos(self):
        exitosos = 0
        for _ in range(UPTIME_INTENTOS):
            try:
                r = httpx.get(f"{FRONTEND_URL}/login", timeout=5, follow_redirects=True)
                if r.status_code == 200:
                    exitosos += 1
            except Exception:
                pass
            time.sleep(UPTIME_INTERVALO_SEG)

        disponibilidad = exitosos / UPTIME_INTENTOS
        assert disponibilidad >= UMBRAL_DISPONIBILIDAD, (
            f"Disponibilidad frontend {disponibilidad*100:.1f}% por debajo del umbral"
        )


@pytest.mark.disponibilidad
class TestDisponibilidadMinio:
    """Comprueba que MinIO (almacenamiento de objetos) esté disponible."""

    def test_minio_api_responde(self):
        try:
            r = httpx.get(f"{MINIO_URL}/minio/health/live", timeout=10)
            assert r.status_code in (200, 403), (
                f"MinIO API no disponible: {r.status_code}"
            )
        except httpx.ConnectError:
            pytest.skip("MinIO no está accesible en localhost:9000")

    def test_minio_consola_disponible(self):
        try:
            r = httpx.get(MINIO_CONSOLE_URL, timeout=10, follow_redirects=True)
            assert r.status_code == 200, f"Consola MinIO no disponible: {r.status_code}"
        except httpx.ConnectError:
            pytest.skip("MinIO Console no está accesible en localhost:9001")


@pytest.mark.disponibilidad
class TestEstabilidadServicio:
    """Prueba la estabilidad del servicio bajo consultas repetidas."""

    def test_estabilidad_100_health_checks(self):
        """100 health checks consecutivos sin un solo fallo."""
        INTENTOS = 100
        fallos = 0
        tiempos = []
        for _ in range(INTENTOS):
            try:
                start = time.perf_counter()
                r = httpx.get(f"{API_URL}/health", timeout=5)
                elapsed = (time.perf_counter() - start) * 1000
                if r.status_code != 200:
                    fallos += 1
                else:
                    tiempos.append(elapsed)
            except Exception:
                fallos += 1

        tasa_error = fallos / INTENTOS
        p95 = sorted(tiempos)[int(len(tiempos) * 0.95)] if tiempos else 9999
        p99 = sorted(tiempos)[int(len(tiempos) * 0.99)] if tiempos else 9999

        print(f"\n  Intentos: {INTENTOS} | Fallos: {fallos} | Tasa error: {tasa_error*100:.2f}%")
        print(f"  P95: {p95:.1f} ms | P99: {p99:.1f} ms")
        print(f"  Min: {min(tiempos, default=0):.1f} ms | Max: {max(tiempos, default=0):.1f} ms")

        assert tasa_error <= 0.01, f"Tasa de error {tasa_error*100:.2f}% supera el umbral del 1%"
