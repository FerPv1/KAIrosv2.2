from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QComboBox, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QGroupBox, QFrame, QSplitter)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon
from app.models.database import Database
from app.utils.styles import AppStyles

class ComunicacionView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Splitter para dividir la pantalla en dos secciones
        splitter = QSplitter(Qt.Vertical)
        
        # Sección para enviar mensajes
        compose_group = QGroupBox("Nuevo Mensaje")
        compose_group.setStyleSheet(AppStyles.get_group_box_style())
        compose_layout = QVBoxLayout()
        
        # Destinatarios (filtros)
        recipients_label = QLabel("Destinatarios:")
        recipients_label.setFont(AppStyles.SUBTITLE_FONT)
        compose_layout.addWidget(recipients_label)
        
        filter_layout = QHBoxLayout()
        
        # Nivel
        nivel_layout = QVBoxLayout()
        nivel_label = QLabel("Nivel:")
        nivel_label.setFont(AppStyles.NORMAL_FONT)
        self.nivel_combo = QComboBox()
        self.nivel_combo.setStyleSheet(AppStyles.get_input_style())
        self.nivel_combo.setMinimumWidth(120)
        self.load_niveles()
        self.nivel_combo.currentIndexChanged.connect(self.on_nivel_changed)
        nivel_layout.addWidget(nivel_label)
        nivel_layout.addWidget(self.nivel_combo)
        filter_layout.addLayout(nivel_layout)
        
        # Grado
        grado_layout = QVBoxLayout()
        grado_label = QLabel("Grado:")
        grado_label.setFont(AppStyles.NORMAL_FONT)
        self.grado_combo = QComboBox()
        self.grado_combo.setStyleSheet(AppStyles.get_input_style())
        self.grado_combo.setMinimumWidth(120)
        self.grado_combo.currentIndexChanged.connect(self.on_grado_changed)
        grado_layout.addWidget(grado_label)
        grado_layout.addWidget(self.grado_combo)
        filter_layout.addLayout(grado_layout)
        
        # Sección
        seccion_layout = QVBoxLayout()
        seccion_label = QLabel("Sección:")
        seccion_label.setFont(AppStyles.NORMAL_FONT)
        self.seccion_combo = QComboBox()
        self.seccion_combo.setStyleSheet(AppStyles.get_input_style())
        self.seccion_combo.setMinimumWidth(120)
        seccion_layout.addWidget(seccion_label)
        seccion_layout.addWidget(self.seccion_combo)
        filter_layout.addLayout(seccion_layout)
        
        filter_layout.addStretch()
        compose_layout.addLayout(filter_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #dddddd;")
        compose_layout.addWidget(separator)
        
        # Asunto
        subject_label = QLabel("Asunto:")
        subject_label.setFont(AppStyles.NORMAL_FONT)
        compose_layout.addWidget(subject_label)
        
        self.subject_input = QLineEdit()
        self.subject_input.setStyleSheet(AppStyles.get_input_style())
        self.subject_input.setPlaceholderText("Ingrese el asunto del mensaje...")
        compose_layout.addWidget(self.subject_input)
        
        # Mensaje
        message_label = QLabel("Mensaje:")
        message_label.setFont(AppStyles.NORMAL_FONT)
        compose_layout.addWidget(message_label)
        
        self.message_input = QTextEdit()
        self.message_input.setStyleSheet("border: 1px solid #dddddd; border-radius: 4px; padding: 8px;")
        self.message_input.setPlaceholderText("Escriba su mensaje aquí...")
        self.message_input.setMinimumHeight(150)
        compose_layout.addWidget(self.message_input)
        
        # Botón de enviar
        send_layout = QHBoxLayout()
        send_layout.addStretch()
        
        self.send_btn = QPushButton("Enviar Mensaje")
        self.send_btn.setIcon(QIcon(AppStyles.get_icon_path("send")))
        self.send_btn.setStyleSheet(AppStyles.get_button_style())
        self.send_btn.clicked.connect(self.send_message)
        send_layout.addWidget(self.send_btn)
        
        compose_layout.addLayout(send_layout)
        compose_group.setLayout(compose_layout)
        
        # Historial de mensajes
        history_group = QGroupBox("Historial de Mensajes")
        history_group.setStyleSheet(AppStyles.get_group_box_style())
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setStyleSheet(AppStyles.get_table_style())
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(["Fecha", "Hora", "Destinatarios", "Asunto", "Estado"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.doubleClicked.connect(self.view_message)
        history_layout.addWidget(self.history_table)
        
        # Botones de acción para historial
        history_actions = QHBoxLayout()
        history_actions.addStretch()
        
        self.refresh_btn = QPushButton("Actualizar Historial")
        self.refresh_btn.setIcon(QIcon(AppStyles.get_icon_path("refresh")))
        self.refresh_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.refresh_btn.clicked.connect(self.load_history)
        history_actions.addWidget(self.refresh_btn)
        
        self.view_btn = QPushButton("Ver Mensaje")
        self.view_btn.setIcon(QIcon(AppStyles.get_icon_path("view")))
        self.view_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.view_btn.clicked.connect(self.view_message)
        history_actions.addWidget(self.view_btn)
        
        history_layout.addLayout(history_actions)
        history_group.setLayout(history_layout)
        
        # Agregar grupos al splitter
        splitter.addWidget(compose_group)
        splitter.addWidget(history_group)
        splitter.setSizes([400, 300])  # Tamaño inicial de cada sección
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Cargar datos iniciales
        self.load_history()
    
    def load_niveles(self):
        """Cargar niveles educativos"""
        try:
            db = Database()
            niveles = db.get_niveles()
            
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Todos los niveles", None)
            
            for nivel in niveles:
                self.nivel_combo.addItem(nivel[1], nivel[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar niveles: {str(e)}")
    
    def on_nivel_changed(self):
        nivel_id = self.nivel_combo.currentData()
        if nivel_id is None:
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nombre FROM grados WHERE nivel_id = ? ORDER BY id", (nivel_id,))
            grados = cursor.fetchall()
            
            self.grado_combo.clear()
            for grado in grados:
                self.grado_combo.addItem(grado[1], grado[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar grados: {str(e)}")
    
    def on_grado_changed(self):
        grado_id = self.grado_combo.currentData()
        if grado_id is None:
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, nombre FROM secciones WHERE grado_id = ? ORDER BY id", (grado_id,))
            secciones = cursor.fetchall()
            
            self.seccion_combo.clear()
            for seccion in secciones:
                self.seccion_combo.addItem(seccion[1], seccion[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar secciones: {str(e)}")
    
    def send_message(self):
        nivel_id = self.nivel_combo.currentData()
        grado_id = self.grado_combo.currentData()
        seccion_id = self.seccion_combo.currentData()
        subject = self.subject_input.text().strip()
        message = self.message_input.toPlainText().strip()
        
        if not subject or not message:
            QMessageBox.warning(self, "Advertencia", "Por favor complete el asunto y el mensaje")
            return
        
        # Determinar destinatarios
        destinatarios = ""
        if seccion_id:
            destinatarios = f"{self.nivel_combo.currentText()} - {self.grado_combo.currentText()} - {self.seccion_combo.currentText()}"
        elif grado_id:
            destinatarios = f"{self.nivel_combo.currentText()} - {self.grado_combo.currentText()}"
        elif nivel_id:
            destinatarios = f"{self.nivel_combo.currentText()}"
        else:
            destinatarios = "Todos"
        
        # En un sistema real, aquí se enviaría el mensaje por correo electrónico, SMS, etc.
        # Para este ejemplo, solo lo guardaremos en la base de datos
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de mensajes, si no, crearla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mensajes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    hora TEXT,
                    destinatarios TEXT,
                    asunto TEXT,
                    mensaje TEXT,
                    estado TEXT,
                    usuario_id INTEGER,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Obtener fecha y hora actual
            now = QDateTime.currentDateTime()
            fecha = now.toString("yyyy-MM-dd")
            hora = now.toString("HH:mm:ss")
            
            # Insertar mensaje
            cursor.execute("""
                INSERT INTO mensajes (fecha, hora, destinatarios, asunto, mensaje, estado, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (fecha, hora, destinatarios, subject, message, "enviado", self.user_data['id']))
            
            conn.commit()
            
            QMessageBox.information(self, "Éxito", "Mensaje enviado correctamente")
            
            # Limpiar formulario
            self.subject_input.clear()
            self.message_input.clear()
            
            # Actualizar historial
            self.load_history()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al enviar mensaje: {str(e)}")
    
    def load_history(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de mensajes
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='mensajes'
            """)
            
            if not cursor.fetchone():
                # Si no existe la tabla, crearla
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS mensajes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        hora TEXT,
                        destinatarios TEXT,
                        asunto TEXT,
                        mensaje TEXT,
                        estado TEXT,
                        usuario_id INTEGER,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                """)
                conn.commit()
            
            # Cargar mensajes del usuario actual
            cursor.execute("""
                SELECT id, fecha, hora, destinatarios, asunto, estado
                FROM mensajes
                WHERE usuario_id = ?
                ORDER BY fecha DESC, hora DESC
            """, (self.user_data['id'],))
            
            messages = cursor.fetchall()
            
            self.history_table.setRowCount(len(messages))
            for row, message in enumerate(messages):
                # Guardar el ID del mensaje como dato oculto
                self.history_table.setItem(row, 0, QTableWidgetItem(message[1]))  # Fecha
                self.history_table.setItem(row, 1, QTableWidgetItem(message[2]))  # Hora
                self.history_table.setItem(row, 2, QTableWidgetItem(message[3]))  # Destinatarios
                self.history_table.setItem(row, 3, QTableWidgetItem(message[4]))  # Asunto
                
                # Estado con color
                estado_item = QTableWidgetItem(message[5])
                if message[5] == "enviado":
                    estado_item.setForeground(QColor(AppStyles.SECONDARY_COLOR))
                elif message[5] == "leído":
                    estado_item.setForeground(QColor("green"))
                elif message[5] == "error":
                    estado_item.setForeground(QColor(AppStyles.ACCENT_COLOR))
                
                self.history_table.setItem(row, 4, estado_item)
                
                # Guardar el ID del mensaje como dato oculto
                self.history_table.item(row, 0).setData(Qt.UserRole, message[0])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar historial: {str(e)}")
    
    def view_message(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Seleccione un mensaje para ver")
            return
        
        row = selected_rows[0].row()
        message_id = self.history_table.item(row, 0).data(Qt.UserRole)
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT fecha, hora, destinatarios, asunto, mensaje
                FROM mensajes
                WHERE id = ?
            """, (message_id,))
            
            message = cursor.fetchone()
            if message:
                # Mostrar detalles del mensaje
                details = f"Fecha: {message[0]} {message[1]}\n\n"
                details += f"Destinatarios: {message[2]}\n\n"
                details += f"Asunto: {message[3]}\n\n"
                details += f"Mensaje:\n{message[4]}"
                
                QMessageBox.information(self, "Detalles del Mensaje", details)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar mensaje: {str(e)}")