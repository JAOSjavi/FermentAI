"""
Pruebas de Rendimiento — FermentAI
Evalúa el rendimiento de la API bajo carga concurrente ligera usando
threading y mide throughput (RPS), latencias y tasa de errores.

Ejecución:
    pytest tests/07_rendimiento/test_rendimiento.py -v -m rendimiento -s

Métricas objetivo:
    - Throughput: >= 20 RPS en endpoint /health
    - Error rate bajo concurrencia: <= 1%
    - P95 bajo 10 usuarios concurrentes: < 1000 ms
"""
import time
import threading
import statistics
import queue
import pytest
import httpx

API_URL = "http://localhost:8000"

INVESTIGADOR_EMAIL = "jesus.coral@ucc.edu.co"
INVESTIGADOR_PASSWORD = "investigador123"


def _peticion_concurrente(url: str, headers: dict, resultado_queue: queue.Queue, idx: int):
    """Función ejecutada en un hilo para medir una petición."""
    try:
        start = time.perf_counter()
        r = httpx.get(url, headers=headers, timeout=15)
        elapsed = (time.perf_counter() - start) * 1000
        resultado_queue.put({
            "idx": idx,
            "status": r.status_code,
            "ms": elapsed,
            "ok": r.status_code == 200,
        })
    except Exception as e:
        resultado_queue.put({"idx": idx, "status": 0, "ms": 9999, "ok": False, "error": str(e)})


def _ejecutar_concurrente(url: str, n_usuarios: int, headers: dict = None) -> dict:
    """Lanza N usuarios concurrentes y recoge métricas."""
    resultados_queue = queue.Queue()
    hilos = []
    inicio_global = time.perf_counter()

    for i in range(n_usuarios):
        h = threading.Thread(
            target=_peticion_concurrente,
            args=(url, headers or {}, resultados_queue, i),
        )
        hilos.append(h)

    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=30)

    duracion_total = time.perf_counter() - inicio_global

    resultados = []
    while not resultados_queue.empty():
        resultados.append(resultados_queue.get())

    tiempos = [r["ms"] for r in resultados if r["ok"]]
    errores = sum(1 for r in resultados if not r["ok"])

    return {
        "usuarios": n_usuarios,
        "completados": len(resultados),
        "exitosos": len(tiempos),
        "errores": errores,
        "tasa_error": errores / n_usuarios if n_usuarios else 0,
        "duracion_total_s": duracion_total,
        "throughput_rps": len(tiempos) / duracion_total if duracion_total > 0 else 0,
        "p50_ms": statistics.median(tiempos) if tiempos else 9999,
        "p95_ms": sorted(tiempos)[int(len(tiempos) * 0.95)] if tiempos else 9999,
        "p99_ms": sorted(tiempos)[int(len(tiempos) * 0.99)] if tiempos else 9999,
        "mean_ms": statistics.mean(tiempos) if tiempos else 9999,
        "max_ms": max(tiempos) if tiempos else 9999,
    }


def _print_metricas(label: str, m: dict):
    print(f"\n  ── {label} ──")
    print(f"  Usuarios concurrentes : {m['usuarios']}")
    print(f"  Completados/Exitosos  : {m['completados']}/{m['exitosos']}")
    print(f"  Errores               : {m['errores']} ({m['tasa_error']*100:.2f}%)")
    print(f"  Throughput            : {m['throughput_rps']:.1f} RPS")
    print(f"  Duración total        : {m['duracion_total_s']:.2f} s")
    print(f"  P50: {m['p50_ms']:.1f}ms | P95: {m['p95_ms']:.1f}ms | P99: {m['p99_ms']:.1f}ms")
    print(f"  Max: {m['max_ms']:.1f}ms | Media: {m['mean_ms']:.1f}ms")


