from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QTabWidget,
                             QGroupBox, QFormLayout, QLineEdit, QTimeEdit, QCheckBox,
                             QMessageBox, QHeaderView, QSplitter, QFrame, QScrollArea,
                             QGridLayout, QDialog, QDialogButtonBox, QTextEdit)
from PySide6.QtCore import Qt, QTime
from PySide6.QtGui import QFont, QColor
from app.models.database import Database
from app.utils.styles import AppStyles

class HorariosView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título
        title = QLabel("Gestión de Horarios")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Crear pestañas
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 5px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                border: 1px solid #ddd;
                border-bottom: none;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
            QTabBar::tab:hover {
                background-color: #e9ecef;
            }
        """)
        
        # Pestaña 1: Ver Horarios por Sección
        self.create_schedule_view_tab()
        
        # Pestaña 2: Ver Horarios por Profesor
        self.create_teacher_schedule_tab()
        
        # Pestaña 3: Gestionar Horarios (solo para directores/administradores)
        if self.user_data.get('tipo') in ['director', 'admin']:
            self.create_schedule_management_tab()
        
        main_layout.addWidget(self.tab_widget)
        self.setLayout(main_layout)
    
    def create_schedule_view_tab(self):
        """Crear pestaña para ver horarios por nivel, grado y sección"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Filtros
        filters_group = QGroupBox("Filtros de Búsqueda")
        filters_layout = QHBoxLayout()
        
        # Nivel
        filters_layout.addWidget(QLabel("Nivel:"))
        self.nivel_combo = QComboBox()
        self.nivel_combo.addItem("Todos los niveles", None)
        self.nivel_combo.currentTextChanged.connect(self.on_nivel_changed)
        filters_layout.addWidget(self.nivel_combo)
        
        # Grado
        filters_layout.addWidget(QLabel("Grado:"))
        self.grado_combo = QComboBox()
        self.grado_combo.addItem("Todos los grados", None)
        self.grado_combo.currentTextChanged.connect(self.on_grado_changed)
        filters_layout.addWidget(self.grado_combo)
        
        # Sección
        filters_layout.addWidget(QLabel("Sección:"))
        self.seccion_combo = QComboBox()
        self.seccion_combo.addItem("Todas las secciones", None)
        self.seccion_combo.currentTextChanged.connect(self.load_schedule_grid)
        filters_layout.addWidget(self.seccion_combo)
        
        filters_layout.addStretch()
        filters_group.setLayout(filters_layout)
        layout.addWidget(filters_group)
        
        # Grilla de horarios
        self.schedule_frame = QFrame()
        self.schedule_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        self.schedule_layout = QVBoxLayout(self.schedule_frame)
        self.create_schedule_grid()
        
        layout.addWidget(self.schedule_frame)
        
        self.tab_widget.addTab(tab, "📅 Horarios por Sección")
    
    def create_teacher_schedule_tab(self):
        """Crear pestaña para ver horarios por profesor"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Filtro de profesor
        teacher_filter_group = QGroupBox("Seleccionar Profesor")
        teacher_filter_layout = QHBoxLayout()
        
        teacher_filter_layout.addWidget(QLabel("Profesor:"))
        self.teacher_combo = QComboBox()
        self.teacher_combo.addItem("Seleccionar profesor...", None)
        self.teacher_combo.currentTextChanged.connect(self.load_teacher_schedule)
        teacher_filter_layout.addWidget(self.teacher_combo)
        
        teacher_filter_layout.addStretch()
        teacher_filter_group.setLayout(teacher_filter_layout)
        layout.addWidget(teacher_filter_group)
        
        # Información del profesor
        self.teacher_info_group = QGroupBox("Información del Profesor")
        self.teacher_info_layout = QFormLayout()
        self.teacher_info_group.setLayout(self.teacher_info_layout)
        self.teacher_info_group.setVisible(False)
        layout.addWidget(self.teacher_info_group)
        
        # Horarios del profesor
        self.teacher_schedule_frame = QFrame()
        self.teacher_schedule_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
        """)
        
        self.teacher_schedule_layout = QVBoxLayout(self.teacher_schedule_frame)
        layout.addWidget(self.teacher_schedule_frame)
        
        self.tab_widget.addTab(tab, "👨‍🏫 Horarios por Profesor")
    
    def create_schedule_management_tab(self):
        """Crear pestaña para gestionar horarios (solo administradores)"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        add_schedule_btn = QPushButton("➕ Agregar Horario")
        add_schedule_btn.setStyleSheet(AppStyles.get_button_style())
        add_schedule_btn.clicked.connect(self.add_schedule)
        actions_layout.addWidget(add_schedule_btn)
        
        add_teacher_btn = QPushButton("👨‍🏫 Agregar Profesor")
        add_teacher_btn.setStyleSheet(AppStyles.get_button_style())
        add_teacher_btn.clicked.connect(self.add_teacher)
        actions_layout.addWidget(add_teacher_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        # Tabla de horarios para edición
        self.management_table = QTableWidget()
        self.management_table.setColumnCount(8)
        self.management_table.setHorizontalHeaderLabels([
            "Día", "Hora Inicio", "Hora Fin", "Materia", "Profesor", "Sección", "Aula", "Acciones"
        ])
        self.management_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.management_table.setStyleSheet(self.get_table_style())
        
        layout.addWidget(self.management_table)
        
        self.tab_widget.addTab(tab, "⚙️ Gestionar Horarios")
    
    def create_schedule_grid(self):
        """Crear grilla de horarios estilo calendario"""
        # Limpiar layout anterior
        for i in reversed(range(self.schedule_layout.count())):
            self.schedule_layout.itemAt(i).widget().setParent(None)
        
        # Título
        title_label = QLabel("Horario de Clases")
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("margin: 10px; color: #2c3e50;")
        self.schedule_layout.addWidget(title_label)
        
        # Crear tabla de horarios
        self.schedule_table = QTableWidget()
        
        # Configurar días de la semana
        days = ["Hora", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        self.schedule_table.setColumnCount(len(days))
        self.schedule_table.setHorizontalHeaderLabels(days)
        
        # Configurar horas (ejemplo: 8:00 AM a 3:00 PM)
        hours = [
            "08:00 - 08:45", "08:45 - 09:30", "09:30 - 10:15",
            "10:15 - 10:30", "10:30 - 11:15", "11:15 - 12:00",
            "12:00 - 12:45", "12:45 - 13:30", "13:30 - 14:15", "14:15 - 15:00"
        ]
        
        self.schedule_table.setRowCount(len(hours))
        
        # Llenar primera columna con horas
        for i, hour in enumerate(hours):
            item = QTableWidgetItem(hour)
            item.setFlags(Qt.ItemIsEnabled)
            if "10:15 - 10:30" in hour:  # Recreo
                item.setBackground(QColor("#f8f9fa"))
                item.setText("RECREO")
                item.setTextAlignment(Qt.AlignCenter)
            self.schedule_table.setItem(i, 0, item)
        
        # Configurar tabla
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.schedule_table.setStyleSheet(self.get_table_style())
        self.schedule_table.setMinimumHeight(400)
        
        self.schedule_layout.addWidget(self.schedule_table)
    
    def load_initial_data(self):
        """Cargar datos iniciales"""
        self.load_niveles()
        self.load_teachers()
        self.load_management_table()
    
    def load_niveles(self):
        """Cargar niveles en el combo"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM niveles ORDER BY nombre")
            niveles = cursor.fetchall()
            
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Todos los niveles", None)
            for nivel in niveles:
                self.nivel_combo.addItem(nivel[1], nivel[0])
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando niveles: {e}")
    
    def on_nivel_changed(self):
        """Manejar cambio de nivel"""
        nivel_id = self.nivel_combo.currentData()
        self.load_grados(nivel_id)
    
    def load_grados(self, nivel_id):
        """Cargar grados según el nivel seleccionado"""
        try:
            self.grado_combo.clear()
            self.grado_combo.addItem("Todos los grados", None)
            
            if nivel_id:
                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM grados WHERE nivel_id = ? ORDER BY nombre", (nivel_id,))
                grados = cursor.fetchall()
                
                for grado in grados:
                    self.grado_combo.addItem(grado[1], grado[0])
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando grados: {e}")
    
    def on_grado_changed(self):
        """Manejar cambio de grado"""
        grado_id = self.grado_combo.currentData()
        self.load_secciones(grado_id)
    
    def load_secciones(self, grado_id):
        """Cargar secciones según el grado seleccionado"""
        try:
            self.seccion_combo.clear()
            self.seccion_combo.addItem("Todas las secciones", None)
            
            if grado_id:
                conn = self.db.connect()
                cursor = conn.cursor()
                cursor.execute("SELECT id, nombre FROM secciones WHERE grado_id = ? ORDER BY nombre", (grado_id,))
                secciones = cursor.fetchall()
                
                for seccion in secciones:
                    self.seccion_combo.addItem(seccion[1], seccion[0])
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando secciones: {e}")
    
    def load_schedule_grid(self):
        """Cargar horarios en la grilla"""
        seccion_id = self.seccion_combo.currentData()
        
        if not seccion_id:
            # Limpiar tabla si no hay sección seleccionada
            for row in range(self.schedule_table.rowCount()):
                for col in range(1, self.schedule_table.columnCount()):
                    self.schedule_table.setItem(row, col, QTableWidgetItem(""))
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Obtener horarios de la sección
            cursor.execute("""
                SELECT h.dia_semana, h.hora_inicio, h.hora_fin, m.nombre as materia, 
                       p.nombre || ' ' || p.apellido as profesor, h.aula
                FROM horarios h
                JOIN materias m ON h.materia_id = m.id
                JOIN profesores p ON h.profesor_id = p.id
                WHERE h.seccion_id = ? AND h.activo = 1
                ORDER BY h.dia_semana, h.hora_inicio
            """, (seccion_id,))
            
            horarios = cursor.fetchall()
            
            # Limpiar tabla
            for row in range(self.schedule_table.rowCount()):
                for col in range(1, self.schedule_table.columnCount()):
                    self.schedule_table.setItem(row, col, QTableWidgetItem(""))
            
            # Mapear días a columnas
            day_columns = {
                "Lunes": 1, "Martes": 2, "Miércoles": 3, "Jueves": 4, "Viernes": 5
            }
            
            # Llenar horarios
            for horario in horarios:
                dia, hora_inicio, hora_fin, materia, profesor, aula = horario
                
                if dia in day_columns:
                    col = day_columns[dia]
                    
                    # Encontrar la fila correspondiente a la hora
                    for row in range(self.schedule_table.rowCount()):
                        hora_item = self.schedule_table.item(row, 0)
                        if hora_item and hora_inicio in hora_item.text():
                            text = f"{materia}\n{profesor}"
                            if aula:
                                text += f"\nAula: {aula}"
                            
                            item = QTableWidgetItem(text)
                            item.setTextAlignment(Qt.AlignCenter)
                            item.setBackground(QColor("#e3f2fd"))
                            self.schedule_table.setItem(row, col, item)
                            break
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando horarios: {e}")
    
    def load_teachers(self):
        """Cargar profesores en el combo"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, apellido FROM profesores ORDER BY apellido, nombre")
            teachers = cursor.fetchall()
            
            self.teacher_combo.clear()
            self.teacher_combo.addItem("Seleccionar profesor...", None)
            for teacher in teachers:
                self.teacher_combo.addItem(f"{teacher[1]} {teacher[2]}", teacher[0])
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando profesores: {e}")
    
    def load_teacher_schedule(self):
        """Cargar horario del profesor seleccionado"""
        teacher_id = self.teacher_combo.currentData()
        
        if not teacher_id:
            self.teacher_info_group.setVisible(False)
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Obtener información del profesor
            cursor.execute("""
                SELECT nombre, apellido, email, telefono, especialidad
                FROM profesores WHERE id = ?
            """, (teacher_id,))
            
            teacher_info = cursor.fetchone()
            
            if teacher_info:
                # Mostrar información del profesor
                self.teacher_info_layout.setRowCount(0)
                self.teacher_info_layout.addRow("Nombre:", QLabel(f"{teacher_info[0]} {teacher_info[1]}"))
                if teacher_info[2]:
                    self.teacher_info_layout.addRow("Email:", QLabel(teacher_info[2]))
                if teacher_info[3]:
                    self.teacher_info_layout.addRow("Teléfono:", QLabel(teacher_info[3]))
                if teacher_info[4]:
                    self.teacher_info_layout.addRow("Especialidad:", QLabel(teacher_info[4]))
                
                self.teacher_info_group.setVisible(True)
            
            # Obtener horarios del profesor
            cursor.execute("""
                SELECT h.dia_semana, h.hora_inicio, h.hora_fin, m.nombre as materia,
                       n.nombre as nivel, g.nombre as grado, s.nombre as seccion, h.aula
                FROM horarios h
                JOIN materias m ON h.materia_id = m.id
                JOIN secciones s ON h.seccion_id = s.id
                JOIN grados g ON s.grado_id = g.id
                JOIN niveles n ON g.nivel_id = n.id
                WHERE h.profesor_id = ? AND h.activo = 1
                ORDER BY h.dia_semana, h.hora_inicio
            """, (teacher_id,))
            
            schedules = cursor.fetchall()
            
            # Limpiar layout anterior
            for i in reversed(range(self.teacher_schedule_layout.count())):
                self.teacher_schedule_layout.itemAt(i).widget().setParent(None)
            
            if schedules:
                # Crear tabla de horarios del profesor
                teacher_table = QTableWidget()
                teacher_table.setColumnCount(7)
                teacher_table.setHorizontalHeaderLabels([
                    "Día", "Hora", "Materia", "Nivel", "Grado", "Sección", "Aula"
                ])
                teacher_table.setRowCount(len(schedules))
                
                for row, schedule in enumerate(schedules):
                    dia, hora_inicio, hora_fin, materia, nivel, grado, seccion, aula = schedule
                    
                    teacher_table.setItem(row, 0, QTableWidgetItem(dia))
                    teacher_table.setItem(row, 1, QTableWidgetItem(f"{hora_inicio} - {hora_fin}"))
                    teacher_table.setItem(row, 2, QTableWidgetItem(materia))
                    teacher_table.setItem(row, 3, QTableWidgetItem(nivel))
                    teacher_table.setItem(row, 4, QTableWidgetItem(grado))
                    teacher_table.setItem(row, 5, QTableWidgetItem(seccion))
                    teacher_table.setItem(row, 6, QTableWidgetItem(aula or "N/A"))
                
                teacher_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
                teacher_table.setStyleSheet(self.get_table_style())
                self.teacher_schedule_layout.addWidget(teacher_table)
            else:
                no_schedule_label = QLabel("Este profesor no tiene horarios asignados.")
                no_schedule_label.setAlignment(Qt.AlignCenter)
                no_schedule_label.setStyleSheet("color: #666; font-style: italic; padding: 40px;")
                self.teacher_schedule_layout.addWidget(no_schedule_label)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando horario del profesor: {e}")
    
    def load_management_table(self):
        """Cargar tabla de gestión de horarios"""
        if not hasattr(self, 'management_table'):
            return
            
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT h.id, h.dia_semana, h.hora_inicio, h.hora_fin, m.nombre as materia,
                       p.nombre || ' ' || p.apellido as profesor,
                       n.nombre || ' - ' || g.nombre || ' - ' || s.nombre as seccion_completa,
                       h.aula
                FROM horarios h
                JOIN materias m ON h.materia_id = m.id
                JOIN profesores p ON h.profesor_id = p.id
                JOIN secciones s ON h.seccion_id = s.id
                JOIN grados g ON s.grado_id = g.id
                JOIN niveles n ON g.nivel_id = n.id
                WHERE h.activo = 1
                ORDER BY h.dia_semana, h.hora_inicio
            """)
            
            horarios = cursor.fetchall()
            self.management_table.setRowCount(len(horarios))
            
            for row, horario in enumerate(horarios):
                horario_id, dia, hora_inicio, hora_fin, materia, profesor, seccion, aula = horario
                
                self.management_table.setItem(row, 0, QTableWidgetItem(dia))
                self.management_table.setItem(row, 1, QTableWidgetItem(hora_inicio))
                self.management_table.setItem(row, 2, QTableWidgetItem(hora_fin))
                self.management_table.setItem(row, 3, QTableWidgetItem(materia))
                self.management_table.setItem(row, 4, QTableWidgetItem(profesor))
                self.management_table.setItem(row, 5, QTableWidgetItem(seccion))
                self.management_table.setItem(row, 6, QTableWidgetItem(aula or "N/A"))
                
                # Botón de acciones
                actions_btn = QPushButton("✏️ Editar")
                actions_btn.setStyleSheet("background-color: #ffc107; color: white; border: none; padding: 5px; border-radius: 3px;")
                actions_btn.clicked.connect(lambda checked, h_id=horario_id: self.edit_schedule(h_id))
                self.management_table.setCellWidget(row, 7, actions_btn)
                
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando horarios: {e}")
    
    def add_schedule(self):
        """Agregar nuevo horario"""
        dialog = ScheduleDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_management_table()
            self.load_schedule_grid()
    
    def add_teacher(self):
        """Agregar nuevo profesor"""
        dialog = TeacherDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_teachers()
    
    def edit_schedule(self, schedule_id):
        """Editar horario existente"""
        dialog = ScheduleDialog(self, schedule_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_management_table()
            self.load_schedule_grid()
    
    def get_table_style(self):
        return """
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 5px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #f0f0f0;
            }
            QHeaderView::section {
                background-color: #f8f9fa;
                padding: 8px;
                border: none;
                font-weight: bold;
                color: #333;
            }
        """

class ScheduleDialog(QDialog):
    """Diálogo para agregar/editar horarios"""
    def __init__(self, parent, schedule_id=None):
        super().__init__(parent)
        self.schedule_id = schedule_id
        self.db = Database()
        self.setup_ui()
        if schedule_id:
            self.load_schedule_data()
    
    def setup_ui(self):
        self.setWindowTitle("Agregar Horario" if not self.schedule_id else "Editar Horario")
        self.setMinimumSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        # Día de la semana
        self.day_combo = QComboBox()
        self.day_combo.addItems(["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"])
        form_layout.addRow("Día:", self.day_combo)
        
        # Horas
        self.start_time = QTimeEdit()
        self.start_time.setTime(QTime(8, 0))
        form_layout.addRow("Hora inicio:", self.start_time)
        
        self.end_time = QTimeEdit()
        self.end_time.setTime(QTime(8, 45))
        form_layout.addRow("Hora fin:", self.end_time)
        
        # Materia
        self.subject_combo = QComboBox()
        self.load_subjects()
        form_layout.addRow("Materia:", self.subject_combo)
        
        # Profesor
        self.teacher_combo = QComboBox()
        self.load_teachers()
        form_layout.addRow("Profesor:", self.teacher_combo)
        
        # Sección
        self.section_combo = QComboBox()
        self.load_sections()
        form_layout.addRow("Sección:", self.section_combo)
        
        # Aula
        self.classroom_edit = QLineEdit()
        form_layout.addRow("Aula:", self.classroom_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_schedule)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def load_subjects(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM materias ORDER BY nombre")
            subjects = cursor.fetchall()
            
            for subject in subjects:
                self.subject_combo.addItem(subject[1], subject[0])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando materias: {e}")
    
    def load_teachers(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre, apellido FROM profesores ORDER BY apellido, nombre")
            teachers = cursor.fetchall()
            
            for teacher in teachers:
                self.teacher_combo.addItem(f"{teacher[1]} {teacher[2]}", teacher[0])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando profesores: {e}")
    
    def load_sections(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT s.id, n.nombre || ' - ' || g.nombre || ' - ' || s.nombre as seccion_completa
                FROM secciones s
                JOIN grados g ON s.grado_id = g.id
                JOIN niveles n ON g.nivel_id = n.id
                ORDER BY n.nombre, g.nombre, s.nombre
            """)
            sections = cursor.fetchall()
            
            for section in sections:
                self.section_combo.addItem(section[1], section[0])
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando secciones: {e}")
    
    def load_schedule_data(self):
        """Cargar datos del horario para edición"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT dia_semana, hora_inicio, hora_fin, materia_id, profesor_id, seccion_id, aula
                FROM horarios WHERE id = ?
            """, (self.schedule_id,))
            
            data = cursor.fetchone()
            if data:
                dia, hora_inicio, hora_fin, materia_id, profesor_id, seccion_id, aula = data
                
                # Establecer valores
                self.day_combo.setCurrentText(dia)
                self.start_time.setTime(QTime.fromString(hora_inicio, "hh:mm"))
                self.end_time.setTime(QTime.fromString(hora_fin, "hh:mm"))
                
                # Buscar y establecer índices
                for i in range(self.subject_combo.count()):
                    if self.subject_combo.itemData(i) == materia_id:
                        self.subject_combo.setCurrentIndex(i)
                        break
                
                for i in range(self.teacher_combo.count()):
                    if self.teacher_combo.itemData(i) == profesor_id:
                        self.teacher_combo.setCurrentIndex(i)
                        break
                
                for i in range(self.section_combo.count()):
                    if self.section_combo.itemData(i) == seccion_id:
                        self.section_combo.setCurrentIndex(i)
                        break
                
                if aula:
                    self.classroom_edit.setText(aula)
                    
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando datos del horario: {e}")
    
    def save_schedule(self):
        """Guardar horario"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            data = (
                self.day_combo.currentText(),
                self.start_time.time().toString("hh:mm"),
                self.end_time.time().toString("hh:mm"),
                self.subject_combo.currentData(),
                self.teacher_combo.currentData(),
                self.section_combo.currentData(),
                self.classroom_edit.text() or None
            )
            
            if self.schedule_id:
                # Actualizar
                cursor.execute("""
                    UPDATE horarios SET dia_semana=?, hora_inicio=?, hora_fin=?, 
                    materia_id=?, profesor_id=?, seccion_id=?, aula=?
                    WHERE id=?
                """, data + (self.schedule_id,))
            else:
                # Insertar
                cursor.execute("""
                    INSERT INTO horarios (dia_semana, hora_inicio, hora_fin, materia_id, 
                    profesor_id, seccion_id, aula, activo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
                """, data)
            
            conn.commit()
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error guardando horario: {e}")

class TeacherDialog(QDialog):
    """Diálogo para agregar profesores"""
    def __init__(self, parent):
        super().__init__(parent)
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("Agregar Profesor")
        self.setMinimumSize(350, 250)
        
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        form_layout.addRow("Nombre:", self.name_edit)
        
        self.lastname_edit = QLineEdit()
        form_layout.addRow("Apellido:", self.lastname_edit)
        
        self.email_edit = QLineEdit()
        form_layout.addRow("Email:", self.email_edit)
        
        self.phone_edit = QLineEdit()
        form_layout.addRow("Teléfono:", self.phone_edit)
        
        self.specialty_edit = QLineEdit()
        form_layout.addRow("Especialidad:", self.specialty_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.save_teacher)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        self.setLayout(layout)
    
    def save_teacher(self):
        """Guardar profesor"""
        if not self.name_edit.text() or not self.lastname_edit.text():
            QMessageBox.warning(self, "Error", "Nombre y apellido son obligatorios")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO profesores (nombre, apellido, email, telefono, especialidad)
                VALUES (?, ?, ?, ?, ?)
            """, (
                self.name_edit.text(),
                self.lastname_edit.text(),
                self.email_edit.text() or None,
                self.phone_edit.text() or None,
                self.specialty_edit.text() or None
            ))
            
            conn.commit()
            self.accept()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error guardando profesor: {e}")