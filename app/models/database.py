from PySide6.QtWidgets import QSizePolicy
import os
import sqlite3  # Añadir esta línea

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
        return cls._instance
    
    def connect(self):
        """Create a new connection each time - don't reuse connections"""
        try:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'database.db')
            # Asegurar que el directorio existe
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            # Habilitar claves foráneas
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            print(f"Error conectando a la base de datos: {e}")
            raise
    
    def close(self):
        """This method is no longer needed since we don't store connections"""
        pass
    
    def _create_tables(self):
        """Create database tables if they don't exist"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Tabla de Usuarios
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                usuario TEXT UNIQUE NOT NULL,
                contrasena TEXT NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('director', 'profesor', 'padre', 'estudiante'))
            )
            ''')
            
            # Tabla de Niveles Educativos
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS niveles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Tabla de Grados
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS grados (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                nivel_id INTEGER NOT NULL,
                FOREIGN KEY (nivel_id) REFERENCES niveles(id),
                UNIQUE(nombre, nivel_id)
            )
            ''')
            
            # Tabla de Secciones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS secciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                grado_id INTEGER NOT NULL,
                FOREIGN KEY (grado_id) REFERENCES grados(id),
                UNIQUE(nombre, grado_id)
            )
            ''')
            
            # Tabla de Estudiantes
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS estudiantes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                fecha_nacimiento TEXT NOT NULL,
                genero TEXT CHECK (genero IN ('M', 'F', 'Otro')),
                codigo TEXT UNIQUE,
                direccion TEXT,
                telefono TEXT,
                email TEXT,
                nivel_id INTEGER,
                grado_id INTEGER,
                seccion_id INTEGER,
                foto_path TEXT,
                facial_data_path TEXT,
                FOREIGN KEY (nivel_id) REFERENCES niveles(id),
                FOREIGN KEY (grado_id) REFERENCES grados(id),
                FOREIGN KEY (seccion_id) REFERENCES secciones(id)
            )
            ''')
            
            # Tabla de Asistencias
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS asistencias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                hora TEXT NOT NULL,
                estado TEXT CHECK (estado IN ('presente', 'ausente', 'tardanza')),
                emocion TEXT CHECK (emocion IN ('feliz', 'triste', 'enojado', 'neutral', 'desconocido')),
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
                UNIQUE(estudiante_id, fecha)
            )
            ''')
            
            # Tabla de Materias
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT UNIQUE NOT NULL
            )
            ''')
            
            # Tabla de Calificaciones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS calificaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                materia_id INTEGER NOT NULL,
                periodo TEXT NOT NULL CHECK (periodo IN ('1er bimestre', '2do bimestre', '3er bimestre', '4to bimestre', '1er trimestre', '2do trimestre', '3er trimestre')),
                nota REAL NOT NULL,
                comentario TEXT,
                fecha TEXT NOT NULL,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id),
                FOREIGN KEY (materia_id) REFERENCES materias(id),
                UNIQUE(estudiante_id, materia_id, periodo)
            )
            ''')
            
            # Tabla de Eventos
            cursor.execute('''
          CREATE TABLE IF NOT EXISTS eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    fecha_inicio TEXT NOT NULL,
    fecha_fin TEXT NOT NULL,
    lugar TEXT,
    creado_por INTEGER NOT NULL,
    FOREIGN KEY (creado_por) REFERENCES usuarios(id)
)
            ''')
            
            # Tabla de relación Eventos-Secciones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos_secciones (
                evento_id INTEGER NOT NULL,
                seccion_id INTEGER NOT NULL,
                PRIMARY KEY (evento_id, seccion_id),
                FOREIGN KEY (evento_id) REFERENCES eventos(id),
                FOREIGN KEY (seccion_id) REFERENCES secciones(id)
            )
            ''')
            
            # Tabla de Emociones
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS emociones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                emocion TEXT NOT NULL CHECK (emocion IN ('feliz', 'triste', 'enojado', 'neutral', 'sorprendido', 'miedo', 'disgusto')),
                confianza REAL DEFAULT 0.0,
                fecha_registro DATETIME DEFAULT CURRENT_TIMESTAMP,
                imagen_path TEXT,
                contexto TEXT,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes (id)
            )
            ''')
            
            # Tabla de Profesores
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS profesores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                email TEXT UNIQUE,
                telefono TEXT,
                especialidad TEXT,
                usuario_id INTEGER,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
            ''')
            
            # Tabla de Horarios
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS horarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dia_semana TEXT NOT NULL CHECK (dia_semana IN ('Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado')),
                hora_inicio TEXT NOT NULL,
                hora_fin TEXT NOT NULL,
                materia_id INTEGER NOT NULL,
                profesor_id INTEGER NOT NULL,
                seccion_id INTEGER NOT NULL,
                aula TEXT,
                activo BOOLEAN DEFAULT 1,
                FOREIGN KEY (materia_id) REFERENCES materias(id),
                FOREIGN KEY (profesor_id) REFERENCES profesores(id),
                FOREIGN KEY (seccion_id) REFERENCES secciones(id)
            )
            ''')
            
            # Tabla de Padres/Tutores
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS padres (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                estudiante_id INTEGER NOT NULL,
                nombre TEXT NOT NULL,
                telefono TEXT NOT NULL,
                email TEXT,
                es_principal BOOLEAN DEFAULT 1,
                FOREIGN KEY (estudiante_id) REFERENCES estudiantes(id)
            )
            ''')
            
            conn.commit()
            print("Tablas creadas correctamente")
            
        except Exception as e:
            print(f"Error creando tablas: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def setup(self):
        """Set up the database by creating tables and inserting initial data"""
        self._create_tables()
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            # Insertar datos iniciales
            self._insert_initial_data(cursor)
            
            conn.commit()
            print("Base de datos configurada correctamente")
            self.migrate_database()  # Ensure migrations run after setup
            
        except Exception as e:
            print(f"Error configurando la base de datos: {e}")
            if 'conn' in locals():
                conn.rollback()
            raise
        finally:
            if 'conn' in locals():
                conn.close()

    def _insert_initial_data(self, cursor):
        try:
            # Verificar si ya existen datos en la tabla usuarios
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            if cursor.fetchone()[0] == 0:
                # Insertar usuarios por defecto
                usuarios_default = [
                    ('Admin', 'Sistema', 'director', 'admin123', 'director'),
                    ('Juan', 'Pérez', 'profesor1', 'prof123', 'profesor'),
                    ('María', 'García', 'estudiante1', 'est123', 'estudiante'),
                    ('Carlos', 'López', 'padre1', 'padre123', 'padre')
                ]
                cursor.executemany('''
                INSERT INTO usuarios (nombre, apellido, usuario, contrasena, tipo)
                VALUES (?, ?, ?, ?, ?)
                ''', usuarios_default)
                print("Usuarios por defecto insertados")
            
            # Insertar niveles educativos
            cursor.execute("SELECT COUNT(*) FROM niveles")
            if cursor.fetchone()[0] == 0:
                niveles = [('Inicial',), ('Primaria',), ('Secundaria',)]
                cursor.executemany("INSERT INTO niveles (nombre) VALUES (?)", niveles)
                print("Niveles educativos insertados")
                
                # Obtener IDs de niveles
                cursor.execute("SELECT id FROM niveles WHERE nombre = 'Inicial'")
                nivel_inicial_id = cursor.fetchone()[0]
                cursor.execute("SELECT id FROM niveles WHERE nombre = 'Primaria'")
                nivel_primaria_id = cursor.fetchone()[0]
                cursor.execute("SELECT id FROM niveles WHERE nombre = 'Secundaria'")
                nivel_secundaria_id = cursor.fetchone()[0]
                
                # Insertar grados para Inicial
                grados_inicial = [
                    ('3 años', nivel_inicial_id),
                    ('4 años', nivel_inicial_id),
                    ('5 años', nivel_inicial_id)
                ]
                cursor.executemany("INSERT INTO grados (nombre, nivel_id) VALUES (?, ?)", grados_inicial)
                
                # Insertar grados para Primaria
                grados_primaria = [
                    ('1° grado', nivel_primaria_id),
                    ('2° grado', nivel_primaria_id),
                    ('3° grado', nivel_primaria_id),
                    ('4° grado', nivel_primaria_id),
                    ('5° grado', nivel_primaria_id),
                    ('6° grado', nivel_primaria_id)
                ]
                cursor.executemany("INSERT INTO grados (nombre, nivel_id) VALUES (?, ?)", grados_primaria)
                
                # Insertar grados para Secundaria
                grados_secundaria = [
                    ('1° año', nivel_secundaria_id),
                    ('2° año', nivel_secundaria_id),
                    ('3° año', nivel_secundaria_id),
                    ('4° año', nivel_secundaria_id),
                    ('5° año', nivel_secundaria_id)
                ]
                cursor.executemany("INSERT INTO grados (nombre, nivel_id) VALUES (?, ?)", grados_secundaria)
                
                print("Grados insertados")
                
                # Insertar secciones para cada grado
                cursor.execute("SELECT id FROM grados")
                grados = cursor.fetchall()
                
                for grado in grados:
                    grado_id = grado[0]
                    secciones = [
                        ('A', grado_id),
                        ('B', grado_id),
                        ('C', grado_id)
                    ]
                    cursor.executemany("INSERT INTO secciones (nombre, grado_id) VALUES (?, ?)", secciones)
                
                print("Secciones insertadas")
            
            # Insertar materias básicas
            cursor.execute("SELECT COUNT(*) FROM materias")
            if cursor.fetchone()[0] == 0:
                materias = [
                    ('Matemática',),
                    ('Comunicación',),
                    ('Ciencia y Tecnología',),
                    ('Personal Social',),
                    ('Arte',),
                    ('Educación Física',),
                    ('Inglés',),
                    ('Religión',),
                    ('Tutoría',)
                ]
                cursor.executemany("INSERT INTO materias (nombre) VALUES (?)", materias)
                print("Materias insertadas")
                
        except Exception as e:
            print(f"Error insertando datos iniciales: {e}")
            raise
    
    def get_niveles(self):
        """Obtener todos los niveles educativos"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM niveles ORDER BY nombre")
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo niveles: {e}")
            return []
    
    def get_grados_by_nivel(self, nivel_id):
        """Obtener grados por nivel"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM grados WHERE nivel_id = ? ORDER BY nombre", (nivel_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo grados: {e}")
            return []
    
    def get_secciones_by_grado(self, grado_id):
        """Obtener secciones por grado"""
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM secciones WHERE grado_id = ? ORDER BY nombre", (grado_id,))
            return cursor.fetchall()
        except Exception as e:
            print(f"Error obteniendo secciones: {e}")
            return []
    
    def migrate_database(self):
        """Check if the database needs migration and perform necessary updates"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check for nivel_id column in estudiantes table
        cursor.execute("PRAGMA table_info(estudiantes)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns if they don't exist
        if 'nivel_id' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN nivel_id INTEGER")
            print("Added nivel_id column to estudiantes table")
            
        if 'grado_id' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN grado_id INTEGER")
            print("Added grado_id column to estudiantes table")
            
        if 'seccion_id' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN seccion_id INTEGER")
            print("Added seccion_id column to estudiantes table")
            
        if 'codigo' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN codigo TEXT")
            print("Added codigo column to estudiantes table")
            
        if 'foto_path' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN foto_path TEXT")
            print("Added foto_path column to estudiantes table")
            
        if 'facial_data_path' not in columns:
            cursor.execute("ALTER TABLE estudiantes ADD COLUMN facial_data_path TEXT")
            print("Added facial_data_path column to estudiantes table")
        
        # Check for columns in eventos table
        cursor.execute("PRAGMA table_info(eventos)")
        eventos_columns = [column[1] for column in cursor.fetchall()]
        
        # Add missing columns to eventos table
        if 'fecha' not in eventos_columns:
            cursor.execute("ALTER TABLE eventos ADD COLUMN fecha TEXT")
            print("Added fecha column to eventos table")
            
        if 'hora' not in eventos_columns:
            cursor.execute("ALTER TABLE eventos ADD COLUMN hora TEXT")
            print("Added hora column to eventos table")
            
        if 'tipo' not in eventos_columns:
            cursor.execute("ALTER TABLE eventos ADD COLUMN tipo TEXT")
            print("Added tipo column to eventos table")
        
        conn.commit()
        conn.close()
        print("Database migration completed successfully")

    def get_connection(self):
        """Get a database connection"""
        try:
            db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data', 'database.db')
            # Ensure directory exists
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            # Enable foreign keys
            conn.execute("PRAGMA foreign_keys = ON")
            return conn
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def buscar_estudiante_por_codigo(self, codigo):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM estudiantes WHERE codigo = ?", (codigo,))
        return cursor.fetchone()
    
    def filtrar_estudiantes(self, nivel_id=None, grado_id=None, seccion_id=None):
        cursor = self.conn.cursor()
        query = "SELECT * FROM estudiantes WHERE 1=1"
        params = []
        
        if nivel_id:
            query += " AND nivel_id = ?"
            params.append(nivel_id)
        if grado_id:
            query += " AND grado_id = ?"
            params.append(grado_id)
        if seccion_id:
            query += " AND seccion_id = ?"
            params.append(seccion_id)
        
        cursor.execute(query, params)
        return cursor.fetchall()