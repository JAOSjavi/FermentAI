"""Tests para el pipeline de depuración — depuracion.py."""
import io
import zipfile
import pytest
from PIL import Image
from unittest.mock import patch, MagicMock

from app.pipeline.depuracion import _paso0_csv, _paso1_estructura, _paso4_resize
from app.pipeline.exceptions import PipelineError
from app.pipeline.reporte import ReporteDepuracion

VALID_HEADER = (
    "ferm_fecha_hora,glucosa_g_l,fructosa_g_l,sacarosa_g_l,etanol_g_l,"
    "acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "validado_asesor,observaciones\n"
)


def make_csv_bytes(rows: list[str]) -> bytes:
    return (VALID_HEADER + "\n".join(rows) + "\n").encode("utf-8")


def make_reporte() -> ReporteDepuracion:
    return ReporteDepuracion(fermentacion_id="FERM01", total_recibidas=0,
                             total_procesadas=0, total_descartadas=0)


def make_jpeg_bytes(width=1280, height=720) -> bytes:
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    return buf.getvalue()


def make_zip_bytes(ferm_code="FERM01", extra_entries: dict | None = None) -> bytes:
    valid_row = "20260526_093800,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,"
    csv_content = VALID_HEADER + valid_row
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr(f"{ferm_code}/imagenes/foto_001.jpg", make_jpeg_bytes())
        zf.writestr(f"{ferm_code}/{ferm_code}_metadata.csv", csv_content)
        for name, content in (extra_entries or {}).items():
            zf.writestr(name, content)
    return buf.getvalue()


# ─── Tests de _paso0_csv ─────────────────────────────────────────────────────

class TestPaso0CSV:
    def test_csv_valido_pasa(self):
        csv = make_csv_bytes(["20260526_093800,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,ok"])
        reporte = make_reporte()
        _paso0_csv(csv, reporte)
        assert reporte.csv_valido is True
        assert reporte.no_conformidades_iso == []

    def test_columna_faltante_lanza_error(self):
        bad = b"ferm_fecha_hora,glucosa_g_l\n20260526_093800,45.0\n"
        with pytest.raises(PipelineError, match="Columnas faltantes"):
            _paso0_csv(bad, make_reporte())

    def test_columna_extra_lanza_error(self):
        header_extra = VALID_HEADER.rstrip("\n") + ",columna_extra\n"
        csv = (header_extra + "0.0,45,22,5,0,0,0,0,0,0,0,0,TRUE,,valor\n").encode()
        with pytest.raises(PipelineError, match="Columnas no reconocidas"):
            _paso0_csv(csv, make_reporte())

    def test_ferm_fecha_hora_formato_invalido_genera_nc(self):
        csv = make_csv_bytes(["26_05_2026_9_38,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,"])
        reporte = make_reporte()
        _paso0_csv(csv, reporte)
        assert reporte.csv_valido is False
        assert any("ferm_fecha_hora" in nc for nc in reporte.no_conformidades_iso)

    def test_ferm_fecha_hora_no_monotona_genera_nc(self):
        csv = make_csv_bytes([
            "20260526_093800,45,22,5,0,0,0,0,0,0,0,0,TRUE,",
            "20260526_093800,44,21,5,0,0,0,0,0,0,0,0,TRUE,",  # misma fecha → no estrictamente posterior
        ])
        reporte = make_reporte()
        _paso0_csv(csv, reporte)
        assert reporte.csv_valido is False
        assert any("no es posterior" in nc for nc in reporte.no_conformidades_iso)

    def test_validado_asesor_invalido_genera_nc(self):
        csv = make_csv_bytes(["0.0,45,22,5,0,0,0,0,0,0,0,0,SI,"])
        reporte = make_reporte()
        _paso0_csv(csv, reporte)
        assert reporte.csv_valido is False
        assert any("validado_asesor" in nc for nc in reporte.no_conformidades_iso)

    def test_csv_vacio_lanza_error(self):
        csv = VALID_HEADER.encode("utf-8")
        with pytest.raises(PipelineError, match="al menos 1 fila"):
            _paso0_csv(csv, make_reporte())

    def test_csv_sin_codificacion_utf8_lanza_error(self):
        with pytest.raises(PipelineError, match="UTF-8"):
            _paso0_csv(b"\xff\xfe datos basura", make_reporte())


# ─── Tests de _paso1_estructura ──────────────────────────────────────────────

