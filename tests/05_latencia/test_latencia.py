"""
Pruebas de Latencia y Tiempos de Respuesta — FermentAI
Mide percentiles P50/P95/P99 de los endpoints principales.

Ejecución:
    pytest tests/05_latencia/test_latencia.py -v -m latencia -s

Umbrales objetivo (SLA):
    - P50 < 200 ms
    - P95 < 500 ms
    - P99 < 1000 ms
"""
import time
import statistics
import pytest
import httpx

API_URL = "http://localhost:8000"

# Umbrales en milisegundos
SLA_P50_MS = 200
SLA_P95_MS = 500
SLA_P99_MS = 1000

MUESTRAS = 30  # solicitudes por endpoint para calcular percentiles

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"


def _percentil(datos: list, p: int) -> float:
    if not datos:
        return float("inf")
    sorted_data = sorted(datos)
    idx = max(0, int(len(sorted_data) * p / 100) - 1)
    return sorted_data[idx]


def _medir_endpoint(url: str, method: str = "GET", headers: dict = None,
                    json: dict = None, n: int = MUESTRAS) -> dict:
    """Realiza N peticiones y retorna estadísticas de latencia."""
    tiempos = []
    errores = 0
    for _ in range(n):
        try:
            start = time.perf_counter()
            r = httpx.request(method, url, headers=headers, json=json, timeout=10)
            elapsed = (time.perf_counter() - start) * 1000
            tiempos.append(elapsed)
        except Exception:
            errores += 1

    if not tiempos:
        return {"error": "Todos los intentos fallaron", "errores": errores}

    return {
        "n": n,
        "errores": errores,
        "min_ms": min(tiempos),
        "max_ms": max(tiempos),
        "mean_ms": statistics.mean(tiempos),
        "median_ms": statistics.median(tiempos),
        "p50_ms": _percentil(tiempos, 50),
        "p95_ms": _percentil(tiempos, 95),
        "p99_ms": _percentil(tiempos, 99),
        "stdev_ms": statistics.stdev(tiempos) if len(tiempos) > 1 else 0,
    }


def _print_stats(label: str, stats: dict):
    print(f"\n  ── {label} ──")
    print(f"  Muestras: {stats.get('n')} | Errores: {stats.get('errores', 0)}")
    print(f"  Min: {stats.get('min_ms', 0):.1f} ms | Max: {stats.get('max_ms', 0):.1f} ms")
    print(f"  Media: {stats.get('mean_ms', 0):.1f} ms | Mediana: {stats.get('median_ms', 0):.1f} ms")
    print(f"  P50: {stats.get('p50_ms', 0):.1f} ms | P95: {stats.get('p95_ms', 0):.1f} ms | P99: {stats.get('p99_ms', 0):.1f} ms")
    print(f"  StdDev: {stats.get('stdev_ms', 0):.1f} ms")


