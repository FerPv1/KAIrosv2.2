from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QComboBox, QTextEdit, QLineEdit, QTableWidget, QTableWidgetItem,
                             QHeaderView, QMessageBox, QGroupBox, QFrame, QSplitter, QSizePolicy,
                             QCheckBox, QRadioButton, QButtonGroup, QScrollArea, QGridLayout)
from PySide6.QtCore import Qt, QDateTime
from PySide6.QtGui import QIcon, QFont, QColor
from app.models.database import Database
from app.utils.styles import AppStyles
import datetime
from PySide6.QtGui import QColor

class AlertasView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Título principal con estilo mejorado
        title_container = QFrame()
        title_container.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                stop:0 #e74c3c, stop:1 #c0392b);
            border-radius: 10px;
            padding: 5px;
        """)
        title_layout = QVBoxLayout(title_container)
        
        title_label = QLabel("Sistema de Alertas")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setStyleSheet("color: white;")
        title_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(title_label)
        
        subtitle_label = QLabel("Envío de notificaciones a padres de familia")
        subtitle_label.setFont(QFont("Segoe UI", 12))
        subtitle_label.setStyleSheet("color: white;")
        subtitle_label.setAlignment(Qt.AlignCenter)
        title_layout.addWidget(subtitle_label)
        
        main_layout.addWidget(title_container)
        
        # Splitter para dividir la pantalla en dos secciones
        splitter = QSplitter(Qt.Vertical)
        
        # Sección para crear alertas
        compose_group = QGroupBox("Crear Nueva Alerta")
        compose_group.setStyleSheet(AppStyles.get_group_box_style())
        compose_layout = QVBoxLayout()
        
        # Tipo de alerta
        alert_type_layout = QHBoxLayout()
        alert_type_label = QLabel("Tipo de Alerta:")
        alert_type_label.setFont(AppStyles.SUBTITLE_FONT)
        alert_type_layout.addWidget(alert_type_label)
        
        self.alert_type_group = QButtonGroup()
        
        self.radio_general = QRadioButton("General")
        self.radio_general.setChecked(True)
        self.alert_type_group.addButton(self.radio_general)
        alert_type_layout.addWidget(self.radio_general)
        
        self.radio_academic = QRadioButton("Académica")
        self.alert_type_group.addButton(self.radio_academic)
        alert_type_layout.addWidget(self.radio_academic)
        
        self.radio_attendance = QRadioButton("Asistencia")
        self.alert_type_group.addButton(self.radio_attendance)
        alert_type_layout.addWidget(self.radio_attendance)
        
        self.radio_behavior = QRadioButton("Comportamiento")
        self.alert_type_group.addButton(self.radio_behavior)
        alert_type_layout.addWidget(self.radio_behavior)
        
        self.radio_emergency = QRadioButton("Emergencia")
        self.alert_type_group.addButton(self.radio_emergency)
        alert_type_layout.addWidget(self.radio_emergency)
        
        alert_type_layout.addStretch()
        compose_layout.addLayout(alert_type_layout)
        
        # Método de envío
        delivery_layout = QHBoxLayout()
        delivery_label = QLabel("Método de envío:")
        delivery_label.setFont(AppStyles.SUBTITLE_FONT)
        delivery_layout.addWidget(delivery_label)
        
        self.check_email = QCheckBox("Correo electrónico")
        self.check_email.setChecked(True)
        delivery_layout.addWidget(self.check_email)
        
        self.check_sms = QCheckBox("SMS")
        self.check_sms.setChecked(True)
        delivery_layout.addWidget(self.check_sms)
        
        self.check_app = QCheckBox("Notificación en App")
        self.check_app.setChecked(True)
        delivery_layout.addWidget(self.check_app)
        
        delivery_layout.addStretch()
        compose_layout.addLayout(delivery_layout)
        
        # Destinatarios (filtros)
        recipients_label = QLabel("Destinatarios:")
        recipients_label.setFont(AppStyles.SUBTITLE_FONT)
        compose_layout.addWidget(recipients_label)
        
        filter_layout = QGridLayout()
        
        # Nivel
        nivel_label = QLabel("Nivel:")
        nivel_label.setFont(AppStyles.NORMAL_FONT)
        filter_layout.addWidget(nivel_label, 0, 0)
        
        self.nivel_combo = QComboBox()
        self.nivel_combo.setStyleSheet(AppStyles.get_input_style())
        self.nivel_combo.setMinimumWidth(120)
        self.load_niveles()
        self.nivel_combo.currentIndexChanged.connect(self.on_nivel_changed)
        filter_layout.addWidget(self.nivel_combo, 0, 1)
        
        # Grado
        grado_label = QLabel("Grado:")
        grado_label.setFont(AppStyles.NORMAL_FONT)
        filter_layout.addWidget(grado_label, 0, 2)
        
        self.grado_combo = QComboBox()
        self.grado_combo.setStyleSheet(AppStyles.get_input_style())
        self.grado_combo.setMinimumWidth(120)
        self.grado_combo.currentIndexChanged.connect(self.on_grado_changed)
        filter_layout.addWidget(self.grado_combo, 0, 3)
        
        # Sección
        seccion_label = QLabel("Sección:")
        seccion_label.setFont(AppStyles.NORMAL_FONT)
        filter_layout.addWidget(seccion_label, 0, 4)
        
        self.seccion_combo = QComboBox()
        self.seccion_combo.setStyleSheet(AppStyles.get_input_style())
        self.seccion_combo.setMinimumWidth(120)
        filter_layout.addWidget(self.seccion_combo, 0, 5)
        
        # Estudiante específico
        estudiante_label = QLabel("Estudiante específico:")
        estudiante_label.setFont(AppStyles.NORMAL_FONT)
        filter_layout.addWidget(estudiante_label, 1, 0)
        
        self.estudiante_combo = QComboBox()
        self.estudiante_combo.setStyleSheet(AppStyles.get_input_style())
        self.estudiante_combo.setMinimumWidth(300)
        filter_layout.addWidget(self.estudiante_combo, 1, 1, 1, 3)
        
        # Botón para cargar estudiantes
        self.load_students_btn = QPushButton("Cargar Estudiantes")
        self.load_students_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.load_students_btn.clicked.connect(self.load_students)
        filter_layout.addWidget(self.load_students_btn, 1, 4, 1, 2)
        
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
        self.subject_input.setPlaceholderText("Ingrese el asunto de la alerta...")
        compose_layout.addWidget(self.subject_input)
        
        # Mensaje
        message_label = QLabel("Mensaje:")
        message_label.setFont(AppStyles.NORMAL_FONT)
        compose_layout.addWidget(message_label)
        
        self.message_input = QTextEdit()
        self.message_input.setStyleSheet("border: 1px solid #dddddd; border-radius: 4px; padding: 8px;")
        self.message_input.setPlaceholderText("Escriba el contenido de la alerta aquí...")
        self.message_input.setMinimumHeight(150)
        compose_layout.addWidget(self.message_input)
        
        # Botón de enviar
        send_layout = QHBoxLayout()
        send_layout.addStretch()
        
        self.preview_btn = QPushButton("Vista Previa")
        self.preview_btn.setIcon(QIcon(AppStyles.get_icon_path("view")))
        self.preview_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.preview_btn.clicked.connect(self.preview_alert)
        send_layout.addWidget(self.preview_btn)
        
        self.send_btn = QPushButton("Enviar Alerta")
        self.send_btn.setIcon(QIcon(AppStyles.get_icon_path("send")))
        self.send_btn.setStyleSheet(AppStyles.get_button_style())
        self.send_btn.clicked.connect(self.send_alert)
        send_layout.addWidget(self.send_btn)
        
        compose_layout.addLayout(send_layout)
        compose_group.setLayout(compose_layout)
        
        # Historial de alertas
        history_group = QGroupBox("Historial de Alertas")
        history_group.setStyleSheet(AppStyles.get_group_box_style())
        history_layout = QVBoxLayout()
        
        # Filtros para el historial
        history_filter_layout = QHBoxLayout()
        
        history_filter_layout.addWidget(QLabel("Filtrar por tipo:"))
        self.history_type_combo = QComboBox()
        self.history_type_combo.addItems(["Todas", "General", "Académica", "Asistencia", "Comportamiento", "Emergencia"])
        self.history_type_combo.setStyleSheet(AppStyles.get_input_style())
        self.history_type_combo.currentTextChanged.connect(self.filter_history)
        history_filter_layout.addWidget(self.history_type_combo)
        
        history_filter_layout.addWidget(QLabel("Buscar:"))
        self.history_search = QLineEdit()
        self.history_search.setStyleSheet(AppStyles.get_input_style())
        self.history_search.setPlaceholderText("Buscar en el historial...")
        self.history_search.textChanged.connect(self.filter_history)
        history_filter_layout.addWidget(self.history_search)
        
        history_layout.addLayout(history_filter_layout)
        
        # Tabla de historial
        self.history_table = QTableWidget()
        self.history_table.setStyleSheet(AppStyles.get_table_style())
        self.history_table.setColumnCount(6)
        self.history_table.setHorizontalHeaderLabels(["Fecha", "Hora", "Tipo", "Destinatarios", "Asunto", "Estado"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.history_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.history_table.setSelectionMode(QTableWidget.SingleSelection)
        self.history_table.doubleClicked.connect(self.view_alert)
        history_layout.addWidget(self.history_table)
        
        # Botones de acción para historial
        history_actions = QHBoxLayout()
        history_actions.addStretch()
        
        self.refresh_btn = QPushButton("Actualizar Historial")
        self.refresh_btn.setIcon(QIcon(AppStyles.get_icon_path("refresh")))
        self.refresh_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.refresh_btn.clicked.connect(self.load_history)
        history_actions.addWidget(self.refresh_btn)
        
        self.view_alert_btn = QPushButton("Ver Alerta")
        self.view_alert_btn.setIcon(QIcon(AppStyles.get_icon_path("view")))
        self.view_alert_btn.setStyleSheet(AppStyles.get_button_style(False))
        self.view_alert_btn.clicked.connect(self.view_alert)
        history_actions.addWidget(self.view_alert_btn)
        
        history_layout.addLayout(history_actions)
        history_group.setLayout(history_layout)
        
        # Agregar grupos al splitter
        splitter.addWidget(compose_group)
        splitter.addWidget(history_group)
        splitter.setSizes([500, 300])  # Tamaño inicial de cada sección
        
        main_layout.addWidget(splitter)
        self.setLayout(main_layout)
        
        # Cargar datos iniciales
        self.load_history()
    
    def load_niveles(self):
        """Cargar niveles educativos"""
        try:
            niveles = self.db.get_niveles()
            
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Todos los niveles", None)
            
            for nivel in niveles:
                self.nivel_combo.addItem(nivel[1], nivel[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar niveles: {str(e)}")
    
    def on_nivel_changed(self):
        nivel_id = self.nivel_combo.currentData()
        if nivel_id is None:
            self.grado_combo.clear()
            return
        
        try:
            grados = self.db.get_grados_by_nivel(nivel_id)
            
            self.grado_combo.clear()
            self.grado_combo.addItem("Todos los grados", None)
            
            for grado in grados:
                self.grado_combo.addItem(grado[1], grado[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar grados: {str(e)}")
    
    def on_grado_changed(self):
        grado_id = self.grado_combo.currentData()
        if grado_id is None:
            self.seccion_combo.clear()
            return
        
        try:
            secciones = self.db.get_secciones_by_grado(grado_id)
            
            self.seccion_combo.clear()
            self.seccion_combo.addItem("Todas las secciones", None)
            
            for seccion in secciones:
                self.seccion_combo.addItem(seccion[1], seccion[0])
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar secciones: {str(e)}")
    
    def load_students(self):
        nivel_id = self.nivel_combo.currentData()
        grado_id = self.grado_combo.currentData()
        seccion_id = self.seccion_combo.currentData()
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            query = "SELECT id, nombre, apellido FROM estudiantes WHERE 1=1"
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
            
            query += " ORDER BY apellido, nombre"
            
            cursor.execute(query, params)
            students = cursor.fetchall()
            
            self.estudiante_combo.clear()
            self.estudiante_combo.addItem("Seleccione un estudiante específico", None)
            
            for student in students:
                self.estudiante_combo.addItem(f"{student[2]}, {student[1]}", student[0])
            
            if students:
                QMessageBox.information(self, "Información", f"Se cargaron {len(students)} estudiantes")
            else:
                QMessageBox.warning(self, "Advertencia", "No se encontraron estudiantes con los filtros seleccionados")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar estudiantes: {str(e)}")
    
    def preview_alert(self):
        # Obtener datos del formulario
        alert_type = self.get_alert_type()
        subject = self.subject_input.text().strip()
        message = self.message_input.toPlainText().strip()
        recipients = self.get_recipients_description()
        delivery_methods = self.get_delivery_methods()
        
        if not subject or not message:
            QMessageBox.warning(self, "Advertencia", "Por favor complete el asunto y el mensaje")
            return
        
        # Mostrar vista previa
        preview_text = f"Tipo de alerta: {alert_type}\n\n"
        preview_text += f"Destinatarios: {recipients}\n\n"
        preview_text += f"Métodos de envío: {delivery_methods}\n\n"
        preview_text += f"Asunto: {subject}\n\n"
        preview_text += f"Mensaje:\n{message}"
        
        QMessageBox.information(self, "Vista Previa de Alerta", preview_text)
    
    def send_alert(self):
        # Obtener datos del formulario
        alert_type = self.get_alert_type()
        subject = self.subject_input.text().strip()
        message = self.message_input.toPlainText().strip()
        recipients = self.get_recipients_description()
        delivery_methods = self.get_delivery_methods()
        
        if not subject or not message:
            QMessageBox.warning(self, "Advertencia", "Por favor complete el asunto y el mensaje")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de alertas, si no, crearla
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alertas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT,
                    hora TEXT,
                    tipo TEXT,
                    destinatarios TEXT,
                    asunto TEXT,
                    mensaje TEXT,
                    metodos_envio TEXT,
                    estado TEXT,
                    usuario_id INTEGER,
                    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                )
            """)
            
            # Obtener fecha y hora actual
            now = QDateTime.currentDateTime()
            fecha = now.toString("yyyy-MM-dd")
            hora = now.toString("HH:mm:ss")
            
            # Insertar alerta
            cursor.execute("""
                INSERT INTO alertas (fecha, hora, tipo, destinatarios, asunto, mensaje, metodos_envio, estado, usuario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fecha, hora, alert_type, recipients, subject, message, delivery_methods, "enviada", self.user_data['id']))
            
            # Si se seleccionó SMS como método de envío, obtener los números de teléfono de los padres
            if self.check_sms.isChecked():
                # Obtener los IDs de los estudiantes según los filtros
                estudiante_id = self.estudiante_combo.currentData()
                nivel_id = self.nivel_combo.currentData()
                grado_id = self.grado_combo.currentData()
                seccion_id = self.seccion_combo.currentData()
                
                query = "SELECT e.id FROM estudiantes e WHERE 1=1"
                params = []
                
                if estudiante_id:
                    query += " AND e.id = ?"
                    params.append(estudiante_id)
                else:
                    if nivel_id:
                        query += " AND e.nivel_id = ?"
                        params.append(nivel_id)
                        
                    if grado_id:
                        query += " AND e.grado_id = ?"
                        params.append(grado_id)
                        
                    if seccion_id:
                        query += " AND e.seccion_id = ?"
                        params.append(seccion_id)
                
                cursor.execute(query, params)
                estudiantes = cursor.fetchall()
                
                # Obtener los números de teléfono de los padres de estos estudiantes
                telefonos_padres = []
                for estudiante in estudiantes:
                    cursor.execute("""
                        SELECT p.telefono, e.nombre || ' ' || e.apellido as estudiante_nombre, p.nombre as padre_nombre
                        FROM padres p
                        JOIN estudiantes e ON p.estudiante_id = e.id
                        WHERE p.estudiante_id = ?
                    """, (estudiante[0],))
                    padres = cursor.fetchall()
                    for padre in padres:
                        telefonos_padres.append({
                            'telefono': padre[0],
                            'estudiante': padre[1],
                            'padre': padre[2]
                        })
                
                # Simular el envío de SMS
                if telefonos_padres:
                    sms_enviados = len(telefonos_padres)
                    sms_details = "\n\nDetalles de SMS enviados:\n"
                    for i, padre in enumerate(telefonos_padres, 1):
                        sms_details += f"{i}. A: {padre['padre']} (Padre/Madre de {padre['estudiante']})\n"
                        sms_details += f"   Teléfono: {padre['telefono']}\n"
                    
                    QMessageBox.information(self, "SMS Enviados", 
                                          f"Se han enviado {sms_enviados} SMS a los padres de familia.{sms_details}")
                else:
                    QMessageBox.warning(self, "Advertencia", 
                                  "No se encontraron números de teléfono de padres para los estudiantes seleccionados.")
            
            conn.commit()
            
            QMessageBox.information(self, "Éxito", "Alerta enviada correctamente")
            
            # Limpiar formulario
            self.subject_input.clear()
            self.message_input.clear()
            
            # Actualizar historial
            self.load_history()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al enviar alerta: {str(e)}")
    
    def load_history(self):
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Verificar si existe la tabla de alertas
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='alertas'
            """)
            
            if not cursor.fetchone():
                # Si no existe la tabla, crearla
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS alertas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        fecha TEXT,
                        hora TEXT,
                        tipo TEXT,
                        destinatarios TEXT,
                        asunto TEXT,
                        mensaje TEXT,
                        metodos_envio TEXT,
                        estado TEXT,
                        usuario_id INTEGER,
                        FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
                    )
                """)
                conn.commit()
            
            # Cargar alertas del usuario actual
            cursor.execute("""
                SELECT id, fecha, hora, tipo, destinatarios, asunto, estado
                FROM alertas
                WHERE usuario_id = ?
                ORDER BY fecha DESC, hora DESC
            """, (self.user_data['id'],))
            
            alerts = cursor.fetchall()
            
            self.history_table.setRowCount(len(alerts))
            for row, alert in enumerate(alerts):
                self.history_table.setItem(row, 0, QTableWidgetItem(alert[1]))  # Fecha
                self.history_table.setItem(row, 1, QTableWidgetItem(alert[2]))  # Hora
                self.history_table.setItem(row, 2, QTableWidgetItem(alert[3]))  # Tipo
                self.history_table.setItem(row, 3, QTableWidgetItem(alert[4]))  # Destinatarios
                self.history_table.setItem(row, 4, QTableWidgetItem(alert[5]))  # Asunto
                
                # Estado con color
                estado_item = QTableWidgetItem(alert[6])
                if alert[6] == "enviada":
                    estado_item.setForeground(QColor(AppStyles.SECONDARY_COLOR))
                elif alert[6] == "entregada":
                    estado_item.setForeground(QColor("green"))
                elif alert[6] == "error":
                    estado_item.setForeground(QColor(AppStyles.ACCENT_COLOR))
                
                self.history_table.setItem(row, 5, estado_item)
                
                # Guardar el ID de la alerta como dato oculto
                self.history_table.item(row, 0).setData(Qt.UserRole, alert[0])
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar historial: {str(e)}")
    
    def filter_history(self):
        filter_type = self.history_type_combo.currentText()
        search_text = self.history_search.text().lower()
        
        for row in range(self.history_table.rowCount()):
            show_row = True
            
            # Filtrar por tipo
            if filter_type != "Todas":
                tipo_cell = self.history_table.item(row, 2)
                if tipo_cell and tipo_cell.text() != filter_type:
                    show_row = False
            
            # Filtrar por texto de búsqueda
            if search_text and show_row:
                row_match = False
                for col in range(self.history_table.columnCount()):
                    cell = self.history_table.item(row, col)
                    if cell and search_text in cell.text().lower():
                        row_match = True
                        break
                show_row = row_match
            
            self.history_table.setRowHidden(row, not show_row)
    
    def view_alert(self):
        selected_rows = self.history_table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Advertencia", "Seleccione una alerta para ver")
            return
        
        row = selected_rows[0].row()
        alert_id = self.history_table.item(row, 0).data(Qt.UserRole)
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT fecha, hora, tipo, destinatarios, asunto, mensaje, metodos_envio
                FROM alertas
                WHERE id = ?
            """, (alert_id,))
            
            alert = cursor.fetchone()
            if alert:
                # Mostrar detalles de la alerta
                details = f"Fecha: {alert[0]} {alert[1]}\n\n"
                details += f"Tipo: {alert[2]}\n\n"
                details += f"Destinatarios: {alert[3]}\n\n"
                details += f"Métodos de envío: {alert[6]}\n\n"
                details += f"Asunto: {alert[4]}\n\n"
                details += f"Mensaje:\n{alert[5]}"
                
                QMessageBox.information(self, "Detalles de la Alerta", details)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar alerta: {str(e)}")
    
    def get_alert_type(self):
        if self.radio_general.isChecked():
            return "General"
        elif self.radio_academic.isChecked():
            return "Académica"
        elif self.radio_attendance.isChecked():
            return "Asistencia"
        elif self.radio_behavior.isChecked():
            return "Comportamiento"
        elif self.radio_emergency.isChecked():
            return "Emergencia"
        return "General"
    
    def get_delivery_methods(self):
        methods = []
        if self.check_email.isChecked():
            methods.append("Correo electrónico")
        if self.check_sms.isChecked():
            methods.append("SMS")
        if self.check_app.isChecked():
            methods.append("App")
        return ", ".join(methods) if methods else "Ninguno"
    
    def get_recipients_description(self):
        estudiante_id = self.estudiante_combo.currentData()
        if estudiante_id:
            return f"Estudiante: {self.estudiante_combo.currentText()}"
        
        nivel_id = self.nivel_combo.currentData()
        grado_id = self.grado_combo.currentData()
        seccion_id = self.seccion_combo.currentData()
        
        if seccion_id:
            return f"{self.nivel_combo.currentText()} - {self.grado_combo.currentText()} - {self.seccion_combo.currentText()}"
        elif grado_id:
            return f"{self.nivel_combo.currentText()} - {self.grado_combo.currentText()}"
        elif nivel_id:
            return f"{self.nivel_combo.currentText()}"
        else:
            return "Todos los estudiantes"


