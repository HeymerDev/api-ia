from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

class ChatRequest(BaseModel):
    """Request para el endpoint de chat"""
    mensaje: str = Field(..., min_length=1, max_length=1000)
    usuario_id: Optional[int] = None
    tipo_usuario: str = Field(default="estudiante")
    incluir_contexto: bool = Field(default=True)
    
    class Config:
        json_schema_extra = {
            "example": {
                "mensaje": "¿Qué profesores hay para Programación I?",
                "usuario_id": 1,
                "tipo_usuario": "estudiante"
            }
        }

class ChatResponse(BaseModel):
    """Response del endpoint de chat"""
    respuesta: str
    intencion: Optional[str] = None
    contexto_usado: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.now)

# ==========================================
# MODELOS DE DOCENTES
# ==========================================

class DocenteBase(BaseModel):
    """Modelo base de docente"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    especialidad: Optional[str] = Field(None, max_length=100)

class DocenteCreate(DocenteBase):
    """Request para crear docente"""
    pass

class DocenteResponse(DocenteBase):
    """Response de docente"""
    id: int
    activo: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS DE ESTUDIANTES
# ==========================================

class EstudianteBase(BaseModel):
    """Modelo base de estudiante"""
    codigo_estudiante: str = Field(..., min_length=3, max_length=20)
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    telefono: Optional[str] = Field(None, max_length=20)
    programa: Optional[str] = Field(None, max_length=100)
    semestre: Optional[int] = Field(None, ge=1, le=12)

class EstudianteCreate(EstudianteBase):
    """Request para crear estudiante"""
    pass

class EstudianteResponse(EstudianteBase):
    """Response de estudiante"""
    id: int
    activo: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS DE MATERIAS
# ==========================================

class MateriaBase(BaseModel):
    """Modelo base de materia"""
    nombre: str = Field(..., min_length=2, max_length=100)
    codigo: str = Field(..., min_length=2, max_length=20)
    creditos: Optional[int] = Field(None, ge=1, le=10)
    descripcion: Optional[str] = None

class MateriaCreate(MateriaBase):
    """Request para crear materia"""
    pass

class MateriaResponse(MateriaBase):
    """Response de materia"""
    id: int
    activo: bool = True
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS DE ASIGNACIONES
# ==========================================

class AsignacionCreate(BaseModel):
    """Request para crear asignación"""
    estudiante_id: int = Field(..., gt=0)
    docente_id: int = Field(..., gt=0)
    materia_id: int = Field(..., gt=0)
    periodo: str = Field(..., min_length=6, max_length=20)  # Ej: "2024-2"
    grupo: str = Field(default="A", max_length=10)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": 1,
                "docente_id": 1,
                "materia_id": 1,
                "periodo": "2024-2",
                "grupo": "A"
            }
        }

class AsignacionResponse(BaseModel):
    """Response de asignación"""
    id: int
    estudiante_id: int
    docente_id: int
    materia_id: int
    periodo: str
    grupo: str
    estado: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS DE TUTORÍAS
# ==========================================

class TutoriaCreate(BaseModel):
    """Request para crear tutoría"""
    estudiante_id: int = Field(..., gt=0)
    docente_id: int = Field(..., gt=0)
    materia_id: int = Field(..., gt=0)
    fecha_hora: datetime
    modalidad: str = Field(default="presencial", pattern="^(presencial|virtual)$")
    duracion_minutos: int = Field(default=60, gt=0, le=180)
    tema: Optional[str] = Field(None, max_length=200)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": 1,
                "docente_id": 1,
                "materia_id": 1,
                "fecha_hora": "2024-03-10T10:00:00",
                "modalidad": "virtual",
                "tema": "Estructuras de control"
            }
        }

class TutoriaResponse(BaseModel):
    """Response de tutoría"""
    id: int
    estudiante_id: int
    docente_id: Optional[int] = None
    materia_id: Optional[int] = None
    fecha_hora: datetime
    duracion_minutos: int
    modalidad: str
    estado: str
    tema: Optional[str] = None
    observaciones: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS DE SEGUIMIENTO ACADÉMICO
# ==========================================

class SeguimientoCreate(BaseModel):
    """Request para crear seguimiento"""
    estudiante_id: int = Field(..., gt=0)
    materia_id: int = Field(..., gt=0)
    nivel: str = Field(..., pattern="^(alto|medio|bajo)$")
    tipo_registro: str = Field(..., max_length=50)  # 'tutoria', 'evaluacion', 'observacion'
    descripcion: str = Field(..., min_length=10, max_length=1000)
    recomendacion: Optional[str] = Field(None, max_length=500)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estudiante_id": 1,
                "materia_id": 1,
                "nivel": "medio",
                "tipo_registro": "tutoria",
                "descripcion": "El estudiante muestra progreso constante",
                "recomendacion": "Continuar con práctica regular"
            }
        }

class SeguimientoResponse(BaseModel):
    """Response de seguimiento"""
    id: int
    estudiante_id: int
    materia_id: Optional[int] = None
    fecha: datetime
    nivel: str
    tipo_registro: str
    descripcion: str
    observaciones: Optional[str] = None
    recomendacion: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==========================================
# MODELOS GENERALES
# ==========================================

class MessageResponse(BaseModel):
    """Response genérico de mensaje"""
    message: str
    success: bool = True
    data: Optional[Any] = None

class ErrorResponse(BaseModel):
    """Response de error"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

class HealthResponse(BaseModel):
    """Response del health check"""
    status: str
    database: bool
    modelo_ia: bool
    timestamp: datetime = Field(default_factory=datetime.now)