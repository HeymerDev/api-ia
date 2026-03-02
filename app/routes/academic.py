from fastapi import APIRouter, HTTPException, status
from app.models.main import TutoriaCreate, SeguimientoCreate
from app.services.ia_service import get_ia_service
from app.services.db_service import get_db_service


router = APIRouter(tags=["Académico"])

# --- TUTORÍAS ---
@router.post("/tutorias", status_code=201)
async def agendar_tutoria(tutoria: TutoriaCreate):
    db_service = get_db_service()
    tutoria_id = db_service.registrar_tutoria(**tutoria.model_dump())
    return {"message": "Tutoría agendada", "id": tutoria_id}

@router.get("/tutorias/estudiante/{id}")
async def ver_tutorias(id: int, proximas: bool = True):
    db_service = get_db_service()
    return db_service.obtener_tutorias_estudiante(id, solo_proximas=proximas)

# --- SEGUIMIENTO ---
@router.get("/seguimiento/{estudiante_id}")
async def ver_seguimiento(estudiante_id: int, materia_id: int = None):
    db_service = get_db_service()
    return db_service.obtener_seguimiento_estudiante(estudiante_id, materia_id)

@router.post("/seguimiento")
async def crear_seguimiento(data: SeguimientoCreate):
    db_service = get_db_service()
    res_id = db_service.registrar_seguimiento(**data.model_dump())
    return {"success": True, "id": res_id}