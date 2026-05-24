from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
from app.database import get_db
from app.dependencies import get_current_user
from app import models, schemas
from app import minio_client

router = APIRouter(prefix="/api/fermentaciones", tags=["fermentaciones"])


@router.get("", response_model=list[schemas.DatasetAporteOut])
def listar_datasets(
    codigo: Optional[str] = Query(None),
    fecha_desde: Optional[datetime] = Query(None),
    fecha_hasta: Optional[datetime] = Query(None),
    db: Session = Depends(get_db),
    _: models.User = Depends(get_current_user),
):
    query = (
        db.query(models.Aporte)
        .join(models.Fermentacion)
        .options(
            joinedload(models.Aporte.fermentacion),
            joinedload(models.Aporte.metadatos),
        )

        .filter(
            models.Aporte.estado == models.EstadoAporteEnum.aprobado,
            models.Aporte.eliminado == False,
        )
    )

    if codigo:
        query = query.filter(models.Fermentacion.codigo.ilike(f"%{codigo}%"))
    if fecha_desde:
        query = query.filter(models.Aporte.fecha_subida >= fecha_desde)
    if fecha_hasta:
        query = query.filter(models.Aporte.fecha_subida <= fecha_hasta)


    aportes = query.order_by(models.Aporte.fecha_subida.desc()).all()

    result = []
    for aporte in aportes:
        imagenes = []
        for meta in aporte.metadatos:
            url = ""
            if aporte.ruta_minio:
                url = minio_client.presigned_url(f"{aporte.ruta_minio}/{meta.imagen}")
            meta_out = schemas.MetadatoImagenOut.model_validate(meta)
            meta_out.url_imagen = url
            imagenes.append(schemas.DatasetImagenOut(
                nombre=meta.imagen,
                url=url,
                metadatos=meta_out,
            ))

        result.append(schemas.DatasetAporteOut(
            id=aporte.id,
            fermentacion=schemas.FermentacionOut.model_validate(aporte.fermentacion),
            imagenes=imagenes,
            total_imagenes=len(imagenes),
        ))

    return result
