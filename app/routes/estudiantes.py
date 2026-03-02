from fastapi import APIRouter, HTTPException, status
from app.models.main import EstudianteCreate, EstudianteResponse
from app.services.ia_service import get_ia_service
from app.services.db_service import get_db_service
from typing import List
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/estudiantes", tags=["Estudiantes"])

@router.get("/buscar", response_model=List[dict])
async def buscar_estudiantes(termino: str):
    db_service = get_db_service()
    return db_service.buscar_estudiantes(termino)

@router.get("/{codigo}", response_model=EstudianteResponse)
async def obtener_estudiante(codigo: str):
    db_service = get_db_service()
    estudiante = db_service.obtener_estudiante_por_codigo(codigo)
    if not estudiante:
        raise HTTPException(status_code=404, detail="Estudiante no encontrado")
    return estudiante

@router.post("/", response_model=EstudianteResponse)
async def registrar_estudiante(estudiante: EstudianteCreate):
    db_service = get_db_service()
    nuevo_id = db_service.crear_estudiante(**estudiante.model_dump())
    if not nuevo_id:
         raise HTTPException(status_code=400, detail="Error al registrar estudiante")
    return {**estudiante.model_dump(), "id": nuevo_id, "created_at": datetime.now()}