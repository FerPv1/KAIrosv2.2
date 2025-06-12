# Add missing import at the top of the file
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QMessageBox,
                             QHeaderView, QDateEdit, QGroupBox, QLineEdit, QFrame, 
                             QTabWidget, QGridLayout, QSplitter, QTextEdit, QCalendarWidget,
                             QScrollArea, QProgressBar)
from PySide6.QtCore import Qt, QDate, QTimer, QDateTime, QThread, Signal
from PySide6.QtGui import QImage, QPixmap, QFont, QIcon, QColor
import cv2
import datetime
import numpy as np
import sqlite3
from app.models.database import Database
from app.utils.facial_recognition import FacialRecognition
from PySide6.QtWidgets import QDialog

class AsistenciaView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.verification_camera_active = False
        self.registration_camera_active = False
        self.verification_cap = None
        self.registration_cap = None
        self.verification_timer = QTimer()
        self.registration_timer = QTimer()
        self.verification_timer.timeout.connect(self.update_verification_camera)
        self.registration_timer.timeout.connect(self.update_registration_camera)
        
        # Inicializar reconocimiento facial
        self.facial_recognition = FacialRecognition()
        
        # Variables para verificación
        self.selected_student_id = None
        self.captured_verification_image = None
        
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Crear pestañas
        tab_widget = QTabWidget()
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #ecf0f1;
                border: 1px solid #bdc3c7;
                padding: 12px 24px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #3498db;
                color: white;
            }
        """)
        
        # Pestaña 1: Verificación de Identidad Facial
        verification_tab = self.create_verification_tab()
        tab_widget.addTab(verification_tab, "🔍 Verificación de Identidad Facial")
        
        # Pestaña 2: Registro Facial de Estudiantes
        registration_tab = self.create_registration_tab()
        tab_widget.addTab(registration_tab, "📝 Registro Facial de Estudiantes")
        
        # Pestaña 3: Gestión de Asistencia
        attendance_management_tab = self.create_attendance_management_tab()
        tab_widget.addTab(attendance_management_tab, "📊 Gestión de Asistencia")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
        
    def create_verification_tab(self):
        """Crear pestaña de verificación de identidad facial"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Título con icono
        title_layout = QHBoxLayout()
        title_icon = QLabel("👤")
        title_icon.setStyleSheet("font-size: 24px;")
        title_text = QLabel("Verificación de Identidad Facial")
        title_text.setFont(QFont("Arial", 18, QFont.Bold))
        title_text.setStyleSheet("color: #2c3e50;")
        title_layout.addWidget(title_icon)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        layout.addLayout(title_layout)
        
        # Sección de selección de estudiante
        student_selection_group = QGroupBox("1. Seleccionar Estudiante")
        student_selection_layout = QVBoxLayout()
        
        # ComboBox para seleccionar estudiante
        student_combo_layout = QHBoxLayout()
        student_combo_layout.addWidget(QLabel("Estudiante:"))
        
        self.student_verification_combo = QComboBox()
        self.student_verification_combo.setStyleSheet("""
            QComboBox {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
                min-width: 300px;
            }
            QComboBox:focus {
                border-color: #3498db;
            }
        """)
        self.student_verification_combo.currentTextChanged.connect(self.on_verification_student_selected)
        student_combo_layout.addWidget(self.student_verification_combo)
        student_combo_layout.addStretch()
        
        student_selection_layout.addLayout(student_combo_layout)
        
        # Información del estudiante seleccionado
        self.student_info_label = QLabel("Seleccione un estudiante para ver su información")
        self.student_info_label.setStyleSheet("""
            padding: 15px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            color: #6c757d;
        """)
        self.student_info_label.setWordWrap(True)
        student_selection_layout.addWidget(self.student_info_label)
        
        student_selection_group.setLayout(student_selection_layout)
        layout.addWidget(student_selection_group)
        
        # Sección de captura de imagen
        capture_group = QGroupBox("2. Capturar Imagen para Verificación")
        capture_layout = QHBoxLayout()
        
        # Lado izquierdo - Cámara
        left_layout = QVBoxLayout()
        camera_label = QLabel("Cámara en Vivo")
        camera_label.setFont(QFont("Arial", 12, QFont.Bold))
        camera_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        left_layout.addWidget(camera_label)
        
        # Área de la cámara
        self.verification_camera_label = QLabel()
        self.verification_camera_label.setFixedSize(350, 250)
        self.verification_camera_label.setStyleSheet("""
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #000000;
            color: white;
            font-size: 12px;
        """)
        self.verification_camera_label.setAlignment(Qt.AlignCenter)
        self.verification_camera_label.setText("Cámara desactivada\nHaz clic en 'Encender Cámara'")
        left_layout.addWidget(self.verification_camera_label)
        
        # Botones de cámara
        camera_buttons_layout = QHBoxLayout()
        
        # Botón encender/apagar cámara
        self.verification_camera_btn = QPushButton("📹 Encender Cámara")
        self.verification_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.verification_camera_btn.clicked.connect(self.toggle_verification_camera)
        camera_buttons_layout.addWidget(self.verification_camera_btn)
        
        # Botón capturar
        self.verification_capture_btn = QPushButton("📷 Capturar")
        self.verification_capture_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.verification_capture_btn.clicked.connect(self.capture_verification_image)
        self.verification_capture_btn.setEnabled(False)
        camera_buttons_layout.addWidget(self.verification_capture_btn)
        
        left_layout.addLayout(camera_buttons_layout)
        capture_layout.addLayout(left_layout)
        
        # Lado derecho - Imagen Capturada
        right_layout = QVBoxLayout()
        captured_label = QLabel("Imagen Capturada")
        captured_label.setFont(QFont("Arial", 12, QFont.Bold))
        captured_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        right_layout.addWidget(captured_label)
        
        # Área de imagen capturada
        self.verification_captured_label = QLabel()
        self.verification_captured_label.setFixedSize(350, 250)
        self.verification_captured_label.setStyleSheet("""
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #f8f9fa;
            color: #6c757d;
        """)
        self.verification_captured_label.setAlignment(Qt.AlignCenter)
        self.verification_captured_label.setText("No hay imagen capturada")
        right_layout.addWidget(self.verification_captured_label)
        
        capture_layout.addLayout(right_layout)
        capture_group.setLayout(capture_layout)
        layout.addWidget(capture_group)
        
        # Sección de verificación
        verification_group = QGroupBox("3. Verificar Identidad")
        verification_layout = QVBoxLayout()
        
        # Botón de verificación
        self.verify_identity_btn = QPushButton("🔍 Verificar Identidad")
        self.verify_identity_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 16px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.verify_identity_btn.clicked.connect(self.verify_student_identity)
        self.verify_identity_btn.setEnabled(False)
        verification_layout.addWidget(self.verify_identity_btn, alignment=Qt.AlignCenter)
        
        # Resultado de la verificación
        self.verification_result_label = QLabel("")
        self.verification_result_label.setStyleSheet("""
            padding: 15px;
            border-radius: 8px;
            font-size: 14px;
            font-weight: bold;
            text-align: center;
        """)
        self.verification_result_label.setAlignment(Qt.AlignCenter)
        self.verification_result_label.setWordWrap(True)
        verification_layout.addWidget(self.verification_result_label)
        
        verification_group.setLayout(verification_layout)
        layout.addWidget(verification_group)
        
        # Cargar estudiantes
        self.load_students_for_verification()
        
        widget.setLayout(layout)
        return widget

    def create_registration_tab(self):
        """Crear pestaña de registro automático de asistencia por reconocimiento facial"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Registro Automático de Asistencia por Reconocimiento Facial")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Instrucciones
        instruction = QLabel("Posiciónese frente a la cámara para que el sistema detecte automáticamente su identidad y registre su asistencia.")
        instruction.setAlignment(Qt.AlignCenter)
        instruction.setStyleSheet("""
            color: #2c3e50;
            font-size: 14px;
            padding: 15px;
            background-color: #e8f4fd;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #3498db;
        """)
        layout.addWidget(instruction)
        
        # Contenedor principal horizontal
        main_container = QHBoxLayout()
        
        # Panel izquierdo - Cámara
        camera_panel = QVBoxLayout()
        
        # Área de la cámara
        camera_frame = QFrame()
        camera_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        camera_layout = QVBoxLayout(camera_frame)
        
        self.auto_camera_label = QLabel()
        self.auto_camera_label.setFixedSize(480, 360)
        self.auto_camera_label.setStyleSheet("""
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: #000000;
            color: white;
            font-size: 14px;
        """)
        self.auto_camera_label.setAlignment(Qt.AlignCenter)
        self.auto_camera_label.setText("Cámara desactivada\nHaz clic en 'Iniciar Detección'")
        camera_layout.addWidget(self.auto_camera_label)
        
        # Botones de control de cámara
        camera_buttons = QHBoxLayout()
        
        self.auto_camera_btn = QPushButton("🎥 Iniciar Detección")
        self.auto_camera_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.auto_camera_btn.clicked.connect(self.toggle_auto_attendance_camera)
        camera_buttons.addWidget(self.auto_camera_btn)
        
        # Estado de detección
        self.detection_status = QLabel("⏸️ Detección detenida")
        self.detection_status.setStyleSheet("""
            padding: 10px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            font-weight: bold;
            color: #6c757d;
        """)
        camera_buttons.addWidget(self.detection_status)
        
        camera_layout.addLayout(camera_buttons)
        camera_panel.addWidget(camera_frame)
        
        # Panel derecho - Información y registros
        info_panel = QVBoxLayout()
        
        # Información del estudiante detectado
        detected_frame = QFrame()
        detected_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #27ae60;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        detected_layout = QVBoxLayout(detected_frame)
        
        detected_title = QLabel("👤 Estudiante Detectado")
        detected_title.setFont(QFont("Arial", 12, QFont.Bold))
        detected_title.setStyleSheet("color: #27ae60; margin-bottom: 10px;")
        detected_layout.addWidget(detected_title)
        
        self.detected_student_info = QLabel("Ningún estudiante detectado")
        self.detected_student_info.setStyleSheet("""
            padding: 15px;
            background-color: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            min-height: 100px;
        """)
        detected_layout.addWidget(self.detected_student_info)
        
        info_panel.addWidget(detected_frame)
        
        # Últimos registros de asistencia
        records_frame = QFrame()
        records_frame.setStyleSheet("""
            QFrame {
                border: 2px solid #3498db;
                border-radius: 10px;
                background-color: #f8f9fa;
            }
        """)
        records_layout = QVBoxLayout(records_frame)
        
        records_title = QLabel("📋 Últimos Registros de Asistencia")
        records_title.setFont(QFont("Arial", 12, QFont.Bold))
        records_title.setStyleSheet("color: #3498db; margin-bottom: 10px;")
        records_layout.addWidget(records_title)
        
        self.recent_attendance_table = QTableWidget()
        self.recent_attendance_table.setColumnCount(4)
        self.recent_attendance_table.setHorizontalHeaderLabels(["Hora", "Estudiante", "Estado", "Método"])
        self.recent_attendance_table.setMaximumHeight(200)
        self.recent_attendance_table.horizontalHeader().setStretchLastSection(True)
        records_layout.addWidget(self.recent_attendance_table)
        
        info_panel.addWidget(records_frame)
        
        # Agregar paneles al contenedor principal
        main_container.addLayout(camera_panel, 2)
        main_container.addLayout(info_panel, 1)
        
        layout.addLayout(main_container)
        
        widget.setLayout(layout)
        return widget
    
    def create_attendance_management_tab(self):
        """Crear pestaña de gestión de asistencia"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Título
        title = QLabel("Gestión de Asistencia")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Filtros
        filters_group = QGroupBox("Filtros")
        filters_layout = QHBoxLayout()
        
        # Búsqueda por código
        filters_layout.addWidget(QLabel("Código:"))
        self.search_code = QLineEdit()
        self.search_code.setPlaceholderText("Buscar por código...")
        self.search_code.textChanged.connect(self.filter_students)
        filters_layout.addWidget(self.search_code)
        
        # Filtro por nivel
        filters_layout.addWidget(QLabel("Nivel:"))
        self.level_combo = QComboBox()
        self.level_combo.addItem("Todos")
        self.level_combo.currentTextChanged.connect(self.filter_students)
        filters_layout.addWidget(self.level_combo)
        
        # Filtro por grado
        filters_layout.addWidget(QLabel("Grado:"))
        self.grade_combo = QComboBox()
        self.grade_combo.addItem("Todos")
        self.grade_combo.currentTextChanged.connect(self.filter_students)
        filters_layout.addWidget(self.grade_combo)
        
        # Filtro por sección
        filters_layout.addWidget(QLabel("Sección:"))
        self.section_combo = QComboBox()
        self.section_combo.addItem("Todos")
        self.section_combo.currentTextChanged.connect(self.filter_students)
        filters_layout.addWidget(self.section_combo)
        
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Tabla de estudiantes
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(6)
        self.students_table.setHorizontalHeaderLabels(["Código", "Nombre", "Nivel", "Grado", "Sección", "Estado"])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.cellClicked.connect(self.on_student_name_clicked)
        layout.addWidget(self.students_table)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        mark_present_btn = QPushButton("Marcar Todos Presentes")
        mark_present_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        mark_present_btn.clicked.connect(self.mark_all_present)
        buttons_layout.addWidget(mark_present_btn)
        
        mark_absent_btn = QPushButton("Marcar Todos Ausentes")
        mark_absent_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        mark_absent_btn.clicked.connect(self.mark_all_absent)
        buttons_layout.addWidget(mark_absent_btn)
        
        save_btn = QPushButton("Guardar Asistencia")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        save_btn.clicked.connect(self.save_attendance)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        
        # Cargar datos iniciales
        self.load_filter_data()
        self.load_students_data()
        
        widget.setLayout(layout)
        return widget
    
    def load_filter_data(self):
        """Cargar datos para los filtros"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Cargar niveles
            cursor.execute("SELECT nombre FROM niveles")
            niveles = cursor.fetchall()
            for nivel in niveles:
                self.level_combo.addItem(nivel[0])
            
            # Cargar grados
            cursor.execute("SELECT nombre FROM grados")
            grados = cursor.fetchall()
            for grado in grados:
                self.grade_combo.addItem(grado[0])
            
            # Cargar secciones
            cursor.execute("SELECT nombre FROM secciones")
            secciones = cursor.fetchall()
            for seccion in secciones:
                self.section_combo.addItem(seccion[0])
            
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar filtros: {str(e)}")
    
    def load_students_data(self):
        """Cargar datos de estudiantes con historial de asistencia"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Obtener fecha actual
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            
            query = """
                SELECT e.id, e.nombre, e.apellido, n.nombre as nivel, g.nombre as grado, s.nombre as seccion,
                       COALESCE(a.estado, 'ausente') as estado_hoy,
                       (
                           SELECT COUNT(*) FROM asistencias a2 
                           WHERE a2.estudiante_id = e.id AND a2.estado = 'presente'
                       ) as total_presentes,
                       (
                           SELECT COUNT(*) FROM asistencias a3 
                           WHERE a3.estudiante_id = e.id AND a3.estado = 'ausente'
                       ) as total_ausentes
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                LEFT JOIN asistencias a ON e.id = a.estudiante_id AND a.fecha = ?
                ORDER BY e.nombre, e.apellido
            """
            
            cursor.execute(query, (fecha_actual,))
            students = cursor.fetchall()
            
            # Expandir tabla para incluir columnas de historial
            self.students_table.setColumnCount(8)
            self.students_table.setHorizontalHeaderLabels([
                "Código", "Nombre", "Nivel", "Grado", "Sección", 
                "Estado Hoy", "Total Presentes", "Total Ausentes"
            ])
            
            self.students_table.setRowCount(len(students))
            
            for row, student in enumerate(students):
                self.students_table.setItem(row, 0, QTableWidgetItem(str(student[0])))
                self.students_table.setItem(row, 1, QTableWidgetItem(f"{student[1]} {student[2]}"))
                self.students_table.setItem(row, 2, QTableWidgetItem(student[3] or ""))
                self.students_table.setItem(row, 3, QTableWidgetItem(student[4] or ""))
                self.students_table.setItem(row, 4, QTableWidgetItem(student[5] or ""))
                
                # Estado de hoy con colores
                estado_item = QTableWidgetItem(student[6])
                if student[6] == "presente":
                    estado_item.setBackground(QColor(212, 237, 218))  # Verde claro
                    estado_item.setForeground(QColor(21, 87, 36))     # Verde oscuro
                else:
                    estado_item.setBackground(QColor(248, 215, 218))  # Rojo claro
                    estado_item.setForeground(QColor(114, 28, 36))    # Rojo oscuro
                self.students_table.setItem(row, 5, estado_item)
                
                self.students_table.setItem(row, 6, QTableWidgetItem(str(student[7])))
                self.students_table.setItem(row, 7, QTableWidgetItem(str(student[8])))
            
            # Ajustar ancho de columnas
            self.students_table.resizeColumnsToContents()
            
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar estudiantes: {str(e)}")
    
    def filter_students(self):
        """Filtrar estudiantes según los criterios seleccionados"""
        search_text = self.search_code.text().lower()
        selected_level = self.level_combo.currentText()
        selected_grade = self.grade_combo.currentText()
        selected_section = self.section_combo.currentText()
        
        for row in range(self.students_table.rowCount()):
            show_row = True
            
            # Filtro por código
            if search_text:
                codigo_item = self.students_table.item(row, 0)
                if codigo_item and search_text not in codigo_item.text().lower():
                    show_row = False
            
            # Filtro por nivel
            if selected_level != "Todos":
                nivel_item = self.students_table.item(row, 2)
                if not nivel_item or nivel_item.text() != selected_level:
                    show_row = False
            
            # Filtro por grado
            if selected_grade != "Todos":
                grado_item = self.students_table.item(row, 3)
                if not grado_item or grado_item.text() != selected_grade:
                    show_row = False
            
            # Filtro por sección
            if selected_section != "Todos":
                seccion_item = self.students_table.item(row, 4)
                if not seccion_item or seccion_item.text() != selected_section:
                    show_row = False
            
            self.students_table.setRowHidden(row, not show_row)
    
    def on_student_name_clicked(self, row, column):
        """Manejar clic en nombre de estudiante"""
        if column == 1:  # Columna de nombre
            codigo_item = self.students_table.item(row, 0)
            if codigo_item:
                self.show_student_details(codigo_item.text())
    
    def show_student_details(self, codigo):
        """Mostrar detalles del estudiante"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, nombre, apellido, fecha_nacimiento, genero, codigo, '', '', email, '', '', '', '', nivel_id, grado_id, seccion_id
                FROM estudiantes 
                WHERE codigo = ?
            """, (codigo,))
            
            student_data = cursor.fetchone()
            if student_data:
                details_window = StudentDetailsWindow(student_data, self)
                details_window.exec()
            
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar detalles del estudiante: {str(e)}")
    
    def mark_all_present(self):
        """Marcar todos los estudiantes como presentes"""
        for row in range(self.students_table.rowCount()):
            if not self.students_table.isRowHidden(row):
                self.students_table.setItem(row, 5, QTableWidgetItem("Presente"))
    
    def mark_all_absent(self):
        """Marcar todos los estudiantes como ausentes"""
        for row in range(self.students_table.rowCount()):
            if not self.students_table.isRowHidden(row):
                self.students_table.setItem(row, 5, QTableWidgetItem("Ausente"))
    
    def save_attendance(self):
        """Guardar la asistencia en la base de datos"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            
            for row in range(self.students_table.rowCount()):
                if not self.students_table.isRowHidden(row):
                    codigo_item = self.students_table.item(row, 0)
                    estado_item = self.students_table.item(row, 5)
                    
                    if codigo_item and estado_item:
                        codigo = codigo_item.text()
                        presente = 1 if estado_item.text() == "Presente" else 0
                        
                        # Verificar si ya existe un registro para hoy
                        cursor.execute("""
                            SELECT id FROM asistencias 
                            WHERE estudiante_codigo = ? AND fecha = ?
                        """, (codigo, fecha_actual))
                        
                        existing = cursor.fetchone()
                        
                        if existing:
                            # Actualizar registro existente
                            cursor.execute("""
                                UPDATE asistencias 
                                SET presente = ?, hora_registro = ?
                                WHERE estudiante_codigo = ? AND fecha = ?
                            """, (presente, datetime.datetime.now().strftime("%H:%M:%S"), codigo, fecha_actual))
                        else:
                            # Crear nuevo registro
                            cursor.execute("""
                                INSERT INTO asistencias (estudiante_codigo, fecha, presente, hora_registro)
                                VALUES (?, ?, ?, ?)
                            """, (codigo, fecha_actual, presente, datetime.datetime.now().strftime("%H:%M:%S")))
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Asistencia guardada correctamente")
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al guardar asistencia: {str(e)}")

    def update_verification_camera(self):
        """Update the verification camera display"""
        if self.verification_cap and self.verification_cap.isOpened():
            ret, frame = self.verification_cap.read()
            if ret:
                # Flip the frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale to fit the label while maintaining aspect ratio
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.verification_camera_label.size(), 
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.verification_camera_label.setPixmap(scaled_pixmap)
    
    def update_registration_camera(self):
        """Update the registration camera display"""
        if self.registration_cap and self.registration_cap.isOpened():
            ret, frame = self.registration_cap.read()
            if ret:
                # Flip the frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Convert to QImage
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                # Scale to fit the label while maintaining aspect ratio
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.registration_camera_label.size(), 
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.registration_camera_label.setPixmap(scaled_pixmap)
    
    def toggle_verification_camera(self):
        """Toggle the verification camera on/off"""
        if not self.verification_camera_active:
            # Turn on camera
            self.verification_cap = cv2.VideoCapture(0)
            if self.verification_cap.isOpened():
                self.verification_camera_active = True
                self.verification_timer.start(30)  # Update every 30ms
                self.verification_camera_btn.setText("Apagar Cámara")
                self.verification_camera_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                self.verification_capture_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "No se pudo acceder a la cámara")
        else:
            # Turn off camera
            self.verification_timer.stop()
            if self.verification_cap:
                self.verification_cap.release()
            self.verification_camera_active = False
            self.verification_camera_label.clear()
            self.verification_camera_label.setText("Cámara apagada")
            self.verification_camera_btn.setText("Encender Cámara")
            self.verification_camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.verification_capture_btn.setEnabled(False)
    
    def toggle_registration_camera(self):
        """Toggle the registration camera on/off"""
        if not self.registration_camera_active:
            # Turn on camera
            self.registration_cap = cv2.VideoCapture(0)
            if self.registration_cap.isOpened():
                self.registration_camera_active = True
                self.registration_timer.start(30)  # Update every 30ms
                self.registration_camera_btn.setText("Apagar Cámara")
                self.registration_camera_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 12px 24px;
                        border-radius: 6px;
                        font-weight: bold;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                self.registration_capture_btn.setEnabled(True)
            else:
                QMessageBox.warning(self, "Error", "No se pudo acceder a la cámara")
        else:
            # Turn off camera
            self.registration_timer.stop()
            if self.registration_cap:
                self.registration_cap.release()
            self.registration_camera_active = False
            self.registration_camera_label.clear()
            self.registration_camera_label.setText("Cámara apagada")
            self.registration_camera_btn.setText("Encender Cámara")
            self.registration_camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 6px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.registration_capture_btn.setEnabled(False)
    
    def load_students_for_verification(self):
        """Cargar lista de estudiantes que tienen datos faciales registrados"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Obtener estudiantes que tienen datos faciales registrados
            query = """
                SELECT e.id, e.nombre, e.apellido, n.nombre as nivel, g.nombre as grado, s.nombre as seccion
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                WHERE e.facial_data_path IS NOT NULL AND e.facial_data_path != ''
                ORDER BY e.nombre, e.apellido
            """
            
            cursor.execute(query)
            students = cursor.fetchall()
            
            self.student_verification_combo.clear()
            self.student_verification_combo.addItem("Seleccionar estudiante...", None)
            
            for student in students:
                display_text = f"{student[1]} {student[2]}"
                if student[3] or student[4] or student[5]:
                    details = []
                    if student[3]: details.append(student[3])
                    if student[4]: details.append(student[4])
                    if student[5]: details.append(student[5])
                    display_text += f" - {' '.join(details)}"
                
                self.student_verification_combo.addItem(display_text, student[0])
            
            conn.close()
            
            if self.student_verification_combo.count() == 1:  # Solo tiene "Seleccionar estudiante..."
                self.student_info_label.setText("⚠️ No hay estudiantes con datos faciales registrados. Primero registre rostros en la pestaña 'Registro Facial de Estudiantes'.")
                self.student_info_label.setStyleSheet("""
                    padding: 15px;
                    background-color: #fff3cd;
                    border: 1px solid #ffeaa7;
                    border-radius: 5px;
                    color: #856404;
                """)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar estudiantes: {str(e)}")
    
    def on_verification_student_selected(self):
        """Manejar selección de estudiante para verificación"""
        current_data = self.student_verification_combo.currentData()
        if current_data:
            self.selected_student_id = current_data
            self.load_student_verification_info(current_data)
            self.update_verification_button_state()
        else:
            self.selected_student_id = None
            self.student_info_label.setText("Seleccione un estudiante para ver su información")
            self.student_info_label.setStyleSheet("""
                padding: 15px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                color: #6c757d;
            """)
            self.update_verification_button_state()
    
    def load_student_verification_info(self, student_id):
        """Cargar información del estudiante seleccionado para verificación"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.nombre, e.apellido, e.codigo, n.nombre as nivel, g.nombre as grado, s.nombre as seccion,
                       e.facial_data_path
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                WHERE e.id = ?
            """, (student_id,))
            
            student = cursor.fetchone()
            if student:
                info_html = f"""
                <div style='color: #2c3e50;'>
                    <h3 style='margin: 0; color: #27ae60;'>✅ Estudiante Seleccionado</h3>
                    <p><b>Nombre:</b> {student[0]} {student[1]}</p>
                    <p><b>Código:</b> {student[2] or 'No asignado'}</p>
                    <p><b>Nivel:</b> {student[3] or 'No asignado'}</p>
                    <p><b>Grado:</b> {student[4] or 'No asignado'}</p>
                    <p><b>Sección:</b> {student[5] or 'No asignado'}</p>
                    <p><b>Estado:</b> <span style='color: #27ae60;'>Datos faciales registrados ✓</span></p>
                </div>
                """
                self.student_info_label.setText(info_html)
                self.student_info_label.setStyleSheet("""
                    padding: 15px;
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                """)
            
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar información del estudiante: {str(e)}")
    
    def update_verification_button_state(self):
        """Actualizar estado del botón de verificación"""
        can_verify = (self.selected_student_id is not None and 
                     self.captured_verification_image is not None)
        self.verify_identity_btn.setEnabled(can_verify)
    
    def capture_verification_image(self):
        """Capturar imagen para verificación"""
        if self.verification_cap and self.verification_cap.isOpened():
            ret, frame = self.verification_cap.read()
            if ret:
                self.captured_verification_image = frame.copy()
                
                # Mostrar imagen capturada
                rgb_image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_image.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_image.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.verification_captured_label.size(), 
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.verification_captured_label.setPixmap(scaled_pixmap)
                
                self.update_verification_button_state()
                
                QMessageBox.information(self, "Éxito", "Imagen capturada correctamente")
    
    def verify_student_identity(self):
        """Verificar identidad del estudiante seleccionado"""
        if not self.selected_student_id or not self.captured_verification_image:
            QMessageBox.warning(self, "Error", "Debe seleccionar un estudiante y capturar una imagen")
            return
        
        try:
            # Usar el sistema de reconocimiento facial para verificar
            recognized_id, confidence_message = self.facial_recognition.recognize_face(self.captured_verification_image)
            
            if recognized_id and str(recognized_id) == str(self.selected_student_id):
                # Identidad verificada correctamente
                self.verification_result_label.setText(
                    f"✅ IDENTIDAD VERIFICADA\n\nEl rostro capturado coincide con el estudiante seleccionado.\n{confidence_message}"
                )
                self.verification_result_label.setStyleSheet("""
                    padding: 20px;
                    background-color: #d4edda;
                    border: 2px solid #27ae60;
                    border-radius: 8px;
                    color: #155724;
                    font-size: 16px;
                    font-weight: bold;
                """)
                
                # Registrar verificación exitosa en la base de datos
                self.log_verification_attempt(self.selected_student_id, True, confidence_message)
                
            elif recognized_id:
                # Se reconoció a otro estudiante
                other_student_name = self.get_student_name(recognized_id)
                self.verification_result_label.setText(
                    f"❌ IDENTIDAD NO VERIFICADA\n\nEl rostro capturado pertenece a: {other_student_name}\nNo coincide con el estudiante seleccionado."
                )
                self.verification_result_label.setStyleSheet("""
                    padding: 20px;
                    background-color: #f8d7da;
                    border: 2px solid #e74c3c;
                    border-radius: 8px;
                    color: #721c24;
                    font-size: 16px;
                    font-weight: bold;
                """)
                
                # Registrar verificación fallida
                self.log_verification_attempt(self.selected_student_id, False, f"Reconocido como: {other_student_name}")
                
            else:
                # No se pudo reconocer el rostro
                self.verification_result_label.setText(
                    f"⚠️ NO SE PUDO VERIFICAR\n\nNo se detectó un rostro válido o el rostro no está registrado en el sistema.\nIntente capturar una nueva imagen con mejor iluminación."
                )
                self.verification_result_label.setStyleSheet("""
                    padding: 20px;
                    background-color: #fff3cd;
                    border: 2px solid #ffc107;
                    border-radius: 8px;
                    color: #856404;
                    font-size: 16px;
                    font-weight: bold;
                """)
                
                # Registrar intento fallido
                self.log_verification_attempt(self.selected_student_id, False, "Rostro no detectado o no registrado")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error durante la verificación: {str(e)}")
    
    def get_student_name(self, student_id):
        """Obtener nombre completo del estudiante por ID"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT nombre, apellido FROM estudiantes WHERE id = ?", (student_id,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return f"{result[0]} {result[1]}"
            return "Estudiante desconocido"
        except:
            return "Error al obtener nombre"
    
    def log_verification_attempt(self, student_id, success, details):
        """Registrar intento de verificación en la base de datos"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Crear tabla de logs de verificación si no existe
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS verification_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    student_id INTEGER,
                    timestamp TEXT,
                    success BOOLEAN,
                    details TEXT,
                    FOREIGN KEY (student_id) REFERENCES estudiantes(id)
                )
            """)
            
            # Insertar log
            cursor.execute("""
                INSERT INTO verification_logs (student_id, timestamp, success, details)
                VALUES (?, ?, ?, ?)
            """, (student_id, datetime.datetime.now().isoformat(), success, details))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al registrar log de verificación: {str(e)}")
    
    def toggle_auto_attendance_camera(self):
        """Alternar cámara de detección automática de asistencia"""
        if not hasattr(self, 'auto_camera_active'):
            self.auto_camera_active = False
            self.auto_cap = None
            self.auto_timer = QTimer()
            self.auto_timer.timeout.connect(self.update_auto_attendance_camera)
        
        if not self.auto_camera_active:
            # Encender cámara
            self.auto_cap = cv2.VideoCapture(0)
            if self.auto_cap.isOpened():
                self.auto_camera_active = True
                self.auto_timer.start(100)  # Actualizar cada 100ms para mejor detección
                self.auto_camera_btn.setText("⏹️ Detener Detección")
                self.auto_camera_btn.setStyleSheet("""
                    QPushButton {
                        background-color: #e74c3c;
                        color: white;
                        border: none;
                        padding: 15px 30px;
                        border-radius: 8px;
                        font-weight: bold;
                        font-size: 14px;
                    }
                    QPushButton:hover {
                        background-color: #c0392b;
                    }
                """)
                self.detection_status.setText("🔍 Detectando rostros...")
                self.detection_status.setStyleSheet("""
                    padding: 10px;
                    background-color: #d4edda;
                    border: 1px solid #c3e6cb;
                    border-radius: 5px;
                    font-weight: bold;
                    color: #155724;
                """)
                self.load_recent_attendance()
            else:
                QMessageBox.warning(self, "Error", "No se pudo acceder a la cámara")
        else:
            # Apagar cámara
            self.auto_timer.stop()
            if self.auto_cap:
                self.auto_cap.release()
            self.auto_camera_active = False
            self.auto_camera_label.clear()
            self.auto_camera_label.setText("Cámara desactivada\nHaz clic en 'Iniciar Detección'")
            self.auto_camera_btn.setText("🎥 Iniciar Detección")
            self.auto_camera_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 15px 30px;
                    border-radius: 8px;
                    font-weight: bold;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            self.detection_status.setText("⏸️ Detección detenida")
            self.detection_status.setStyleSheet("""
                padding: 10px;
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                font-weight: bold;
                color: #6c757d;
            """)
            self.detected_student_info.setText("Ningún estudiante detectado")

    def update_auto_attendance_camera(self):
        """Actualizar cámara de detección automática y procesar reconocimiento facial"""
        if self.auto_cap and self.auto_cap.isOpened():
            ret, frame = self.auto_cap.read()
            if ret:
                # Voltear frame horizontalmente
                frame = cv2.flip(frame, 1)
                
                # Procesar reconocimiento facial
                try:
                    recognized_id, confidence_message = self.facial_recognition.recognize_face(frame)
                    
                    if recognized_id:
                        # Estudiante reconocido
                        self.process_automatic_attendance(recognized_id, confidence_message)
                        
                        # Dibujar rectángulo verde alrededor del rostro detectado
                        import face_recognition
                        face_locations = face_recognition.face_locations(frame)
                        for (top, right, bottom, left) in face_locations:
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
                            cv2.putText(frame, "RECONOCIDO", (left, top-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    else:
                        # Rostro no reconocido
                        import face_recognition
                        face_locations = face_recognition.face_locations(frame)
                        for (top, right, bottom, left) in face_locations:
                            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
                            cv2.putText(frame, "NO RECONOCIDO", (left, top-10), 
                                      cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                        
                        self.detected_student_info.setText("Rostro detectado pero no reconocido\nAsegúrese de estar registrado en el sistema")
                        
                except Exception as e:
                    print(f"Error en reconocimiento: {str(e)}")
                
                # Mostrar frame en la interfaz
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(self.auto_camera_label.size(), 
                                            Qt.KeepAspectRatio, Qt.SmoothTransformation)
                
                self.auto_camera_label.setPixmap(scaled_pixmap)

    def process_automatic_attendance(self, student_id, confidence_message):
        """Procesar asistencia automática para estudiante reconocido"""
        try:
            # Verificar si ya se registró asistencia hoy para este estudiante
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            fecha_actual = datetime.datetime.now().strftime("%Y-%m-%d")
            
            cursor.execute("""
                SELECT id FROM asistencias 
                WHERE estudiante_id = ? AND fecha = ?
            """, (student_id, fecha_actual))
            
            existing_record = cursor.fetchone()
            
            if existing_record:
                # Ya tiene asistencia registrada hoy
                student_name = self.get_student_name(student_id)
                self.detected_student_info.setText(f"""
                <div style='color: #856404;'>
                    <h3 style='margin: 0; color: #ffc107;'>⚠️ Ya Registrado</h3>
                    <p><b>Estudiante:</b> {student_name}</p>
                    <p><b>Estado:</b> Asistencia ya registrada hoy</p>
                    <p><b>Confianza:</b> {confidence_message}</p>
                </div>
                """)
            else:
                # Registrar nueva asistencia
                hora_actual = datetime.datetime.now().strftime("%H:%M:%S")
                
                cursor.execute("""
                    INSERT INTO asistencias (estudiante_id, fecha, hora, estado, metodo)
                    VALUES (?, ?, ?, ?, ?)
                """, (student_id, fecha_actual, hora_actual, "presente", "reconocimiento_facial"))
                
                conn.commit()
                
                # Mostrar información del estudiante registrado
                student_info = self.get_detailed_student_info(student_id)
                self.detected_student_info.setText(f"""
                <div style='color: #155724;'>
                    <h3 style='margin: 0; color: #27ae60;'>✅ Asistencia Registrada</h3>
                    <p><b>Estudiante:</b> {student_info['nombre']}</p>
                    <p><b>Código:</b> {student_info['codigo']}</p>
                    <p><b>Nivel:</b> {student_info['nivel']}</p>
                    <p><b>Hora:</b> {hora_actual}</p>
                    <p><b>Confianza:</b> {confidence_message}</p>
                </div>
                """)
                
                # Actualizar tabla de registros recientes
                self.load_recent_attendance()
                
                # Mostrar notificación
                QMessageBox.information(self, "Asistencia Registrada", 
                                      f"Asistencia registrada para {student_info['nombre']} a las {hora_actual}")
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al procesar asistencia automática: {str(e)}")

    def get_detailed_student_info(self, student_id):
        """Obtener información detallada del estudiante"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT e.nombre, e.apellido, e.codigo, n.nombre as nivel, g.nombre as grado, s.nombre as seccion
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                WHERE e.id = ?
            """, (student_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if result:
                return {
                    'nombre': f"{result[0]} {result[1]}",
                    'codigo': result[2] or 'No asignado',
                    'nivel': result[3] or 'No asignado',
                    'grado': result[4] or 'No asignado',
                    'seccion': result[5] or 'No asignado'
                }
            return {'nombre': 'Desconocido', 'codigo': '', 'nivel': '', 'grado': '', 'seccion': ''}
        except:
            return {'nombre': 'Error', 'codigo': '', 'nivel': '', 'grado': '', 'seccion': ''}

    def load_recent_attendance(self):
        """Cargar registros recientes de asistencia"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT a.hora, e.nombre, e.apellido, a.estado, a.metodo
                FROM asistencias a
                JOIN estudiantes e ON a.estudiante_id = e.id
                WHERE a.fecha = ?
                ORDER BY a.hora DESC
                LIMIT 10
            """, (datetime.datetime.now().strftime("%Y-%m-%d"),))
            
            records = cursor.fetchall()
            
            self.recent_attendance_table.setRowCount(len(records))
            
            for row, record in enumerate(records):
                self.recent_attendance_table.setItem(row, 0, QTableWidgetItem(record[0]))
                self.recent_attendance_table.setItem(row, 1, QTableWidgetItem(f"{record[1]} {record[2]}"))
                self.recent_attendance_table.setItem(row, 2, QTableWidgetItem(record[3]))
                self.recent_attendance_table.setItem(row, 3, QTableWidgetItem(record[4] or "manual"))
            
            conn.close()
            
        except Exception as e:
            print(f"Error cargando registros recientes: {str(e)}")

    def capture_registration_image(self):
        """Capture image from registration camera"""
        if self.registration_cap and self.registration_cap.isOpened():
            ret, frame = self.registration_cap.read()
            if ret:
                # Flip the frame horizontally for mirror effect
                frame = cv2.flip(frame, 1)
                
                # Save the captured image
                timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"registration_capture_{timestamp}.jpg"
                filepath = f"data/facial_data/{filename}"
                
                # Create directory if it doesn't exist
                import os
                os.makedirs("data/facial_data", exist_ok=True)
                
                cv2.imwrite(filepath, frame)
                
                QMessageBox.information(self, "Éxito", f"Imagen capturada y guardada como {filename}")
            else:
                QMessageBox.warning(self, "Error", "No se pudo capturar la imagen")
        else:
            QMessageBox.warning(self, "Error", "La cámara no está activa")

class StudentDetailsWindow(QDialog):
    def __init__(self, student_data, parent=None):
        super().__init__(parent)
        self.student_data = student_data
        self.setWindowTitle(f"Detalles de {student_data[1]} {student_data[2]}")
        self.setMinimumSize(800, 600)
        self.setup_ui()
        self.load_academic_data()
    
    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Información personal
        personal_group = QGroupBox("Información Personal")
        personal_layout = QVBoxLayout()
        
        info_layout = QHBoxLayout()
        
        # Columna izquierda
        left_info = QVBoxLayout()
        left_info.addWidget(QLabel(f"<b>Nombre:</b> {self.student_data[1]} {self.student_data[2]}"))
        left_info.addWidget(QLabel(f"<b>Código:</b> {self.student_data[5] or 'No asignado'}"))
        left_info.addWidget(QLabel(f"<b>Fecha de Nacimiento:</b> {self.student_data[3]}"))
        left_info.addWidget(QLabel(f"<b>Género:</b> {self.student_data[4] or 'No especificado'}"))
        
        # Columna derecha
        right_info = QVBoxLayout()
        right_info.addWidget(QLabel(f"<b>Nivel:</b> {self.student_data[13] or 'No asignado'}"))
        right_info.addWidget(QLabel(f"<b>Grado:</b> {self.student_data[14] or 'No asignado'}"))
        right_info.addWidget(QLabel(f"<b>Sección:</b> {self.student_data[15] or 'No asignado'}"))
        right_info.addWidget(QLabel(f"<b>Email:</b> {self.student_data[8] or 'No registrado'}"))
        
        info_layout.addLayout(left_info)
        info_layout.addLayout(right_info)
        personal_layout.addLayout(info_layout)
        personal_group.setLayout(personal_layout)
        layout.addWidget(personal_group)
        
        # Pestañas para información académica
        tab_widget = QTabWidget()
        
        # Pestaña de calificaciones
        grades_tab = self.create_grades_tab()
        tab_widget.addTab(grades_tab, "📊 Calificaciones")
        
        # Pestaña de asistencia
        attendance_tab = self.create_attendance_tab()
        tab_widget.addTab(attendance_tab, "📅 Historial de Asistencia")
        
        layout.addWidget(tab_widget)
        self.setLayout(layout)
    
    def create_grades_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.grades_table = QTableWidget()
        self.grades_table.setColumnCount(4)
        self.grades_table.setHorizontalHeaderLabels(["Materia", "Período", "Nota", "Comentario"])
        
        layout.addWidget(self.grades_table)
        widget.setLayout(layout)
        return widget
    
    def create_attendance_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.attendance_table = QTableWidget()
        self.attendance_table.setColumnCount(4)
        self.attendance_table.setHorizontalHeaderLabels(["Fecha", "Hora", "Estado", "Emoción"])
        
        layout.addWidget(self.attendance_table)
        widget.setLayout(layout)
        return widget
    
    def load_academic_data(self):
        """Cargar datos académicos del estudiante"""
        try:
            from app.models.database import Database
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Cargar calificaciones
            cursor.execute("""
                SELECT m.nombre, c.periodo, c.nota, c.comentario
                FROM calificaciones c
                JOIN materias m ON c.materia_id = m.id
                WHERE c.estudiante_id = ?
                ORDER BY c.periodo, m.nombre
            """, (self.student_data[0],))
            
            grades = cursor.fetchall()
            self.grades_table.setRowCount(len(grades))
            
            for row, grade in enumerate(grades):
                self.grades_table.setItem(row, 0, QTableWidgetItem(grade[0]))
                self.grades_table.setItem(row, 1, QTableWidgetItem(grade[1]))
                self.grades_table.setItem(row, 2, QTableWidgetItem(str(grade[2])))
                self.grades_table.setItem(row, 3, QTableWidgetItem(grade[3] or ""))
            
            # Cargar historial de asistencia
            cursor.execute("""
                SELECT fecha, hora, estado, emocion
                FROM asistencias
                WHERE estudiante_id = ?
                ORDER BY fecha DESC, hora DESC
                LIMIT 50
            """, (self.student_data[0],))
            
            attendance = cursor.fetchall()
            self.attendance_table.setRowCount(len(attendance))
            
            for row, record in enumerate(attendance):
                self.attendance_table.setItem(row, 0, QTableWidgetItem(record[0]))
                self.attendance_table.setItem(row, 1, QTableWidgetItem(record[1]))
                self.attendance_table.setItem(row, 2, QTableWidgetItem(record[2]))
                self.attendance_table.setItem(row, 3, QTableWidgetItem(record[3] or ""))
            
            conn.close()
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error cargando datos académicos: {str(e)}")