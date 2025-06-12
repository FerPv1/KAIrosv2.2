from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QLineEdit, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QFormLayout, QComboBox, QDateEdit, QFileDialog,
                             QGroupBox, QGridLayout)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QPixmap, QFont, QImage
import cv2
import os
from app.models.database import Database
# from app.utils.facial_recognition import FacialRecognition  # Temporarily commented out

class EstudiantesView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.facial_recognition = None  # Add this line
        self.current_student_id = None
        # Agregar variables para la cámara
        self.camera = None
        self.camera_timer = None
        self.is_camera_active = False
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Filtros y búsqueda
        filtros_layout = QHBoxLayout()
        
        # Campo de búsqueda por código
        self.buscar_input = QLineEdit()
        self.buscar_input.setPlaceholderText("Buscar por código...")
        self.buscar_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                min-width: 200px;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """)
        filtros_layout.addWidget(self.buscar_input)
        
        # Botón de búsqueda
        buscar_btn = QPushButton("🔍 Buscar")
        buscar_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 15px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        buscar_btn.clicked.connect(self.buscar_estudiante)
        filtros_layout.addWidget(buscar_btn)
        
        # Filtros
        filtros_layout.addWidget(QLabel("Nivel:"))
        self.nivel_filter = QComboBox()
        self.nivel_filter.currentTextChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.nivel_filter)
        
        filtros_layout.addWidget(QLabel("Grado:"))
        self.grado_filter = QComboBox()
        self.grado_filter.currentTextChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.grado_filter)
        
        filtros_layout.addWidget(QLabel("Sección:"))
        self.seccion_filter = QComboBox()
        self.seccion_filter.currentTextChanged.connect(self.on_filtro_changed)
        filtros_layout.addWidget(self.seccion_filter)
        
        filtros_layout.addStretch()
        main_layout.addLayout(filtros_layout)
        
        # Título principal
        title_layout = QHBoxLayout()
        
        back_btn = QPushButton("← Volver a la lista")
        back_btn.setStyleSheet("""
            QPushButton {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        title_layout.addWidget(back_btn)
        
        title_layout.addStretch()
        
        main_title = QLabel("Agregar Nuevo Estudiante")
        main_title.setFont(QFont("Arial", 18, QFont.Bold))
        main_title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(main_title)
        
        title_layout.addStretch()
        
        main_layout.addLayout(title_layout)
        
        # Contenido principal
        content_layout = QHBoxLayout()
        
        # Panel izquierdo: Foto
        left_panel = QVBoxLayout()
        
        # Foto del estudiante
        self.photo_label = QLabel()
        self.photo_label.setFixedSize(180, 180)
        self.photo_label.setStyleSheet("""
            QLabel {
                border: 3px dashed #4A90E2;
                border-radius: 90px;
                background-color: #f9f9f9;
            }
        """)
        self.photo_label.setAlignment(Qt.AlignCenter)
        
        # Icono de usuario por defecto
        default_pixmap = QPixmap(180, 180)
        default_pixmap.fill(Qt.lightGray)
        self.photo_label.setPixmap(default_pixmap)
        
        left_panel.addWidget(self.photo_label, alignment=Qt.AlignCenter)
        
        # Botón subir foto
        # Botón subir foto
        upload_btn = QPushButton("📷 Subir Foto")
        upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #4A90E2;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
        """)
        upload_btn.clicked.connect(self.upload_photo)
        left_panel.addWidget(upload_btn)
        
        # Botón tomar imagen
        take_photo_btn = QPushButton("📸 Tomar Imagen")
        take_photo_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px;
                font-size: 13px;
                font-weight: bold;
                margin-top: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        take_photo_btn.clicked.connect(self.take_photo_from_camera)
        left_panel.addWidget(take_photo_btn)
        
        # Código generado automáticamente (destacado)
        codigo_group = QGroupBox("Código de Estudiante")
        codigo_layout = QVBoxLayout()
        
        self.codigo_input = QLineEdit()
        self.codigo_input.setPlaceholderText("Se genera automáticamente")
        self.codigo_input.setReadOnly(True)
        self.codigo_input.setStyleSheet("""
            QLineEdit {
                background-color: #E8F4FD;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
                color: #2C5282;
            }
        """)
        codigo_layout.addWidget(self.codigo_input)
        
        codigo_info = QLabel("El código se genera automáticamente\nbasado en nivel, grado y sección")
        codigo_info.setStyleSheet("color: #666; font-size: 11px;")
        codigo_info.setAlignment(Qt.AlignCenter)
        codigo_layout.addWidget(codigo_info)
        
        codigo_group.setLayout(codigo_layout)
        left_panel.addWidget(codigo_group)
        
        left_panel.addStretch()
        
        content_layout.addLayout(left_panel)
        
        # Panel derecho: Formulario
        right_panel = QVBoxLayout()
        
        # NUEVA SECCIÓN: Información Académica
        academic_group = QGroupBox("📚 Información Académica")
        academic_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #4A90E2;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #4A90E2;
            }
        """)
        academic_layout = QGridLayout()
        
        # Nivel
        academic_layout.addWidget(QLabel("Nivel Educativo *"), 0, 0)
        self.nivel_combo = QComboBox()
        self.nivel_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #4A90E2;
            }
        """)
        self.nivel_combo.currentTextChanged.connect(self.on_nivel_changed)
        academic_layout.addWidget(self.nivel_combo, 0, 1)
        
        # Grado
        academic_layout.addWidget(QLabel("Grado *"), 0, 2)
        self.grado_combo = QComboBox()
        self.grado_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #4A90E2;
            }
        """)
        self.grado_combo.currentTextChanged.connect(self.on_grado_changed)
        academic_layout.addWidget(self.grado_combo, 0, 3)
        
        # Sección
        academic_layout.addWidget(QLabel("Sección *"), 1, 0)
        self.seccion_combo = QComboBox()
        self.seccion_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #4A90E2;
            }
        """)
        self.seccion_combo.currentTextChanged.connect(self.generate_email_and_code)
        academic_layout.addWidget(self.seccion_combo, 1, 1)
        
        academic_group.setLayout(academic_layout)
        right_panel.addWidget(academic_group)
        
        # Datos Personales
        personal_group = QGroupBox("👤 Datos Personales")
        personal_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #28a745;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #28a745;
            }
        """)
        personal_layout = QGridLayout()
        
        # Primera fila: Nombres
        personal_layout.addWidget(QLabel("Nombres *"), 0, 0)
        self.nombres_input = QLineEdit()
        self.nombres_input.setPlaceholderText("Nombres completos")
        self.nombres_input.textChanged.connect(self.generate_email_and_code)
        self.nombres_input.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.nombres_input, 0, 1)
        
        personal_layout.addWidget(QLabel("Primer Apellido *"), 0, 2)
        self.primer_apellido_input = QLineEdit()
        self.primer_apellido_input.setPlaceholderText("Primer apellido")
        self.primer_apellido_input.textChanged.connect(self.generate_email_and_code)
        self.primer_apellido_input.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.primer_apellido_input, 0, 3)
        
        # Segunda fila: Segundo apellido y género
        personal_layout.addWidget(QLabel("Segundo Apellido *"), 1, 0)
        self.segundo_apellido_input = QLineEdit()
        self.segundo_apellido_input.setPlaceholderText("Segundo apellido")
        self.segundo_apellido_input.textChanged.connect(self.generate_email_and_code)
        self.segundo_apellido_input.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.segundo_apellido_input, 1, 1)
        
        personal_layout.addWidget(QLabel("Género *"), 1, 2)
        self.genero_combo = QComboBox()
        self.genero_combo.addItems(["M", "F"])
        self.genero_combo.setStyleSheet(self.get_combo_style())
        personal_layout.addWidget(self.genero_combo, 1, 3)
        
        # Tercera fila: Fecha de nacimiento y email
        personal_layout.addWidget(QLabel("Fecha de Nacimiento *"), 2, 0)
        self.fecha_nacimiento = QDateEdit()
        self.fecha_nacimiento.setCalendarPopup(True)
        self.fecha_nacimiento.setDate(QDate.currentDate())
        self.fecha_nacimiento.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.fecha_nacimiento, 2, 1)
        
        personal_layout.addWidget(QLabel("Email (Generado) *"), 2, 2)
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Se genera automáticamente")
        self.email_input.setReadOnly(True)
        self.email_input.setStyleSheet("""
            QLineEdit {
                background-color: #f8f9fa;
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
                color: #495057;
            }
        """)
        personal_layout.addWidget(self.email_input, 2, 3)
        
        # Cuarta fila: Contacto
        personal_layout.addWidget(QLabel("Dirección"), 3, 0)
        self.direccion_input = QLineEdit()
        self.direccion_input.setPlaceholderText("Dirección completa")
        self.direccion_input.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.direccion_input, 3, 1, 1, 2)
        
        personal_layout.addWidget(QLabel("Teléfono"), 3, 3)
        self.telefono_input = QLineEdit()
        self.telefono_input.setPlaceholderText("Número de teléfono")
        self.telefono_input.setStyleSheet(self.get_input_style())
        personal_layout.addWidget(self.telefono_input, 3, 4)
        
        personal_group.setLayout(personal_layout)
        right_panel.addWidget(personal_group)
        
        # Datos del Padre/Madre/Tutor
        tutor_group = QGroupBox("👨‍👩‍👧‍👦 Datos del Padre/Madre/Tutor")
        tutor_group.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ffc107;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #ffc107;
            }
        """)
        tutor_layout = QGridLayout()
        
        tutor_layout.addWidget(QLabel("Nombre Completo *"), 0, 0)
        self.tutor_nombre_input = QLineEdit()
        self.tutor_nombre_input.setPlaceholderText("Nombre completo del tutor")
        self.tutor_nombre_input.setStyleSheet(self.get_input_style())
        tutor_layout.addWidget(self.tutor_nombre_input, 0, 1)
        
        tutor_layout.addWidget(QLabel("Teléfono *"), 0, 2)
        self.tutor_telefono_input = QLineEdit()
        self.tutor_telefono_input.setPlaceholderText("Teléfono del tutor")
        self.tutor_telefono_input.setStyleSheet(self.get_input_style())
        tutor_layout.addWidget(self.tutor_telefono_input, 0, 3)
        
        tutor_layout.addWidget(QLabel("Correo Electrónico"), 1, 0)
        self.tutor_email_input = QLineEdit()
        self.tutor_email_input.setPlaceholderText("Email del tutor")
        self.tutor_email_input.setStyleSheet(self.get_input_style())
        tutor_layout.addWidget(self.tutor_email_input, 1, 1, 1, 3)
        
        tutor_group.setLayout(tutor_layout)
        right_panel.addWidget(tutor_group)
        
        # Botón guardar
        save_btn = QPushButton("💾 Guardar Estudiante")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 20px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """)
        save_btn.clicked.connect(self.save_student)
        right_panel.addWidget(save_btn)
        
        content_layout.addLayout(right_panel, 2)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
        
        # Cargar datos iniciales
        self.load_niveles()
        
        # Generar código inicial
        self.generate_email_and_code()
    
    def get_input_style(self):
        return """
            QLineEdit {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QLineEdit:focus {
                border-color: #4A90E2;
            }
        """
    
    def get_combo_style(self):
        return """
            QComboBox {
                border: 2px solid #ddd;
                border-radius: 6px;
                padding: 8px;
                font-size: 13px;
            }
            QComboBox:focus {
                border-color: #4A90E2;
            }
        """
    
    def load_niveles(self):
        """Cargar niveles educativos"""
        try:
            db = Database()
            niveles = db.get_niveles()
            
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Seleccionar nivel", None)
            
            for nivel in niveles:
                self.nivel_combo.addItem(nivel[1], nivel[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar niveles: {str(e)}")
    
    def on_nivel_changed(self):
        """Cargar grados cuando se selecciona un nivel"""
        nivel_id = self.nivel_combo.currentData()
        if nivel_id:
            self.load_grados(nivel_id)
            self.generate_email_and_code()  # Regenerar código al cambiar nivel
        else:
            self.grado_combo.clear()
            self.seccion_combo.clear()
    
    def load_grados(self, nivel_id):
        """Cargar grados por nivel"""
        try:
            self.grado_combo.clear()
            self.seccion_combo.clear()
            
            if nivel_id is None:
                self.grado_combo.addItem("Seleccionar grado", None)
                return
            
            db = Database()
            grados = db.get_grados_by_nivel(nivel_id)
            
            self.grado_combo.addItem("Seleccionar grado", None)
            
            for grado in grados:
                self.grado_combo.addItem(grado[1], grado[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar grados: {str(e)}")
    
    def on_grado_changed(self):
        """Cargar secciones cuando se selecciona un grado"""
        grado_id = self.grado_combo.currentData()
        if grado_id:
            self.load_secciones(grado_id)
            self.generate_email_and_code()  # Regenerar código al cambiar grado
        else:
            self.seccion_combo.clear()
    
    def load_secciones(self, grado_id):
        """Cargar secciones por grado"""
        try:
            self.seccion_combo.clear()
            
            if grado_id is None:
                self.seccion_combo.addItem("Seleccionar sección", None)
                return
            
            db = Database()
            secciones = db.get_secciones_by_grado(grado_id)
            
            self.seccion_combo.addItem("Seleccionar sección", None)
            
            for seccion in secciones:
                self.seccion_combo.addItem(seccion[1], seccion[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar secciones: {str(e)}")
    
    def generate_email_and_code(self):
        """Generar automáticamente el email y código del estudiante"""
        nombres = self.nombres_input.text().strip()
        primer_apellido = self.primer_apellido_input.text().strip()
        segundo_apellido = self.segundo_apellido_input.text().strip()
        
        if nombres and primer_apellido and segundo_apellido:
            # Generar email: nombre+2primeras_primer_apellido+2primeras_segundo_apellido@kairos.pe
            nombre_clean = nombres.split()[0].lower() if nombres else ""
            primer_2 = primer_apellido[:2].lower() if len(primer_apellido) >= 2 else primer_apellido.lower()
            segundo_2 = segundo_apellido[:2].lower() if len(segundo_apellido) >= 2 else segundo_apellido.lower()
            
            email = f"{nombre_clean}{primer_2}{segundo_2}@kairos.pe"
            self.email_input.setText(email)
            
            # Generar código mejorado basado en nivel, grado y sección
            nivel_text = self.nivel_combo.currentText()
            grado_text = self.grado_combo.currentText()
            seccion_text = self.seccion_combo.currentText()
            
            if nivel_text and grado_text and seccion_text and nivel_text != "Seleccionar nivel" and grado_text != "Seleccionar grado" and seccion_text != "Seleccionar sección":
                # Prefijo por nivel
                if "Inicial" in nivel_text:
                    nivel_prefix = "I"
                elif "Primaria" in nivel_text:
                    nivel_prefix = "P"
                elif "Secundaria" in nivel_text:
                    nivel_prefix = "S"
                else:
                    nivel_prefix = "X"
                
                # Número de grado (extraer primer dígito)
                import re
                grado_num = re.findall(r'\d+', grado_text)
                grado_code = grado_num[0] if grado_num else "0"
                
                # Letra de sección
                seccion_code = seccion_text.upper()
                
                # Número correlativo (simulado con números aleatorios por ahora)
                import random
                correlativo = f"{random.randint(100, 999):03d}"
                
                # Formato: NIVEL + GRADO + SECCIÓN + CORRELATIVO
                # Ejemplo: P3A001, S1B045, I5C123
                codigo = f"{nivel_prefix}{grado_code}{seccion_code}{correlativo}"
                self.codigo_input.setText(codigo)
            else:
                self.codigo_input.setText("Seleccione nivel, grado y sección")
    
    def upload_photo(self):
        """Subir foto del estudiante"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Seleccionar Foto", "", 
            "Imágenes (*.png *.jpg *.jpeg *.bmp *.gif)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.photo_label.setPixmap(scaled_pixmap)
    
    def save_student(self):
        """Guardar estudiante"""
        """Guardar estudiante"""
        # Validaciones
        if not self.nombres_input.text().strip() or not self.primer_apellido_input.text().strip() or not self.segundo_apellido_input.text().strip():
            QMessageBox.warning(self, "Error", "Nombres y apellidos son obligatorios")
            return
        
        if not self.tutor_nombre_input.text().strip() or not self.tutor_telefono_input.text().strip():
            QMessageBox.warning(self, "Error", "Datos del tutor son obligatorios")
            return
        
        if self.nivel_combo.currentData() is None or self.grado_combo.currentData() is None or self.seccion_combo.currentData() is None:
            QMessageBox.warning(self, "Error", "Debe seleccionar nivel, grado y sección")
            return
        
        try:
            db = Database()
            conn = db.connect()
            
            with conn:  # Usar context manager
                cursor = conn.cursor()
                
                # Crear nuevo estudiante
                cursor.execute("""
                    INSERT INTO estudiantes 
                    (nombre, apellido, fecha_nacimiento, genero, 
                     direccion, telefono, email, codigo, seccion_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    f"{self.nombres_input.text().strip()} {self.primer_apellido_input.text().strip()}",
                    self.segundo_apellido_input.text().strip(),
                    self.fecha_nacimiento.date().toString("yyyy-MM-dd"),
                    self.genero_combo.currentText(),
                    self.direccion_input.text().strip(),
                    self.telefono_input.text().strip(),
                    self.email_input.text().strip(),
                    self.codigo_input.text().strip(),
                    self.seccion_combo.currentData()
                ))
                
                # Obtener el ID del estudiante recién creado
                estudiante_id = cursor.lastrowid
                
                # Guardar información del tutor
                cursor.execute("""
                    INSERT INTO padres 
                    (estudiante_id, nombre, telefono, email, es_principal)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    estudiante_id,
                    self.tutor_nombre_input.text().strip(),
                    self.tutor_telefono_input.text().strip(),
                    self.tutor_email_input.text().strip(),
                    1  # Es el tutor principal
                ))
                
                QMessageBox.information(self, "Éxito", "Estudiante y datos del tutor guardados correctamente")
                self.clear_form()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar estudiante: {str(e)}")
    
    def clear_form(self):
        """Limpiar formulario"""
        self.nombres_input.clear()
        self.primer_apellido_input.clear()
        self.segundo_apellido_input.clear()
        self.direccion_input.clear()
        self.telefono_input.clear()
        self.email_input.clear()
        self.codigo_input.clear()
        self.tutor_nombre_input.clear()
        self.tutor_telefono_input.clear()
        self.tutor_email_input.clear()
        self.fecha_nacimiento.setDate(QDate.currentDate())
        self.genero_combo.setCurrentIndex(0)
        
        # Resetear combos
        self.nivel_combo.setCurrentIndex(0)
        self.grado_combo.clear()
        self.seccion_combo.clear()
        
        # Resetear foto
        default_pixmap = QPixmap(180, 180)
        default_pixmap.fill(Qt.lightGray)
        self.photo_label.setPixmap(default_pixmap)
    
    def take_photo_from_camera(self):
        """Tomar foto desde la cámara"""
        try:
            # Inicializar la cámara
            cap = cv2.VideoCapture(0)
            
            if not cap.isOpened():
                QMessageBox.warning(self, "Error", "No se pudo acceder a la cámara")
                return
            
            # Capturar frame
            ret, frame = cap.read()
            
            if ret:
                # Voltear la imagen horizontalmente para efecto espejo
                frame = cv2.flip(frame, 1)
                
                # Convertir de BGR a RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Crear QPixmap desde el frame
                height, width, channel = rgb_frame.shape
                bytes_per_line = 3 * width
                q_image = QImage(rgb_frame.data, width, height, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_image)
                
                # Escalar y mostrar la imagen
                scaled_pixmap = pixmap.scaled(180, 180, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.photo_label.setPixmap(scaled_pixmap)
                
                # Guardar la imagen capturada
                self.save_captured_image(frame)
                
                QMessageBox.information(self, "Éxito", "Imagen capturada correctamente")
            else:
                QMessageBox.warning(self, "Error", "No se pudo capturar la imagen")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al acceder a la cámara: {str(e)}")
        finally:
            # Liberar la cámara
            if 'cap' in locals():
                cap.release()
    
    def save_captured_image(self, frame):
        """Guardar imagen capturada en el directorio de datos faciales"""
        try:
            # Crear directorio si no existe
            facial_data_dir = "data/facial_data"
            os.makedirs(facial_data_dir, exist_ok=True)
            
            # Generar nombre único para la imagen
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"student_capture_{timestamp}.jpg"
            filepath = os.path.join(facial_data_dir, filename)
            
            # Guardar la imagen
            cv2.imwrite(filepath, frame)
            
        except Exception as e:
            print(f"Error al guardar imagen: {str(e)}")
    
    def buscar_estudiante(self):
        codigo = self.buscar_input.text().strip()
        if codigo:
            try:
                db = Database()
                estudiante = db.buscar_estudiante_por_codigo(codigo)
                self.actualizar_tabla_estudiantes([estudiante] if estudiante else [])
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al buscar estudiante: {str(e)}")
    
    def on_filtro_changed(self):
        try:
            nivel_id = self.nivel_filter.currentData()
            grado_id = self.grado_filter.currentData()
            seccion_id = self.seccion_filter.currentData()
            
            db = Database()
            estudiantes = db.filtrar_estudiantes(nivel_id, grado_id, seccion_id)
            self.actualizar_tabla_estudiantes(estudiantes)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al filtrar estudiantes: {str(e)}")
    
    def actualizar_tabla_estudiantes(self, estudiantes):
        self.tabla_estudiantes.setRowCount(0)
        for estudiante in estudiantes:
            row = self.tabla_estudiantes.rowCount()
            self.tabla_estudiantes.insertRow(row)
            self.tabla_estudiantes.setItem(row, 0, QTableWidgetItem(estudiante[1]))  # Código
            self.tabla_estudiantes.setItem(row, 1, QTableWidgetItem(estudiante[2]))  # Nombre
            # ... agregar más columnas según tu estructura de datos ...

    def create_list_view(self):
        """Crear la vista de lista de estudiantes"""
        list_widget = QWidget()
        layout = QVBoxLayout(list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título y botones de acción
        header_layout = QHBoxLayout()
        
        title = QLabel("Lista de Estudiantes")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para agregar nuevo estudiante
        add_btn = QPushButton("Agregar Estudiante")
        add_btn.setIcon(QIcon(AppStyles.get_icon_path("add")))
        add_btn.setStyleSheet(AppStyles.get_button_style())
        add_btn.clicked.connect(self.show_form_view)
        header_layout.addWidget(add_btn)
        
        # Botón para exportar a PDF
        export_btn = QPushButton("Exportar a PDF")
        export_btn.setIcon(QIcon(AppStyles.get_icon_path("pdf")))
        export_btn.setStyleSheet(AppStyles.get_button_style())
        export_btn.clicked.connect(self.export_to_pdf)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Filtros de búsqueda
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_group.setStyleSheet(AppStyles.get_group_box_style())
        filter_layout = QHBoxLayout()
        
        # Búsqueda por texto
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.setStyleSheet(AppStyles.get_line_edit_style())
        self.search_input.textChanged.connect(self.filter_students)
        filter_layout.addWidget(self.search_input)
        
        # Filtro por nivel académico
        filter_layout.addWidget(QLabel("Nivel:"))
        self.nivel_combo = QComboBox()
        self.nivel_combo.addItem("Todos", None)
        self.nivel_combo.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.nivel_combo)
        
        # Filtro por grado
        filter_layout.addWidget(QLabel("Grado:"))
        self.grado_combo = QComboBox()
        self.grado_combo.addItem("Todos", None)
        self.grado_combo.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.grado_combo)
        
        # Filtro por sección
        filter_layout.addWidget(QLabel("Sección:"))
        self.seccion_combo = QComboBox()
        self.seccion_combo.addItem("Todas", None)
        self.seccion_combo.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.seccion_combo)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tabla de estudiantes
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels(["Código", "Nombre", "Nivel", "Grado", "Sección", "Email", "Acciones"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setStyleSheet("""QTableWidget {
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: white;
        }
        QTableWidget::item {
            padding: 5px;
        }
        QHeaderView::section {
            background-color: #f8f9fa;
            padding: 5px;
            border: 1px solid #ddd;
            font-weight: bold;
        }"""
        )
        layout.addWidget(self.students_table)
        
        return list_widget

def load_initial_data(self):
    """Cargar datos iniciales"""
    self.load_filter_options()
    self.load_students_list()

def load_filter_options(self):
    """Cargar opciones de filtro"""
    try:
        conn = self.db.connect()
        cursor = conn.cursor()
        
        # Cargar niveles
        cursor.execute("SELECT id, nombre FROM niveles ORDER BY id")
        niveles = cursor.fetchall()
        
        self.nivel_combo.clear()
        self.nivel_combo.addItem("Todos", None)
        for nivel in niveles:
            self.nivel_combo.addItem(nivel[1], nivel[0])
        
        conn.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", f"Error cargando opciones de filtro: {e}")

def on_nivel_changed(self, index):
    """Actualizar grados cuando cambia el nivel"""
    nivel_id = self.nivel_combo.currentData()
    
    try:
        conn = self.db.connect()
        cursor = conn.cursor()
        
        self.grado_combo.clear()
        self.grado_combo.addItem("Todos", None)
        
        if nivel_id:
            cursor.execute("SELECT id, nombre FROM grados WHERE nivel_id = ? ORDER BY nombre", (nivel_id,))
            grados = cursor.fetchall()
            
            for grado in grados:
                self.grado_combo.addItem(grado[1], grado[0])
        
        conn.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", f"Error cargando grados: {e}")

def on_grado_changed(self, index):
    """Actualizar secciones cuando cambia el grado"""
    grado_id = self.grado_combo.currentData()
    
    try:
        conn = self.db.connect()
        cursor = conn.cursor()
        
        self.seccion_combo.clear()
        self.seccion_combo.addItem("Todas", None)
        
        if grado_id:
            cursor.execute("SELECT id, nombre FROM secciones WHERE grado_id = ? ORDER BY nombre", (grado_id,))
            secciones = cursor.fetchall()
            
            for seccion in secciones:
                self.seccion_combo.addItem(seccion[1], seccion[0])
        
        conn.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", f"Error cargando secciones: {e}")

def load_students_list(self):
    """Cargar lista de estudiantes"""
    try:
        conn = self.db.connect()
        cursor = conn.cursor()
        
        query = """
            SELECT e.id, e.codigo, e.nombre, e.apellido, e.email,
                   n.nombre as nivel, g.nombre as grado, s.nombre as seccion
            FROM estudiantes e
            LEFT JOIN niveles n ON e.nivel_id = n.id
            LEFT JOIN grados g ON e.grado_id = g.id
            LEFT JOIN secciones s ON e.seccion_id = s.id
            ORDER BY e.apellido, e.nombre
        """
        
        cursor.execute(query)
        self.all_students = cursor.fetchall()
        
        self.display_students(self.all_students)
        
        conn.close()
    except Exception as e:
        QMessageBox.warning(self, "Error", f"Error cargando estudiantes: {e}")

def display_students(self, students):
    """Mostrar estudiantes en la tabla"""
    self.students_table.setRowCount(len(students))
    
    for row, student in enumerate(students):
        # Código
        self.students_table.setItem(row, 0, QTableWidgetItem(student[1] or "N/A"))
        # Nombre completo
        self.students_table.setItem(row, 1, QTableWidgetItem(f"{student[2]} {student[3]}"))
        # Nivel
        self.students_table.setItem(row, 2, QTableWidgetItem(student[5] or "N/A"))
        # Grado
        self.students_table.setItem(row, 3, QTableWidgetItem(student[6] or "N/A"))
        # Sección
        self.students_table.setItem(row, 4, QTableWidgetItem(student[7] or "N/A"))
        # Email
        self.students_table.setItem(row, 5, QTableWidgetItem(student[4] or "N/A"))
        
        # Botones de acción
        actions_widget = QWidget()
        actions_layout = QHBoxLayout(actions_widget)
        actions_layout.setContentsMargins(0, 0, 0, 0)
        
        # Botón Editar
        edit_btn = QPushButton("Editar")
        edit_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 3px;")
        edit_btn.clicked.connect(lambda checked, s=student[0]: self.edit_student(s))
        actions_layout.addWidget(edit_btn)
        
        # Botón Eliminar
        delete_btn = QPushButton("Eliminar")
        delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 3px;")
        delete_btn.clicked.connect(lambda checked, s=student[0]: self.delete_student(s))
        actions_layout.addWidget(delete_btn)
        
        self.students_table.setCellWidget(row, 6, actions_widget)
        
        # Guardar ID del estudiante en la primera columna
        self.students_table.item(row, 0).setData(Qt.UserRole, student[0])

def filter_students(self):
    """Filtrar estudiantes según criterios seleccionados"""
    search_text = self.search_input.text().lower()
    nivel_id = self.nivel_combo.currentData()
    grado_id = self.grado_combo.currentData()
    seccion_id = self.seccion_combo.currentData()
    
    filtered_students = []
    
    for student in self.all_students:
        # Filtrar por texto de búsqueda
        if search_text and search_text not in f"{student[1]} {student[2]} {student[3]}".lower():
            continue
        
        # Filtrar por nivel
        if nivel_id and student[8] != nivel_id:
            continue
        
        # Filtrar por grado
        if grado_id and student[9] != grado_id:
            continue
        
        # Filtrar por sección
        if seccion_id and student[10] != seccion_id:
            continue
        
        filtered_students.append(student)
    
    self.display_students(filtered_students)