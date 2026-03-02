
DROP TABLE IF EXISTS conversaciones CASCADE;
DROP TABLE IF EXISTS seguimiento_academico CASCADE;
DROP TABLE IF EXISTS tutorias CASCADE;
DROP TABLE IF EXISTS asignaciones CASCADE;
DROP TABLE IF EXISTS materias CASCADE;
DROP TABLE IF EXISTS estudiantes CASCADE;
DROP TABLE IF EXISTS docentes CASCADE;

-- ============================================
-- TABLA: docentes
-- ============================================
CREATE TABLE docentes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    especialidad VARCHAR(100),
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: estudiantes
-- ============================================
CREATE TABLE estudiantes (
    id SERIAL PRIMARY KEY,
    codigo_estudiante VARCHAR(20) UNIQUE NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    telefono VARCHAR(20),
    programa VARCHAR(100),
    semestre INTEGER,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: materias
-- ============================================
CREATE TABLE materias (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    codigo VARCHAR(20) UNIQUE NOT NULL,
    creditos INTEGER,
    descripcion TEXT,
    activo BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: asignaciones (Docente-Materia)
-- ============================================
CREATE TABLE asignaciones (
    id SERIAL PRIMARY KEY,
    docente_id INTEGER REFERENCES docentes(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE CASCADE,
    estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE,
    periodo VARCHAR(20) NOT NULL, -- Ej: "2024-1"
    grupo VARCHAR(10),
    estado VARCHAR(20) DEFAULT 'activo', -- 'activo', 'completado', 'cancelado'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(docente_id, materia_id, estudiante_id, periodo)
);

-- ============================================
-- TABLA: tutorias
-- ============================================
CREATE TABLE tutorias (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE,
    docente_id INTEGER REFERENCES docentes(id) ON DELETE SET NULL,
    materia_id INTEGER REFERENCES materias(id) ON DELETE SET NULL,
    fecha_hora TIMESTAMP NOT NULL,
    duracion_minutos INTEGER DEFAULT 60,
    modalidad VARCHAR(20) DEFAULT 'presencial', -- 'presencial', 'virtual'
    estado VARCHAR(20) DEFAULT 'programada', -- 'programada', 'completada', 'cancelada'
    tema TEXT,
    observaciones TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: seguimiento_academico
-- ============================================
CREATE TABLE seguimiento_academico (
    id SERIAL PRIMARY KEY,
    estudiante_id INTEGER REFERENCES estudiantes(id) ON DELETE CASCADE,
    materia_id INTEGER REFERENCES materias(id) ON DELETE SET NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    nivel VARCHAR(20) DEFAULT 'medio', -- 'alto', 'medio', 'bajo'
    tipo_registro VARCHAR(50) NOT NULL, -- 'tutoria', 'evaluacion', 'observacion'
    descripcion TEXT NOT NULL,
    observaciones TEXT,
    recomendacion TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- TABLA: conversaciones (Historial IA)
-- ============================================
CREATE TABLE conversaciones (
    id SERIAL PRIMARY KEY,
    usuario_id INTEGER, -- ID del estudiante o docente
    tipo_usuario VARCHAR(20), -- 'estudiante', 'docente', 'admin'
    mensaje TEXT NOT NULL,
    respuesta TEXT NOT NULL,
    contexto JSONB, -- Datos usados para generar la respuesta
    intencion VARCHAR(50), -- Intención detectada
    funcion_ejecutada VARCHAR(100), -- Función de BD ejecutada
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- ÍNDICES PARA OPTIMIZACIÓN
-- ============================================

-- Índices para búsquedas frecuentes
CREATE INDEX idx_estudiantes_codigo ON estudiantes(codigo_estudiante);
CREATE INDEX idx_estudiantes_email ON estudiantes(email);
CREATE INDEX idx_docentes_email ON docentes(email);
CREATE INDEX idx_tutorias_estudiante ON tutorias(estudiante_id);
CREATE INDEX idx_tutorias_docente ON tutorias(docente_id);
CREATE INDEX idx_tutorias_fecha ON tutorias(fecha_hora);
CREATE INDEX idx_seguimiento_estudiante ON seguimiento_academico(estudiante_id);
CREATE INDEX idx_asignaciones_estudiante ON asignaciones(estudiante_id);
CREATE INDEX idx_conversaciones_usuario ON conversaciones(usuario_id, tipo_usuario);

-- Índice para búsqueda de texto completo en conversaciones
CREATE INDEX idx_conversaciones_mensaje ON conversaciones USING gin(to_tsvector('spanish', mensaje));

-- ============================================
-- DATOS DE EJEMPLO (SEED)
-- ============================================

-- Insertar docentes
INSERT INTO docentes (nombre, apellido, email, telefono, especialidad) VALUES
('Laura', 'Pérez', 'laura.perez@cul.edu.co', '3001234567', 'Programación'),
('Carlos', 'Mendoza', 'carlos.mendoza@cul.edu.co', '3007654321', 'Matemáticas'),
('Ana', 'Torres', 'ana.torres@cul.edu.co', '3009876543', 'Bases de Datos'),
('Jorge', 'Ramírez', 'jorge.ramirez@cul.edu.co', '3005551234', 'Redes');

-- Insertar materias
INSERT INTO materias (nombre, codigo, creditos, descripcion) VALUES
('Programación I', 'PROG101', 4, 'Introducción a la programación con Python'),
('Cálculo I', 'CALC101', 4, 'Fundamentos de cálculo diferencial'),
('Base de Datos', 'BD101', 3, 'Diseño y gestión de bases de datos relacionales'),
('Redes', 'RED101', 3, 'Fundamentos de redes de computadores'),
('Física I', 'FIS101', 4, 'Mecánica clásica y cinemática');

-- Insertar estudiantes
INSERT INTO estudiantes (codigo_estudiante, nombre, apellido, email, programa, semestre) VALUES
('EST001', 'Juan', 'García', 'juan.garcia@estudiantes.cul.edu.co', 'Ingeniería de Sistemas', 3),
('EST002', 'María', 'López', 'maria.lopez@estudiantes.cul.edu.co', 'Ingeniería de Sistemas', 2),
('EST003', 'Pedro', 'Martínez', 'pedro.martinez@estudiantes.cul.edu.co', 'Ingeniería Industrial', 4),
('EST004', 'Ana', 'Rodríguez', 'ana.rodriguez@estudiantes.cul.edu.co', 'Administración', 1),
('EST005', 'Luis', 'Fernández', 'luis.fernandez@estudiantes.cul.edu.co', 'Ingeniería de Sistemas', 3);

-- Insertar asignaciones (Estudiante-Docente-Materia)
INSERT INTO asignaciones (estudiante_id, docente_id, materia_id, periodo, grupo) VALUES
(1, 1, 1, '2024-2', 'A'), -- Juan con Laura en Programación I
(1, 2, 2, '2024-2', 'A'), -- Juan con Carlos en Cálculo I
(2, 1, 1, '2024-2', 'B'), -- María con Laura en Programación I
(3, 3, 3, '2024-2', 'A'), -- Pedro con Ana en Base de Datos
(5, 1, 1, '2024-2', 'A'); -- Luis con Laura en Programación I

-- Insertar tutorías de ejemplo
INSERT INTO tutorias (estudiante_id, docente_id, materia_id, fecha_hora, modalidad, estado, tema) VALUES
(1, 1, 1, '2024-03-05 10:00:00', 'virtual', 'programada', 'Estructuras de control'),
(2, 1, 1, '2024-03-06 14:00:00', 'presencial', 'completada', 'Funciones en Python'),
(5, 2, 2, '2024-03-07 09:00:00', 'virtual', 'programada', 'Derivadas');

-- Insertar seguimiento académico
INSERT INTO seguimiento_academico (estudiante_id, materia_id, nivel, tipo_registro, descripcion, recomendacion) VALUES
(1, 1, 'medio', 'tutoria', 'Progreso constante en programación', 'Continuar con ejercicios prácticos'),
(2, 1, 'alto', 'evaluacion', 'Excelente desempeño en el primer parcial', 'Mantener el ritmo de estudio'),
(5, 2, 'bajo', 'observacion', 'Dificultades con derivadas', 'Programar tutorías adicionales');

-- ============================================
-- FUNCIONES ÚTILES
-- ============================================

-- Función para obtener docentes por materia
CREATE OR REPLACE FUNCTION obtener_docentes_por_materia(p_materia_nombre VARCHAR)
RETURNS TABLE(docente_nombre VARCHAR, docente_email VARCHAR, materia VARCHAR) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.nombre || ' ' || d.apellido as docente_nombre,
        d.email as docente_email,
        m.nombre as materia
    FROM docentes d
    JOIN asignaciones a ON d.id = a.docente_id
    JOIN materias m ON a.materia_id = m.id
    WHERE LOWER(m.nombre) LIKE LOWER('%' || p_materia_nombre || '%')
    GROUP BY d.id, d.nombre, d.apellido, d.email, m.nombre
    ORDER BY d.apellido;
END;
$$ LANGUAGE plpgsql;

-- Función para obtener avance de estudiante
CREATE OR REPLACE FUNCTION obtener_avance_estudiante(p_codigo_estudiante VARCHAR, p_materia_nombre VARCHAR DEFAULT NULL)
RETURNS TABLE(
    materia VARCHAR,
    nivel VARCHAR,
    ultima_actualizacion TIMESTAMP,
    recomendacion TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        m.nombre as materia,
        s.nivel,
        s.fecha as ultima_actualizacion,
        s.recomendacion
    FROM seguimiento_academico s
    JOIN estudiantes e ON s.estudiante_id = e.id
    JOIN materias m ON s.materia_id = m.id
    WHERE e.codigo_estudiante = p_codigo_estudiante
    AND (p_materia_nombre IS NULL OR LOWER(m.nombre) LIKE LOWER('%' || p_materia_nombre || '%'))
    ORDER BY s.fecha DESC;
END;
$$ LANGUAGE plpgsql;

-- ============================================
-- VISTAS ÚTILES
-- ============================================

-- Vista: Resumen de estudiantes
CREATE OR REPLACE VIEW vista_estudiantes_resumen AS
SELECT 
    e.id,
    e.codigo_estudiante,
    e.nombre || ' ' || e.apellido as nombre_completo,
    e.programa,
    e.semestre,
    COUNT(DISTINCT a.materia_id) as total_materias,
    COUNT(DISTINCT t.id) as total_tutorias,
    AVG(CASE 
        WHEN s.nivel = 'alto' THEN 3
        WHEN s.nivel = 'medio' THEN 2
        WHEN s.nivel = 'bajo' THEN 1
        ELSE 2
    END) as nivel_promedio
FROM estudiantes e
LEFT JOIN asignaciones a ON e.id = a.estudiante_id
LEFT JOIN tutorias t ON e.id = t.estudiante_id
LEFT JOIN seguimiento_academico s ON e.id = s.estudiante_id
WHERE e.activo = TRUE
GROUP BY e.id, e.codigo_estudiante, e.nombre, e.apellido, e.programa, e.semestre;

-- Vista: Tutorías próximas
CREATE OR REPLACE VIEW vista_tutorias_proximas AS
SELECT 
    t.id,
    t.fecha_hora,
    e.codigo_estudiante,
    e.nombre || ' ' || e.apellido as estudiante_nombre,
    d.nombre || ' ' || d.apellido as docente_nombre,
    m.nombre as materia_nombre,
    t.modalidad,
    t.tema
FROM tutorias t
JOIN estudiantes e ON t.estudiante_id = e.id
LEFT JOIN docentes d ON t.docente_id = d.id
LEFT JOIN materias m ON t.materia_id = m.id
WHERE t.estado = 'programada'
AND t.fecha_hora >= CURRENT_TIMESTAMP
ORDER BY t.fecha_hora;

COMMIT;
