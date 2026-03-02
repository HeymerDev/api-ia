from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

# 1. Imports de configuración y base de datos
from app.config import settings
from app.db import init_db

# 2. Imports de servicios
from app.services.db_service import init_db_service
from app.services.ia_service import init_ia_service

# 3. Imports de rutas
from app.routes import chat, docentes, estudiantes, academic, seguiments

# Configuración de logs
logging.basicConfig(level=settings.LOG_LEVEL)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Sistema de Gestión Académica con IA Local",
    version="1.0.0",
    debug=settings.DEBUG
)

# Configuración de CORS usando la lista de settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# INICIALIZACIÓN DE SERVICIOS (Ciclo de Vida)
# ==========================================
@app.on_event("startup")
async def startup_event():
    try:
        # PASO 1: Inicializar Base de Datos
        logger.info("🔗 Conectando a la base de datos...")
        db_instance = init_db(settings)
        init_db_service(db_instance)
        logger.info("✅ Base de datos inicializada")

        # PASO 2: Inicializar Servicio de IA (Carga de Modelo Local + LoRA)
        # Esto usará MODEL_BASE_PATH y LORA_PATH de tus settings
        logger.info(f"⏳ Cargando Modelo IA Local (esto puede tardar unos minutos)...")
        init_ia_service(settings) 
        logger.info("✅ Servicio de IA Local cargado correctamente")

    except Exception as e:
        logger.error(f"❌ Error crítico durante el inicio de los servicios: {e}")
        # En producción, podrías querer detener la app si la IA o DB fallan
        # import sys; sys.exit(1)

# ==========================================
# REGISTRO DE RUTAS (ROUTERS)
# ==========================================

# Ruta de Chat (IA)
app.include_router(chat.router, prefix="/api/chat", tags=["IA Chat"])

# Rutas de Entidades
app.include_router(docentes.router, prefix="/api", tags=["Docentes"])
app.include_router(estudiantes.router, prefix="/api", tags=["Estudiantes"])
app.include_router(seguiments.router, prefix="/api", tags=["Seguimiento"])
app.include_router(academic.router, prefix="/api", tags=["Académico"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "API CUL-IA operando correctamente",
        "model_loaded": settings.MODEL_BASE_PATH.split('/')[-1]
    }