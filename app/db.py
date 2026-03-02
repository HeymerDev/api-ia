import psycopg
from psycopg.rows import dict_row
from contextlib import contextmanager
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class Database:
    """Clase para manejar la conexión a PostgreSQL usando DATABASE_URL"""
    
    def __init__(self, config):
        self.config = config
        self.database_url = config.DATABASE_URL
        self._connection = None
    
    def connect(self):
        """Crear conexión a la base de datos usando URL"""
        try:
            self._connection = psycopg.connect(
                self.database_url,
                row_factory=dict_row
            )
            logger.info("✅ Conexión a PostgreSQL establecida")
            return self._connection
        except Exception as e:
            logger.error(f"❌ Error al conectar a PostgreSQL: {e}")
            raise
    
    def disconnect(self):
        """Cerrar conexión"""
        if self._connection:
            self._connection.close()
            logger.info("🔌 Conexión a PostgreSQL cerrada")
    
    @contextmanager
    def get_cursor(self):
        """Context manager para obtener un cursor"""
        connection = self.connect()
        cursor = connection.cursor()
        try:
            yield cursor
            connection.commit()
        except Exception as e:
            connection.rollback()
            logger.error(f"Error en transacción: {e}")
            raise
        finally:
            cursor.close()
            connection.close()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Ejecutar una consulta SELECT y retornar resultados"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchall()
    
    def execute_one(self, query: str, params: tuple = None) -> Optional[Dict[str, Any]]:
        """Ejecutar consulta y retornar un solo resultado"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()
    
    def execute_insert(self, query: str, params: tuple = None) -> Optional[int]:
        """Ejecutar INSERT y retornar el ID insertado"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            result = cursor.fetchone()
            return result['id'] if result else None
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Ejecutar UPDATE/DELETE y retornar número de filas afectadas"""
        with self.get_cursor() as cursor:
            cursor.execute(query, params)
            return cursor.rowcount
    
    def test_connection(self) -> bool:
        """Probar conexión a la base de datos"""
        try:
            with self.get_cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                return result is not None
        except Exception as e:
            logger.error(f"Error en test de conexión: {e}")
            return False

# Instancia global
db = None

def init_db(config):
    """Inicializar la base de datos"""
    global db
    db = Database(config)
    return db

def get_db():
    """Obtener instancia de la base de datos"""
    if db is None:
        raise RuntimeError("Base de datos no inicializada")
    return db