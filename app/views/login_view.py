from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, QLineEdit, 
                             QPushButton, QMessageBox, QHBoxLayout, QFrame, QComboBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont, QIcon
import os
from app.models.database import Database
from app.views.main_window import MainWindow
from app.utils.styles import AppStyles

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KairosApp - Login")
        self.setMinimumSize(800, 500)
        self.setup_ui()
    
    def setup_ui(self):
        # Layout principal
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel izquierdo (imagen/logo)
        left_panel = QFrame()
        left_panel.setStyleSheet(f"background-color: {AppStyles.PRIMARY_COLOR};")
        left_layout = QVBoxLayout(left_panel)
        
        # Título en el panel izquierdo
        app_title = QLabel("KAIROSAPP")
        app_title.setFont(QFont("Segoe UI", 36, QFont.Bold))
        app_title.setStyleSheet(f"color: {AppStyles.LIGHT_TEXT_COLOR};")
        app_title.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(app_title)
        
        # Subtítulo
        app_subtitle = QLabel("Gestión Escolar Inteligente")
        app_subtitle.setFont(QFont("Segoe UI", 16))
        app_subtitle.setStyleSheet(f"color: {AppStyles.LIGHT_TEXT_COLOR};")
        app_subtitle.setAlignment(Qt.AlignCenter)
        left_layout.addWidget(app_subtitle)
        
        # Panel derecho (formulario)
        right_panel = QFrame()
        right_panel.setStyleSheet(f"background-color: {AppStyles.BACKGROUND_COLOR};")
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título del formulario
        login_title = QLabel("Iniciar Sesión")
        login_title.setFont(AppStyles.TITLE_FONT)
        login_title.setAlignment(Qt.AlignCenter)
        right_layout.addWidget(login_title)
        
        # Espaciador
        right_layout.addSpacing(30)
        
        # Usuario
        user_label = QLabel("Usuario")
        user_label.setFont(AppStyles.NORMAL_FONT)
        right_layout.addWidget(user_label)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Ingrese su nombre de usuario")
        self.user_input.setStyleSheet(AppStyles.get_input_style())
        self.user_input.setMinimumHeight(40)
        right_layout.addWidget(self.user_input)
        
        right_layout.addSpacing(20)
        
        # Contraseña
        password_label = QLabel("Contraseña")
        password_label.setFont(AppStyles.NORMAL_FONT)
        right_layout.addWidget(password_label)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Ingrese su contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet(AppStyles.get_input_style())
        self.password_input.setMinimumHeight(40)
        right_layout.addWidget(self.password_input)
        
        right_layout.addSpacing(20)
        
        # Tipo de usuario
        user_type_label = QLabel("Tipo de Usuario")
        user_type_label.setFont(AppStyles.NORMAL_FONT)
        right_layout.addWidget(user_type_label)
        
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Director/Profesor", "Estudiante", "Padre de Familia"])
        self.user_type_combo.setStyleSheet(AppStyles.get_input_style())
        self.user_type_combo.setMinimumHeight(40)
        right_layout.addWidget(self.user_type_combo)
        
        right_layout.addSpacing(30)
        
        # Botón de login
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setMinimumHeight(50)
        self.login_button.setStyleSheet(AppStyles.get_button_style())
        self.login_button.clicked.connect(self.login)
        right_layout.addWidget(self.login_button)
        
        # Información de usuarios de prueba
        info_label = QLabel(
            "Usuarios de prueba:\n"
            "• Director: director / admin123\n"
            "• Profesor: profesor1 / prof123\n"
            "• Estudiante: estudiante1 / est123\n"
            "• Padre: padre1 / padre123"
        )
        info_label.setFont(QFont("Segoe UI", 9))
        info_label.setStyleSheet("color: #666; background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        right_layout.addWidget(info_label)
        
        # Espaciador
        right_layout.addStretch()
        
        # Agregar paneles al layout principal
        main_layout.addWidget(left_panel, 1)
        main_layout.addWidget(right_panel, 1)
    
    def login(self):
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()
        selected_type = self.user_type_combo.currentText()
        
        # Mapear tipo seleccionado a tipo en BD
        type_mapping = {
            "Director/Profesor": ["director", "profesor"],
            "Estudiante": ["estudiante"],
            "Padre de Familia": ["padre"]
        }
        
        if not username or not password:
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return
        
        try:
            # Verificar credenciales en la base de datos
            db = Database()
            conn = db.connect()
            
            with conn:  # Use context manager for automatic cleanup
                cursor = conn.cursor()
                
                # Verificar credenciales y tipo de usuario
                allowed_types = type_mapping[selected_type]
                placeholders = ','.join(['?' for _ in allowed_types])
                
                cursor.execute(
                    f"SELECT id, nombre, apellido, tipo FROM usuarios WHERE usuario = ? AND contrasena = ? AND tipo IN ({placeholders})", 
                    [username, password] + allowed_types
                )
                user = cursor.fetchone()
                
                if user:
                    user_data = {
                        'id': user[0],
                        'nombre': user[1],
                        'apellido': user[2],
                        'tipo': user[3],
                        'usuario': username
                    }
                    
                    # Abrir ventana principal
                    self.main_window = MainWindow(user_data)
                    self.main_window.show()
                    self.close()
                else:
                    QMessageBox.warning(
                        self, "Error", 
                        f"Usuario o contraseña incorrectos, o no tiene permisos como {selected_type.lower()}"
                    )
                    
        except Exception as e:
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al conectar con la base de datos: {str(e)}")
            print(f"Error en login: {e}")


import os
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QPushButton, QComboBox, QFrame)
from PySide6.QtGui import QPixmap, QIcon, QFont, QColor, QPainter, QBrush, QLinearGradient
from PySide6.QtCore import Qt, QSize

