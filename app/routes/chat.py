from fastapi import APIRouter, HTTPException, status
from app.models.main import ChatRequest, ChatResponse
from app.services.ia_service import get_ia_service
from app.services.db_service import get_db_service
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    try:
        ia_service = get_ia_service()
        db_service = get_db_service()
        
        # 1. Detectar intención del usuario
        intencion = ia_service.detectar_intencion(request.mensaje)
        logger.info(f"Intención detectada: {intencion}")
        
        contexto = {}
        mensaje_lower = request.mensaje.lower()

        # ======================================================
        # PASO 2: EJECUCIÓN DE ACCIONES (Escritura en BD)
        # ======================================================
        if intencion == 'registrar_tutoria' and request.usuario_id:
            # Lógica simple de registro: En un caso real, usarías la IA para extraer 
            # la materia y fecha. Aquí registramos la intención en la tabla.
            # Suponemos IDs por defecto (1) si no se encuentran en el texto.
            try:
                # Intentar buscar si menciona alguna materia en el mensaje para el registro
                materias_db = db_service.buscar_materias()
                materia_id = 1 # Default
                for m in materias_db:
                    if m['nombre'].lower() in mensaje_lower:
                        materia_id = m['id']
                        break

                res_registro = db_service.registrar_tutoria(
                    estudiante_id=request.usuario_id,
                    docente_id=1, # Se podría dinamizar buscando al docente de la materia
                    materia_id=materia_id,
                    fecha_hora=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), # O extraer fecha del texto
                    tema=f"Tutoría solicitada vía Chat: {request.mensaje[:50]}..."
                )
                contexto['registro_nuevo'] = "Exitoso" if res_registro else "Fallido"
            except Exception as e:
                logger.error(f"Error registrando tutoría: {e}")

        # ======================================================
        # PASO 3: OBTENCIÓN DE CONTEXTO ACTUALIZADO (Lectura de BD)
        # ======================================================
        if request.incluir_contexto and request.usuario_id:
            
            # Caso A: Consultar Seguimiento Académico
            if intencion == 'consultar_avance':
                seguimiento = db_service.obtener_seguimiento_estudiante(request.usuario_id)
                contexto['seguimiento'] = seguimiento
                # También traemos datos básicos del estudiante para personalizar
                contexto['estudiante'] = db_service.obtener_estudiante_por_id(request.usuario_id)

            # Caso B: Consultar Tutorías (propias o generales)
            elif intencion in ['registrar_tutoria', 'consultar_avance', 'consulta_general']:
                # Traemos las tutorías programadas para que la IA las muestre
                tutorias = db_service.obtener_tutorias_estudiante(request.usuario_id)
                contexto['tutorias'] = tutorias

            # Caso C: Consultar Docentes
            elif intencion == 'consultar_docentes':
                materias = db_service.buscar_materias()
                for materia in materias:
                    if materia['nombre'].lower() in mensaje_lower:
                        docentes = db_service.obtener_docentes_por_materia(materia['nombre'])
                        contexto['docentes'] = docentes
                        contexto['materia_consultada'] = materia['nombre']
                        break

        # ======================================================
        # PASO 4: GENERACIÓN DE RESPUESTA CON IA
        # ======================================================
        # Le pasamos a tu modelo local el mensaje y el diccionario de contexto 
        # que acabamos de armar con datos reales de la BD.
        respuesta = ia_service.generar_respuesta(
            request.mensaje,
            contexto=contexto if contexto else None
        )
        
        # 5. Guardar la conversación en el historial de la BD
        if request.usuario_id:
            db_service.guardar_conversacion(
                usuario_id=request.usuario_id,
                tipo_usuario=request.tipo_usuario,
                mensaje=request.mensaje,
                respuesta=respuesta,
                contexto=contexto,
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
            detail=f"Error al procesar: {str(e)}"
        )