import csv
import io
from datetime import datetime
from typing import List, Dict, Any


def parse_metadata_csv(csv_bytes: bytes) -> List[Dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(csv_bytes.decode("utf-8-sig")))
    rows = []
    for row in reader:
        parsed = {
            "imagen": row.get("imagen", "").strip(),
            "timestamp": _parse_dt(row.get("timestamp", "")),
            "tiempo_horas": _float(row.get("tiempo_horas")),
            "glucosa_g_l": _float(row.get("glucosa_g_l")),
            "fructosa_g_l": _float(row.get("fructosa_g_l")),
            "sacarosa_g_l": _float(row.get("sacarosa_g_l")),
            "etanol_g_l": _float(row.get("etanol_g_l")),
            "acido_lactico_g_l": _float(row.get("acido_lactico_g_l")),
            "acido_acetico_g_l": _float(row.get("acido_acetico_g_l")),
            "acido_citrico_g_l": _float(row.get("acido_citrico_g_l")),
            "acido_succinico_g_l": _float(row.get("acido_succinico_g_l")),
            "acido_malico_g_l": _float(row.get("acido_malico_g_l")),
            "acido_oxalico_g_l": _float(row.get("acido_oxalico_g_l")),
            "acido_formico_g_l": _float(row.get("acido_formico_g_l")),
            "intervalo_incertidumbre_min": _int(row.get("intervalo_incertidumbre_min")),
            "validado_asesor": _bool(row.get("validado_asesor")),
            "observaciones": row.get("observaciones", "").strip() or None,
        }
        rows.append(parsed)
    return rows


def _float(val) -> float | None:
    if val is None:
        return None
    try:
        return float(str(val).strip())
    except (ValueError, TypeError):
        return None


def _int(val) -> int | None:
    if val is None:
        return None
    try:
        return int(str(val).strip())
    except (ValueError, TypeError):
        return None


def _bool(val) -> bool:
    if val is None:
        return False
    return str(val).strip().lower() in ("1", "true", "sí", "si", "yes")


def _parse_dt(val: str):
    if not val:
        return None
    val = val.strip()
    for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(val, fmt)
        except ValueError:
            continue
    return None
