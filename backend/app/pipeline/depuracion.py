import csv
import io
import logging
import re
import zipfile

import cv2
import numpy as np
from PIL import Image

from app import minio_client
from .exceptions import PipelineError
from .reporte import ReporteDepuracion

logger = logging.getLogger("fermentai.pipeline")

FERM_CODE_RE = re.compile(r"^FERM(0[1-9]|1[0-2])$")
JPEG_MAGIC = bytes([0xFF, 0xD8, 0xFF])

_NUMERIC_COLS = [
    "tiempo_horas",
    "glucosa_g_l", "fructosa_g_l", "sacarosa_g_l", "etanol_g_l",
    "acido_lactico_g_l", "acido_acetico_g_l", "acido_citrico_g_l",
    "acido_succinico_g_l", "acido_malico_g_l", "acido_oxalico_g_l", "acido_formico_g_l",
]
_REQUIRED_COLS = frozenset(_NUMERIC_COLS + ["validado_asesor", "observaciones"])
_MAX_ROWS = 500
_TARGET_W, _TARGET_H = 1280, 720


def ejecutar_pipeline(zip_bytes: bytes, aporte_id: int) -> ReporteDepuracion:
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        raise PipelineError("El archivo no es un ZIP válido")

    names = zf.namelist()

    # Paso 1: validación estructural → extrae ferm_code
    ferm_code = _paso1_estructura(names)

    reporte = ReporteDepuracion(
        fermentacion_id=ferm_code,
        total_recibidas=0,
        total_procesadas=0,
        total_descartadas=0,
    )

    # Paso 0: validación del CSV
    csv_path = f"{ferm_code}/{ferm_code}_metadata.csv"
    _paso0_csv(zf.read(csv_path), reporte)

    # Recopilar imágenes del ZIP
    img_prefix = f"{ferm_code}/imagenes/"
    all_entries = [n for n in names if n.startswith(img_prefix) and not n.endswith("/")]

    # Descartar silenciosamente extensiones no soportadas
    jpeg_entries: list[tuple[str, bytes]] = []
    for entry in all_entries:
        fn = entry.split("/")[-1]
        if fn.lower().endswith((".jpg", ".jpeg")):
            jpeg_entries.append((fn, zf.read(entry)))
        else:
            ext = fn.rsplit(".", 1)[-1] if "." in fn else "sin extensión"
            reporte.advertencias.append(f"Ignorado (extensión .{ext} no soportada): {fn}")

    reporte.total_recibidas = len(jpeg_entries)
    logger.info("Aporte %d: %d imágenes JPEG encontradas", aporte_id, len(jpeg_entries))

    # Paso 2: magic bytes JPEG (FF D8 FF)
    valid_p2: list[tuple[str, bytes]] = []
    for fn, raw in jpeg_entries:
        if raw[:3] == JPEG_MAGIC:
            valid_p2.append((fn, raw))
        else:
            reporte.imagenes_descartadas.append(
                {"nombre": fn, "motivo": "cabecera JPEG inválida", "paso": 2}
            )

    n_total = len(jpeg_entries)
    n_invalid = n_total - len(valid_p2)
    if n_total and n_invalid > n_total * 0.5:
        raise PipelineError(
            f"Más del 50% de las imágenes ({n_invalid}/{n_total}) tienen cabecera JPEG inválida"
        )
    if not valid_p2:
        raise PipelineError("No quedan imágenes tras la validación de cabecera JPEG (paso 2)")

    # Paso 3: resolución mínima 1280×720
    valid_p3: list[tuple[str, bytes, Image.Image]] = []
    low_res_count = 0
    for fn, raw in valid_p2:
        try:
            img = Image.open(io.BytesIO(raw)).convert("RGB")
        except Exception as exc:
            reporte.imagenes_descartadas.append(
                {"nombre": fn, "motivo": f"imagen no legible: {exc}", "paso": 3}
            )
            continue
        w, h = img.size
        if w < _TARGET_W or h < _TARGET_H:
            reporte.imagenes_descartadas.append(
                {"nombre": fn, "motivo": f"resolución insuficiente ({w}x{h} real)", "paso": 3}
            )
            low_res_count += 1
        else:
            valid_p3.append((fn, raw, img))

    if low_res_count:
        reporte.advertencias.append(
            f"{low_res_count} imagen(es) descartada(s) por baja resolución — "
            "se recomienda usar cámara de mayor resolución"
        )
    if not valid_p3:
        raise PipelineError("No quedan imágenes tras la validación de resolución mínima (paso 3)")

    # Pasos 4 y 5 + subida a MinIO
    minio_client.ensure_bucket()
    uploaded_raw: list[str] = []
    uploaded_proc: list[str] = []

    try:
        for fn, raw_bytes, img in valid_p3:
            std = _paso4_resize(img)
            proc_bytes = _paso5_clahe(std)

            raw_key = f"raw/{aporte_id}/{fn}"
            proc_key = f"processed/{aporte_id}/{fn}"

            minio_client.upload_bytes(raw_bytes, raw_key)
            uploaded_raw.append(raw_key)

            minio_client.upload_bytes(proc_bytes, proc_key)
            uploaded_proc.append(proc_key)

    except Exception as exc:
        logger.error("Error en MinIO, iniciando rollback: %s", exc)
        for key in uploaded_raw + uploaded_proc:
            try:
                minio_client.delete_object(key)
            except Exception as rb_err:
                logger.warning("Rollback falló para %s: %s", key, rb_err)
        raise PipelineError(f"Error al subir imágenes a MinIO: {exc}")

    reporte.rutas_raw = uploaded_raw
    reporte.rutas_processed = uploaded_proc
    reporte.total_procesadas = len(uploaded_proc)
    reporte.total_descartadas = len(reporte.imagenes_descartadas)
    logger.info(
        "Aporte %d: pipeline OK — %d procesadas, %d descartadas",
        aporte_id, reporte.total_procesadas, reporte.total_descartadas,
    )
    return reporte


