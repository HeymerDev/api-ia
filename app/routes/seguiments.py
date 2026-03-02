from fastapi import APIRouter
from app.models.main import AsignacionCreate
from app.services.db_service import get_db_service

router = APIRouter(tags=["Materias"])

@router.get("/materias")
async def buscar_materias(q: str = None):
    db_service = get_db_service()
    return db_service.buscar_materias(q)

@router.post("/asignaciones")
async def asignar_materia(asignacion: AsignacionCreate):
    db_service = get_db_service()
    asig_id = db_service.crear_asignacion(**asignacion.model_dump())
    return {"message": "Asignación exitosa", "id": asig_id}