def update_sms_preview(self):
    """Actualizar la vista previa del SMS"""
    subject = self.subject_input.text().strip()
    message = self.message_input.toPlainText().strip()
    
    if not subject or not message:
        self.sms_preview.setText("Complete el asunto y mensaje para ver la vista previa del SMS")
        return
    
    # Construir el SMS
    sms_text = ""
    
    if self.include_school_name.isChecked():
        sms_text += "KAIROS: "
    
    if self.include_student_name.isChecked():
        estudiante_id = self.estudiante_combo.currentData()
        if estudiante_id:
            sms_text += f"[{self.estudiante_combo.currentText()}] "
    
    # Añadir asunto y mensaje resumido (limitado a 160 caracteres en total)
    sms_text += f"{subject}: "
    
    # Calcular caracteres restantes para el mensaje
    chars_left = 160 - len(sms_text)
    if chars_left > 0:
        if len(message) > chars_left:
            message = message[:chars_left-3] + "..."
        sms_text += message
    
    if self.request_confirmation.isChecked():
        if len(sms_text) + 35 <= 160:  # Verificar si hay espacio
            sms_text += "\n\nResponda OK para confirmar recepción."
    
    # Mostrar contador de caracteres
    char_count = len(sms_text)
    sms_text += f"\n\n[{char_count}/160 caracteres]"
    
    self.sms_preview.setText(sms_text)
    self.include_school_name.stateChanged.connect(self.update_sms_preview)
    self.include_student_name.stateChanged.connect(self.update_sms_preview)
    self.request_confirmation.stateChanged.connect(self.update_sms_preview)
    self.subject_input.textChanged.connect(self.update_sms_preview)
    self.message_input.textChanged.connect(self.update_sms_preview)
    self.update_sms_preview()