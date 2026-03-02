# 🎓 API Asistente Académico CUL

API REST con FastAPI para el asistente virtual de la Corporación Universitaria Latinoamericana.

## 📋 Características

- ✅ Chat con IA usando modelo fine-tuned con LoRA
- ✅ Gestión de tutorías
- ✅ Seguimiento académico
- ✅ Consulta de docentes y materias
- ✅ Historial de conversaciones
- ✅ Base de datos PostgreSQL
- ✅ Documentación automática (Swagger)

---

## 🚀 Instalación

### 1. Requisitos Previos

- Python 3.10 o superior
- Cuenta en Neon PostgreSQL (https://neon.tech) o cualquier PostgreSQL
- Git

### 2. Clonar/Crear Proyecto

```bash
mkdir proyecto-cul-api
cd proyecto-cul-api
```

### 3. Crear Entorno Virtual

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 5. Configurar Base de Datos (Neon)

**Opción A: Usar Neon (Recomendado - Gratis)**

1. Crear cuenta en https://neon.tech
2. Crear nuevo proyecto
3. Copiar la connection string (DATABASE_URL)

**Opción B: PostgreSQL Local**

```bash
psql -U postgres -c "CREATE DATABASE cul_db;"
```

### 6. Ejecutar Schema

**Con psql:**

```bash
psql "tu_database_url_de_neon" -f schema_cul_completo.sql
```

**O desde SQL Editor de Neon:**

- Copia el contenido de `schema_cul_completo.sql`
- Pégalo en el SQL Editor
- Ejecuta

### 7. Configurar Variables de Entorno

Editar `.env` con tus valores:

```env
# Base de Datos (copiar de Neon)
DATABASE_URL=postgresql://usuario:password@ep-xxx.neon.tech/neondb?sslmode=require

# Rutas del Modelo (ajustar a tus rutas)
MODEL_BASE_PATH=C:/Users/Usuario/Desktop/Heymer/model_enfermeria_final
LORA_PATH=C:/Users/Usuario/Desktop/Heymer/modelo_cul_lora/modelo_cul_lora
```

**Nota:** Las rutas en Windows deben usar `/` (no `\`)

### 7. Verificar Estructura de Archivos

```
proyecto-cul-api/
├── app_main.py              # Archivo principal FastAPI
├── app_config.py            # Configuración
├── app_database.py          # Conexión a PostgreSQL
├── app_ia_service.py        # Servicio de IA
├── app_db_service.py        # Servicio de consultas BD
├── app_models.py            # Modelos Pydantic
├── requirements.txt         # Dependencias
├── .env                     # Variables de entorno
├── schema_cul_completo.sql  # Schema de BD
└── README.md                # Este archivo
```

---

## ▶️ Ejecución

### Modo Desarrollo

```bash
python app_main.py
```

O con uvicorn directamente:

```bash
uvicorn app_main:app --reload --host 0.0.0.0 --port 8000
```

La API estará disponible en: **http://localhost:8000**

### Documentación Interactiva

- Swagger UI: **http://localhost:8000/docs**
- ReDoc: **http://localhost:8000/redoc**

---

## 📡 Endpoints Disponibles

### Health Check

```http
GET /health
```

**Response:**

```json
{
  "status": "healthy",
  "database": true,
  "modelo_ia": true,
  "timestamp": "2024-03-02T10:30:00"
}
```

### Chat

```http
POST /chat
Content-Type: application/json

{
  "mensaje": "¿Qué profesores hay para Programación I?",
  "usuario_id": 1,
  "tipo_usuario": "estudiante",
  "incluir_contexto": true
}
```

**Response:**

```json
{
  "respuesta": "Para Programación I están disponibles: Laura Pérez, Carlos Mendoza, Ana Torres, Jorge Ramírez.",
  "intencion": "consultar_docentes",
  "contexto_usado": {
    "docentes": [...],
    "materia": "Programación I"
  },
  "timestamp": "2024-03-02T10:30:00"
}
```

### Docentes

```http
GET /docentes
GET /docentes?materia=Programación
```

### Estudiantes

```http
GET /estudiantes/{codigo}
```

### Materias

```http
GET /materias
GET /materias?buscar=Programación
```

### Tutorías

```http
POST /tutorias
Content-Type: application/json

{
  "estudiante_id": 1,
  "docente_id": 2,
  "materia_id": 1,
  "fecha_hora": "2024-03-10T10:00:00",
  "modalidad": "virtual",
  "tema": "Estructuras de control"
}
```

```http
GET /tutorias/estudiante/{estudiante_id}
GET /tutorias/estudiante/{estudiante_id}?proximas=false
```

### Seguimiento

```http
POST /seguimiento
Content-Type: application/json

{
  "estudiante_id": 1,
  "materia_id": 1,
  "nivel": "medio",
  "tipo_registro": "tutoria",
  "descripcion": "El estudiante muestra progreso constante",
  "recomendacion": "Continuar con práctica regular"
}
```

```http
GET /seguimiento/estudiante/{estudiante_id}
GET /seguimiento/estudiante/{estudiante_id}?materia_id=1
```

---

## 🧪 Pruebas con cURL

### Test de Health

```bash
curl http://localhost:8000/health
```

### Test de Chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "mensaje": "Hola",
    "usuario_id": 1,
    "tipo_usuario": "estudiante"
  }'
```

### Listar Docentes

```bash
curl http://localhost:8000/docentes
```

---

## 🐍 Cliente Python (Ejemplo)

```python
import requests

API_URL = "http://localhost:8000"

# Chat
response = requests.post(
    f"{API_URL}/chat",
    json={
        "mensaje": "¿Qué profesores hay para Programación I?",
        "usuario_id": 1,
        "tipo_usuario": "estudiante"
    }
)

print(response.json())

# Listar docentes
response = requests.get(f"{API_URL}/docentes")
docentes = response.json()

for docente in docentes:
    print(f"{docente['nombre']} {docente['apellido']} - {docente['especialidad']}")
```

---

## 🔧 Troubleshooting

### Error: No se puede conectar a PostgreSQL

```bash
# Verificar que PostgreSQL está corriendo
# Windows
net start postgresql-x64-14

# Linux
sudo systemctl status postgresql
sudo systemctl start postgresql
```

### Error: Modelo no se puede cargar

Verificar rutas en `.env`:

```env
MODEL_BASE_PATH=C:/ruta/correcta/modelo/base
LORA_PATH=C:/ruta/correcta/lora
```

Las rutas deben usar `/` (no `\`) incluso en Windows.

### Error: Port 8000 already in use

Cambiar puerto en `.env`:

```env
API_PORT=8001
```

---

## 📊 Logs

Los logs se guardan en: `logs/api.log`

Ver logs en tiempo real:

```bash
# Linux/Mac
tail -f logs/api.log

# Windows PowerShell
Get-Content logs/api.log -Wait
```

---

## 🚀 Despliegue en Producción

### Usando Gunicorn (Linux)

```bash
pip install gunicorn

gunicorn app_main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Usando Docker (Próximamente)

```bash
docker build -t api-cul .
docker run -p 8000:8000 api-cul
```

---

## 📚 Documentación Adicional

- **FastAPI**: https://fastapi.tiangolo.com/
- **PostgreSQL**: https://www.postgresql.org/docs/
- **Transformers**: https://huggingface.co/docs/transformers
- **PEFT (LoRA)**: https://huggingface.co/docs/peft

---

## 🤝 Contribuir

1. Fork el proyecto
2. Crea tu rama de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Abre un Pull Request

---

## 📝 Licencia

Este proyecto es privado de la Corporación Universitaria Latinoamericana (CUL).

---

## 👥 Contacto

- **Desarrollador**: Tu Nombre
- **Email**: tu.email@cul.edu.co
- **GitHub**: https://github.com/tu-usuario

---

¡Gracias por usar el Asistente Académico CUL! 🎓
