from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTabWidget,
                             QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
                             QGroupBox, QFormLayout, QMessageBox, QHeaderView, QLabel,
                             QPushButton)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from app.models.database import Database
from app.utils.styles import AppStyles
from datetime import datetime
import os
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class ListaCombinadaView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        # Layout principal
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Crear TabWidget para alternar entre estudiantes y profesores
        self.tab_widget = QTabWidget()
        
        # Tab de estudiantes
        self.students_tab = QWidget()
        self.setup_students_tab()
        self.tab_widget.addTab(self.students_tab, "Lista de Estudiantes")
        
        # Tab de profesores
        self.teachers_tab = QWidget()
        self.setup_teachers_tab()
        self.tab_widget.addTab(self.teachers_tab, "Lista de Profesores")
        
        self.main_layout.addWidget(self.tab_widget)
    
    def setup_students_tab(self):
        layout = QVBoxLayout(self.students_tab)
        
        # Título y botones de acción
        header_layout = QHBoxLayout()
        
        title = QLabel("Lista de Estudiantes")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para exportar a PDF
        export_btn = QPushButton("Exportar a PDF")
        export_btn.setIcon(QIcon(AppStyles.get_icon_path("pdf")))
        export_btn.setStyleSheet(AppStyles.get_button_style())
        export_btn.clicked.connect(self.export_students_to_pdf)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Filtros de búsqueda
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_group.setStyleSheet(AppStyles.get_group_box_style())
        filter_layout = QHBoxLayout()
        
        # Búsqueda por texto
        self.student_search_input = QLineEdit()
        self.student_search_input.setPlaceholderText("Buscar por nombre o código...")
        self.student_search_input.setStyleSheet(AppStyles.get_line_edit_style())
        self.student_search_input.textChanged.connect(self.filter_students)
        filter_layout.addWidget(self.student_search_input)
        
        # Filtros académicos
        filter_layout.addWidget(QLabel("Nivel:"))
        self.nivel_combo = QComboBox()
        self.nivel_combo.addItem("Todos", None)
        self.nivel_combo.currentIndexChanged.connect(self.filter_students)
        filter_layout.addWidget(self.nivel_combo)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tabla de estudiantes
        self.students_table = QTableWidget()
        self.students_table.setColumnCount(7)
        self.students_table.setHorizontalHeaderLabels(["Código", "Nombre", "Nivel", "Grado", "Sección", "Email", "Acciones"])
        self.students_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.students_table.setStyleSheet(AppStyles.get_table_style())
        layout.addWidget(self.students_table)
    
    def setup_teachers_tab(self):
        layout = QVBoxLayout(self.teachers_tab)
        
        # Título y botones de acción
        header_layout = QHBoxLayout()
        
        title = QLabel("Lista de Profesores")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para exportar a PDF
        export_btn = QPushButton("Exportar a PDF")
        export_btn.setIcon(QIcon(AppStyles.get_icon_path("pdf")))
        export_btn.setStyleSheet(AppStyles.get_button_style())
        export_btn.clicked.connect(self.export_teachers_to_pdf)
        header_layout.addWidget(export_btn)
        
        layout.addLayout(header_layout)
        
        # Filtros de búsqueda
        filter_group = QGroupBox("Filtros de Búsqueda")
        filter_group.setStyleSheet(AppStyles.get_group_box_style())
        filter_layout = QHBoxLayout()
        
        # Búsqueda por texto
        self.teacher_search_input = QLineEdit()
        self.teacher_search_input.setPlaceholderText("Buscar por nombre o especialidad...")
        self.teacher_search_input.setStyleSheet(AppStyles.get_line_edit_style())
        self.teacher_search_input.textChanged.connect(self.filter_teachers)
        filter_layout.addWidget(self.teacher_search_input)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tabla de profesores
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(6)
        self.teachers_table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono", "Especialidad", "Acciones"])
        self.teachers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachers_table.setStyleSheet(AppStyles.get_table_style())
        layout.addWidget(self.teachers_table)
    
    def load_initial_data(self):
        self.load_students_list()
        self.load_teachers_list()
    
    def load_students_list(self):
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
    
    def load_teachers_list(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            query = """
                SELECT id, nombre, apellido, email, telefono, especialidad
                FROM profesores
                ORDER BY apellido, nombre
            """
            
            cursor.execute(query)
            self.all_teachers = cursor.fetchall()
            
            self.display_teachers(self.all_teachers)
            
            conn.close()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando profesores: {e}")
    
    def display_students(self, students):
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
    
    def display_teachers(self, teachers):
        self.teachers_table.setRowCount(len(teachers))
        
        for row, teacher in enumerate(teachers):
            # ID
            self.teachers_table.setItem(row, 0, QTableWidgetItem(str(teacher[0])))
            # Nombre completo
            self.teachers_table.setItem(row, 1, QTableWidgetItem(f"{teacher[1]} {teacher[2]}"))
            # Email
            self.teachers_table.setItem(row, 2, QTableWidgetItem(teacher[3] or "N/A"))
            # Teléfono
            self.teachers_table.setItem(row, 3, QTableWidgetItem(teacher[4] or "N/A"))
            # Especialidad
            self.teachers_table.setItem(row, 4, QTableWidgetItem(teacher[5] or "N/A"))
            
            # Botones de acción
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            # Botón Editar
            edit_btn = QPushButton("Editar")
            edit_btn.setStyleSheet("background-color: #3498db; color: white; border-radius: 3px; padding: 3px;")
            edit_btn.clicked.connect(lambda checked, t=teacher[0]: self.edit_teacher(t))
            actions_layout.addWidget(edit_btn)
            
            # Botón Eliminar
            delete_btn = QPushButton("Eliminar")
            delete_btn.setStyleSheet("background-color: #e74c3c; color: white; border-radius: 3px; padding: 3px;")
            delete_btn.clicked.connect(lambda checked, t=teacher[0]: self.delete_teacher(t))
            actions_layout.addWidget(delete_btn)
            
            self.teachers_table.setCellWidget(row, 5, actions_widget)
    
    def filter_students(self):
        search_text = self.student_search_input.text().lower()
        nivel_id = self.nivel_combo.currentData()
        
        filtered_students = []
        
        for student in self.all_students:
            # Filtrar por texto de búsqueda
            if search_text and search_text not in f"{student[1]} {student[2]} {student[3]}".lower():
                continue
            
            # Filtrar por nivel
            if nivel_id and student[8] != nivel_id:
                continue
            
            filtered_students.append(student)
        
        self.display_students(filtered_students)
    
    def filter_teachers(self):
        search_text = self.teacher_search_input.text().lower()
        
        filtered_teachers = []
        
        for teacher in self.all_teachers:
            # Filtrar por texto de búsqueda
            if search_text and search_text not in f"{teacher[1]} {teacher[2]} {teacher[5]}".lower():
                continue
            
            filtered_teachers.append(teacher)
        
        self.display_teachers(filtered_teachers)
    
    def export_students_to_pdf(self):
        try:
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"lista_estudiantes_{timestamp}.pdf")
            
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            story.append(Paragraph("Lista de Estudiantes", title_style))
            story.append(Spacer(1, 12))
            
            # Tabla de estudiantes
            data = [["Código", "Nombre", "Nivel", "Grado", "Sección", "Email"]]
            
            for student in self.all_students:
                data.append([
                    student[1] or "N/A",
                    f"{student[2]} {student[3]}",
                    student[5] or "N/A",
                    student[6] or "N/A",
                    student[7] or "N/A",
                    student[4] or "N/A"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            
            # Generar PDF
            doc.build(story)
            
            QMessageBox.information(self, "Éxito", f"Lista de estudiantes exportada exitosamente:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar lista de estudiantes: {str(e)}")
    
    def export_teachers_to_pdf(self):
        try:
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"lista_profesores_{timestamp}.pdf")
            
            # Crear documento
            doc = SimpleDocTemplate(filename, pagesize=A4)
            story = []
            styles = getSampleStyleSheet()
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=18,
                spaceAfter=30,
                alignment=1  # Centrado
            )
            story.append(Paragraph("Lista de Profesores", title_style))
            story.append(Spacer(1, 12))
            
            # Tabla de profesores
            data = [["ID", "Nombre", "Email", "Teléfono", "Especialidad"]]
            
            for teacher in self.all_teachers:
                data.append([
                    str(teacher[0]),
                    f"{teacher[1]} {teacher[2]}",
                    teacher[3] or "N/A",
                    teacher[4] or "N/A",
                    teacher[5] or "N/A"
                ])
            
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(table)
            
            # Generar PDF
            doc.build(story)
            
            QMessageBox.information(self, "Éxito", f"Lista de profesores exportada exitosamente:\n{filename}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar lista de profesores: {str(e)}")