@pytest.fixture(scope="module")
def auth_headers():
    r = httpx.post(
        f"{API_URL}/api/auth/login",
        json={"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200
    token = r.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.mark.latencia
class TestLatenciaEndpointsPublicos:
    """Latencia de endpoints que no requieren autenticación."""

    def test_health_check_p95(self):
        stats = _medir_endpoint(f"{API_URL}/health")
        _print_stats("GET /health", stats)
        assert stats["p95_ms"] < SLA_P95_MS, (
            f"P95 health check: {stats['p95_ms']:.1f} ms > {SLA_P95_MS} ms"
        )

    def test_health_check_p50(self):
        stats = _medir_endpoint(f"{API_URL}/health")
        _print_stats("GET /health (P50)", stats)
        assert stats["p50_ms"] < SLA_P50_MS, (
            f"P50 health check: {stats['p50_ms']:.1f} ms > {SLA_P50_MS} ms"
        )

    def test_openapi_json_latencia(self):
        stats = _medir_endpoint(f"{API_URL}/openapi.json")
        _print_stats("GET /openapi.json", stats)
        assert stats["p95_ms"] < SLA_P95_MS * 2, (
            f"P95 openapi.json demasiado lento: {stats['p95_ms']:.1f} ms"
        )


@pytest.mark.latencia
class TestLatenciaAutenticacion:
    """Latencia de los endpoints de autenticación."""

    def test_login_latencia_p50(self):
        stats = _medir_endpoint(
            f"{API_URL}/api/auth/login",
            method="POST",
            json={"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD},
        )
        _print_stats("POST /api/auth/login", stats)
        assert stats["p50_ms"] < SLA_P50_MS * 3, (
            f"P50 login: {stats['p50_ms']:.1f} ms (el hashing de contraseña puede añadir latencia)"
        )

    def test_login_latencia_p95(self):
        stats = _medir_endpoint(
            f"{API_URL}/api/auth/login",
            method="POST",
            json={"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD},
        )
        _print_stats("POST /api/auth/login (P95)", stats)
        assert stats["p95_ms"] < SLA_P99_MS, (
            f"P95 login: {stats['p95_ms']:.1f} ms supera el umbral P99 de {SLA_P99_MS} ms"
        )

    def test_me_endpoint_latencia(self, auth_headers):
        stats = _medir_endpoint(f"{API_URL}/api/auth/me", headers=auth_headers)
        _print_stats("GET /api/auth/me", stats)
        assert stats["p95_ms"] < SLA_P95_MS, (
            f"P95 /auth/me: {stats['p95_ms']:.1f} ms > {SLA_P95_MS} ms"
        )


@pytest.mark.latencia
class TestLatenciaEndpointsProtegidos:
    """Latencia de endpoints que requieren autenticación."""

    def test_fermentaciones_latencia_p50(self, auth_headers):
        stats = _medir_endpoint(f"{API_URL}/api/fermentaciones", headers=auth_headers)
        _print_stats("GET /api/fermentaciones", stats)
        assert stats["p50_ms"] < SLA_P50_MS, (
            f"P50 fermentaciones: {stats['p50_ms']:.1f} ms > {SLA_P50_MS} ms"
        )

    def test_fermentaciones_latencia_p95(self, auth_headers):
        stats = _medir_endpoint(f"{API_URL}/api/fermentaciones", headers=auth_headers)
        _print_stats("GET /api/fermentaciones (P95)", stats)
        assert stats["p95_ms"] < SLA_P95_MS, (
            f"P95 fermentaciones: {stats['p95_ms']:.1f} ms > {SLA_P95_MS} ms"
        )

    def test_mis_aportes_latencia_p95(self, auth_headers):
        stats = _medir_endpoint(f"{API_URL}/api/aportes/me", headers=auth_headers)
        _print_stats("GET /api/aportes/me", stats)
        assert stats["p95_ms"] < SLA_P95_MS, (
            f"P95 aportes/me: {stats['p95_ms']:.1f} ms > {SLA_P95_MS} ms"
        )

    def test_notificaciones_latencia_p95(self, auth_headers):
        stats = _medir_endpoint(f"{API_URL}/api/notificaciones", headers=auth_headers)
        _print_stats("GET /api/notificaciones", stats)
        assert stats["p95_ms"] < SLA_P95_MS, (
            f"P95 notificaciones: {stats['p95_ms']:.1f} ms > {SLA_P95_MS} ms"
        )


@pytest.mark.latencia
class TestLatenciaResumen:
    """Genera un resumen comparativo de latencias de todos los endpoints."""

    def test_resumen_latencias_todos_los_endpoints(self, auth_headers):
        endpoints = [
            ("GET /health", f"{API_URL}/health", "GET", None),
            ("POST /auth/login", f"{API_URL}/api/auth/login", "POST",
             {"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD}),
            ("GET /auth/me", f"{API_URL}/api/auth/me", "GET", None),
            ("GET /fermentaciones", f"{API_URL}/api/fermentaciones", "GET", None),
            ("GET /aportes/me", f"{API_URL}/api/aportes/me", "GET", None),
        ]

        print("\n\n  ══════════════ RESUMEN DE LATENCIAS ══════════════")
        print(f"  {'Endpoint':<30} {'P50':>8} {'P95':>8} {'P99':>8} {'Max':>8}")
        print(f"  {'-'*30} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        for label, url, method, body in endpoints:
            hdrs = auth_headers if "auth/me" in url or "fermentaciones" in url or "aportes" in url else None
            stats = _medir_endpoint(url, method=method, headers=hdrs, json=body, n=20)
            if "error" not in stats:
                print(
                    f"  {label:<30} {stats['p50_ms']:>7.1f}ms {stats['p95_ms']:>7.1f}ms "
                    f"{stats['p99_ms']:>7.1f}ms {stats['max_ms']:>7.1f}ms"
                )
        print("  ══════════════════════════════════════════════════")

        assert True  # Este test es solo informativo
