from fastapi import APIRouter, HTTPException, status
from app.models.main import ChatRequest, ChatResponse
from app.services.ia_service import get_ia_service
from app.services.db_service import get_db_service
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        ia_service = get_ia_service()
        db_service = get_db_service()
        
        # Detectar intención
        intencion = ia_service.detectar_intencion(request.mensaje)
        logger.info(f"Intención detectada: {intencion}")
        
        # Obtener contexto de la BD según la intención
        contexto = {}
        
        if request.incluir_contexto:
            mensaje_lower = request.mensaje.lower()
            
            # Consultar docentes si menciona materias
            if intencion == 'consultar_docentes':
                materias = db_service.buscar_materias()
                for materia in materias:
                    if materia['nombre'].lower() in mensaje_lower:
                        docentes = db_service.obtener_docentes_por_materia(materia['nombre'])
                        contexto['docentes'] = docentes
                        contexto['materia'] = materia['nombre']
                        break
            
            # Consultar avance si hay usuario_id
            elif intencion == 'consultar_avance' and request.usuario_id:
                seguimiento = db_service.obtener_seguimiento_estudiante(request.usuario_id)
                contexto['seguimiento'] = seguimiento
                
                estudiante = db_service.obtener_estudiante_por_id(request.usuario_id)
                if estudiante:
                    contexto['estudiante'] = estudiante
            
            # Consultar tutorías
            elif intencion == 'registrar_tutoria' and request.usuario_id:
                tutorias = db_service.obtener_tutorias_estudiante(request.usuario_id)
                contexto['tutorias'] = tutorias
        
        # Generar respuesta con el modelo
        respuesta = ia_service.generar_respuesta(
            request.mensaje,
            contexto=contexto if contexto else None
        )
        
        # Guardar conversación en BD
        if request.usuario_id:
            db_service.guardar_conversacion(
                usuario_id=request.usuario_id,
                tipo_usuario=request.tipo_usuario,
                mensaje=request.mensaje,
                respuesta=respuesta,
                contexto=contexto if contexto else None,
                intencion=intencion
            )
        
        return ChatResponse(
            respuesta=respuesta,
            intencion=intencion,
            contexto_usado=contexto if contexto else None
        )
        
    except Exception as e:
        logger.error(f"Error en /chat: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al procesar mensaje: {str(e)}"
        )