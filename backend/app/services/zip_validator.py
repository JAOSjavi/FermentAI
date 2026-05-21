import zipfile
import re
import csv
import io
from dataclasses import dataclass
from typing import List, Tuple

FERM_CODE_RE = re.compile(r"^FERM\d{2,}$")
IMG_NAME_RE = re.compile(r"^FERM\d{2,}_\d{8}_\d{6}\.(jpg|jpeg)$", re.IGNORECASE)
MAX_IMAGE_BYTES = 20 * 1024 * 1024   # 20 MB
MAX_ZIP_BYTES = 2 * 1024 * 1024 * 1024  # 2 GB
REQUIRED_CSV_COLUMNS = {
    "imagen", "timestamp", "tiempo_horas",
    "glucosa_g_l", "fructosa_g_l", "sacarosa_g_l", "etanol_g_l",
    "acido_lactico_g_l", "acido_acetico_g_l", "acido_citrico_g_l",
    "acido_succinico_g_l", "acido_malico_g_l", "acido_oxalico_g_l",
    "acido_formico_g_l", "estado_fermentacion",
    "intervalo_incertidumbre_min", "validado_asesor", "observaciones",
}
VALID_ESTADOS = {"semi_fermentado", "fermentado", "sobre_fermentado"}


@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    ferm_code: str = ""
    image_keys: List[str] = None

    def __post_init__(self):
        if self.image_keys is None:
            self.image_keys = []


def validate_zip(zip_path: str, zip_size_bytes: int) -> ValidationResult:
    errors: List[str] = []

    # Regla 5: tamaño total del ZIP
    if zip_size_bytes > MAX_ZIP_BYTES:
        return ValidationResult(False, ["El ZIP supera el límite de 2 GB"])

    try:
        zf = zipfile.ZipFile(zip_path)
    except zipfile.BadZipFile:
        return ValidationResult(False, ["El archivo no es un ZIP válido"])

    names = zf.namelist()

    # Regla 1: estructura esperada FERM##/imagenes/ y FERM##/FERM##_metadata.csv
    ferm_codes = _extract_ferm_codes(names)
    if not ferm_codes:
        errors.append("No se encontró la estructura FERM##/imagenes/ en el ZIP")
        return ValidationResult(False, errors)
    if len(ferm_codes) > 1:
        errors.append(f"El ZIP contiene múltiples códigos de fermentación: {ferm_codes}")
        return ValidationResult(False, errors)

    ferm_code = ferm_codes.pop()
    expected_csv = f"{ferm_code}/{ferm_code}_metadata.csv"
    img_prefix = f"{ferm_code}/imagenes/"

    image_entries = [n for n in names if n.startswith(img_prefix) and not n.endswith("/")]
    csv_entries = [n for n in names if n == expected_csv]

    if not csv_entries:
        errors.append(f"No se encontró el CSV requerido: {expected_csv}")

    if not image_entries:
        errors.append(f"No se encontraron imágenes en {img_prefix}")

    if errors:
        return ValidationResult(False, errors, ferm_code)

    # Regla 2 & 3: nombre e formato imágenes
    for entry in image_entries:
        filename = entry.split("/")[-1]
        if not IMG_NAME_RE.match(filename):
            errors.append(f"Nombre de imagen inválido: {filename} (esperado FERM##_YYYYMMDD_HHMMSS.jpg)")
        if not filename.lower().endswith((".jpg", ".jpeg")):
            errors.append(f"Formato inválido: {filename} (solo .jpg/.jpeg)")

    # Regla 4: tamaño individual de imágenes
    for info in zf.infolist():
        if info.filename in image_entries and info.file_size > MAX_IMAGE_BYTES:
            errors.append(f"Imagen demasiado grande: {info.filename} ({info.file_size / 1024 / 1024:.1f} MB, máx 20 MB)")

    if errors:
        return ValidationResult(False, errors, ferm_code)

    # Regla 6: integridad del CSV (columnas requeridas)
    csv_data = zf.read(expected_csv).decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(csv_data))
    if reader.fieldnames is None:
        return ValidationResult(False, ["El CSV está vacío"], ferm_code)

    actual_cols = {c.strip().lower() for c in reader.fieldnames}
    missing_cols = REQUIRED_CSV_COLUMNS - actual_cols
    if missing_cols:
        errors.append(f"Columnas faltantes en CSV: {sorted(missing_cols)}")
        return ValidationResult(False, errors, ferm_code)

    # Regla 7: correspondencia imágenes ↔ CSV + Regla 8: valores válidos
    csv_rows = list(reader)
    csv_image_names = {row["imagen"].strip() for row in csv_rows}
    zip_image_names = {e.split("/")[-1] for e in image_entries}

    only_in_zip = zip_image_names - csv_image_names
    only_in_csv = csv_image_names - zip_image_names
    if only_in_zip:
        errors.append(f"Imágenes sin fila en CSV: {sorted(only_in_zip)}")
    if only_in_csv:
        errors.append(f"Filas en CSV sin imagen correspondiente: {sorted(only_in_csv)}")

    # Regla 8: valores válidos
    for i, row in enumerate(csv_rows, start=2):
        row_id = row.get("imagen", f"fila {i}")
        _validate_row(row, row_id, errors)

    if errors:
        return ValidationResult(False, errors, ferm_code)

    image_keys = [f"{ferm_code}/imagenes/{n}" for n in zip_image_names]
    return ValidationResult(True, [], ferm_code, image_keys)


def _extract_ferm_codes(names: List[str]) -> set:
    codes = set()
    for name in names:
        parts = name.split("/")
        if len(parts) >= 2 and FERM_CODE_RE.match(parts[0]):
            codes.add(parts[0])
    return codes


def _validate_row(row: dict, row_id: str, errors: List[str]):
    numeric_fields = [
        "tiempo_horas", "glucosa_g_l", "fructosa_g_l", "sacarosa_g_l",
        "etanol_g_l", "acido_lactico_g_l", "acido_acetico_g_l",
        "acido_citrico_g_l", "acido_succinico_g_l", "acido_malico_g_l",
        "acido_oxalico_g_l", "acido_formico_g_l",
    ]
    for field in numeric_fields:
        val = row.get(field, "").strip()
        if val:
            try:
                float(val)
            except ValueError:
                errors.append(f"[{row_id}] Campo '{field}' no es numérico: '{val}'")

    estado = row.get("estado_fermentacion", "").strip().lower()
    if estado and estado not in VALID_ESTADOS:
        errors.append(f"[{row_id}] estado_fermentacion inválido: '{estado}'")

    ts = row.get("timestamp", "").strip()
    if ts:
        from datetime import datetime
        parsed = False
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%SZ"):
            try:
                datetime.strptime(ts, fmt)
                parsed = True
                break
            except ValueError:
                continue
        if not parsed:
            errors.append(f"[{row_id}] timestamp no es ISO 8601: '{ts}'")