def _paso1_estructura(names: list[str]) -> str:
    ferm_codes: set[str] = set()
    for name in names:
        parts = name.split("/")
        if len(parts) >= 2 and FERM_CODE_RE.match(parts[0]):
            ferm_codes.add(parts[0])

    if not ferm_codes:
        raise PipelineError("No se encontró carpeta raíz FERM01–FERM12 en el ZIP")
    if len(ferm_codes) > 1:
        raise PipelineError(f"El ZIP contiene múltiples carpetas FERM##: {sorted(ferm_codes)}")

    ferm_code = next(iter(ferm_codes))
    img_prefix = f"{ferm_code}/imagenes/"
    csv_expected = f"{ferm_code}/{ferm_code}_metadata.csv"

    if not any(n.startswith(img_prefix) and not n.endswith("/") for n in names):
        raise PipelineError(f"La subcarpeta {img_prefix} no existe o está vacía")
    if csv_expected not in names:
        raise PipelineError(f"No se encontró el CSV requerido: {csv_expected}")

    return ferm_code


def _paso0_csv(csv_bytes: bytes, reporte: ReporteDepuracion) -> None:
    try:
        text = csv_bytes.decode("utf-8-sig")
    except UnicodeDecodeError:
        raise PipelineError("El CSV no está codificado en UTF-8")

    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames:
        raise PipelineError("El CSV no tiene cabecera")

    actual_cols = {c.strip().lower() for c in reader.fieldnames if c}
    missing = _REQUIRED_COLS - actual_cols
    extra = actual_cols - _REQUIRED_COLS

    if missing:
        raise PipelineError(f"Columnas faltantes en el CSV: {sorted(missing)}")
    if extra:
        raise PipelineError(f"Columnas no reconocidas en el CSV: {sorted(extra)}")

    rows = [
        {k.strip().lower(): v for k, v in row.items() if k}
        for row in reader
    ]

    if len(rows) < 1:
        raise PipelineError("El CSV debe tener al menos 1 fila de datos")
    if len(rows) > _MAX_ROWS:
        raise PipelineError(f"El CSV supera las {_MAX_ROWS} filas ({len(rows)} encontradas)")

    nc: list[str] = []
    prev_t: float | None = None

    for i, row in enumerate(rows, 1):
        # tiempo_horas: float >= 0, sin nulos, estrictamente creciente
        t_raw = row.get("tiempo_horas", "").strip()
        if not t_raw:
            nc.append(f"Fila {i}: tiempo_horas nulo")
        else:
            try:
                t = float(t_raw)
                if t < 0:
                    nc.append(f"Fila {i}: tiempo_horas={t} es negativo")
                elif prev_t is not None and t <= prev_t:
                    nc.append(
                        f"Fila {i}: tiempo_horas={t} no es estrictamente mayor que fila anterior ({prev_t})"
                    )
                prev_t = t
            except ValueError:
                nc.append(f"Fila {i}: tiempo_horas='{t_raw}' no es numérico")

        # glucosa…acido_formico: float >= 0, sin nulos
        for col in _NUMERIC_COLS[1:]:
            v = row.get(col, "").strip()
            if not v:
                nc.append(f"Fila {i}: {col} nulo")
            else:
                try:
                    fv = float(v)
                    if fv < 0:
                        nc.append(f"Fila {i}: {col}={fv} es negativo")
                except ValueError:
                    nc.append(f"Fila {i}: {col}='{v}' no es numérico")

        # validado_asesor: TRUE/FALSE case-insensitive, sin nulos
        va = row.get("validado_asesor", "").strip()
        if not va:
            nc.append(f"Fila {i}: validado_asesor nulo")
        elif va.upper() not in ("TRUE", "FALSE"):
            nc.append(f"Fila {i}: validado_asesor='{va}' no es TRUE/FALSE")

    reporte.no_conformidades_iso = nc
    reporte.csv_valido = not nc


def _paso4_resize(img: Image.Image) -> Image.Image:
    w, h = img.size
    if w == _TARGET_W and h == _TARGET_H:
        return img
    aspect = w / h
    target_aspect = _TARGET_W / _TARGET_H
    if abs(aspect - target_aspect) < 1e-3:
        return img.resize((_TARGET_W, _TARGET_H), Image.LANCZOS)
    # Cover-fit: escalar para que ambas dimensiones >= objetivo
    scale = max(_TARGET_W / w, _TARGET_H / h)
    new_w, new_h = round(w * scale), round(h * scale)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    # Recorte central a exactamente 1280×720
    left = (new_w - _TARGET_W) // 2
    top = (new_h - _TARGET_H) // 2
    return img.crop((left, top, left + _TARGET_W, top + _TARGET_H))


def _paso5_clahe(img: Image.Image) -> bytes:
    arr = np.array(img)
    lab = cv2.cvtColor(arr, cv2.COLOR_RGB2LAB)
    l, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_clahe = clahe.apply(l)
    lab_clahe = cv2.merge([l_clahe, a, b])
    rgb = cv2.cvtColor(lab_clahe, cv2.COLOR_LAB2RGB)
    buf = io.BytesIO()
    Image.fromarray(rgb).save(buf, format="JPEG", quality=95)
    return buf.getvalue()