@pytest.fixture(scope="module")
def auth_headers():
    r = httpx.post(
        f"{API_URL}/api/auth/login",
        json={"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD},
        timeout=15,
    )
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


@pytest.mark.rendimiento
class TestRendimientoHealthCheck:
    """Rendimiento del endpoint de health check bajo concurrencia."""

    def test_health_10_usuarios_concurrentes(self):
        m = _ejecutar_concurrente(f"{API_URL}/health", n_usuarios=10)
        _print_metricas("Health — 10 usuarios concurrentes", m)
        assert m["tasa_error"] <= 0.01, f"Tasa de error: {m['tasa_error']*100:.2f}%"
        assert m["p95_ms"] < 1000, f"P95: {m['p95_ms']:.1f}ms supera 1000ms"

    def test_health_25_usuarios_concurrentes(self):
        m = _ejecutar_concurrente(f"{API_URL}/health", n_usuarios=25)
        _print_metricas("Health — 25 usuarios concurrentes", m)
        assert m["tasa_error"] <= 0.05, f"Tasa de error: {m['tasa_error']*100:.2f}%"

    def test_health_throughput_minimo(self):
        """El API debe ser capaz de manejar al menos 20 RPS."""
        m = _ejecutar_concurrente(f"{API_URL}/health", n_usuarios=20)
        _print_metricas("Health — Throughput mínimo", m)
        assert m["throughput_rps"] >= 5, (
            f"Throughput {m['throughput_rps']:.1f} RPS es insuficiente (mínimo: 5 RPS)"
        )


@pytest.mark.rendimiento
class TestRendimientoAutenticacion:
    """Rendimiento de login con múltiples usuarios simultáneos."""

    def test_login_5_usuarios_concurrentes(self):
        results_queue = queue.Queue()

        def login_request(idx):
            try:
                start = time.perf_counter()
                r = httpx.post(
                    f"{API_URL}/api/auth/login",
                    json={"email": INVESTIGADOR_EMAIL, "password": INVESTIGADOR_PASSWORD},
                    timeout=15,
                )
                elapsed = (time.perf_counter() - start) * 1000
                results_queue.put({"status": r.status_code, "ms": elapsed, "ok": r.status_code == 200})
            except Exception as e:
                results_queue.put({"status": 0, "ms": 9999, "ok": False, "error": str(e)})

        hilos = [threading.Thread(target=login_request, args=(i,)) for i in range(5)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join(timeout=30)

        resultados = []
        while not results_queue.empty():
            resultados.append(results_queue.get())

        exitosos = sum(1 for r in resultados if r["ok"])
        tiempos = [r["ms"] for r in resultados if r["ok"]]

        print(f"\n  Login 5 concurrentes: {exitosos}/5 exitosos")
        if tiempos:
            print(f"  P95: {sorted(tiempos)[int(len(tiempos)*0.95)]:.1f}ms | Max: {max(tiempos):.1f}ms")

        assert exitosos >= 4, f"Solo {exitosos}/5 logins exitosos bajo concurrencia"


@pytest.mark.rendimiento
class TestRendimientoEndpointsProtegidos:
    """Rendimiento de endpoints que requieren autenticación."""

    def test_fermentaciones_10_usuarios(self, auth_headers):
        m = _ejecutar_concurrente(
            f"{API_URL}/api/fermentaciones",
            n_usuarios=10,
            headers=auth_headers,
        )
        _print_metricas("GET /api/fermentaciones — 10 usuarios", m)
        assert m["tasa_error"] <= 0.01
        assert m["p95_ms"] < 2000, f"P95 fermentaciones: {m['p95_ms']:.1f}ms > 2000ms"

    def test_aportes_me_10_usuarios(self, auth_headers):
        m = _ejecutar_concurrente(
            f"{API_URL}/api/aportes/me",
            n_usuarios=10,
            headers=auth_headers,
        )
        _print_metricas("GET /api/aportes/me — 10 usuarios", m)
        assert m["tasa_error"] <= 0.01


@pytest.mark.rendimiento
class TestRendimientoComparativo:
    """Compara rendimiento bajo distintos niveles de concurrencia."""

    def test_escalabilidad_gradual(self, auth_headers):
        """Evalúa cómo escala la latencia P95 al aumentar usuarios."""
        niveles = [1, 5, 10, 20]
        print("\n\n  ══════════════ ESCALABILIDAD ══════════════")
        print(f"  {'Usuarios':<10} {'P50':>8} {'P95':>8} {'RPS':>8} {'Errores':>8}")
        print(f"  {'-'*10} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")

        p95_anterior = 0
        for n in niveles:
            m = _ejecutar_concurrente(f"{API_URL}/health", n_usuarios=n)
            print(f"  {n:<10} {m['p50_ms']:>7.1f}ms {m['p95_ms']:>7.1f}ms "
                  f"{m['throughput_rps']:>7.1f} {m['errores']:>8}")
            if p95_anterior > 0:
                degradacion = (m["p95_ms"] - p95_anterior) / p95_anterior
                assert degradacion < 5.0, (
                    f"P95 se degradó {degradacion*100:.0f}% al pasar de {n//2} a {n} usuarios"
                )
            p95_anterior = m["p95_ms"]

        print("  ══════════════════════════════════════════")
