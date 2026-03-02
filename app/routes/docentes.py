from fastapi import APIRouter, HTTPException, status
from typing import List
from app.models.main import DocenteCreate, DocenteResponse
from app.services.db_service import get_db_service

router = APIRouter(prefix="/docentes", tags=["Docentes"])

@router.get("/", response_model=List[DocenteResponse])
async def listar_docentes():
    db_service = get_db_service()
    docentes = db_service.listar_todos_docentes()
    return docentes

@router.post("/", response_model=DocenteResponse, status_code=status.HTTP_201_CREATED)
async def crear_docente(docente: DocenteCreate):
    db_service = get_db_service()
    docente_id = db_service.crear_docente(
        nombre=docente.nombre,
        apellido=docente.apellido,
        email=docente.email,
        telefono=docente.telefono,
        especialidad=docente.especialidad
    )
    if not docente_id:
        raise HTTPException(status_code=400, detail="No se pudo crear el docente")
    
    # Retornamos el objeto creado (puedes hacer un fetch aquí si prefieres)
    return {**docente.model_dump(), "id": docente_id, "activo": True, "created_at": datetime.now()}