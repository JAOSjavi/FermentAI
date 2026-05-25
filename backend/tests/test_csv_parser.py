"""Tests for csv_parser service — formato actual 14 columnas."""
import pytest
from app.services.csv_parser import parse_metadata_csv

VALID_HEADER = (
    "tiempo_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,etanol_g_l,"
    "acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
    "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
    "validado_asesor,observaciones\n"
)


def make_csv(rows: list[str]) -> bytes:
    return (VALID_HEADER + "\n".join(rows) + "\n").encode("utf-8")


def test_parses_basic_row():
    csv = make_csv(["0.0,45.2,22.1,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,Buena muestra"])
    rows = parse_metadata_csv(csv)
    assert len(rows) == 1
    r = rows[0]
    assert r["tiempo_horas"] == pytest.approx(0.0)
    assert r["glucosa_g_l"] == pytest.approx(45.2)
    assert r["validado_asesor"] is True
    assert r["observaciones"] == "Buena muestra"


def test_parses_multiple_rows():
    rows_data = [
        "0.0,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,",
        "6.0,44.0,21.5,4.8,0.5,0.1,0.0,0.0,0.0,0.0,0.0,0.0,FALSE,",
        "12.0,42.0,20.0,4.5,1.2,0.3,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,",
    ]
    rows = parse_metadata_csv(make_csv(rows_data))
    assert len(rows) == 3
    assert rows[1]["etanol_g_l"] == pytest.approx(0.5)
    assert rows[2]["tiempo_horas"] == pytest.approx(12.0)


def test_handles_empty_observaciones():
    csv = make_csv(["0.0,45.0,22.0,5.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,TRUE,"])
    rows = parse_metadata_csv(csv)
    assert rows[0]["observaciones"] is None


def test_bool_parsing():
    rows_data = [
        "0.0,1,1,1,0,0,0,0,0,0,0,0,1,",
        "6.0,1,1,1,0,0,0,0,0,0,0,0,false,",
        "12.0,1,1,1,0,0,0,0,0,0,0,0,True,",
    ]
    rows = parse_metadata_csv(make_csv(rows_data))
    assert rows[0]["validado_asesor"] is True
    assert rows[1]["validado_asesor"] is False
    assert rows[2]["validado_asesor"] is True


def test_bom_handling():
    header_bom = (
        "﻿time_horas,glucosa_g_l,fructosa_g_l,sacarosa_g_l,etanol_g_l,"
        "acido_lactico_g_l,acido_acetico_g_l,acido_citrico_g_l,"
        "acido_succinico_g_l,acido_malico_g_l,acido_oxalico_g_l,acido_formico_g_l,"
        "validado_asesor,observaciones\n"
        "0.0,1,1,1,0,0,0,0,0,0,0,0,true,\n"
    )
    rows = parse_metadata_csv(header_bom.encode("utf-8-sig"))
    assert len(rows) == 1