class TestPaso1Estructura:
    def test_estructura_valida_retorna_ferm_code(self):
        names = ["FERM01/imagenes/foto.jpg", "FERM01/FERM01_metadata.csv"]
        assert _paso1_estructura(names) == "FERM01"

    def test_sin_carpeta_ferm_lanza_error(self):
        with pytest.raises(PipelineError, match="FERM01"):
            _paso1_estructura(["archivo.txt"])

    def test_multiples_carpetas_ferm_lanza_error(self):
        names = [
            "FERM01/imagenes/a.jpg", "FERM01/FERM01_metadata.csv",
            "FERM02/imagenes/b.jpg", "FERM02/FERM02_metadata.csv",
        ]
        with pytest.raises(PipelineError, match="múltiples"):
            _paso1_estructura(names)

    def test_sin_subcarpeta_imagenes_lanza_error(self):
        names = ["FERM01/FERM01_metadata.csv"]
        with pytest.raises(PipelineError):
            _paso1_estructura(names)

    def test_sin_csv_lanza_error(self):
        names = ["FERM01/imagenes/foto.jpg"]
        with pytest.raises(PipelineError, match="CSV"):
            _paso1_estructura(names)

    def test_ferm_code_fuera_de_rango_rechazado(self):
        """FERM13 no es válido — solo FERM01 a FERM12."""
        names = ["FERM13/imagenes/foto.jpg", "FERM13/FERM13_metadata.csv"]
        with pytest.raises(PipelineError):
            _paso1_estructura(names)


# ─── Tests de _paso4_resize ──────────────────────────────────────────────────

class TestPaso4Resize:
    def test_imagen_exacta_no_cambia(self):
        img = Image.new("RGB", (1280, 720))
        result = _paso4_resize(img)
        assert result.size == (1280, 720)

    def test_imagen_mayor_se_recorta_a_1280x720(self):
        img = Image.new("RGB", (1920, 1080))
        result = _paso4_resize(img)
        assert result.size == (1280, 720)

    def test_imagen_cuadrada_se_recorta_a_1280x720(self):
        img = Image.new("RGB", (2000, 2000))
        result = _paso4_resize(img)
        assert result.size == (1280, 720)


# ─── Test de integración del pipeline completo (mock MinIO) ──────────────────

class TestEjecutarPipeline:
    @patch("app.pipeline.depuracion.minio_client")
    def test_pipeline_completo_con_imagen_valida(self, mock_minio):
        mock_minio.ensure_bucket = MagicMock()
        mock_minio.upload_bytes = MagicMock()

        from app.pipeline.depuracion import ejecutar_pipeline
        zip_bytes = make_zip_bytes("FERM01")
        reporte = ejecutar_pipeline(zip_bytes, aporte_id=999)

        assert reporte.total_procesadas == 1
        assert reporte.total_descartadas == 0
        assert reporte.csv_valido is True
        assert len(reporte.rutas_processed) == 1

    @patch("app.pipeline.depuracion.minio_client")
    def test_imagen_sin_magic_bytes_es_descartada(self, mock_minio):
        mock_minio.ensure_bucket = MagicMock()
        mock_minio.upload_bytes = MagicMock()

        valid_row = "20260526_093800,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,"
        csv_content = VALID_HEADER + valid_row
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("FERM01/imagenes/falsa.jpg", b"\x00\x00\x00 no es jpeg")
            zf.writestr("FERM01/imagenes/real.jpg", make_jpeg_bytes())
            zf.writestr("FERM01/FERM01_metadata.csv", csv_content)

        from app.pipeline.depuracion import ejecutar_pipeline
        reporte = ejecutar_pipeline(buf.getvalue(), aporte_id=998)

        assert reporte.total_procesadas == 1
        assert reporte.total_descartadas == 1
        assert any(d["paso"] == 2 for d in reporte.imagenes_descartadas)

    @patch("app.pipeline.depuracion.minio_client")
    def test_imagen_baja_resolucion_es_descartada(self, mock_minio):
        mock_minio.ensure_bucket = MagicMock()
        mock_minio.upload_bytes = MagicMock()

        valid_row = "20260526_093800,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,"
        csv_content = VALID_HEADER + valid_row
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            zf.writestr("FERM01/imagenes/pequena.jpg", make_jpeg_bytes(640, 480))
            zf.writestr("FERM01/imagenes/grande.jpg", make_jpeg_bytes(1280, 720))
            zf.writestr("FERM01/FERM01_metadata.csv", csv_content)

        from app.pipeline.depuracion import ejecutar_pipeline
        reporte = ejecutar_pipeline(buf.getvalue(), aporte_id=997)

        assert reporte.total_procesadas == 1
        assert reporte.total_descartadas == 1
        assert any(d["paso"] == 3 for d in reporte.imagenes_descartadas)
