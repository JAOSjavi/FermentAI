"""Tests for zip_validator service."""
import io
import os
import zipfile
import tempfile
import pytest
from app.services.zip_validator import validate_zip

VALID_CSV_HEADER = (
    "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
    "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "intervalo_incertidumbre_min,validado_asesor,observaciones\n"
)
VALID_CSV_ROW = (
    "FERM01_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,"
    "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5,true,\n"
)


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
        img_data = b"\xff\xd8\xff" + b"\x00" * 100
        csv_content = VALID_CSV_HEADER + VALID_CSV_ROW
        path, size = _make_zip({
            "FERM01/imagenes/FERM01_20240101_120000.jpg": img_data,
            "FERM01/FERM01_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert result.valid, f"Errores: {result.errors}"
            assert result.ferm_code == "FERM01"
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
        img_data = b"\xff\xd8\xff" + b"\x00" * 100
        path, size = _make_zip({
            "FERM01/imagenes/FERM01_20240101_120000.jpg": img_data,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("CSV" in e for e in result.errors)
        finally:
            teardown_zip(path)

    def test_invalid_image_name(self):
        img_data = b"\xff\xd8\xff" + b"\x00" * 100
        csv_content = VALID_CSV_HEADER + "invalid_name.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5,true,\n"
        path, size = _make_zip({
            "FERM01/imagenes/invalid_name.jpg": img_data,
            "FERM01/FERM01_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("inválido" in e for e in result.errors)
        finally:
            teardown_zip(path)


class TestCSVErrors:
    def test_missing_columns(self):
        bad_csv = "imagen,timestamp\nFERM01_20240101_120000.jpg,2024-01-01T12:00:00\n"
        img_data = b"\xff\xd8\xff" + b"\x00" * 100
        path, size = _make_zip({
            "FERM01/imagenes/FERM01_20240101_120000.jpg": img_data,
            "FERM01/FERM01_metadata.csv": bad_csv,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("Columnas faltantes" in e for e in result.errors)
        finally:
            teardown_zip(path)

    def test_image_csv_mismatch(self):
        img_data = b"\xff\xd8\xff" + b"\x00" * 100
        csv_content = VALID_CSV_HEADER + (
            "FERM01_20240101_130000.jpg,2024-01-01T13:00:00,1.0,44.0,21.0,5.0,"
            "0.1,0.0,0.0,0.0,0.0,0.0,0.0,0.0,5,true,\n"
        )
        path, size = _make_zip({
            "FERM01/imagenes/FERM01_20240101_120000.jpg": img_data,
            "FERM01/FERM01_metadata.csv": csv_content,
        })
        try:
            result = validate_zip(path, size)
            assert not result.valid
            assert any("sin fila" in e or "sin imagen" in e for e in result.errors)
        finally:
            teardown_zip(path)


class TestSizeValidation:
    def test_zip_size_limit(self):
        path, _ = _make_zip({"FERM01/imagenes/FERM01_20240101_120000.jpg": b"x"})
        oversized = 2 * 1024 * 1024 * 1024 + 1
        try:
            result = validate_zip(path, oversized)
            assert not result.valid
            assert any("2 GB" in e for e in result.errors)
        finally:
            teardown_zip(path)
