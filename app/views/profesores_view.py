from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QTableWidget, QTableWidgetItem, QComboBox, QLineEdit,
                             QGroupBox, QFormLayout, QMessageBox, QHeaderView, QDialog,
                             QDialogButtonBox, QStackedWidget)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon
from app.models.database import Database
from app.utils.styles import AppStyles
import os
from datetime import datetime

class ProfesoresView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.load_initial_data()
    
    def setup_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        
        # Crear el stacked widget para alternar entre vistas
        self.stacked_widget = QStackedWidget()
        
        # Crear la vista de lista
        self.list_view = self.create_list_view()
        self.stacked_widget.addWidget(self.list_view)
        
        # Crear la vista de formulario
        self.form_view = self.create_form_view()
        self.stacked_widget.addWidget(self.form_view)
        
        self.main_layout.addWidget(self.stacked_widget)
        
        # Mostrar la vista de lista por defecto
        self.show_list_view()
    
    def create_list_view(self):
        """Crear la vista de lista de profesores"""
        list_widget = QWidget()
        layout = QVBoxLayout(list_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Título y botones de acción
        header_layout = QHBoxLayout()
        
        title = QLabel("Lista de Profesores")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        
        # Botón para agregar nuevo profesor
        add_btn = QPushButton("Agregar Profesor")
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
        self.search_input.setPlaceholderText("Buscar por nombre o especialidad...")
        self.search_input.setStyleSheet(AppStyles.get_line_edit_style())
        self.search_input.textChanged.connect(self.filter_teachers)
        filter_layout.addWidget(self.search_input)
        
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tabla de profesores
        self.teachers_table = QTableWidget()
        self.teachers_table.setColumnCount(6)
        self.teachers_table.setHorizontalHeaderLabels(["ID", "Nombre", "Email", "Teléfono", "Especialidad", "Acciones"])
        self.teachers_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.teachers_table.setStyleSheet("""QTableWidget {
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
        layout.addWidget(self.teachers_table)
        
        return list_widget

    def load_initial_data(self):
        """Cargar datos iniciales"""
        self.load_teachers_list()
    
    def load_teachers_list(self):
        """Cargar lista de profesores"""
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
    
    def display_teachers(self, teachers):
        """Mostrar profesores en la tabla"""
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
    
    def filter_teachers(self):
        """Filtrar profesores según texto de búsqueda"""
        search_text = self.search_input.text().lower()
        
        filtered_teachers = []
        
        for teacher in self.all_teachers:
            # Filtrar por texto de búsqueda
            if search_text and search_text not in f"{teacher[1]} {teacher[2]} {teacher[5]}".lower():
                continue
            
            filtered_teachers.append(teacher)
        
        self.display_teachers(filtered_teachers)