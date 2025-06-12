from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDoubleSpinBox, QTextEdit, QGroupBox, QFrame,
                             QDialog, QTabWidget, QLineEdit, QSplitter, QScrollArea, QSizePolicy,
                             QCheckBox)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QIcon, QFont, QColor, QPainter, QPixmap
from app.models.database import Database
from app.utils.styles import AppStyles
import datetime
import math

class CalificacionesView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Encabezado con estadísticas
        header_widget = self.create_header()
        main_layout.addWidget(header_widget)
        
        # Crear splitter para dividir la vista
        splitter = QSplitter(Qt.Horizontal)
        
        # Panel izquierdo - Lista de estudiantes
        left_panel = self.create_students_panel()
        splitter.addWidget(left_panel)
        
        # Panel derecho - Detalles del estudiante
        right_panel = self.create_student_details_panel()
        splitter.addWidget(right_panel)
        
        # Configurar proporciones del splitter
        splitter.setSizes([400, 600])
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Cargar datos iniciales
        self.load_students_list()
    
    def create_header(self):
        """Crear encabezado con estadísticas generales"""
        header_widget = QWidget()
        header_layout = QVBoxLayout(header_widget)
        
        # Título principal con estilo mejorado
        title_container = QWidget()
        title_container.setStyleSheet(f"background-color: {AppStyles.PRIMARY_COLOR}; border-radius: 8px;")
        title_layout = QHBoxLayout(title_container)
        
        title = QLabel("Sistema de Gestión de Calificaciones")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("color: white; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title)
        
        header_layout.addWidget(title_container)
        
        # Tarjetas de estadísticas
        stats_layout = QHBoxLayout()
        
        # Función para crear tarjetas de estadísticas
        def create_stat_card(title, value, icon_color):
            card = QFrame()
            card.setStyleSheet(f"""
                background-color: white;
                border-radius: 8px;
                border: 1px solid #e0e0e0;
            """)
            card.setMinimumHeight(100)
            card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            
            card_layout = QHBoxLayout(card)
            
            # Indicador de color
            color_indicator = QFrame()
            color_indicator.setStyleSheet(f"background-color: {icon_color}; border-radius: 4px;")
            color_indicator.setFixedWidth(8)
            card_layout.addWidget(color_indicator)
            
            # Contenido
            content_layout = QVBoxLayout()
            
            title_label = QLabel(title)
            title_label.setStyleSheet("color: #666; font-size: 12px;")
            content_layout.addWidget(title_label)
            
            value_label = QLabel(value)
            value_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
            content_layout.addWidget(value_label)
            
            card_layout.addLayout(content_layout)
            card_layout.setStretch(1, 1)
            
            return card
        
        # Obtener estadísticas de la base de datos
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Total de estudiantes
            cursor.execute("SELECT COUNT(*) FROM estudiantes")
            total_students = cursor.fetchone()[0]
            
            # Promedio general
            cursor.execute("""
                SELECT AVG(c.nota)
                FROM calificaciones c
            """)
            avg_result = cursor.fetchone()[0]
            avg_grade = round(avg_result, 2) if avg_result else 0
            
            # Estudiantes con bajo rendimiento
            cursor.execute("""
                SELECT COUNT(DISTINCT estudiante_id)
                FROM calificaciones
                WHERE nota < 11
            """)
            low_performance = cursor.fetchone()[0]
            
            conn.close()
            
        except Exception as e:
            total_students = 0
            avg_grade = 0
            low_performance = 0
            print(f"Error al obtener estadísticas: {e}")
        
        # Crear tarjetas
        stats_layout.addWidget(create_stat_card("Total de Estudiantes", str(total_students), "#3498db"))
        stats_layout.addWidget(create_stat_card("Promedio General", f"{avg_grade}", "#2ecc71"))
        stats_layout.addWidget(create_stat_card("Bajo Rendimiento", str(low_performance), "#e74c3c"))
        
        header_layout.addLayout(stats_layout)
        
        return header_widget
        
    def create_students_panel(self):
        """Crear panel de lista de estudiantes"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # Filtros
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_group.setStyleSheet(AppStyles.get_group_box_style())
        filter_layout = QVBoxLayout()
        
        # Búsqueda por nombre con icono
        search_layout = QHBoxLayout()
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 20px;
                padding: 5px;
            }
        """)
        search_inner_layout = QHBoxLayout(search_frame)
        search_inner_layout.setContentsMargins(10, 0, 10, 0)
        
        search_icon = QLabel("🔍")
        search_inner_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Buscar por nombre o código...")
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 5px;
                background: transparent;
            }
        """)
        self.search_input.textChanged.connect(self.filter_students)
        search_inner_layout.addWidget(self.search_input)
        
        search_layout.addWidget(search_frame)
        filter_layout.addLayout(search_layout)
        
        # Filtros por nivel, grado, sección
        filters_row = QHBoxLayout()
        
        # Nivel
        nivel_layout = QVBoxLayout()
        nivel_label = QLabel("Nivel:")
        nivel_label.setStyleSheet("font-weight: bold; color: #555;")
        nivel_layout.addWidget(nivel_label)
        self.nivel_combo = QComboBox()
        self.nivel_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QComboBox::drop-down {
                width: 20px;
            }
        """)
        self.nivel_combo.currentIndexChanged.connect(self.on_nivel_changed)
        nivel_layout.addWidget(self.nivel_combo)
        filters_row.addLayout(nivel_layout)
        
        # Grado
        grado_layout = QVBoxLayout()
        grado_label = QLabel("Grado:")
        grado_label.setStyleSheet("font-weight: bold; color: #555;")
        grado_layout.addWidget(grado_label)
        self.grado_combo = QComboBox()
        self.grado_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        self.grado_combo.currentIndexChanged.connect(self.on_grado_changed)
        grado_layout.addWidget(self.grado_combo)
        filters_row.addLayout(grado_layout)
        
        # Sección
        seccion_layout = QVBoxLayout()
        seccion_label = QLabel("Sección:")
        seccion_label.setStyleSheet("font-weight: bold; color: #555;")
        seccion_layout.addWidget(seccion_label)
        self.seccion_combo = QComboBox()
        self.seccion_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        self.seccion_combo.currentIndexChanged.connect(self.filter_students)
        seccion_layout.addWidget(self.seccion_combo)
        filters_row.addLayout(seccion_layout)
        
        filter_layout.addLayout(filters_row)
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Lista de estudiantes
        students_group = QGroupBox("Lista de Estudiantes")
        students_group.setStyleSheet(AppStyles.get_group_box_style())
        students_layout = QVBoxLayout()
        
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(5)
        self.students_table.setHorizontalHeaderLabels(["Código", "Nombre", "Nivel", "Grado", "Sección"])
        self.students_table.horizontalHeader().setStretchLastSection(True)
        self.students_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.students_table.cellClicked.connect(self.on_student_selected)
        self.students_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: none;
                border-radius: 8px;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        # Configurar para filas alternadas
        self.students_table.setAlternatingRowColors(True)
        
        students_layout.addWidget(self.students_table)
        students_group.setLayout(students_layout)
        layout.addWidget(students_group)
        
        return panel
    
    def create_student_details_panel(self):
        """Crear panel de detalles del estudiante"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)
        
        # Información del estudiante seleccionado
        self.student_info_group = QGroupBox("Información del Estudiante")
        self.student_info_group.setStyleSheet("""
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 8px;
                margin-top: 12px;
                font-weight: bold;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #3498db;
            }
        """)
        info_layout = QVBoxLayout()
        
        self.student_info_label = QLabel("Seleccione un estudiante para ver sus detalles")
        self.student_info_label.setStyleSheet("""
            padding: 20px;
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            border-radius: 8px;
            color: #6c757d;
            font-size: 14px;
        """)
        self.student_info_label.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(self.student_info_label)
        
        self.student_info_group.setLayout(info_layout)
        layout.addWidget(self.student_info_group)
        
        # Pestañas para calificaciones
        self.grades_tabs = QTabWidget()
        self.grades_tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #ddd;
                background-color: white;
                border-radius: 8px;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                padding: 10px 20px;
                margin-right: 2px;
                border: 1px solid #ddd;
                border-bottom: none;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #3498db;
                font-weight: bold;
                color: #3498db;
            }
        """)
        
        # Pestaña de calificaciones por curso
        self.grades_by_course_tab = self.create_grades_by_course_tab()
        self.grades_tabs.addTab(self.grades_by_course_tab, "📊 Calificaciones por Curso")
        
        # Pestaña de resumen de promedios
        self.averages_tab = self.create_averages_tab()
        self.grades_tabs.addTab(self.averages_tab, "📈 Promedios")
        
        # Pestaña de gráficos
        self.charts_tab = self.create_charts_tab()
        self.grades_tabs.addTab(self.charts_tab, "📉 Gráficos")
        
        # Pestaña de alertas y notificaciones
        self.alerts_tab = self.create_alerts_tab()
        self.grades_tabs.addTab(self.alerts_tab, "🔔 Alertas")
        
        layout.addWidget(self.grades_tabs)
        
        # Inicialmente ocultar las pestañas
        self.grades_tabs.setVisible(False)
        
        return panel
        
    def create_charts_tab(self):
        """Crear pestaña de gráficos"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Área de gráficos
        charts_scroll = QScrollArea()
        charts_scroll.setWidgetResizable(True)
        charts_content = QWidget()
        charts_layout = QVBoxLayout(charts_content)
        
        # Título
        title = QLabel("Visualización de Rendimiento Académico")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        charts_layout.addWidget(title)
        
        # Gráfico de barras para promedios por materia
        self.subject_chart = QFrame()
        self.subject_chart.setMinimumHeight(300)
        self.subject_chart.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px;")
        charts_layout.addWidget(self.subject_chart)
        
        # Gráfico de línea para evolución de calificaciones
        self.evolution_chart = QFrame()
        self.evolution_chart.setMinimumHeight(300)
        self.evolution_chart.setStyleSheet("background-color: white; border: 1px solid #ddd; border-radius: 8px; margin-top: 20px;")
        charts_layout.addWidget(self.evolution_chart)
        
        charts_scroll.setWidget(charts_content)
        layout.addWidget(charts_scroll)
        
        return widget
        
    def create_alerts_tab(self):
        """Crear pestaña de alertas y notificaciones"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Configuración de alertas
        alerts_config = QGroupBox("Configuración de Alertas")
        alerts_config.setStyleSheet(AppStyles.get_group_box_style())
        config_layout = QVBoxLayout()
        
        # Alertas por bajo rendimiento
        low_performance_layout = QHBoxLayout()
        low_performance_layout.addWidget(QLabel("Alerta por calificación menor a:"))
        self.low_grade_threshold = QDoubleSpinBox()
        self.low_grade_threshold.setRange(0, 20)
        self.low_grade_threshold.setValue(11.0)
        self.low_grade_threshold.setDecimals(1)
        low_performance_layout.addWidget(self.low_grade_threshold)
        config_layout.addLayout(low_performance_layout)
        
        # Opciones de notificación
        notification_layout = QHBoxLayout()
        notification_layout.addWidget(QLabel("Enviar notificación por:"))
        self.email_checkbox = QCheckBox("Email")
        self.email_checkbox.setChecked(True)
        self.sms_checkbox = QCheckBox("SMS")
        notification_layout.addWidget(self.email_checkbox)
        notification_layout.addWidget(self.sms_checkbox)
        notification_layout.addStretch()
        config_layout.addLayout(notification_layout)
        
        # Botón para guardar configuración
        save_button = QPushButton("Guardar Configuración")
        save_button.setStyleSheet(AppStyles.get_button_style())
        config_layout.addWidget(save_button)
        
        alerts_config.setLayout(config_layout)
        layout.addWidget(alerts_config)
        
        # Lista de alertas generadas
        alerts_list = QGroupBox("Alertas Generadas")
        alerts_list.setStyleSheet(AppStyles.get_group_box_style())
        alerts_layout = QVBoxLayout()
        
        self.alerts_table = QTableWidget()
        self.alerts_table.setColumnCount(4)
        self.alerts_table.setHorizontalHeaderLabels(["Estudiante", "Materia", "Calificación", "Fecha"])
        self.alerts_table.horizontalHeader().setStretchLastSection(True)
        self.alerts_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
                border: none;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #eee;
            }
            QHeaderView::section {
                background-color: #e74c3c;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        alerts_layout.addWidget(self.alerts_table)
        
        # Botones de acción
        actions_layout = QHBoxLayout()
        
        notify_button = QPushButton("Notificar a Padres")
        notify_button.setStyleSheet(AppStyles.get_button_style())
        actions_layout.addWidget(notify_button)
        
        export_button = QPushButton("Exportar Alertas")
        export_button.setStyleSheet(AppStyles.get_button_style(primary=False))
        actions_layout.addWidget(export_button)
        
        alerts_layout.addLayout(actions_layout)
        alerts_list.setLayout(alerts_layout)
        layout.addWidget(alerts_list)
        
        return widget
    
    def create_grades_by_course_tab(self):
        """Crear pestaña de calificaciones por curso"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Botón para agregar nueva nota
        add_grade_button = QPushButton("Agregar Nota")
        add_grade_button.setStyleSheet(AppStyles.get_button_style())
        add_grade_button.setIcon(QIcon("resources/icons/add.png"))
        add_grade_button.clicked.connect(self.show_add_grade_dialog)
        add_grade_button.setFixedWidth(150)
        
        button_layout = QHBoxLayout()
        button_layout.addWidget(add_grade_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Tabla de calificaciones por curso y bimestre
        self.course_grades_table = QTableWidget()
        self.course_grades_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #34495e;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.course_grades_table)
        
        return widget
    
    def create_averages_tab(self):
        """Crear pestaña de promedios"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Tabla de promedios
        self.averages_table = QTableWidget()
        self.averages_table.setColumnCount(6)
        self.averages_table.setHorizontalHeaderLabels([
            "Curso", "1er Bimestre", "2do Bimestre", "3er Bimestre", "4to Bimestre", "Promedio Final"
        ])
        self.averages_table.horizontalHeader().setStretchLastSection(True)
        self.averages_table.setStyleSheet("""
            QTableWidget {
                gridline-color: #ddd;
                background-color: white;
            }
            QTableWidget::item {
                padding: 8px;
                text-align: center;
            }
            QHeaderView::section {
                background-color: #27ae60;
                color: white;
                padding: 10px;
                border: none;
                font-weight: bold;
            }
        """)
        
        layout.addWidget(self.averages_table)
        
        # Promedio general
        self.general_average_label = QLabel()
        self.general_average_label.setStyleSheet("""
            background-color: #3498db;
            color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            text-align: center;
        """)
        self.general_average_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.general_average_label)
        
        return widget
    
    def load_students_list(self):
        """Cargar lista de estudiantes"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            query = """
                SELECT e.id, e.codigo, e.nombre, e.apellido, e.email,
                       n.nombre as nivel, g.nombre as grado, s.nombre as seccion,
                       e.nivel_id, e.grado_id, e.seccion_id
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                ORDER BY e.apellido, e.nombre
            """
            
            cursor.execute(query)
            self.all_students = cursor.fetchall()
            
            # Cargar filtros
            self.load_filter_options()
            
            # Mostrar estudiantes
            self.display_students(self.all_students)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar estudiantes: {str(e)}")
    
    def load_filter_options(self):
        """Cargar opciones para los filtros"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Cargar niveles
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Todos los niveles", None)
            cursor.execute("SELECT id, nombre FROM niveles ORDER BY nombre")
            for nivel in cursor.fetchall():
                self.nivel_combo.addItem(nivel[1], nivel[0])
            
            # Cargar grados
            self.grado_combo.clear()
            self.grado_combo.addItem("Todos los grados", None)
            cursor.execute("SELECT id, nombre FROM grados ORDER BY nombre")
            for grado in cursor.fetchall():
                self.grado_combo.addItem(grado[1], grado[0])
            
            # Cargar secciones
            self.seccion_combo.clear()
            self.seccion_combo.addItem("Todas las secciones", None)
            cursor.execute("SELECT id, nombre FROM secciones ORDER BY nombre")
            for seccion in cursor.fetchall():
                self.seccion_combo.addItem(seccion[1], seccion[0])
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar filtros: {str(e)}")
    
    def on_nivel_changed(self):
        """Manejar cambio de nivel"""
        self.filter_students()
    
    def on_grado_changed(self):
        """Manejar cambio de grado"""
        self.filter_students()
    
    def filter_students(self):
        """Filtrar estudiantes según criterios seleccionados"""
        search_text = self.search_input.text().lower()
        nivel_id = self.nivel_combo.currentData()
        grado_id = self.grado_combo.currentData()
        seccion_id = self.seccion_combo.currentData()
        
        filtered_students = []
        
        for student in self.all_students:
            # Filtro por texto de búsqueda
            if search_text:
                full_name = f"{student[2]} {student[3]}".lower()
                codigo = str(student[1]).lower() if student[1] else ""
                if search_text not in full_name and search_text not in codigo:
                    continue
            
            # Filtro por nivel
            if nivel_id is not None and student[8] != nivel_id:
                continue
            
            # Filtro por grado
            if grado_id is not None and student[9] != grado_id:
                continue
            
            # Filtro por sección
            if seccion_id is not None and student[10] != seccion_id:
                continue
            
            filtered_students.append(student)
        
        self.display_students(filtered_students)
    
    def display_students(self, students):
        """Mostrar estudiantes en la tabla"""
        self.students_table.setRowCount(len(students))
        
        for row, student in enumerate(students):
            self.students_table.setItem(row, 0, QTableWidgetItem(str(student[1]) if student[1] else "N/A"))
            self.students_table.setItem(row, 1, QTableWidgetItem(f"{student[2]} {student[3]}"))
            self.students_table.setItem(row, 2, QTableWidgetItem(student[5] or "N/A"))
            self.students_table.setItem(row, 3, QTableWidgetItem(student[6] or "N/A"))
            self.students_table.setItem(row, 4, QTableWidgetItem(student[7] or "N/A"))
            
            # Guardar ID del estudiante en la primera columna
            self.students_table.item(row, 0).setData(Qt.UserRole, student[0])
    
    def on_student_selected(self, row, column):
        """Manejar selección de estudiante"""
        if row >= 0:
            student_id = self.students_table.item(row, 0).data(Qt.UserRole)
            self.load_student_details(student_id)
    
    def load_student_details(self, student_id):
        """Cargar detalles del estudiante seleccionado"""
        try:
            # Guardar el ID del estudiante seleccionado
            self.current_student_id = student_id
            
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Obtener información del estudiante
            cursor.execute("""
                SELECT e.id, e.codigo, e.nombre, e.apellido, e.email,
                       n.nombre as nivel, g.nombre as grado, s.nombre as seccion
                FROM estudiantes e
                LEFT JOIN niveles n ON e.nivel_id = n.id
                LEFT JOIN grados g ON e.grado_id = g.id
                LEFT JOIN secciones s ON e.seccion_id = s.id
                WHERE e.id = ?
            """, (student_id,))
            
            student = cursor.fetchone()
            
            if student:
                # Mostrar información del estudiante
                info_html = f"""
                <div style='color: #2c3e50;'>
                    <h2 style='margin: 0; color: #3498db;'>👤 {student[2]} {student[3]}</h2>
                    <hr style='border: 1px solid #bdc3c7; margin: 10px 0;'>
                    <p><b>📋 Código:</b> {student[1] or 'No asignado'}</p>
                    <p><b>📧 Email:</b> {student[4] or 'No registrado'}</p>
                    <p><b>🎓 Nivel:</b> {student[5] or 'No asignado'}</p>
                    <p><b>📚 Grado:</b> {student[6] or 'No asignado'}</p>
                    <p><b>🏫 Sección:</b> {student[7] or 'No asignado'}</p>
                </div>
                """
                
                self.student_info_label.setText(info_html)
                self.student_info_label.setStyleSheet("""
                    padding: 20px;
                    background-color: #f8f9fa;
                    border: 2px solid #3498db;
                    border-radius: 8px;
                """)
                
                # Cargar calificaciones del estudiante
                self.load_student_grades(student_id)
                
                # Mostrar pestañas
                self.grades_tabs.setVisible(True)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar detalles del estudiante: {str(e)}")
    
    def load_student_grades(self, student_id):
        """Cargar calificaciones del estudiante"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Obtener todas las calificaciones del estudiante
            cursor.execute("""
                SELECT m.nombre as materia, c.periodo, c.nota, c.comentario
                FROM calificaciones c
                JOIN materias m ON c.materia_id = m.id
                WHERE c.estudiante_id = ?
                ORDER BY m.nombre, c.periodo
            """, (student_id,))
            
            grades_data = cursor.fetchall()
            
            # Organizar datos por materia y período
            grades_by_subject = {}
            for grade in grades_data:
                materia = grade[0]
                periodo = grade[1]
                calificacion = grade[2]
                comentario = grade[3]
                
                if materia not in grades_by_subject:
                    grades_by_subject[materia] = {}
                
                grades_by_subject[materia][periodo] = {
                    'calificacion': calificacion,
                    'comentario': comentario
                }
            
            # Mostrar en tabla de calificaciones por curso
            self.display_grades_by_course(grades_by_subject)
            
            # Calcular y mostrar promedios
            self.calculate_and_display_averages(grades_by_subject)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar calificaciones: {str(e)}")
    
    def display_grades_by_course(self, grades_by_subject):
        """Mostrar calificaciones por curso en la tabla con diseño mejorado"""
        periods = ['1er bimestre', '2do bimestre', '3er bimestre', '4to bimestre']
        
        # Configurar tabla
        self.course_grades_table.setColumnCount(6)
        self.course_grades_table.setHorizontalHeaderLabels([
            'Curso', '1er Bimestre', '2do Bimestre', '3er Bimestre', '4to Bimestre', 'Promedio'
        ])
        
        subjects = list(grades_by_subject.keys())
        self.course_grades_table.setRowCount(len(subjects))
        
        for row, subject in enumerate(subjects):
            # Nombre del curso con estilo
            subject_item = QTableWidgetItem(subject)
            subject_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
            subject_item.setForeground(QColor(AppStyles.PRIMARY_COLOR))
            self.course_grades_table.setItem(row, 0, subject_item)
            
            # Calificaciones por período
            period_grades = []
            for col, period in enumerate(periods, 1):
                if period in grades_by_subject[subject]:
                    grade = grades_by_subject[subject][period]['calificacion']
                    comment = grades_by_subject[subject][period]['comentario']
                    
                    item = QTableWidgetItem(str(grade))
                    if comment:
                        item.setToolTip(f"<b>Comentario:</b><br>{comment}")
                    
                    # Colorear según la calificación
                    if grade >= 16:
                        item.setBackground(QColor(212, 237, 218))  # Verde
                        item.setForeground(QColor(21, 87, 36))  # Verde oscuro
                        item.setToolTip(f"{item.toolTip()}<br><b>Excelente rendimiento</b>")
                    elif grade >= 11:
                        item.setBackground(QColor(255, 243, 205))  # Amarillo
                        item.setForeground(QColor(133, 100, 4))  # Amarillo oscuro
                        item.setToolTip(f"{item.toolTip()}<br><b>Rendimiento aceptable</b>")
                    else:
                        item.setBackground(QColor(248, 215, 218))  # Rojo
                        item.setForeground(QColor(114, 28, 36))  # Rojo oscuro
                        item.setToolTip(f"{item.toolTip()}<br><b>Necesita mejorar</b>")
                    
                    item.setTextAlignment(Qt.AlignCenter)
                    self.course_grades_table.setItem(row, col, item)
                    period_grades.append(grade)
                else:
                    item = QTableWidgetItem("-")
                    item.setTextAlignment(Qt.AlignCenter)
                    self.course_grades_table.setItem(row, col, item)
            
            # Calcular promedio del curso con estilo mejorado
            if period_grades:
                average = sum(period_grades) / len(period_grades)
                avg_item = QTableWidgetItem(f"{average:.2f}")
                avg_item.setTextAlignment(Qt.AlignCenter)
                
                # Estilo según el promedio
                if average >= 16:
                    avg_item.setBackground(QColor(52, 152, 219, 100))  # Azul claro
                    avg_item.setForeground(QColor(41, 128, 185))  # Azul oscuro
                elif average >= 11:
                    avg_item.setBackground(QColor(52, 152, 219, 70))  # Azul más claro
                    avg_item.setForeground(QColor(41, 128, 185))  # Azul oscuro
                else:
                    avg_item.setBackground(QColor(231, 76, 60, 100))  # Rojo claro
                    avg_item.setForeground(QColor(192, 57, 43))  # Rojo oscuro
                
                avg_item.setFont(QFont("Segoe UI", 10, QFont.Bold))
                self.course_grades_table.setItem(row, 5, avg_item)
            else:
                item = QTableWidgetItem("-")
                item.setTextAlignment(Qt.AlignCenter)
                self.course_grades_table.setItem(row, 5, item)
        
        # Ajustar tamaño de columnas y filas
        self.course_grades_table.resizeColumnsToContents()
        self.course_grades_table.resizeRowsToContents()
        
        # Actualizar gráficos si están visibles
        if hasattr(self, 'charts_tab') and self.grades_tabs.isVisible():
            self.update_charts(grades_by_subject)
    
    def calculate_and_display_averages(self, grades_by_subject):
        """Calcular y mostrar promedios"""
        periods = ['1er bimestre', '2do bimestre', '3er bimestre', '4to bimestre']
        
        subjects = list(grades_by_subject.keys())
        self.averages_table.setRowCount(len(subjects))
        
        all_averages = []
        
        for row, subject in enumerate(subjects):
            # Nombre del curso
            self.averages_table.setItem(row, 0, QTableWidgetItem(subject))
            
            # Promedios por período y promedio final
            period_grades = []
            for col, period in enumerate(periods, 1):
                if period in grades_by_subject[subject]:
                    grade = grades_by_subject[subject][period]['calificacion']
                    self.averages_table.setItem(row, col, QTableWidgetItem(str(grade)))
                    period_grades.append(grade)
                else:
                    self.averages_table.setItem(row, col, QTableWidgetItem("-"))
            
            # Promedio final del curso
            if period_grades:
                course_average = sum(period_grades) / len(period_grades)
                avg_item = QTableWidgetItem(f"{course_average:.2f}")
                
                # Colorear según el promedio
                if course_average >= 16:
                    avg_item.setBackground(QColor(212, 237, 218))  # Verde
                elif course_average >= 11:
                    avg_item.setBackground(QColor(255, 243, 205))  # Amarillo
                else:
                    avg_item.setBackground(QColor(248, 215, 218))  # Rojo
                
                avg_item.setFont(QFont("Arial", 10, QFont.Bold))
                self.averages_table.setItem(row, 5, avg_item)
                all_averages.append(course_average)
            else:
                self.averages_table.setItem(row, 5, QTableWidgetItem("-"))
        
        # Promedio general
        if all_averages:
            general_average = sum(all_averages) / len(all_averages)
            self.general_average_label.setText(f"📊 PROMEDIO GENERAL: {general_average:.2f}")
            
            # Cambiar color según el promedio general
            if general_average >= 16:
                self.general_average_label.setStyleSheet("""
                    background-color: #27ae60;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                """)
            elif general_average >= 11:
                self.general_average_label.setStyleSheet("""
                    background-color: #f39c12;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                """)
            else:
                self.general_average_label.setStyleSheet("""
                    background-color: #e74c3c;
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    font-size: 16px;
                    font-weight: bold;
                    text-align: center;
                """)
        else:
            self.general_average_label.setText("📊 PROMEDIO GENERAL: No hay calificaciones")
            self.general_average_label.setStyleSheet("""
                background-color: #95a5a6;
                color: white;
                padding: 15px;
                border-radius: 8px;
                font-size: 16px;
                font-weight: bold;
                text-align: center;
            """)
        
        self.averages_table.resizeColumnsToContents()

    def update_charts(self, grades_by_subject):
        """Actualizar gráficos con los datos de calificaciones"""
        # Implementación básica de gráficos usando QFrame y QPainter
        # En una implementación real, se podría usar matplotlib o PyQtChart
        
        # Limpiar gráficos anteriores
        for chart in [self.subject_chart, self.evolution_chart]:
            layout = chart.layout()
            if layout:
                while layout.count():
                    item = layout.takeAt(0)
                    widget = item.widget()
                    if widget:
                        widget.deleteLater()
            else:
                chart.setLayout(QVBoxLayout())
        
        # Gráfico de barras para promedios por materia
        subject_layout = QVBoxLayout()
        
        title = QLabel("Promedio por Materia")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        subject_layout.addWidget(title)
        
        # Aquí iría el código para dibujar el gráfico de barras
        # Como ejemplo, mostramos una representación textual
        subjects_avg = {}
        for subject, periods in grades_by_subject.items():
            grades = []
            for period, data in periods.items():
                grades.append(data['calificacion'])
            if grades:
                subjects_avg[subject] = sum(grades) / len(grades)
        
        # Crear una representación visual simple
        chart_widget = QWidget()
        chart_layout = QVBoxLayout(chart_widget)
        chart_layout.setSpacing(5)
        
        max_avg = max(subjects_avg.values()) if subjects_avg else 20
        
        for subject, avg in subjects_avg.items():
            row_layout = QHBoxLayout()
            
            label = QLabel(subject)
            label.setMinimumWidth(150)
            label.setMaximumWidth(150)
            row_layout.addWidget(label)
            
            bar = QFrame()
            bar_width = int((avg / max_avg) * 400)
            bar.setFixedSize(bar_width, 25)
            
            # Color según promedio
            if avg >= 16:
                bar.setStyleSheet("background-color: #2ecc71; border-radius: 3px;")
            elif avg >= 11:
                bar.setStyleSheet("background-color: #f39c12; border-radius: 3px;")
            else:
                bar.setStyleSheet("background-color: #e74c3c; border-radius: 3px;")
                
            row_layout.addWidget(bar)
            
            value = QLabel(f"{avg:.2f}")
            value.setMinimumWidth(50)
            row_layout.addWidget(value)
            
            row_layout.addStretch()
            chart_layout.addLayout(row_layout)
        
        subject_layout.addWidget(chart_widget)
        self.subject_chart.setLayout(subject_layout)
        
        # Gráfico de evolución por período
        evolution_layout = QVBoxLayout()
        
        title = QLabel("Evolución por Período")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        evolution_layout.addWidget(title)
        
        # Aquí iría el código para dibujar el gráfico de líneas
        # Como ejemplo, mostramos una representación textual
        periods = ['1er bimestre', '2do bimestre', '3er bimestre', '4to bimestre']
        period_avgs = {period: [] for period in periods}
        
        for subject, subject_periods in grades_by_subject.items():
            for period in periods:
                if period in subject_periods:
                    period_avgs[period].append(subject_periods[period]['calificacion'])
        
        period_avg_values = {}
        for period, grades in period_avgs.items():
            if grades:
                period_avg_values[period] = sum(grades) / len(grades)
            else:
                period_avg_values[period] = 0
        
        # Crear una representación visual simple
        evolution_widget = QWidget()
        evolution_widget.setMinimumHeight(200)
        self.evolution_chart.setLayout(evolution_layout)
        evolution_layout.addWidget(evolution_widget)
        
        # Aquí se podría implementar un gráfico de líneas real
        # Por ahora, mostramos los valores promedio por período
        period_text = ", ".join([f"{period}: {avg:.2f}" for period, avg in period_avg_values.items() if avg > 0])
        period_label = QLabel(f"Promedios por período: {period_text}")
        period_label.setAlignment(Qt.AlignCenter)
        evolution_layout.addWidget(period_label)
        
    def show_add_grade_dialog(self):
        """Mostrar diálogo para agregar una nueva nota"""
        # Verificar si hay un estudiante seleccionado
        if not hasattr(self, 'current_student_id') or not self.current_student_id:
            QMessageBox.warning(self, "Advertencia", "Debe seleccionar un estudiante primero.")
            return
        
        # Crear diálogo
        dialog = QDialog(self)
        dialog.setWindowTitle("Agregar Nueva Nota")
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("background-color: white;")
        
        layout = QVBoxLayout(dialog)
        
        # Formulario
        form_layout = QVBoxLayout()
        
        # Materia
        subject_layout = QHBoxLayout()
        subject_label = QLabel("Materia:")
        subject_label.setStyleSheet("font-weight: bold;")
        subject_layout.addWidget(subject_label)
        
        self.subject_combo = QComboBox()
        self.subject_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        
        # Cargar materias desde la base de datos
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM materias ORDER BY nombre")
            subjects = cursor.fetchall()
            conn.close()
            
            for subject in subjects:
                self.subject_combo.addItem(subject[1], subject[0])
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar materias: {str(e)}")
        
        subject_layout.addWidget(self.subject_combo)
        form_layout.addLayout(subject_layout)
        
        # Período
        period_layout = QHBoxLayout()
        period_label = QLabel("Período:")
        period_label.setStyleSheet("font-weight: bold;")
        period_layout.addWidget(period_label)
        
        self.period_combo = QComboBox()
        self.period_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        self.period_combo.addItems(["1er bimestre", "2do bimestre", "3er bimestre", "4to bimestre"])
        period_layout.addWidget(self.period_combo)
        form_layout.addLayout(period_layout)
        
        # Calificación
        grade_layout = QHBoxLayout()
        grade_label = QLabel("Calificación:")
        grade_label.setStyleSheet("font-weight: bold;")
        grade_layout.addWidget(grade_label)
        
        self.grade_spinbox = QDoubleSpinBox()
        self.grade_spinbox.setRange(0, 20)
        self.grade_spinbox.setDecimals(2)
        self.grade_spinbox.setValue(15.0)
        self.grade_spinbox.setStyleSheet("""
            QDoubleSpinBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        grade_layout.addWidget(self.grade_spinbox)
        form_layout.addLayout(grade_layout)
        
        # Comentario
        comment_label = QLabel("Comentario:")
        comment_label.setStyleSheet("font-weight: bold;")
        form_layout.addWidget(comment_label)
        
        self.comment_text = QTextEdit()
        self.comment_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
        """)
        self.comment_text.setMaximumHeight(100)
        form_layout.addWidget(self.comment_text)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancelar")
        cancel_button.setStyleSheet(AppStyles.get_button_style(primary=False))
        cancel_button.clicked.connect(dialog.reject)
        buttons_layout.addWidget(cancel_button)
        
        save_button = QPushButton("Guardar")
        save_button.setStyleSheet(AppStyles.get_button_style())
        save_button.clicked.connect(lambda: self.save_grade(dialog))
        buttons_layout.addWidget(save_button)
        
        layout.addLayout(buttons_layout)
        
        dialog.exec()
    
    def save_grade(self, dialog):
        """Guardar la nueva calificación en la base de datos"""
        try:
            # Obtener datos del formulario
            subject_id = self.subject_combo.currentData()
            period = self.period_combo.currentText()
            grade = self.grade_spinbox.value()
            comment = self.comment_text.toPlainText()
            
            # Validar datos
            if not subject_id:
                QMessageBox.warning(self, "Advertencia", "Debe seleccionar una materia.")
                return
            
            # Guardar en la base de datos
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Verificar si ya existe una calificación para este estudiante, materia y período
            cursor.execute("""
                SELECT id FROM calificaciones 
                WHERE estudiante_id = ? AND materia_id = ? AND periodo = ?
            """, (self.current_student_id, subject_id, period))
            
            existing_grade = cursor.fetchone()
            
            if existing_grade:
                # Actualizar calificación existente
                cursor.execute("""
                    UPDATE calificaciones 
                    SET nota = ?, comentario = ?, fecha = date('now') 
                    WHERE id = ?
                """, (grade, comment, existing_grade[0]))
                message = "Calificación actualizada correctamente."
            else:
                # Insertar nueva calificación
                cursor.execute("""
                    INSERT INTO calificaciones (estudiante_id, materia_id, periodo, nota, comentario, fecha) 
                    VALUES (?, ?, ?, ?, ?, date('now'))
                """, (self.current_student_id, subject_id, period, grade, comment))
                message = "Calificación agregada correctamente."
            
            conn.commit()
            conn.close()
            
            # Mostrar mensaje de éxito
            QMessageBox.information(self, "Éxito", message)
            
            # Cerrar diálogo
            dialog.accept()
            
            # Recargar calificaciones del estudiante
            self.load_student_grades(self.current_student_id)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar calificación: {str(e)}")