"""Tests for csv_parser service."""
import pytest
from app.services.csv_parser import parse_metadata_csv


def make_csv(rows: list[str]) -> bytes:
    header = (
        "imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
        "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
        "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
        "estado_fermentacion,intervalo_incertidumbre_min,validado_asesor,observaciones\n"
    )
    return (header + "\n".join(rows) + "\n").encode("utf-8")


def test_parses_basic_row():
    csv = make_csv([
        "FERM01_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.2,22.1,5.0,"
        "0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,semi_fermentado,5,true,Buena muestra"
    ])
    rows = parse_metadata_csv(csv)
    assert len(rows) == 1
    r = rows[0]
    assert r["imagen"] == "FERM01_20240101_120000.jpg"
    assert r["tiempo_horas"] == 0.0
    assert r["glucosa_g_l"] == pytest.approx(45.2)
    assert r["estado_fermentacion"] == "semi_fermentado"
    assert r["validado_asesor"] is True
    assert r["observaciones"] == "Buena muestra"


def test_parses_multiple_rows():
    rows_data = [
        "FERM01_20240101_120000.jpg,2024-01-01T12:00:00,0.0,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,semi_fermentado,5,true,",
        "FERM01_20240101_130000.jpg,2024-01-01T13:00:00,1.0,44.0,21.5,4.8,0.5,0.1,0.0,0.0,0.0,0.0,0.0,0.0,semi_fermentado,5,false,",
        "FERM01_20240101_140000.jpg,2024-01-01T14:00:00,2.0,42.0,20.0,4.5,1.2,0.3,0.0,0.0,0.0,0.0,0.0,0.0,fermentado,5,true,",
    ]
    rows = parse_metadata_csv(make_csv(rows_data))
    assert len(rows) == 3
    assert rows[1]["etanol_g_l"] == pytest.approx(0.5)
    assert rows[2]["estado_fermentacion"] == "fermentado"


def test_handles_empty_numerics():
    csv = make_csv([
        "FERM01_20240101_120000.jpg,2024-01-01T12:00:00,,,,,,,,,,,,,,semi_fermentado,5,false,"
    ])
    rows = parse_metadata_csv(csv)
    assert rows[0]["tiempo_horas"] is None
    assert rows[0]["glucosa_g_l"] is None


def test_bool_parsing():
    csv = make_csv([
        "img1.jpg,2024-01-01T12:00:00,0,1,1,1,0,0,0,0,0,0,0,0,fermentado,5,1,",
        "img2.jpg,2024-01-01T12:00:00,0,1,1,1,0,0,0,0,0,0,0,0,fermentado,5,false,",
        "img3.jpg,2024-01-01T12:00:00,0,1,1,1,0,0,0,0,0,0,0,0,fermentado,5,True,",
    ])
    rows = parse_metadata_csv(csv)
    assert rows[0]["validado_asesor"] is True
    assert rows[1]["validado_asesor"] is False
    assert rows[2]["validado_asesor"] is True


def test_bom_handling():
    header = (
        "﻿imagen,timestamp,tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,"
        "etanol_g_l,acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
        "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
        "estado_fermentacion,intervalo_incertidumbre_min,validado_asesor,observaciones\n"
        "img.jpg,2024-01-01T12:00:00,0,1,1,1,0,0,0,0,0,0,0,0,fermentado,5,true,\n"
    )
    rows = parse_metadata_csv(header.encode("utf-8-sig"))
    assert len(rows) == 1
    assert rows[0]["imagen"] == "img.jpg"
