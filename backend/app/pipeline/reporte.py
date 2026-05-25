from dataclasses import dataclass, field


@dataclass
class ReporteDepuracion:
    fermentacion_id: str
    total_recibidas: int
    total_procesadas: int
    total_descartadas: int
    imagenes_descartadas: list = field(default_factory=list)
    rutas_raw: list = field(default_factory=list)
    rutas_processed: list = field(default_factory=list)
    csv_valido: bool = True
    no_conformidades_iso: list = field(default_factory=list)
    advertencias: list = field(default_factory=list)
