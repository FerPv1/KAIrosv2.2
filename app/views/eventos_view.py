from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                             QComboBox, QLineEdit, QFrame, QGroupBox, QCalendarWidget,
                             QTextEdit, QTableWidget, QTableWidgetItem, QHeaderView,
                             QMessageBox, QDialog, QFormLayout, QDateEdit, QTimeEdit,
                             QScrollArea, QGridLayout)
from PySide6.QtCore import Qt, QDate, QTime, QDateTime
from PySide6.QtGui import QFont, QIcon, QColor
import sqlite3  # Agregar esta línea
from app.models.database import Database
from app.utils.styles import AppStyles

class EventosView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.setup_ui()
        self.load_events()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Título principal
        title_label = QLabel("Gestión de Eventos")
        title_label.setFont(QFont("Segoe UI", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                margin-bottom: 20px;
                padding: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, 
                    stop:0 #e74c3c, stop:1 #c0392b);
                color: white;
                border-radius: 10px;
            }
        """)
        main_layout.addWidget(title_label)
        
        # Layout principal horizontal
        main_content = QHBoxLayout()
        
        # Panel izquierdo: Calendario y filtros
        left_panel = QVBoxLayout()
        
        # Filtros y controles
        filters_group = QGroupBox("Filtros y Controles")
        filters_group.setStyleSheet(self.get_group_style())
        filters_layout = QVBoxLayout()
        
        # Buscador
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Buscar eventos:"))
        self.event_search = QLineEdit()
        self.event_search.setPlaceholderText("Buscar eventos")
        self.event_search.setStyleSheet(self.get_input_style())
        self.event_search.textChanged.connect(self.filter_events)
        search_layout.addWidget(self.event_search)
        filters_layout.addLayout(search_layout)
        
        # Filtro por tipo
        type_layout = QHBoxLayout()
        type_layout.addWidget(QLabel("Filtrar por tipo:"))
        self.event_type_combo = QComboBox()
        self.event_type_combo.addItems(["Todos los tipos", "Académicos", "Culturales", "Deportivos", "Reuniones", "Otros"])
        self.event_type_combo.setStyleSheet(self.get_combo_style())
        self.event_type_combo.currentTextChanged.connect(self.filter_events)
        type_layout.addWidget(self.event_type_combo)
        filters_layout.addLayout(type_layout)
        
        # Botón nuevo evento
        self.new_event_btn = QPushButton("➕ Nuevo Evento")
        self.new_event_btn.setStyleSheet(self.get_button_style("#3498db"))
        self.new_event_btn.clicked.connect(self.create_new_event)
        filters_layout.addWidget(self.new_event_btn)
        
        filters_group.setLayout(filters_layout)
        left_panel.addWidget(filters_group)
        
        # Calendario
        calendar_group = QGroupBox("Calendario de Eventos")
        calendar_group.setStyleSheet(self.get_group_style())
        calendar_layout = QVBoxLayout()
        
        self.calendar = QCalendarWidget()
        self.calendar.setStyleSheet("""
            QCalendarWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
            }
            QCalendarWidget QToolButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
                font-weight: bold;
            }
            QCalendarWidget QToolButton:hover {
                background-color: #c0392b;
            }
            QCalendarWidget QAbstractItemView:enabled {
                background-color: white;
                selection-background-color: #e74c3c;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:enabled:hover {
                background-color: #fadbd8;
            }
        """)
        self.calendar.clicked.connect(self.on_date_selected)
        calendar_layout.addWidget(self.calendar)
        
        calendar_group.setLayout(calendar_layout)
        left_panel.addWidget(calendar_group)
        
        main_content.addLayout(left_panel, 1)
        
        # Panel derecho: Lista de eventos y detalles
        right_panel = QVBoxLayout()
        
        # Eventos próximos
        upcoming_group = QGroupBox("Eventos Próximos")
        upcoming_group.setStyleSheet(self.get_group_style())
        upcoming_layout = QVBoxLayout()
        
        self.upcoming_events_scroll = QScrollArea()
        self.upcoming_events_widget = QWidget()
        self.upcoming_events_layout = QVBoxLayout(self.upcoming_events_widget)
        self.upcoming_events_scroll.setWidget(self.upcoming_events_widget)
        self.upcoming_events_scroll.setWidgetResizable(True)
        self.upcoming_events_scroll.setMaximumHeight(200)
        self.upcoming_events_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        upcoming_layout.addWidget(self.upcoming_events_scroll)
        upcoming_group.setLayout(upcoming_layout)
        right_panel.addWidget(upcoming_group)
        
        # Eventos para la fecha seleccionada
        self.selected_date_group = QGroupBox(f"Eventos para {QDate.currentDate().toString('dd/MM/yyyy')}")
        self.selected_date_group.setStyleSheet(self.get_group_style())
        selected_date_layout = QVBoxLayout()
        
        self.selected_date_scroll = QScrollArea()
        self.selected_date_widget = QWidget()
        self.selected_date_layout = QVBoxLayout(self.selected_date_widget)
        self.selected_date_scroll.setWidget(self.selected_date_widget)
        self.selected_date_scroll.setWidgetResizable(True)
        self.selected_date_scroll.setMaximumHeight(200)
        self.selected_date_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                border-radius: 8px;
                background-color: white;
            }
        """)
        
        selected_date_layout.addWidget(self.selected_date_scroll)
        
        # Botón agregar evento para fecha
        self.add_event_btn = QPushButton("➕ Agregar evento para esta fecha")
        self.add_event_btn.setStyleSheet(self.get_button_style("#27ae60"))
        self.add_event_btn.clicked.connect(self.add_event_for_date)
        selected_date_layout.addWidget(self.add_event_btn)
        
        self.selected_date_group.setLayout(selected_date_layout)
        right_panel.addWidget(self.selected_date_group)
        
        # Tabla de todos los eventos
        events_table_group = QGroupBox("Todos los Eventos")
        events_table_group.setStyleSheet(self.get_group_style())
        events_table_layout = QVBoxLayout()
        
        self.events_table = QTableWidget()
        self.events_table.setColumnCount(6)
        self.events_table.setHorizontalHeaderLabels(["Fecha", "Hora", "Título", "Tipo", "Descripción", "Acciones"])
        self.events_table.setStyleSheet(self.get_table_style())
        
        # Configurar tabla
        header = self.events_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)  # Fecha
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)  # Hora
        header.setSectionResizeMode(2, QHeaderView.Stretch)           # Título
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)  # Tipo
        header.setSectionResizeMode(4, QHeaderView.Stretch)           # Descripción
        header.setSectionResizeMode(5, QHeaderView.ResizeToContents)  # Acciones
        
        self.events_table.setAlternatingRowColors(True)
        self.events_table.setSelectionBehavior(QTableWidget.SelectRows)
        events_table_layout.addWidget(self.events_table)
        
        events_table_group.setLayout(events_table_layout)
        right_panel.addWidget(events_table_group)
        
        main_content.addLayout(right_panel, 2)
        
        main_layout.addLayout(main_content)  # Changed from layout.addLayout to main_layout.addLayout
        self.setLayout(main_layout)
    
    def get_group_style(self):
        return """
            QGroupBox {
                font-weight: bold;
                font-size: 14px;
                color: #2c3e50;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: white;
            }
        """
    
    def get_button_style(self, color):
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                min-width: 120px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """
    
    def get_combo_style(self):
        return """
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
                min-width: 150px;
            }
            QComboBox:focus {
                border-color: #e74c3c;
            }
            QComboBox::drop-down {
                border: none;
            }
        """
    
    def get_input_style(self):
        return """
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border-color: #e74c3c;
            }
        """
    
    def get_table_style(self):
        return """
            QTableWidget {
                gridline-color: #e0e0e0;
                background-color: white;
                alternate-background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                selection-background-color: #fadbd8;
            }
            QTableWidget::item {
                padding: 12px;
                border-bottom: 1px solid #e0e0e0;
            }
            QHeaderView::section {
                background-color: #f1f3f4;
                padding: 12px;
                border: none;
                font-weight: bold;
                color: #333;
                border-bottom: 2px solid #dee2e6;
            }
        """
    
    def darken_color(self, color, factor=0.9):
        """Oscurecer un color para efectos hover"""
        color_map = {
            "#3498db": "#2980b9",
            "#27ae60": "#229954",
            "#e74c3c": "#c0392b",
            "#9b59b6": "#8e44ad",
            "#f39c12": "#e67e22"
        }
        return color_map.get(color, color)
    
    def create_event_card(self, event_data):
        """Crear tarjeta de evento"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #e74c3c;
                background-color: #fdf2f2;
            }
        """)
        
        layout = QVBoxLayout(card)
        
        # Título del evento
        title = QLabel(event_data.get('titulo', 'Sin título'))
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title.setStyleSheet("color: #2c3e50;")
        layout.addWidget(title)
        
        # Hora
        time_label = QLabel(f"🕐 {event_data.get('hora', 'Sin hora')}")
        time_label.setStyleSheet("color: #7f8c8d; font-size: 11px;")
        layout.addWidget(time_label)
        
        # Tipo
        type_label = QLabel(f"📋 {event_data.get('tipo', 'Sin tipo')}")
        type_label.setStyleSheet("color: #e74c3c; font-size: 11px; font-weight: bold;")
        layout.addWidget(type_label)
        
        # Descripción (truncada)
        desc = event_data.get('descripcion', 'Sin descripción')
        if len(desc) > 50:
            desc = desc[:50] + "..."
        desc_label = QLabel(desc)
        desc_label.setStyleSheet("color: #34495e; font-size: 10px;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        return card
    
    def load_events(self):
        """Cargar eventos desde la base de datos"""
        try:
            conn = self.db.connect()  # Usar el objeto Database en lugar de sqlite3 directo
            cursor = conn.cursor()
            
            # Load events using the correct column names
            cursor.execute("""
                SELECT id, titulo, descripcion, fecha_inicio, fecha_fin, lugar
                FROM eventos 
                ORDER BY fecha_inicio
            """)
            
            events = cursor.fetchall()
            self.populate_events_table(events)
            conn.close()
            
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error al cargar eventos: {str(e)}")
    
    def populate_events_table(self, events):
        """Poblar tabla de eventos"""
        self.events_table.setRowCount(len(events))
        
        for row, event in enumerate(events):
            # Fecha
            self.events_table.setItem(row, 0, QTableWidgetItem(event[3]))
            
            # Hora
            self.events_table.setItem(row, 1, QTableWidgetItem(event[4]))
            
            # Título
            self.events_table.setItem(row, 2, QTableWidgetItem(event[1]))
            
            # Tipo
            self.events_table.setItem(row, 3, QTableWidgetItem(event[5]))
            
            # Descripción
            desc = event[2] if event[2] else "Sin descripción"
            self.events_table.setItem(row, 4, QTableWidgetItem(desc))
            
            # Botones de acción
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 5, 5, 5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setStyleSheet(self.get_button_style("#3498db"))
            edit_btn.setMaximumWidth(30)
            edit_btn.clicked.connect(lambda checked, event_id=event[0]: self.edit_event(event_id))
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setStyleSheet(self.get_button_style("#e74c3c"))
            delete_btn.setMaximumWidth(30)
            delete_btn.clicked.connect(lambda checked, event_id=event[0]: self.delete_event(event_id))
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            
            self.events_table.setCellWidget(row, 5, actions_widget)
    
    def populate_upcoming_events(self, events):
        """Poblar eventos próximos"""
        # Limpiar layout anterior
        for i in reversed(range(self.upcoming_events_layout.count())):
            self.upcoming_events_layout.itemAt(i).widget().setParent(None)
        
        current_date = QDate.currentDate()
        upcoming_events = []
        
        for event in events:
            event_date = QDate.fromString(event[3], "yyyy-MM-dd")
            if event_date >= current_date:
                upcoming_events.append({
                    'titulo': event[1],
                    'descripcion': event[2],
                    'fecha': event[3],
                    'hora': event[4],
                    'tipo': event[5]
                })
        
        if not upcoming_events:
            no_events_label = QLabel("📅 No hay eventos próximos programados.")
            no_events_label.setStyleSheet("""
                QLabel {
                    background-color: #e8f4fd;
                    border: 1px solid #bee5eb;
                    border-radius: 8px;
                    padding: 15px;
                    color: #0c5460;
                    font-size: 14px;
                }
            """)
            self.upcoming_events_layout.addWidget(no_events_label)
        else:
            for event in upcoming_events[:5]:  # Mostrar solo los próximos 5
                card = self.create_event_card(event)
                self.upcoming_events_layout.addWidget(card)
    
    def on_date_selected(self, date):
        """Manejar selección de fecha en calendario"""
        selected_date = date.toString("yyyy-MM-dd")
        self.selected_date_group.setTitle(f"Eventos para {date.toString('dd/MM/yyyy')}")
        
        # Limpiar layout anterior
        for i in reversed(range(self.selected_date_layout.count())):
            self.selected_date_layout.itemAt(i).widget().setParent(None)
        
        # Buscar eventos para la fecha seleccionada
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT titulo, descripcion, hora, tipo 
                FROM eventos 
                WHERE fecha = ? 
                ORDER BY hora
            """, (selected_date,))
            
            events = cursor.fetchall()
            
            if not events:
                no_events_label = QLabel("ℹ️ No hay eventos programados para esta fecha.")
                no_events_label.setStyleSheet("""
                    QLabel {
                        background-color: #fff3cd;
                        border: 1px solid #ffeaa7;
                        border-radius: 8px;
                        padding: 15px;
                        color: #856404;
                        font-size: 14px;
                    }
                """)
                self.selected_date_layout.addWidget(no_events_label)
            else:
                for event in events:
                    event_data = {
                        'titulo': event[0],
                        'descripcion': event[1],
                        'hora': event[2],
                        'tipo': event[3]
                    }
                    card = self.create_event_card(event_data)
                    self.selected_date_layout.addWidget(card)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar eventos: {str(e)}")
    
    def create_new_event(self):
        """Crear nuevo evento"""
        dialog = EventDialog(self)
        if dialog.exec() == QDialog.Accepted:
            self.load_events()
    
    def add_event_for_date(self):
        """Agregar evento para fecha seleccionada"""
        selected_date = self.calendar.selectedDate()
        dialog = EventDialog(self, selected_date)
        if dialog.exec() == QDialog.Accepted:
            self.load_events()
            self.on_date_selected(selected_date)
    
    def edit_event(self, event_id):
        """Editar evento"""
        dialog = EventDialog(self, event_id=event_id)
        if dialog.exec() == QDialog.Accepted:
            self.load_events()
    
    def delete_event(self, event_id):
        """Eliminar evento"""
        reply = QMessageBox.question(self, "Confirmar eliminación", 
                                   "¿Está seguro que desea eliminar este evento?",
                                   QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            try:
                conn = self.db.connect()
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM eventos WHERE id = ?", (event_id,))
                conn.commit()
                conn.close()
                
                QMessageBox.information(self, "Éxito", "Evento eliminado correctamente")
                self.load_events()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error al eliminar evento: {str(e)}")
    
    def filter_events(self):
        """Filtrar eventos por búsqueda y tipo"""
        search_text = self.event_search.text().lower()
        event_type = self.event_type_combo.currentText()
        
        for row in range(self.events_table.rowCount()):
            show_row = True
            
            # Filtro por texto
            if search_text:
                title_item = self.events_table.item(row, 2)
                desc_item = self.events_table.item(row, 4)
                
                title_match = search_text in title_item.text().lower() if title_item else False
                desc_match = search_text in desc_item.text().lower() if desc_item else False
                
                if not (title_match or desc_match):
                    show_row = False
            
            # Filtro por tipo
            if event_type != "Todos los tipos":
                type_item = self.events_table.item(row, 3)
                if not type_item or type_item.text() != event_type:
                    show_row = False
            
            self.events_table.setRowHidden(row, not show_row)


class EventDialog(QDialog):
    def __init__(self, parent, selected_date=None, event_id=None):
        super().__init__(parent)
        self.db = Database()
        self.event_id = event_id
        self.selected_date = selected_date
        self.setup_ui()
        
        if event_id:
            self.load_event_data()
        elif selected_date:
            self.date_edit.setDate(selected_date)
    
    def setup_ui(self):
        self.setWindowTitle("Nuevo Evento" if not self.event_id else "Editar Evento")
        self.setModal(True)
        self.setFixedSize(500, 400)
        
        layout = QVBoxLayout()
        
        # Formulario
        form_layout = QFormLayout()
        
        # Título
        self.title_edit = QLineEdit()
        self.title_edit.setStyleSheet("""
            QLineEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Título:", self.title_edit)
        
        # Fecha
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setStyleSheet("""
            QDateEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Fecha:", self.date_edit)
        
        # Hora
        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.currentTime())
        self.time_edit.setStyleSheet("""
            QTimeEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Hora:", self.time_edit)
        
        # Tipo
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Académicos", "Culturales", "Deportivos", "Reuniones", "Otros"])
        self.type_combo.setStyleSheet("""
            QComboBox {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Tipo:", self.type_combo)
        
        # Descripción
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        self.description_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                padding: 8px;
                font-size: 14px;
            }
        """)
        form_layout.addRow("Descripción:", self.description_edit)
        
        layout.addLayout(form_layout)
        
        # Botones
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.reject)
        buttons_layout.addWidget(cancel_btn)
        
        save_btn = QPushButton("Guardar")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_event)
        buttons_layout.addWidget(save_btn)
        
        layout.addLayout(buttons_layout)
        self.setLayout(layout)
    
    def load_event_data(self):
        """Cargar datos del evento para edición"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT titulo, descripcion, fecha, hora, tipo 
                FROM eventos WHERE id = ?
            """, (self.event_id,))
            
            event = cursor.fetchone()
            if event:
                self.title_edit.setText(event[0])
                self.description_edit.setPlainText(event[1] or "")
                self.date_edit.setDate(QDate.fromString(event[2], "yyyy-MM-dd"))
                self.time_edit.setTime(QTime.fromString(event[3], "HH:mm"))
                
                # Seleccionar tipo
                type_index = self.type_combo.findText(event[4])
                if type_index >= 0:
                    self.type_combo.setCurrentIndex(type_index)
            
            conn.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar evento: {str(e)}")
    
    def save_event(self):
        """Guardar evento"""
        if not self.title_edit.text().strip():
            QMessageBox.warning(self, "Advertencia", "El título es obligatorio")
            return
        
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            title = self.title_edit.text().strip()
            description = self.description_edit.toPlainText().strip()
            date = self.date_edit.date().toString("yyyy-MM-dd")
            time = self.time_edit.time().toString("HH:mm")
            event_type = self.type_combo.currentText()
            
            if self.event_id:
                # Actualizar evento existente
                cursor.execute("""
                    UPDATE eventos 
                    SET titulo = ?, descripcion = ?, fecha = ?, hora = ?, tipo = ?
                    WHERE id = ?
                """, (title, description, date, time, event_type, self.event_id))
            else:
                # Crear nuevo evento
                cursor.execute("""
                    INSERT INTO eventos (titulo, descripcion, fecha, hora, tipo, creado_por)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (title, description, date, time, event_type, 1))  # Usar ID del usuario actual
            
            conn.commit()
            conn.close()
            
            QMessageBox.information(self, "Éxito", "Evento guardado correctamente")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al guardar evento: {str(e)}")