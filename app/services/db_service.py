from typing import List, Dict, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)

class DBService:
    """Servicio para consultas específicas a la BD"""
    
    def __init__(self, db):
        self.db = db

    def obtener_o_crear_estudiante_por_nombre(self, nombre: str):
    # 1. Buscar si ya existe
        query_busqueda = "SELECT id, nombre FROM estudiantes WHERE LOWER(nombre) = %s LIMIT 1"
        resultado = self.db.execute_query(query_busqueda, (nombre.lower(),))
    
        if resultado:
            return resultado[0]
    
    # 2. Si no existe, crearlo (usamos un código de estudiante genérico o nulo)
        query_insercion = """
            INSERT INTO estudiantes (nombre, codigo_estudiante, fecha_registro) 
            VALUES (%s, %s, CURRENT_TIMESTAMP) RETURNING id, nombre
        """
        codigo_temporal = f"CHAT-{datetime.now().strftime('%M%S')}"
        nuevo = self.db.execute_query(query_insercion, (nombre, codigo_temporal))
        return nuevo[0] if nuevo else None

    def obtener_o_crear_estudiante(self, nombre: str):
        query = "SELECT * FROM estudiantes WHERE LOWER(nombre) = %s LIMIT 1"
        estudiante = self.db.execute_query(query, (nombre.lower(),))
    
        if estudiante:
            return estudiante[0]
    
        insert_query = """
            INSERT INTO estudiantes (nombre, fuente_registro, fecha_creacion) 
            VALUES (%s, 'chat', CURRENT_TIMESTAMP) 
            RETURNING *
        """
        nuevo_estudiante = self.db.execute_query(insert_query, (nombre,))
        return nuevo_estudiante[0] if nuevo_estudiante else None
    
    def obtener_docentes_por_materia(self, nombre_materia: str) -> List[Dict[str, Any]]:
        """Obtener docentes que dictan una materia"""
        query = """
            SELECT DISTINCT
                d.id, d.nombre, d.apellido, d.email, d.especialidad,
                m.nombre as materia_nombre
            FROM docentes d
            JOIN asignaciones a ON d.id = a.docente_id
            JOIN materias m ON a.materia_id = m.id
            WHERE LOWER(m.nombre) LIKE LOWER(%s)
            AND d.activo = TRUE
            ORDER BY d.apellido
        """
        return self.db.execute_query(query, (f'%{nombre_materia}%',))
    
    def listar_todos_docentes(self) -> List[Dict[str, Any]]:
        """Listar todos los docentes activos"""
        query = """
            SELECT id, nombre, apellido, email, especialidad, created_at
            FROM docentes
            WHERE activo = TRUE
            ORDER BY apellido
        """
        return self.db.execute_query(query)
    
    def crear_docente(self, nombre: str, apellido: str, email: str, 
                     telefono: str = None, especialidad: str = None) -> Optional[int]:
        """Crear un nuevo docente"""
        query = """
            INSERT INTO docentes (nombre, apellido, email, telefono, especialidad)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """
        return self.db.execute_insert(query, (nombre, apellido, email, telefono, especialidad))
    
    # ==========================================
    # MATERIAS
    # ==========================================
    
    def buscar_materias(self, termino: str = None) -> List[Dict[str, Any]]:
        """Buscar materias por nombre o código"""
        if termino:
            query = """
                SELECT id, nombre, codigo, creditos, descripcion, created_at
                FROM materias
                WHERE (LOWER(nombre) LIKE LOWER(%s) OR LOWER(codigo) LIKE LOWER(%s))
                AND activo = TRUE
                ORDER BY nombre
            """
            return self.db.execute_query(query, (f'%{termino}%', f'%{termino}%'))
        else:
            query = """
                SELECT id, nombre, codigo, creditos, descripcion, created_at
                FROM materias
                WHERE activo = TRUE
                ORDER BY nombre
            """
            return self.db.execute_query(query)
    
    def crear_materia(self, nombre: str, codigo: str, creditos: int = None, 
                     descripcion: str = None) -> Optional[int]:
        """Crear una nueva materia"""
        query = """
            INSERT INTO materias (nombre, codigo, creditos, descripcion)
            VALUES (%s, %s, %s, %s)
            RETURNING id
        """
        return self.db.execute_insert(query, (nombre, codigo, creditos, descripcion))
    
    # ==========================================
    # ESTUDIANTES
    # ==========================================
    
    def obtener_estudiante_por_codigo(self, codigo: str) -> Optional[Dict[str, Any]]:
        """Obtener información de un estudiante por su código"""
        query = """
            SELECT id, codigo_estudiante, nombre, apellido, email, 
                   telefono, programa, semestre, created_at
            FROM estudiantes
            WHERE codigo_estudiante = %s
            AND activo = TRUE
        """
        return self.db.execute_one(query, (codigo,))
    
    def obtener_estudiante_por_id(self, estudiante_id: int) -> Optional[Dict[str, Any]]:
        """Obtener información de un estudiante por ID"""
        query = """
            SELECT id, codigo_estudiante, nombre, apellido, email, 
                   telefono, programa, semestre, created_at
            FROM estudiantes
            WHERE id = %s
            AND activo = TRUE
        """
        return self.db.execute_one(query, (estudiante_id,))
    
    def buscar_estudiantes(self, termino: str) -> List[Dict[str, Any]]:
        """Buscar estudiantes por nombre o código"""
        query = """
            SELECT id, codigo_estudiante, nombre, apellido, programa, semestre
            FROM estudiantes
            WHERE (LOWER(nombre) LIKE LOWER(%s) 
                   OR LOWER(apellido) LIKE LOWER(%s)
                   OR LOWER(codigo_estudiante) LIKE LOWER(%s))
            AND activo = TRUE
            ORDER BY apellido
            LIMIT 20
        """
        termino_like = f'%{termino}%'
        return self.db.execute_query(query, (termino_like, termino_like, termino_like))
    
    def crear_estudiante(self, codigo_estudiante: str, nombre: str, apellido: str,
                        email: str, telefono: str = None, programa: str = None,
                        semestre: int = None) -> Optional[int]:
        """Crear un nuevo estudiante"""
        query = """
            INSERT INTO estudiantes (codigo_estudiante, nombre, apellido, email, telefono, programa, semestre)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        return self.db.execute_insert(
            query, 
            (codigo_estudiante, nombre, apellido, email, telefono, programa, semestre)
        )
    
    # ==========================================
    # TUTORÍAS
    # ==========================================
    
    def registrar_tutoria(
        self,
        estudiante_id: int,
        docente_id: int,
        materia_id: int,
        fecha_hora: str,
        modalidad: str = 'presencial',
        duracion_minutos: int = 60,
        tema: str = None
    ) -> Optional[int]:
        """Registrar una nueva tutoría"""
        query = """
            INSERT INTO tutorias 
            (estudiante_id, docente_id, materia_id, fecha_hora, modalidad, duracion_minutos, tema, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'programada')
            RETURNING id
        """
        return self.db.execute_insert(
            query,
            (estudiante_id, docente_id, materia_id, fecha_hora, modalidad, duracion_minutos, tema)
        )
    
    def obtener_tutorias_estudiante(
        self,
        estudiante_id: int,
        solo_proximas: bool = True
    ) -> List[Dict[str, Any]]:
        """Obtener tutorías de un estudiante"""
        
        if solo_proximas:
            query = """
                SELECT 
                    t.id, t.estudiante_id, t.docente_id, t.materia_id,
                    t.fecha_hora, t.duracion_minutos, t.modalidad, t.tema, t.estado, t.created_at
                FROM tutorias t
                WHERE t.estudiante_id = %s
                AND t.fecha_hora >= CURRENT_TIMESTAMP
                AND t.estado = 'programada'
                ORDER BY t.fecha_hora
            """
        else:
            query = """
                SELECT 
                    t.id, t.estudiante_id, t.docente_id, t.materia_id,
                    t.fecha_hora, t.duracion_minutos, t.modalidad, t.tema, 
                    t.estado, t.observaciones, t.created_at
                FROM tutorias t
                WHERE t.estudiante_id = %s
                ORDER BY t.fecha_hora DESC
                LIMIT 50
            """
        
        return self.db.execute_query(query, (estudiante_id,))
    
    # ==========================================
    # SEGUIMIENTO ACADÉMICO
    # ==========================================
    
    def obtener_seguimiento_estudiante(
        self,
        estudiante_id: int,
        materia_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """Obtener seguimiento académico de un estudiante"""
        
        if materia_id:
            query = """
                SELECT 
                    s.id, s.estudiante_id, s.materia_id, s.fecha, s.nivel,
                    s.tipo_registro, s.descripcion, s.observaciones, s.recomendacion, s.created_at
                FROM seguimiento_academico s
                WHERE s.estudiante_id = %s
                AND s.materia_id = %s
                ORDER BY s.fecha DESC
                LIMIT 10
            """
            return self.db.execute_query(query, (estudiante_id, materia_id))
        else:
            query = """
                SELECT 
                    s.id, s.estudiante_id, s.materia_id, s.fecha, s.nivel,
                    s.tipo_registro, s.descripcion, s.observaciones, s.recomendacion, s.created_at
                FROM seguimiento_academico s
                WHERE s.estudiante_id = %s
                ORDER BY s.fecha DESC
                LIMIT 20
            """
            return self.db.execute_query(query, (estudiante_id,))
    
    def registrar_seguimiento(
        self,
        estudiante_id: int,
        materia_id: int,
        nivel: str,
        tipo_registro: str,
        descripcion: str,
        observaciones: str = None,
        recomendacion: str = None
    ) -> Optional[int]:
        """Registrar seguimiento académico"""
        query = """
            INSERT INTO seguimiento_academico 
            (estudiante_id, materia_id, nivel, tipo_registro, descripcion, observaciones, recomendacion)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        return self.db.execute_insert(
            query,
            (estudiante_id, materia_id, nivel, tipo_registro, descripcion, observaciones, recomendacion)
        )
    
    # ==========================================
    # ASIGNACIONES
    # ==========================================
    
    def crear_asignacion(
        self,
        estudiante_id: int,
        docente_id: int,
        materia_id: int,
        periodo: str,
        grupo: str = 'A'
    ) -> Optional[int]:
        """Crear asignación estudiante-docente-materia"""
        query = """
            INSERT INTO asignaciones (estudiante_id, docente_id, materia_id, periodo, grupo, estado)
            VALUES (%s, %s, %s, %s, %s, 'activo')
            ON CONFLICT (docente_id, materia_id, estudiante_id, periodo) 
            DO UPDATE SET updated_at = CURRENT_TIMESTAMP
            RETURNING id
        """
        return self.db.execute_insert(
            query,
            (estudiante_id, docente_id, materia_id, periodo, grupo)
        )
    
    def obtener_asignaciones_estudiante(self, estudiante_id: int) -> List[Dict[str, Any]]:
        """Obtener asignaciones de un estudiante"""
        query = """
            SELECT 
                a.id, a.estudiante_id, a.docente_id, a.materia_id,
                a.periodo, a.grupo, a.estado, a.created_at
            FROM asignaciones a
            WHERE a.estudiante_id = %s
            AND a.estado = 'activo'
            ORDER BY a.created_at DESC
        """
        return self.db.execute_query(query, (estudiante_id,))
    
    # ==========================================
    # CONVERSACIONES (Historial IA)
    # ==========================================
    
    def guardar_conversacion(
        self,
        usuario_id: int,
        tipo_usuario: str,
        mensaje: str,
        respuesta: str,
        contexto: Dict[str, Any] = None,
        intencion: str = None,
        funcion_ejecutada: str = None
    ) -> Optional[int]:
        """Guardar conversación en historial"""
        
        query = """
            INSERT INTO conversaciones 
            (usuario_id, tipo_usuario, mensaje, respuesta, contexto, intencion, funcion_ejecutada)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        """
        
        contexto_json = json.dumps(contexto) if contexto else None
        
        return self.db.execute_insert(
            query,
            (usuario_id, tipo_usuario, mensaje, respuesta, contexto_json, intencion, funcion_ejecutada)
        )
    
    def obtener_historial_conversaciones(
        self,
        usuario_id: int,
        tipo_usuario: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Obtener historial de conversaciones"""
        query = """
            SELECT id, mensaje, respuesta, intencion, timestamp
            FROM conversaciones
            WHERE usuario_id = %s
            AND tipo_usuario = %s
            ORDER BY timestamp DESC
            LIMIT %s
        """
        return self.db.execute_query(query, (usuario_id, tipo_usuario, limit))

# Instancia global
db_service = None

def init_db_service(db):
    """Inicializar servicio de BD"""
    global db_service
    db_service = DBService(db)
    return db_service

def get_db_service():
    """Obtener instancia del servicio de BD"""
    if db_service is None:
        raise RuntimeError("Servicio de BD no inicializado")
    return db_service