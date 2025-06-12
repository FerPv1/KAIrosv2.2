from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QLineEdit, QGroupBox, QFormLayout, QMessageBox, QFileDialog,
                             QFrame, QSizePolicy)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QIcon, QPixmap
import os
from app.models.database import Database
from app.utils.styles import AppStyles

class ConfiguracionView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.profile_image_path = None
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título principal con estilo mejorado
        title_container = QFrame()
        title_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #3498db, stop:1 #2980b9);
            border-radius: 10px;
            padding: 5px;
        """)
        title_layout = QVBoxLayout(title_container)
        
        title_label = QLabel("Configuración de Perfil")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Gestiona tu información personal y preferencias")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: white;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(title_container)
        
        # Contenido principal
        content_layout = QHBoxLayout()
        
        # Panel izquierdo - Imagen de perfil
        left_panel = QGroupBox("Imagen de Perfil")
        left_panel.setStyleSheet(AppStyles.get_group_box_style())
        left_layout = QVBoxLayout(left_panel)
        
        # Imagen de perfil
        self.profile_image = QLabel()
        self.profile_image.setAlignment(Qt.AlignCenter)
        self.profile_image.setMinimumSize(200, 200)
        self.profile_image.setMaximumSize(200, 200)
        self.profile_image.setStyleSheet("""
            background-color: #f5f5f5;
            border: 2px solid #ddd;
            border-radius: 100px;
        """)
        
        # Cargar imagen de perfil si existe
        default_image = QPixmap("resources/icons/user.png")
        if default_image.isNull():
            # Si no se encuentra la imagen, usar un texto
            self.profile_image.setText(f"{self.user_data['nombre'][0]}{self.user_data['apellido'][0]}")
            self.profile_image.setStyleSheet("""
                background-color: #3498db;
                color: white;
                font-size: 48px;
                font-weight: bold;
                border-radius: 100px;
            """)
        else:
            # Redimensionar y hacer circular la imagen
            default_image = default_image.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_image.setPixmap(default_image)
        
        left_layout.addWidget(self.profile_image)
        
        # Botón para cambiar imagen
        change_image_btn = QPushButton("Cambiar Imagen")
        change_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        change_image_btn.clicked.connect(self.change_profile_image)
        left_layout.addWidget(change_image_btn)
        
        content_layout.addWidget(left_panel)
        
        # Panel derecho - Información del perfil
        right_panel = QGroupBox("Información del Perfil")
        right_panel.setStyleSheet(AppStyles.get_group_box_style())
        right_layout = QVBoxLayout(right_panel)
        
        # Formulario de datos personales
        form_layout = QFormLayout()
        
        # Nombre
        self.nombre_edit = QLineEdit(self.user_data['nombre'])
        self.nombre_edit.setStyleSheet(AppStyles.get_line_edit_style())
        form_layout.addRow("Nombre:", self.nombre_edit)
        
        # Apellido
        self.apellido_edit = QLineEdit(self.user_data['apellido'])
        self.apellido_edit.setStyleSheet(AppStyles.get_line_edit_style())
        form_layout.addRow("Apellido:", self.apellido_edit)
        
        # Email
        self.email_edit = QLineEdit(self.user_data.get('email', ''))
        self.email_edit.setStyleSheet(AppStyles.get_line_edit_style())
        form_layout.addRow("Email:", self.email_edit)
        
        # Rol (no editable)
        self.rol_label = QLabel(self.user_data.get('rol', 'Usuario'))
        form_layout.addRow("Rol:", self.rol_label)
        
        right_layout.addLayout(form_layout)
        
        # Sección para cambiar contraseña
        password_group = QGroupBox("Cambiar Contraseña")
        password_group.setStyleSheet(AppStyles.get_group_box_style())
        password_layout = QFormLayout(password_group)
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        self.current_password.setStyleSheet(AppStyles.get_line_edit_style())
        password_layout.addRow("Contraseña Actual:", self.current_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        self.new_password.setStyleSheet(AppStyles.get_line_edit_style())
        password_layout.addRow("Nueva Contraseña:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        self.confirm_password.setStyleSheet(AppStyles.get_line_edit_style())
        password_layout.addRow("Confirmar Contraseña:", self.confirm_password)
        
        right_layout.addWidget(password_group)
        
        # Botones de acción
        buttons_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar Cambios")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.clicked.connect(self.save_changes)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_changes)
        buttons_layout.addWidget(cancel_btn)
        
        right_layout.addLayout(buttons_layout)
        content_layout.addWidget(right_panel)
        
        main_layout.addLayout(content_layout)
        self.setLayout(main_layout)
    
    def change_profile_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, "Seleccionar Imagen de Perfil", "", "Imágenes (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            self.profile_image_path = file_path
            pixmap = QPixmap(file_path)
            pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.profile_image.setPixmap(pixmap)
            self.profile_image.setStyleSheet("""
                border: 2px solid #ddd;
                border-radius: 100px;
            """)
    
    def save_changes(self):
        # Validar cambios de contraseña
        if self.new_password.text() or self.confirm_password.text() or self.current_password.text():
            if not self.current_password.text():
                QMessageBox.warning(self, "Error", "Debe ingresar su contraseña actual para cambiarla.")
                return
            
            if self.new_password.text() != self.confirm_password.text():
                QMessageBox.warning(self, "Error", "Las contraseñas nuevas no coinciden.")
                return
            
            # Aquí iría la validación con la base de datos
            # self.db.validate_password(self.user_data['id'], self.current_password.text())
            
            # Actualizar contraseña
            # self.db.update_password(self.user_data['id'], self.new_password.text())
        
        # Actualizar datos del perfil
        updated_data = {
            'nombre': self.nombre_edit.text(),
            'apellido': self.apellido_edit.text(),
            'email': self.email_edit.text()
        }
        
        # Actualizar imagen si se cambió
        if self.profile_image_path:
            # Aquí iría el código para guardar la imagen en el servidor/sistema
            # y actualizar la ruta en la base de datos
            pass
        
        # Actualizar en la base de datos
        # self.db.update_user_profile(self.user_data['id'], updated_data)
        
        # Actualizar datos locales
        self.user_data.update(updated_data)
        
        QMessageBox.information(self, "Éxito", "Los cambios han sido guardados correctamente.")
    
    def cancel_changes(self):
        # Restaurar valores originales
        self.nombre_edit.setText(self.user_data['nombre'])
        self.apellido_edit.setText(self.user_data['apellido'])
        self.email_edit.setText(self.user_data.get('email', ''))
        
        self.current_password.clear()
        self.new_password.clear()
        self.confirm_password.clear()
        
        # Restaurar imagen original
        default_image = QPixmap("resources/icons/user.png")
        if not default_image.isNull():
            self.profile_image.setPixmap(default_image.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        self.profile_image_path = None
        
        QMessageBox.information(self, "Cancelado", "Los cambios han sido descartados.")