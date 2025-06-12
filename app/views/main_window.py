from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QLabel, QStackedWidget, QMessageBox,
                             QFrame, QSizePolicy, QTableWidget, QTableWidgetItem,
                             QHeaderView, QGroupBox, QFormLayout, QComboBox, QTabWidget)
from PySide6.QtCore import Qt, QSize, QDate
from PySide6.QtGui import QFont, QIcon, QPixmap, QColor
from PySide6.QtGui import QColor
import os
from datetime import datetime

from app.views.asistencia_view import AsistenciaView
from app.views.estudiantes_view import EstudiantesView
from app.views.reportes_view import ReportesView
from app.views.calificaciones_view import CalificacionesView
from app.views.comunicacion_view import ComunicacionView
from app.views.horarios_view import HorariosView
from app.utils.styles import AppStyles
from app.models.database import Database
from app.views.eventos_view import EventosView
from app.views.emotion_live_view import EmotionLiveView
from app.views.alertas_view import AlertasView
from app.views.configuracion_view import ConfiguracionView
from app.views.lista_combinada_view import ListaCombinadaView

class MainWindow(QMainWindow):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle(f"KairosApp - {self.user_data['nombre']} {self.user_data['apellido']}")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet(f"background-color: {AppStyles.BACKGROUND_COLOR};")
        
        # Definir los títulos de las páginas
        # Modificar la lista de títulos
        self.titles = ["Dashboard", "Estudiantes", "Lista Combinada", "Asistencia", "Eventos", 
                      "Horarios", "Calificaciones", "Alertas", "Reporte Emociones", "Configuración"]
        
        # Widget central
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Panel lateral (menú)
        sidebar = QWidget()
        sidebar.setMaximumWidth(250)
        sidebar.setMinimumWidth(250)
        sidebar.setStyleSheet(AppStyles.get_sidebar_style())
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo y título
        logo_container = QWidget()
        logo_layout = QVBoxLayout(logo_container)
        logo_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título del menú
        menu_title = QLabel("kAIrosApp")
        menu_title.setFont(QFont("Arial", 18, QFont.Bold))
        menu_title.setAlignment(Qt.AlignCenter)
        menu_title.setStyleSheet("color: white; margin-bottom: 10px;")
        logo_layout.addWidget(menu_title)
        
        sidebar_layout.addWidget(logo_container)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sidebar_layout.addWidget(separator)
        
        # Información del usuario
        user_info = QLabel(f"Bienvenido, {self.user_data['nombre']}")
        user_info.setAlignment(Qt.AlignCenter)
        user_info.setStyleSheet("padding: 10px; font-size: 12px; color: rgba(255,255,255,0.8);")
        sidebar_layout.addWidget(user_info)
        
        # Separador
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.HLine)
        separator2.setFrameShadow(QFrame.Sunken)
        separator2.setStyleSheet("background-color: rgba(255,255,255,0.2);")
        sidebar_layout.addWidget(separator2)
        
        # Botones del menú
        self.btn_dashboard = QPushButton("  Dashboard")
        self.btn_dashboard.setIcon(QIcon(AppStyles.get_icon_path("dashboard")))
        self.btn_dashboard.setIconSize(QSize(20, 20))
        self.btn_dashboard.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_dashboard.setCheckable(True)
        self.btn_dashboard.setChecked(True)
        self.btn_dashboard.clicked.connect(lambda: self.change_page(0))
        sidebar_layout.addWidget(self.btn_dashboard)
        
        self.btn_estudiantes = QPushButton("  Estudiantes")
        self.btn_estudiantes.setIcon(QIcon(AppStyles.get_icon_path("students")))
        self.btn_estudiantes.setIconSize(QSize(20, 20))
        self.btn_estudiantes.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_estudiantes.setCheckable(True)
        self.btn_estudiantes.clicked.connect(lambda: self.change_page(1))
        sidebar_layout.addWidget(self.btn_estudiantes)
        
        self.btn_asistencia = QPushButton("  Asistencia")
        self.btn_asistencia.setIcon(QIcon(AppStyles.get_icon_path("attendance")))
        self.btn_asistencia.setIconSize(QSize(20, 20))
        self.btn_asistencia.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_asistencia.setCheckable(True)
        self.btn_asistencia.clicked.connect(lambda: self.change_page(2))
        sidebar_layout.addWidget(self.btn_asistencia)
        
        self.btn_eventos = QPushButton("  Eventos")
        self.btn_eventos.setIcon(QIcon(AppStyles.get_icon_path("events")))
        self.btn_eventos.setIconSize(QSize(20, 20))
        self.btn_eventos.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_eventos.setCheckable(True)
        self.btn_eventos.clicked.connect(lambda: self.change_page(3))
        sidebar_layout.addWidget(self.btn_eventos)
        
        self.btn_horarios = QPushButton("  Horarios")
        self.btn_horarios.setIcon(QIcon(AppStyles.get_icon_path("schedule")))
        self.btn_horarios.setIconSize(QSize(20, 20))
        self.btn_horarios.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_horarios.setCheckable(True)
        self.btn_horarios.clicked.connect(lambda: self.change_page(4))  # Cambiar a índice 4
        sidebar_layout.addWidget(self.btn_horarios)
        
        self.btn_calificaciones = QPushButton("  Calificaciones")
        self.btn_calificaciones.setIcon(QIcon(AppStyles.get_icon_path("grades")))
        self.btn_calificaciones.setIconSize(QSize(20, 20))
        self.btn_calificaciones.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_calificaciones.setCheckable(True)
        self.btn_calificaciones.clicked.connect(lambda: self.change_page(5))  # Cambiar a índice 5
        sidebar_layout.addWidget(self.btn_calificaciones)
        
        self.btn_alertas = QPushButton("  Alertas")
        self.btn_alertas.setIcon(QIcon(AppStyles.get_icon_path("alerts")))
        self.btn_alertas.setIconSize(QSize(20, 20))
        self.btn_alertas.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_alertas.setCheckable(True)
        self.btn_alertas.clicked.connect(lambda: self.change_page(6))  # Cambiar a índice 6
        sidebar_layout.addWidget(self.btn_alertas)

        # Nuevo botón para Reporte de Emociones
        self.btn_Reporteemociones = QPushButton("  Reporte Emociones")
        self.btn_Reporteemociones.setIcon(QIcon(AppStyles.get_icon_path("emotions")))
        self.btn_Reporteemociones.setIconSize(QSize(20, 20))
        self.btn_Reporteemociones.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_Reporteemociones.setCheckable(True)
        self.btn_Reporteemociones.clicked.connect(lambda: self.change_page(7))  # Cambiar a índice 7
        sidebar_layout.addWidget(self.btn_Reporteemociones)

        self.btn_configuracion = QPushButton("  Configuración")
        self.btn_configuracion.setIcon(QIcon(AppStyles.get_icon_path("settings")))
        self.btn_configuracion.setIconSize(QSize(20, 20))
        self.btn_configuracion.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_configuracion.setCheckable(True)
        self.btn_configuracion.clicked.connect(lambda: self.change_page(8))
        sidebar_layout.addWidget(self.btn_configuracion)
        
        # Botón para Lista Combinada
        self.btn_lista_combinada = QPushButton("  Lista Combinada")
        self.btn_lista_combinada.setIcon(QIcon(AppStyles.get_icon_path("students")))
        self.btn_lista_combinada.setIconSize(QSize(20, 20))
        self.btn_lista_combinada.setStyleSheet(AppStyles.get_sidebar_button_style())
        self.btn_lista_combinada.setCheckable(True)
        # Actualizar los índices de los botones para que coincidan con el nuevo orden
        self.btn_dashboard.clicked.connect(lambda: self.change_page(0))  # Dashboard
        self.btn_estudiantes.clicked.connect(lambda: self.change_page(1))  # Estudiantes
        self.btn_lista_combinada.clicked.connect(lambda: self.change_page(2))  # Lista Combinada
        self.btn_asistencia.clicked.connect(lambda: self.change_page(3))  # Asistencia
        self.btn_eventos.clicked.connect(lambda: self.change_page(4))  # Eventos
        self.btn_horarios.clicked.connect(lambda: self.change_page(5))  # Horarios
        self.btn_calificaciones.clicked.connect(lambda: self.change_page(6))  # Calificaciones
        self.btn_alertas.clicked.connect(lambda: self.change_page(7))  # Alertas
        self.btn_Reporteemociones.clicked.connect(lambda: self.change_page(8))  # Reporte Emociones
        self.btn_configuracion.clicked.connect(lambda: self.change_page(9))  # Configuración
        sidebar_layout.addWidget(self.btn_lista_combinada)
        # Agregar widgets al layout principal
        main_layout.addWidget(sidebar)
        
        # Después de definir todos los botones del sidebar y antes de agregar widgets al layout principal
        # Definir el contenedor principal y el stacked widget
        content_container = QWidget()
        content_layout = QVBoxLayout(content_container)
        
        # Barra superior con título de la página
        top_bar = QWidget()
        top_bar.setStyleSheet("background-color: white; border-bottom: 1px solid #e0e0e0;")
        top_bar_layout = QHBoxLayout(top_bar)
        top_bar_layout.setContentsMargins(20, 10, 20, 10)
        
        self.page_title = QLabel(self.titles[0])
        self.page_title.setFont(AppStyles.TITLE_FONT)
        top_bar_layout.addWidget(self.page_title)
        
        content_layout.addWidget(top_bar)
        
        # Stacked widget para las diferentes páginas
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        main_layout.addWidget(content_container, 1)

        self.setCentralWidget(central_widget)
        
        # Inicializar y añadir todas las vistas al stacked widget
        # 0: Dashboard
        dashboard_widget = self.create_dashboard_widget()
        self.stacked_widget.addWidget(dashboard_widget)
        
        # 1: Estudiantes
        estudiantes_view = EstudiantesView(self.user_data)
        self.stacked_widget.addWidget(estudiantes_view)
        
        # 2: Lista Combinada (después de Estudiantes como solicitado)
        lista_combinada_view = ListaCombinadaView(self.user_data)
        self.stacked_widget.addWidget(lista_combinada_view)
        
        # 3: Asistencia
        asistencia_view = AsistenciaView(self.user_data)
        self.stacked_widget.addWidget(asistencia_view)
        
        # 4: Eventos
        eventos_view = EventosView(self.user_data)
        self.stacked_widget.addWidget(eventos_view)
        
        # 5: Horarios
        horarios_view = HorariosView(self.user_data)
        self.stacked_widget.addWidget(horarios_view)
        
        # 6: Calificaciones
        calificaciones_view = CalificacionesView(self.user_data)
        self.stacked_widget.addWidget(calificaciones_view)
        
        # 7: Alertas
        alertas_view = AlertasView(self.user_data)
        self.stacked_widget.addWidget(alertas_view)
        
        # 8: Reporte Emociones
        reportes_view = ReportesView(self.user_data)
        self.stacked_widget.addWidget(reportes_view)
        
        # 9: Configuración
        configuracion_view = ConfiguracionView(self.user_data)
        self.stacked_widget.addWidget(configuracion_view)
        
        # Eliminar esta línea duplicada
        # lista_combinada_view = ListaCombinadaView(self.user_data)
        # self.stacked_widget.addWidget(lista_combinada_view)
        
        # Establecer la página inicial (Dashboard)
        self.change_page(0)

    def create_dashboard_widget(self):
        """Crear el dashboard principal con estadísticas y calendario"""
        # Página 1: Dashboard
        dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_widget)
        
        # Título de bienvenida
        welcome_label = QLabel(f"Bienvenido, {self.user_data['nombre']}")
        welcome_label.setFont(AppStyles.SUBTITLE_FONT)
        welcome_label.setStyleSheet("color: #333; margin-bottom: 20px;")
        dashboard_layout.addWidget(welcome_label)
        
        # Tarjetas de estadísticas
        stats_layout = QHBoxLayout()
        
        # Tarjeta Estudiantes
        estudiantes_card = self.create_stat_card("Estudiantes", "320", "#4A90E2", "👥")
        stats_layout.addWidget(estudiantes_card)
        
        # Tarjeta Asistencia Hoy
        asistencia_card = self.create_stat_card("Asistencia Hoy", "87%", "#7ED321", "✓")
        stats_layout.addWidget(asistencia_card)
        
        # Tarjeta Eventos Próximos
        eventos_card = self.create_stat_card("Eventos Próximos", "0", "#50E3C2", "📅")
        stats_layout.addWidget(eventos_card)
        
        # Tarjeta Calificaciones
        calificaciones_card = self.create_stat_card("Calificaciones", "15", "#F5A623", "📊")
        stats_layout.addWidget(calificaciones_card)
        
        dashboard_layout.addLayout(stats_layout)
        
        # Pestañas para Calendario/Horarios y Notas
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { 
                border: 1px solid #e0e0e0; 
                background-color: white; 
                border-radius: 5px; 
            }
            QTabBar::tab { 
                background-color: #f5f5f5; 
                padding: 8px 15px; 
                margin-right: 2px; 
                border-top-left-radius: 4px; 
                border-top-right-radius: 4px; 
            }
            QTabBar::tab:selected { 
                background-color: white; 
                border: 1px solid #e0e0e0; 
                border-bottom: none; 
            }
        """)
        
        # Pestaña de Calendario y Horarios
        calendar_tab = QWidget()
        calendar_layout = QHBoxLayout(calendar_tab)
        
        # Sección de Calendario
        calendar_section = QWidget()
        calendar_section.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
        calendar_section_layout = QVBoxLayout(calendar_section)
        
        calendar_title = QLabel("Calendario")
        calendar_title.setFont(QFont("Arial", 12, QFont.Bold))
        calendar_section_layout.addWidget(calendar_title)
        
        calendar_message = QLabel("Calendario no disponible temporalmente")
        calendar_message.setStyleSheet("color: #666; margin: 20px 0;")
        calendar_section_layout.addWidget(calendar_message)
        
        date_label = QLabel("Fecha seleccionada: 05/06/2025")
        date_label.setStyleSheet("color: #666; margin-bottom: 10px;")
        calendar_section_layout.addWidget(date_label)
        
        nav_buttons = QHBoxLayout()
        prev_day = QPushButton("Día Anterior")
        next_day = QPushButton("Día Siguiente")
        prev_day.setStyleSheet("background-color: #f0f0f0; padding: 5px 10px; border-radius: 4px;")
        next_day.setStyleSheet("background-color: #f0f0f0; padding: 5px 10px; border-radius: 4px;")
        nav_buttons.addWidget(prev_day)
        nav_buttons.addWidget(next_day)
        calendar_section_layout.addLayout(nav_buttons)
        
        calendar_layout.addWidget(calendar_section)
        
        # Sección de Horario
        schedule_section = QWidget()
        schedule_section.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
        schedule_section_layout = QVBoxLayout(schedule_section)
        
        schedule_title = QLabel("Horario para jueves 5 junio 2025")
        schedule_title.setFont(QFont("Arial", 12, QFont.Bold))
        schedule_section_layout.addWidget(schedule_title)
        
        # Tabla de horario
        schedule_table = QTableWidget(5, 2)
        schedule_table.setHorizontalHeaderLabels(["Hora", "Asignatura"])
        schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        schedule_table.setStyleSheet("border: none;")
        
        # Datos de horario
        schedule_data = [
            ("8:00 - 9:30", "Matemáticas", "#4A90E2"),
            ("9:30 - 11:00", "Personal Social", "#F5A623"),
            ("11:00 - 11:30", "Recreo", "#FFFFFF"),
            ("11:30 - 13:00", "Comunicación", "#FF4081"),
            ("13:00 - 14:30", "Religión", "#F5A623")
        ]
        
        for row, (time, subject, color) in enumerate(schedule_data):
            time_item = QTableWidgetItem(time)
            schedule_table.setItem(row, 0, time_item)
            
            subject_item = QTableWidgetItem(subject)
            if subject != "Recreo":
                subject_item.setBackground(QColor(color))
                subject_item.setForeground(QColor("white"))
            schedule_table.setItem(row, 1, subject_item)
        
        schedule_section_layout.addWidget(schedule_table)
        calendar_layout.addWidget(schedule_section)
        
        # Sección de Eventos Próximos
        events_section = QWidget()
        events_section.setStyleSheet("background-color: white; border-radius: 5px; padding: 10px;")
        events_section_layout = QVBoxLayout(events_section)
        
        events_title = QLabel("Eventos Próximos")
        events_title.setFont(QFont("Arial", 12, QFont.Bold))
        events_section_layout.addWidget(events_title)
        
        no_events = QLabel("No hay eventos próximos programados")
        no_events.setStyleSheet("color: #666; margin: 20px 0;")
        events_section_layout.addWidget(no_events)
        
        calendar_layout.addWidget(events_section)
        
        # Pestaña de Notas por Alumnos
        notes_tab = QWidget()
        notes_layout = QVBoxLayout(notes_tab)
        notes_label = QLabel("Sección de notas por alumnos en desarrollo")
        notes_label.setAlignment(Qt.AlignCenter)
        notes_layout.addWidget(notes_label)
        
        # Añadir pestañas al widget de pestañas
        tabs.addTab(calendar_tab, "CALENDARIO Y HORARIOS")
        tabs.addTab(notes_tab, "NOTAS POR ALUMNOS")
        
        dashboard_layout.addWidget(tabs)
        
        return dashboard_widget

    def create_stat_card(self, title, value, color, icon):
        """Crear tarjeta de estadística"""
        card = QFrame()
        card.setFrameStyle(QFrame.Box)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
                margin: 5px;
                min-height: 120px;
            }}
            QFrame:hover {{
                box-shadow: 0 4px 8px rgba(0,0,0,0.1);
                border-color: {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        # Icono y valor
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
        top_layout.addWidget(icon_label)
        
        top_layout.addStretch()
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 24, QFont.Bold))
        value_label.setStyleSheet(f"color: {color};")
        top_layout.addWidget(value_label)
        
        layout.addLayout(top_layout)
        
        # Título
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12))
        title_label.setStyleSheet("color: #666; margin-top: 10px;")
        layout.addWidget(title_label)
        
        return card

    def change_page(self, index):
        """Cambiar a la página seleccionada en el stacked widget"""
        # Desmarcar todos los botones del sidebar
        for button in [self.btn_dashboard, self.btn_estudiantes, self.btn_lista_combinada, 
                       self.btn_asistencia, self.btn_eventos, self.btn_horarios, 
                       self.btn_calificaciones, self.btn_alertas, self.btn_Reporteemociones, 
                       self.btn_configuracion]:
            button.setChecked(False)
        
        # Marcar el botón correspondiente a la página actual
        if index == 0:
            self.btn_dashboard.setChecked(True)
        elif index == 1:
            self.btn_estudiantes.setChecked(True)
        elif index == 2:
            self.btn_lista_combinada.setChecked(True)
        elif index == 3:
            self.btn_asistencia.setChecked(True)
        elif index == 4:
            self.btn_eventos.setChecked(True)
        elif index == 5:
            self.btn_horarios.setChecked(True)
        elif index == 6:
            self.btn_calificaciones.setChecked(True)
        elif index == 7:
            self.btn_alertas.setChecked(True)
        elif index == 8:
            self.btn_Reporteemociones.setChecked(True)
        elif index == 9:
            self.btn_configuracion.setChecked(True)
        
        # Actualizar el título de la página
        self.page_title.setText(self.titles[index])
        
        # Cambiar la página en el stacked widget
        self.stacked_widget.setCurrentIndex(index)
