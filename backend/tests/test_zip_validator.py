"""Tests for zip_validator service — formato actual 14 columnas."""
import io
import os
import zipfile
import tempfile
import pytest
from app.services.zip_validator import validate_zip

VALID_HEADER = (
    "ferm_fecha_hora,glucosa_g_l,fructosa_g_l,sacarosa_g_l,etanol_g_l,"
    "acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "validado_asesor,observaciones\n"
)
VALID_ROW = "20260526_093800,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,\n"
JPEG_MAGIC = b"\xff\xd8\xff" + b"\x00" * 100


def _make_zip(entries: dict) -> tuple[str, int]:
    tmp = tempfile.NamedTemporaryFile(suffix=".zip", delete=False)
    tmp.close()
    with zipfile.ZipFile(tmp.name, "w") as zf:
        for name, content in entries.items():
            zf.writestr(name, content)
    size = os.path.getsize(tmp.name)
    return tmp.name, size


def teardown_zip(path: str):
    try:
        os.unlink(path)
    except OSError:
        pass


class TestValidZip:
    def test_valid_structure_passes(self):
        csv_content = VALID_HEADER + VALID_ROW
        path, size = _make_zip({
            "FERM01/imagenes/foto_001.jpg": JPEG_MAGIC,
            "FERM01/FERM01_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert result.valid, f"Errores: {result.errors}"
            assert result.ferm_code == "FERM01"
        finally:
            teardown_zip(path)

    def test_accepts_any_jpeg_filename(self):
        """El pipeline no exige formato de nombre específico en imágenes."""
        csv_content = VALID_HEADER + VALID_ROW
        path, size = _make_zip({
            "FERM03/imagenes/webcam_20260519_175904.jpg": JPEG_MAGIC,
            "FERM03/FERM03_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert result.valid, f"Errores: {result.errors}"
        finally:
            teardown_zip(path)


class TestStructureErrors:
    def test_missing_ferm_folder(self):
        path, size = _make_zip({"archivo.txt": "hola"})
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("FERM" in e for e in result.errors)
        finally:
            teardown_zip(path)

    def test_missing_csv(self):
        path, size = _make_zip({
            "FERM01/imagenes/foto_001.jpg": JPEG_MAGIC,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("CSV" in e for e in result.errors)
        finally:
            teardown_zip(path)

    def test_missing_imagenes_folder(self):
        csv_content = VALID_HEADER + VALID_ROW
        path, size = _make_zip({
            "FERM01/FERM01_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
        finally:
            teardown_zip(path)


class TestCSVErrors:
    def test_missing_columns(self):
        bad_csv = "ferm_fecha_hora,glucosa_g_l\n20260526_093800,45.0\n"
        path, size = _make_zip({
            "FERM01/imagenes/foto_001.jpg": JPEG_MAGIC,
            "FERM01/FERM01_metadata.csv": bad_csv,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("Columnas faltantes" in e for e in result.errors)
        finally:
            teardown_zip(path)


class TestSizeValidation:
    def test_zip_size_limit(self):
        path, _ = _make_zip({"FERM01/imagenes/foto_001.jpg": JPEG_MAGIC})
        oversized = 2 * 1024 * 1024 * 1024 + 1
        try:
            result = validate_zip(path, oversized)
            assert not result.valid
            assert any("2 GB" in e for e in result.errors)
        finally:
            teardown_zip(path)