class LoginView(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("KAIROSAPP - Login")
        self.setMinimumSize(400, 600)
        
        # Configurar el fondo con degradado
        self.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, 
                                          stop:0 #6a11cb, stop:1 #2575fc);
            }
        """)
        
        # Layout principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        main_layout.setAlignment(Qt.AlignCenter)
        
        # Panel de login (tarjeta semi-transparente)
        login_panel = QFrame()
        login_panel.setObjectName("loginPanel")
        login_panel.setStyleSheet("""
            #loginPanel {
                background-color: rgba(255, 255, 255, 0.15);
                border-radius: 20px;
                padding: 20px;
            }
        """)
        
        panel_layout = QVBoxLayout(login_panel)
        panel_layout.setSpacing(15)
        panel_layout.setContentsMargins(30, 30, 30, 30)
        
        # Logo y título
        logo_layout = QVBoxLayout()
        logo_layout.setAlignment(Qt.AlignCenter)
        
        # Logo personalizado
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "icons", "kairos_logo.png")
        
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_pixmap = logo_pixmap.scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            logo_label.setPixmap(logo_pixmap)
            logo_label.setFixedSize(80, 80)
        else:
            # Crear un logo temporal con colores similares a la imagen
            logo_label.setText("")
            logo_label.setFixedSize(80, 80)
            logo_label.setStyleSheet("""
                background-color: #1e3a8a;
                border-radius: 40px;
                border: 2px solid #3b82f6;
            """)
        
        logo_layout.addWidget(logo_label)
        
        # Nombre de la aplicación
        app_name = QLabel("KAIROSAPP")
        app_name.setStyleSheet("""
            font-size: 24px; 
            font-weight: bold; 
            color: white;
        """)
        app_name.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(app_name)
        
        # Subtítulo
        subtitle = QLabel("Gestión Escolar Inteligente")
        subtitle.setStyleSheet("""
            font-size: 14px; 
            color: white;
            margin-bottom: 10px;
        """)
        subtitle.setAlignment(Qt.AlignCenter)
        logo_layout.addWidget(subtitle)
        
        panel_layout.addLayout(logo_layout)
        panel_layout.addSpacing(20)
        
        # Campo de usuario con ícono
        user_container = QFrame()
        user_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 5px;
        """)
        user_layout = QHBoxLayout(user_container)
        user_layout.setContentsMargins(10, 0, 10, 0)
        
        user_icon = QLabel()
        user_icon.setText("👤")
        user_icon.setStyleSheet("color: #333; font-size: 16px;")
        user_layout.addWidget(user_icon)
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Usuario")
        self.user_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 10px 5px;
                background: transparent;
                color: #333;
                font-size: 14px;
            }
        """)
        user_layout.addWidget(self.user_input)
        panel_layout.addWidget(user_container)
        
        # Campo de contraseña con ícono
        password_container = QFrame()
        password_container.setStyleSheet("""
            background-color: rgba(255, 255, 255, 0.7);
            border-radius: 5px;
        """)
        password_layout = QHBoxLayout(password_container)
        password_layout.setContentsMargins(10, 0, 10, 0)
        
        password_icon = QLabel()
        password_icon.setText("🔒")
        password_icon.setStyleSheet("color: #333; font-size: 16px;")
        password_layout.addWidget(password_icon)
        
        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Contraseña")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("""
            QLineEdit {
                border: none;
                padding: 10px 5px;
                background: transparent;
                color: #333;
                font-size: 14px;
            }
        """)
        password_layout.addWidget(self.password_input)
        panel_layout.addWidget(password_container)
        
        # Selector de tipo de usuario
        user_type_label = QLabel("Tipo de Usuario")
        user_type_label.setStyleSheet("color: white; font-size: 14px;")
        panel_layout.addWidget(user_type_label)
        
        self.user_type_combo = QComboBox()
        self.user_type_combo.addItems(["Director/Profesor", "Estudiante", "Administrador"])
        self.user_type_combo.setStyleSheet("""
            QComboBox {
                padding: 10px;
                background-color: rgba(255, 255, 255, 0.7);
                border-radius: 5px;
                color: #333;
                font-size: 14px;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
        """)
        panel_layout.addWidget(self.user_type_combo)
        
        panel_layout.addSpacing(20)
        
        # Botón de inicio de sesión
        self.login_button = QPushButton("Iniciar Sesión")
        self.login_button.setCursor(Qt.PointingHandCursor)
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1c6ea4;
            }
        """)
        self.login_button.clicked.connect(self.login)
        panel_layout.addWidget(self.login_button)
        
        # Enlace para recuperar contraseña
        forgot_password = QPushButton("¿Olvidaste tu contraseña?")
        forgot_password.setCursor(Qt.PointingHandCursor)
        forgot_password.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: none;
                font-size: 12px;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #3498db;
            }
        """)
        panel_layout.addWidget(forgot_password)
        
        main_layout.addWidget(login_panel)
        self.setLayout(main_layout)
    
    def login(self):
        username = self.user_input.text().strip()
        password = self.password_input.text().strip()
        selected_type = self.user_type_combo.currentText()
        
        # Mapear tipo seleccionado a tipo en BD
        type_mapping = {
            "Director/Profesor": ["director", "profesor"],
            "Estudiante": ["estudiante"],
            "Administrador": ["admin"]
        }
        
        if not username or not password:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Por favor ingrese usuario y contraseña")
            return
        
        try:
            # Verificar credenciales en la base de datos
            db = Database()
            conn = db.connect()
            
            with conn:  # Use context manager for automatic cleanup
                cursor = conn.cursor()
                
                # Verificar credenciales y tipo de usuario
                allowed_types = type_mapping[selected_type]
                placeholders = ','.join(['?' for _ in allowed_types])
                
                cursor.execute(
                    f"SELECT id, nombre, apellido, tipo FROM usuarios WHERE usuario = ? AND contrasena = ? AND tipo IN ({placeholders})", 
                    [username, password] + allowed_types
                )
                user = cursor.fetchone()
                
                if user:
                    user_data = {
                        'id': user[0],
                        'nombre': user[1],
                        'apellido': user[2],
                        'tipo': user[3],
                        'usuario': username
                    }
                    
                    # Abrir ventana principal
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.information(self, "Éxito", f"Bienvenido {user_data['nombre']} {user_data['apellido']}")
                    
                    self.main_window = MainWindow(user_data)
                    self.main_window.show()
                    self.close()
                else:
                    from PySide6.QtWidgets import QMessageBox
                    QMessageBox.warning(
                        self, "Error", 
                        f"Usuario o contraseña incorrectos, o no tiene permisos como {selected_type.lower()}"
                    )
                    
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error de Base de Datos", f"Error al conectar con la base de datos: {str(e)}")
            print(f"Error en login: {e}")
        
    def paintEvent(self, event):
        # Agregar efecto de partículas/puntos brillantes en el fondo
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Dibujar algunos puntos brillantes aleatorios
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(255, 255, 255, 30)))
        
        # Puntos fijos para el efecto de brillo
        points = [(50, 50), (150, 100), (250, 200), (350, 150), 
                 (100, 300), (200, 400), (300, 350), (400, 450),
                 (75, 125), (175, 225), (275, 325), (375, 425)]
        
        for x, y in points:
            size = 2 + (x % 3)  # Tamaños variables para los puntos
            painter.drawEllipse(x, y, size, size)