from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
                             QComboBox, QDateEdit, QGroupBox, QFileDialog, QMessageBox,
                             QTextEdit, QProgressBar)
from PySide6.QtCore import Qt, QDate, QThread, QTimer, Signal  # Cambiar pyqtSignal por Signal
from PySide6.QtGui import QPixmap, QImage
import os
import cv2
import matplotlib.pyplot as plt
import numpy as np
import time
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from app.models.database import Database
from app.utils.emotion_recognition import EmotionRecognition

class EmotionAnalysisThread(QThread):
    """Hilo para análisis de emociones en tiempo real"""
    emotion_detected = Signal(str, float, str)  # Cambiar pyqtSignal por Signal
    frame_ready = Signal(QPixmap)  # Nueva señal para enviar frames
    emotions_data_ready = Signal(dict)  # Nueva señal para enviar todos los datos de emociones
    
    def __init__(self):
        super().__init__()
        self.emotion_recognition = EmotionRecognition()
        self.running = False
        self.camera = None
    
    def start_analysis(self):
        self.running = True
        self.camera = cv2.VideoCapture(0)
        self.start()
    
    def stop_analysis(self):
        self.running = False
        if self.camera:
            self.camera.release()
        self.quit()
        self.wait()
    
    def run(self):
        while self.running and self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Detectar emoción cada 2 segundos
                emotion, confidence, emotions_scores = self.emotion_recognition.detect_emotion(frame)
                
                # Dibujar el mapeo facial y las barras de emociones en el frame
                frame_with_overlay = self.draw_facial_mapping_and_bars(frame, emotions_scores)
                
                # Convertir el frame a QPixmap y enviarlo
                rgb_frame = cv2.cvtColor(frame_with_overlay, cv2.COLOR_BGR2RGB)
                h, w, ch = rgb_frame.shape
                bytes_per_line = ch * w
                q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
                pixmap = QPixmap.fromImage(q_img)
                self.frame_ready.emit(pixmap)
                
                # Emitir los datos de emociones para actualizar la UI
                self.emotions_data_ready.emit(emotions_scores)
                
                if emotion != 'desconocido':
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.emotion_detected.emit(emotion, confidence, timestamp)
                
                self.msleep(100)  # Actualizar más rápido para una visualización fluida
    
    def draw_facial_mapping_and_bars(self, frame, emotions_scores):
        """Dibujar el mapeo facial y las barras de emociones en el frame"""
        try:
            # Crear una copia del frame para no modificar el original
            result_frame = frame.copy()
            
            # Detectar rostros usando OpenCV
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            # Dibujar barras de emociones en la parte izquierda
            bar_width = 150
            bar_height = 20
            start_x = 10
            start_y = 10
            max_value = 100  # El valor máximo para las barras
            
            # Mapear nombres de emociones y colores
            emotion_colors = {
                'angry': (0, 0, 255),      # Rojo
                'disgust': (0, 128, 128),  # Marrón
                'fear': (128, 0, 128),     # Púrpura
                'happy': (0, 255, 0),      # Verde
                'sad': (255, 0, 0),        # Azul
                'surprise': (0, 255, 255),  # Amarillo
                'neutral': (128, 128, 128)  # Gris
            }
            
            # Dibujar barras para cada emoción
            for i, (emotion, score) in enumerate(emotions_scores.items()):
                # Normalizar el valor a un porcentaje
                value = int(score)
                
                # Calcular la posición y tamaño de la barra
                y_pos = start_y + i * (bar_height + 5)
                
                # Dibujar el nombre de la emoción
                cv2.putText(result_frame, emotion, (start_x, y_pos - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                
                # Dibujar el fondo de la barra
                cv2.rectangle(result_frame, 
                              (start_x, y_pos), 
                              (start_x + bar_width, y_pos + bar_height), 
                              (50, 50, 50), 
                              -1)
                
                # Dibujar la barra de progreso
                bar_length = int((value / max_value) * bar_width)
                color = emotion_colors.get(emotion, (200, 200, 200))
                cv2.rectangle(result_frame, 
                              (start_x, y_pos), 
                              (start_x + bar_length, y_pos + bar_height), 
                              color, 
                              -1)
                
                # Mostrar el valor
                cv2.putText(result_frame, f"{value}%", 
                            (start_x + bar_width + 5, y_pos + bar_height - 5), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
            
            # Para cada rostro detectado, dibujar el mapeo facial
            for (x, y, w, h) in faces:
                # Dibujar un rectángulo alrededor del rostro
                cv2.rectangle(result_frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                
                # Simular puntos faciales (en una implementación real, usaríamos un detector de landmarks)
                # Estos son puntos aproximados para simular el efecto de la imagen
                
                # Puntos para los ojos
                left_eye_x, left_eye_y = x + int(w * 0.3), y + int(h * 0.4)
                right_eye_x, right_eye_y = x + int(w * 0.7), y + int(h * 0.4)
                
                # Puntos para la nariz
                nose_x, nose_y = x + int(w * 0.5), y + int(h * 0.6)
                
                # Puntos para la boca
                mouth_left_x, mouth_left_y = x + int(w * 0.3), y + int(h * 0.7)
                mouth_right_x, mouth_right_y = x + int(w * 0.7), y + int(h * 0.7)
                
                # Dibujar los puntos faciales
                cv2.circle(result_frame, (left_eye_x, left_eye_y), 3, (0, 255, 255), -1)
                cv2.circle(result_frame, (right_eye_x, right_eye_y), 3, (0, 255, 255), -1)
                cv2.circle(result_frame, (nose_x, nose_y), 3, (0, 255, 255), -1)
                cv2.circle(result_frame, (mouth_left_x, mouth_left_y), 3, (0, 255, 255), -1)
                cv2.circle(result_frame, (mouth_right_x, mouth_right_y), 3, (0, 255, 255), -1)
                
                # Dibujar líneas para conectar los puntos (malla facial)
                cv2.line(result_frame, (left_eye_x, left_eye_y), (right_eye_x, right_eye_y), (0, 255, 255), 1)
                cv2.line(result_frame, (left_eye_x, left_eye_y), (nose_x, nose_y), (0, 255, 255), 1)
                cv2.line(result_frame, (right_eye_x, right_eye_y), (nose_x, nose_y), (0, 255, 255), 1)
                cv2.line(result_frame, (nose_x, nose_y), (mouth_left_x, mouth_left_y), (0, 255, 255), 1)
                cv2.line(result_frame, (nose_x, nose_y), (mouth_right_x, mouth_right_y), (0, 255, 255), 1)
                cv2.line(result_frame, (mouth_left_x, mouth_left_y), (mouth_right_x, mouth_right_y), (0, 255, 255), 1)
            
            return result_frame
        except Exception as e:
            print(f"Error al dibujar mapeo facial: {str(e)}")
            return frame  # Devolver el frame original si hay un error

class ReportesView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.emotion_recognition = EmotionRecognition()
        self.emotion_thread = EmotionAnalysisThread()
        self.emotion_thread.emotion_detected.connect(self.on_emotion_detected)
        self.emotion_thread.frame_ready.connect(self.update_camera_view)

        self.emotion_thread.emotions_data_ready.connect(self.update_emotion_stats)
        self.setup_ui()
    
    def setup_ui(self):
        main_layout = QVBoxLayout()
        
        # Título
        title = QLabel("Generación de Reportes")
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Filtros para reportes
        filter_group = QGroupBox("Filtros")
        filter_layout = QHBoxLayout()
        
        # Tipo de reporte
        report_type_label = QLabel("Tipo de Reporte:")
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["Asistencia Diaria", "Asistencia Mensual", "Emociones"])
        filter_layout.addWidget(report_type_label)
        filter_layout.addWidget(self.report_type_combo)
        
        # Nivel
        nivel_label = QLabel("Nivel:")
        self.nivel_combo = QComboBox()
        self.load_niveles()
        self.nivel_combo.currentIndexChanged.connect(self.on_nivel_changed)
        filter_layout.addWidget(nivel_label)
        filter_layout.addWidget(self.nivel_combo)
        
        # Grado
        grado_label = QLabel("Grado:")
        self.grado_combo = QComboBox()
        self.grado_combo.currentIndexChanged.connect(self.on_grado_changed)
        filter_layout.addWidget(grado_label)
        filter_layout.addWidget(self.grado_combo)
        
        # Sección
        seccion_label = QLabel("Sección:")
        self.seccion_combo = QComboBox()
        filter_layout.addWidget(seccion_label)
        filter_layout.addWidget(self.seccion_combo)
        
        # Fechas
        fecha_inicio_label = QLabel("Fecha Inicio:")
        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setDate(QDate.currentDate().addDays(-30))
        self.fecha_inicio.setCalendarPopup(True)
        filter_layout.addWidget(fecha_inicio_label)
        filter_layout.addWidget(self.fecha_inicio)
        
        fecha_fin_label = QLabel("Fecha Fin:")
        self.fecha_fin = QDateEdit()
        self.fecha_fin.setDate(QDate.currentDate())
        self.fecha_fin.setCalendarPopup(True)
        filter_layout.addWidget(fecha_fin_label)
        filter_layout.addWidget(self.fecha_fin)
        
        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)
        
        # Agregar sección de análisis de emociones
        emotion_analysis_ui = self.setup_emotion_analysis_ui()
        main_layout.addWidget(emotion_analysis_ui)
        
        # Botones de acción
        button_layout = QHBoxLayout()
        
        generate_btn = QPushButton("📊 Generar Reporte")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_btn.clicked.connect(self.generate_report)
        button_layout.addWidget(generate_btn)
        
        # Botón para análisis de patrones
        pattern_btn = QPushButton("📈 Analizar Patrones Emocionales")
        pattern_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #732d91;
            }
        """)
        pattern_btn.clicked.connect(self.analyze_emotion_patterns)
        button_layout.addWidget(pattern_btn)
        
        export_btn = QPushButton("📄 Exportar PDF")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_btn.clicked.connect(self.generate_pdf)
        button_layout.addWidget(export_btn)
        
        main_layout.addLayout(button_layout)
        
        # Área para mostrar gráficos
        self.chart_area = QLabel()
        self.chart_area.setMinimumHeight(400)
        self.chart_area.setStyleSheet("border: 1px solid #ccc; background-color: white;")
        self.chart_area.setAlignment(Qt.AlignCenter)
        self.chart_area.setText("Los gráficos aparecerán aquí")
        main_layout.addWidget(self.chart_area)
        
        self.setLayout(main_layout)
    
    def setup_emotion_analysis_ui(self):
        """Configurar interfaz para análisis de emociones en tiempo real"""
        emotion_group = QGroupBox("🧠 Análisis de Emociones con IA")
        emotion_layout = QVBoxLayout()
        
        # Crear un layout horizontal para la cámara y las barras de emociones
        camera_emotion_layout = QHBoxLayout()
        
        # Panel izquierdo: Cámara
        camera_panel = QVBoxLayout()
        
        # Área para mostrar la cámara
        self.camera_view = QLabel()
        self.camera_view.setMinimumSize(480, 360)
        self.camera_view.setAlignment(Qt.AlignCenter)
        self.camera_view.setStyleSheet("border: 2px solid #3498db; background-color: #000;")
        self.camera_view.setText("La cámara se mostrará aquí...")
        camera_panel.addWidget(self.camera_view)
        
        # Botones de control bajo la cámara
        control_layout = QHBoxLayout()
        
        self.start_emotion_btn = QPushButton("🎥 Iniciar Análisis")
        self.start_emotion_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.start_emotion_btn.clicked.connect(self.start_emotion_analysis)
        
        self.stop_emotion_btn = QPushButton("⏹️ Detener Análisis")
        self.stop_emotion_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        self.stop_emotion_btn.clicked.connect(self.stop_emotion_analysis)
        self.stop_emotion_btn.setEnabled(False)
        
        # Botón para exportar análisis en tiempo real a PDF
        self.export_realtime_btn = QPushButton("📄 Exportar Análisis")
        self.export_realtime_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.export_realtime_btn.clicked.connect(self.export_realtime_analysis)
        self.export_realtime_btn.setEnabled(False)
        
        control_layout.addWidget(self.start_emotion_btn)
        control_layout.addWidget(self.stop_emotion_btn)
        control_layout.addWidget(self.export_realtime_btn)
        
        camera_panel.addLayout(control_layout)
        camera_emotion_layout.addLayout(camera_panel, 3)  # Proporción 3
        
        # Panel derecho: Resultados y estadísticas en tiempo real
        results_panel = QVBoxLayout()
        
        # Título para resultados
        results_title = QLabel("Resultados en Tiempo Real:")
        results_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        results_panel.addWidget(results_title)
        
        # Área de resultados en tiempo real
        self.emotion_results = QTextEdit()
        self.emotion_results.setMaximumHeight(150)
        self.emotion_results.setPlaceholderText("Los resultados del análisis de emociones aparecerán aquí...")
        results_panel.addWidget(self.emotion_results)
        
        # Área para estadísticas en tiempo real
        stats_title = QLabel("Estadísticas:")
        stats_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        results_panel.addWidget(stats_title)
        
        self.emotion_stats = QTextEdit()
        self.emotion_stats.setMaximumHeight(150)
        self.emotion_stats.setPlaceholderText("Las estadísticas aparecerán aquí...")
        self.emotion_stats.setReadOnly(True)
        results_panel.addWidget(self.emotion_stats)
        
        # Botón para analizar imagen
        self.analyze_image_btn = QPushButton("🖼️ Analizar Imagen")
        self.analyze_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #8e44ad;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #732d91;
            }
        """)
        self.analyze_image_btn.clicked.connect(self.analyze_image_emotion)
        results_panel.addWidget(self.analyze_image_btn)
        
        camera_emotion_layout.addLayout(results_panel, 2)  # Proporción 2
        
        emotion_layout.addLayout(camera_emotion_layout)
        emotion_group.setLayout(emotion_layout)
        
        # Conectar la señal de frame_ready
        self.emotion_thread.frame_ready.connect(self.update_camera_view)
        
        return emotion_group
    
    def start_emotion_analysis(self):
        """Iniciar análisis de emociones en tiempo real"""
        try:
            self.emotion_thread.start_analysis()
            self.start_emotion_btn.setEnabled(False)
            self.stop_emotion_btn.setEnabled(True)
            self.emotion_results.clear()
            self.emotion_stats.clear()
            self.emotion_results.append("🎥 Análisis de emociones iniciado...\n")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"No se pudo iniciar el análisis: {str(e)}")
    
    def stop_emotion_analysis(self):
        """Detener análisis de emociones"""
        self.emotion_thread.stop_analysis()
        self.start_emotion_btn.setEnabled(True)
        self.stop_emotion_btn.setEnabled(False)
        self.emotion_results.append("⏹️ Análisis de emociones detenido.\n")
        
        # Habilitar botón de exportación si hay resultados
        if self.emotion_results.toPlainText().strip():
            self.export_realtime_btn.setEnabled(True)
    
    def on_emotion_detected(self, emotion, confidence, timestamp):
        """Manejar emoción detectada"""
        # Mostrar en tiempo real
        emotion_text = f"[{timestamp}] Emoción: {emotion.upper()} (Confianza: {confidence:.2f})\n"
        self.emotion_results.append(emotion_text)
        
        # Habilitar botón de exportación cuando hay datos
        self.export_realtime_btn.setEnabled(True)
        
        # Guardar en base de datos (aquí necesitarías el ID del estudiante actual)
        self.save_emotion_to_database(1, emotion, confidence, timestamp)  # ID 1 como ejemplo
    
    def save_emotion_to_database(self, student_id, emotion, confidence, timestamp):
        """Guardar emoción detectada en la base de datos"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO emociones (estudiante_id, emocion, confianza, fecha_registro)
                VALUES (?, ?, ?, ?)
            """, (student_id, emotion, confidence, timestamp))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al guardar emoción: {str(e)}")
    
    def analyze_emotion_patterns(self):
        """Analizar patrones de emociones por horarios, días, etc."""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Obtener fechas del filtro
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            
            # Análisis por hora del día
            cursor.execute("""
                SELECT 
                    strftime('%H', fecha_registro) as hora,
                    emocion,
                    COUNT(*) as cantidad
                FROM emociones 
                WHERE fecha_registro BETWEEN ? AND ?
                GROUP BY hora, emocion
                ORDER BY hora, cantidad DESC
            """, (fecha_inicio, fecha_fin))
            
            hourly_data = cursor.fetchall()
            
            # Análisis por día de la semana
            cursor.execute("""
                SELECT 
                    CASE strftime('%w', fecha_registro)
                        WHEN '0' THEN 'Domingo'
                        WHEN '1' THEN 'Lunes'
                        WHEN '2' THEN 'Martes'
                        WHEN '3' THEN 'Miércoles'
                        WHEN '4' THEN 'Jueves'
                        WHEN '5' THEN 'Viernes'
                        WHEN '6' THEN 'Sábado'
                    END as dia_semana,
                    emocion,
                    COUNT(*) as cantidad,
                    AVG(confianza) as confianza_promedio
                FROM emociones 
                WHERE fecha_registro BETWEEN ? AND ?
                GROUP BY dia_semana, emocion
                ORDER BY cantidad DESC
            """, (fecha_inicio, fecha_fin))
            
            weekly_data = cursor.fetchall()
            conn.close()
            
            # Crear visualización de patrones
            plt.figure(figsize=(12, 10))
            
            # Gráfico 1: Emociones por hora del día
            plt.subplot(2, 1, 1)
            
            # Procesar datos por hora
            horas = sorted(set([row[0] for row in hourly_data]))
            emociones = sorted(set([row[1] for row in hourly_data]))
            
            # Crear diccionario para almacenar datos
            emotion_by_hour = {emocion: [0] * len(horas) for emocion in emociones}
            
            for row in hourly_data:
                hora, emocion, cantidad = row
                hora_idx = horas.index(hora)
                emotion_by_hour[emocion][hora_idx] = cantidad
            
            # Colores para cada emoción
            colors = {
                'happy': '#2ecc71',
                'sad': '#3498db',
                'angry': '#e74c3c',
                'surprised': '#f39c12',
                'scared': '#9b59b6',
                'disgusted': '#34495e',
                'neutral': '#95a5a6'
            }
            
            # Crear gráfico de barras apiladas
            bottom = [0] * len(horas)
            for emocion in emociones:
                plt.bar(horas, emotion_by_hour[emocion], bottom=bottom, 
                       label=emocion.title(), color=colors.get(emocion, '#bdc3c7'))
                bottom = [bottom[i] + emotion_by_hour[emocion][i] for i in range(len(horas))]
            
            plt.title('Patrones de Emociones por Hora del Día')
            plt.xlabel('Hora')
            plt.ylabel('Cantidad de Detecciones')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            # Gráfico 2: Emociones por día de la semana
            plt.subplot(2, 1, 2)
            
            # Procesar datos por día
            dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
            dias_presentes = [dia for dia in dias if dia in [row[0] for row in weekly_data]]
            
            # Crear diccionario para almacenar datos
            emotion_by_day = {emocion: [0] * len(dias_presentes) for emocion in emociones}
            
            for row in weekly_data:
                dia, emocion, cantidad, _ = row
                if dia in dias_presentes:
                    dia_idx = dias_presentes.index(dia)
                    emotion_by_day[emocion][dia_idx] = cantidad
            
            # Crear gráfico de barras apiladas
            bottom = [0] * len(dias_presentes)
            for emocion in emociones:
                plt.bar(dias_presentes, emotion_by_day[emocion], bottom=bottom, 
                       label=emocion.title(), color=colors.get(emocion, '#bdc3c7'))
                bottom = [bottom[i] + emotion_by_day[emocion][i] for i in range(len(dias_presentes))]
            
            plt.title('Patrones de Emociones por Día de la Semana')
            plt.xlabel('Día')
            plt.ylabel('Cantidad de Detecciones')
            plt.legend()
            plt.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Guardar y mostrar
            chart_path = 'temp_pattern_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            pixmap = QPixmap(chart_path)
            self.chart_area.setPixmap(pixmap.scaled(self.chart_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            if os.path.exists(chart_path):
                os.remove(chart_path)
                
            # Mostrar también texto de análisis
            analysis_text = "📊 ANÁLISIS DE PATRONES EMOCIONALES\n\n"
            analysis_text += f"Período analizado: {fecha_inicio} a {fecha_fin}\n\n"
            analysis_text += "📈 Patrones por día de la semana:\n"
            for row in weekly_data[:10]:  # Top 10
                analysis_text += f"  {row[0]}: {row[1].title()} ({row[2]} veces, confianza: {row[3]:.2f})\n"
            
            self.emotion_results.clear()
            self.emotion_results.append(analysis_text)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en análisis de patrones: {str(e)}")
    
    def generate_pdf(self):
        """Generar reporte en PDF"""
        try:
            report_type = self.report_type_combo.currentText()
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Reporte PDF", f"reporte_{report_type.lower().replace(' ', '_')}.pdf", "PDF Files (*.pdf)"
            )
            
            if file_path:
                if report_type == "Emociones":
                    self.generate_emotion_pdf(file_path)
                else:
                    self.generate_attendance_pdf(file_path)
                    
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF: {str(e)}")
    
    def generate_emotion_pdf(self, file_path):
        """Generar PDF específico para reporte de emociones"""
        try:
            # Obtener fechas del filtro
            fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
            fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
            
            # Obtener datos de emociones
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT emocion, COUNT(*) as cantidad, AVG(confianza) as confianza_promedio
                FROM emociones 
                WHERE fecha_registro BETWEEN ? AND ?
                GROUP BY emocion
                ORDER BY cantidad DESC
            """, (fecha_inicio, fecha_fin))
            
            emotion_data = cursor.fetchall()
            
            # Crear documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título y encabezado
            title = Paragraph("Reporte de Análisis de Emociones", styles['Title'])
            story.append(title)
            
            # Información del reporte
            report_info = f"Período: {fecha_inicio} a {fecha_fin}"
            story.append(Paragraph(report_info, styles['Normal']))
            story.append(Paragraph("<br/>", styles['Normal']))
            
            # Tabla de resumen de emociones
            if emotion_data:
                story.append(Paragraph("Resumen de Emociones Detectadas", styles['Heading2']))
                
                # Crear tabla
                data = [["Emoción", "Cantidad", "Confianza Promedio"]]
                for row in emotion_data:
                    emocion = row[0].title()
                    cantidad = str(row[1])
                    confianza = f"{row[2]:.2f}"
                    data.append([emocion, cantidad, confianza])
                
                # Añadir fila de totales
                total_detecciones = sum(row[1] for row in emotion_data)
                confianza_general = sum(row[1] * row[2] for row in emotion_data) / total_detecciones if total_detecciones > 0 else 0
                data.append(["TOTAL", str(total_detecciones), f"{confianza_general:.2f}"])
                
                table = Table(data, colWidths=[doc.width/3.0]*3)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.blue),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),
                    ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                story.append(table)
                story.append(Paragraph("<br/>", styles['Normal']))
                
                # Generar gráficos para el PDF
                # Gráfico de pastel
                plt.figure(figsize=(8, 5))
                emociones = [row[0].title() for row in emotion_data]
                valores = [row[1] for row in emotion_data]
                
                colors_map = {
                    'Happy': '#2ecc71',
                    'Neutral': '#95a5a6', 
                    'Sad': '#3498db',
                    'Angry': '#e74c3c',
                    'Surprised': '#f39c12',
                    'Scared': '#9b59b6',
                    'Disgusted': '#34495e'
                }
                pie_colors = [colors_map.get(emo, '#bdc3c7') for emo in emociones]
                
                plt.pie(valores, labels=emociones, autopct='%1.1f%%', startangle=90, colors=pie_colors)
                plt.title('Distribución de Emociones')
                
                # Guardar gráfico
                chart_path = 'temp_emotion_pie.png'
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                
                # Añadir gráfico al PDF
                story.append(Paragraph("Distribución de Emociones", styles['Heading2']))
                story.append(Paragraph("<br/>", styles['Normal']))
                story.append(Image(chart_path, width=400, height=300))
                story.append(Paragraph("<br/>", styles['Normal']))
                
                # Limpiar archivo temporal
                if os.path.exists(chart_path):
                    os.remove(chart_path)
                
                # Análisis de patrones
                story.append(Paragraph("Análisis de Patrones", styles['Heading2']))
                story.append(Paragraph("<br/>", styles['Normal']))
                
                # Obtener datos de patrones por día
                cursor.execute("""
                    SELECT 
                        CASE strftime('%w', fecha_registro)
                            WHEN '0' THEN 'Domingo'
                            WHEN '1' THEN 'Lunes'
                            WHEN '2' THEN 'Martes'
                            WHEN '3' THEN 'Miércoles'
                            WHEN '4' THEN 'Jueves'
                            WHEN '5' THEN 'Viernes'
                            WHEN '6' THEN 'Sábado'
                        END as dia_semana,
                        emocion,
                        COUNT(*) as cantidad
                    FROM emociones 
                    WHERE fecha_registro BETWEEN ? AND ?
                    GROUP BY dia_semana, emocion
                    ORDER BY dia_semana, cantidad DESC
                """, (fecha_inicio, fecha_fin))
                
                weekly_data = cursor.fetchall()
                
                if weekly_data:
                    # Crear tabla de patrones por día
                    story.append(Paragraph("Emociones por Día de la Semana", styles['Heading3']))
                    
                    # Procesar datos para la tabla
                    dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
                    dias_presentes = sorted(set([row[0] for row in weekly_data]), 
                                          key=lambda x: dias.index(x) if x in dias else 999)
                    
                    # Crear tabla
                    pattern_data = [["Día", "Emoción Dominante", "Cantidad"]]
                    
                    for dia in dias_presentes:
                        dia_emociones = [row for row in weekly_data if row[0] == dia]
                        if dia_emociones:
                            emocion_dominante = dia_emociones[0][1].title()
                            cantidad = dia_emociones[0][2]
                            pattern_data.append([dia, emocion_dominante, str(cantidad)])
                    
                    pattern_table = Table(pattern_data, colWidths=[doc.width/3.0]*3)
                    pattern_table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.purple),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    
                    story.append(pattern_table)
                
                # Conclusiones y recomendaciones
                story.append(Paragraph("<br/>", styles['Normal']))
                story.append(Paragraph("Conclusiones y Recomendaciones", styles['Heading2']))
                
                # Determinar emoción dominante
                emocion_dominante = emotion_data[0][0].title() if emotion_data else "Neutral"
                
                conclusions = f"""Durante el período analizado, la emoción predominante fue {emocion_dominante}. 
                Este análisis puede ayudar a entender el estado emocional general de los estudiantes y 
                adaptar las estrategias pedagógicas según sea necesario."""
                
                story.append(Paragraph(conclusions, styles['Normal']))
                
            else:
                story.append(Paragraph("No hay datos de emociones para el período seleccionado", styles['Heading2']))
            
            # Construir el PDF
            doc.build(story)
            conn.close()
            
            QMessageBox.information(self, "Éxito", f"Reporte de emociones guardado en: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF de emociones: {str(e)}")
    
    def generate_attendance_pdf(self, file_path):
        """Generar reporte en PDF para asistencia"""
        try:
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título
            title = Paragraph("Reporte de Asistencia", styles['Title'])
            story.append(title)
            
            # Datos de ejemplo para la tabla
            data = [
                ['Estudiante', 'Grado', 'Sección', 'Asistencias', 'Faltas'],
                ['Juan Pérez', '1° A', 'A', '18', '2'],
                ['María García', '1° A', 'A', '20', '0'],
                ['Carlos López', '1° A', 'A', '17', '3']
            ]
            
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
            doc.build(story)
            
            QMessageBox.information(self, "Éxito", f"Reporte de asistencia guardado en: {file_path}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar PDF: {str(e)}")
    
    def load_niveles(self):
        """Cargar niveles desde la base de datos"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM niveles")
            niveles = cursor.fetchall()
            
            self.nivel_combo.clear()
            self.nivel_combo.addItem("Todos", None)
            for nivel in niveles:
                self.nivel_combo.addItem(nivel[1], nivel[0])
            
            conn.close()
        except Exception as e:
            print(f"Error cargando niveles: {e}")
    
    def on_nivel_changed(self):
        """Manejar cambio de nivel"""
        nivel_id = self.nivel_combo.currentData()
        self.load_grados(nivel_id)
    
    def load_grados(self, nivel_id):
        """Cargar grados según el nivel seleccionado"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            if nivel_id:
                cursor.execute("SELECT id, nombre FROM grados WHERE nivel_id = ?", (nivel_id,))
            else:
                cursor.execute("SELECT id, nombre FROM grados")
            
            grados = cursor.fetchall()
            
            self.grado_combo.clear()
            self.grado_combo.addItem("Todos", None)
            for grado in grados:
                self.grado_combo.addItem(grado[1], grado[0])
            
            conn.close()
        except Exception as e:
            print(f"Error cargando grados: {e}")
    
    def on_grado_changed(self):
        """Manejar cambio de grado"""
        grado_id = self.grado_combo.currentData()
        self.load_secciones(grado_id)
    
    def load_secciones(self, grado_id):
        """Cargar secciones según el grado seleccionado"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            if grado_id:
                cursor.execute("SELECT id, nombre FROM secciones WHERE grado_id = ?", (grado_id,))
            else:
                cursor.execute("SELECT id, nombre FROM secciones")
            
            secciones = cursor.fetchall()
            
            self.seccion_combo.clear()
            self.seccion_combo.addItem("Todas", None)
            for seccion in secciones:
                self.seccion_combo.addItem(seccion[1], seccion[0])
            
            conn.close()
        except Exception as e:
            print(f"Error cargando secciones: {e}")
    
    def generate_report(self):
        """Generar reporte según el tipo seleccionado"""
        report_type = self.report_type_combo.currentText()
        fecha_inicio = self.fecha_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.fecha_fin.date().toString("yyyy-MM-dd")
        
        if report_type == "Emociones":
            self.generate_emotion_chart(fecha_inicio, fecha_fin)
        elif report_type == "Asistencia Diaria":
            self.generate_attendance_chart(fecha_inicio, fecha_fin)
        elif report_type == "Asistencia Mensual":
            self.generate_monthly_attendance_chart(fecha_inicio, fecha_fin)
    
    def generate_emotion_chart(self, fecha_inicio, fecha_fin):
        """Generar gráfico de emociones con datos reales de la base de datos"""
        try:
            db = Database()
            conn = db.connect()
            cursor = conn.cursor()
            
            # Obtener datos de emociones del período especificado
            cursor.execute("""
                SELECT emocion, COUNT(*) as cantidad, AVG(confianza) as confianza_promedio
                FROM emociones 
                WHERE fecha_registro BETWEEN ? AND ?
                GROUP BY emocion
                ORDER BY cantidad DESC
            """, (fecha_inicio, fecha_fin))
            
            results = cursor.fetchall()
            conn.close()
            
            if not results:
                # Si no hay datos, mostrar mensaje
                plt.figure(figsize=(10, 6))
                plt.text(0.5, 0.5, 'No hay datos de emociones\nen el período seleccionado', 
                        horizontalalignment='center', verticalalignment='center',
                        fontsize=16, transform=plt.gca().transAxes)
                plt.title('Distribución de Emociones')
            else:
                # Crear gráfico con datos reales
                emociones = [row[0].title() for row in results]
                valores = [row[1] for row in results]
                confianzas = [row[2] for row in results]
                
                # Crear gráfico de pastel
                plt.figure(figsize=(12, 8))
                
                # Subplot 1: Gráfico de pastel
                plt.subplot(2, 2, 1)
                colors_map = {
                    'Feliz': '#2ecc71',
                    'Neutral': '#95a5a6', 
                    'Triste': '#3498db',
                    'Enojado': '#e74c3c',
                    'Sorprendido': '#f39c12',
                    'Miedo': '#9b59b6',
                    'Disgusto': '#34495e'
                }
                pie_colors = [colors_map.get(emo, '#bdc3c7') for emo in emociones]
                
                plt.pie(valores, labels=emociones, autopct='%1.1f%%', startangle=90, colors=pie_colors)
                plt.title('Distribución de Emociones')
                
                # Subplot 2: Gráfico de barras con confianza
                plt.subplot(2, 2, 2)
                bars = plt.bar(emociones, valores, color=pie_colors)
                plt.title('Frecuencia de Emociones')
                plt.ylabel('Cantidad')
                plt.xticks(rotation=45)
                
                # Subplot 3: Confianza promedio
                plt.subplot(2, 2, 3)
                plt.bar(emociones, confianzas, color=pie_colors, alpha=0.7)
                plt.title('Confianza Promedio por Emoción')
                plt.ylabel('Confianza')
                plt.xticks(rotation=45)
                plt.ylim(0, 1)
                
                # Subplot 4: Estadísticas
                plt.subplot(2, 2, 4)
                plt.axis('off')
                total_detecciones = sum(valores)
                emocion_dominante = emociones[0] if emociones else 'N/A'
                confianza_general = sum(confianzas) / len(confianzas) if confianzas else 0
                
                stats_text = f"""
                ESTADÍSTICAS GENERALES
                
                Total de detecciones: {total_detecciones}
                Emoción dominante: {emocion_dominante}
                Confianza general: {confianza_general:.2f}
                Período: {fecha_inicio} - {fecha_fin}
                """
                plt.text(0.1, 0.9, stats_text, fontsize=12, verticalalignment='top')
            
            plt.tight_layout()
            
            # Guardar y mostrar
            chart_path = 'temp_emotion_chart.png'
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            pixmap = QPixmap(chart_path)
            self.chart_area.setPixmap(pixmap.scaled(self.chart_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
            
            if os.path.exists(chart_path):
                os.remove(chart_path)
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al generar gráfico de emociones: {str(e)}")
    
    def generate_attendance_chart(self, fecha_inicio, fecha_fin):
        """Generar gráfico de asistencia diaria"""
        plt.figure(figsize=(10, 6))
        
        # Datos de ejemplo
        fechas = ['2024-01-01', '2024-01-02', '2024-01-03', '2024-01-04', '2024-01-05']
        asistencias = [85, 90, 78, 92, 88]
        
        plt.plot(fechas, asistencias, marker='o', linewidth=2, markersize=8)
        plt.title('Asistencia Diaria')
        plt.xlabel('Fecha')
        plt.ylabel('Porcentaje de Asistencia')
        plt.xticks(rotation=45)
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        
        chart_path = 'temp_chart.png'
        plt.savefig(chart_path)
        plt.close()
        
        pixmap = QPixmap(chart_path)
        self.chart_area.setPixmap(pixmap.scaled(self.chart_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        if os.path.exists(chart_path):
            os.remove(chart_path)
    
    def generate_monthly_attendance_chart(self, fecha_inicio, fecha_fin):
        """Generar gráfico de asistencia mensual"""
        plt.figure(figsize=(10, 6))
        
        # Datos de ejemplo
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo']
        asistencias = [88, 92, 85, 90, 87]
        
        plt.bar(meses, asistencias, color=['#3498db', '#2ecc71', '#f39c12', '#e74c3c', '#9b59b6'])
        plt.title('Asistencia Mensual')
        plt.xlabel('Mes')
        plt.ylabel('Porcentaje de Asistencia')
        plt.ylim(0, 100)
        plt.tight_layout()
        
        chart_path = 'temp_chart.png'
        plt.savefig(chart_path)
        plt.close()
        
        pixmap = QPixmap(chart_path)
        self.chart_area.setPixmap(pixmap.scaled(self.chart_area.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        if os.path.exists(chart_path):
            os.remove(chart_path)
    
    def update_camera_view(self, pixmap):
        """Actualizar la vista de la cámara con el frame recibido"""
        if self.camera_view:
            self.camera_view.setPixmap(pixmap.scaled(
                self.camera_view.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
    def update_emotion_stats(self, emotions_scores):
        """Actualizar estadísticas de emociones en tiempo real"""
        try:
            # Limpiar el área de estadísticas
            self.emotion_stats.clear()
            
            # Mostrar estadísticas de emociones
            self.emotion_stats.append("📊 DISTRIBUCIÓN DE EMOCIONES:\n")
            
            # Ordenar emociones por valor (de mayor a menor)
            sorted_emotions = sorted(emotions_scores.items(), key=lambda x: x[1], reverse=True)
            
            # Mostrar cada emoción con su valor
            for emotion, score in sorted_emotions:
                # Convertir el score a un porcentaje entero
                percentage = int(score)
                
                # Crear una barra visual con caracteres
                bar_length = int(percentage / 5)  # 20 caracteres = 100%
                bar = '█' * bar_length
                
                # Añadir la emoción con su barra y porcentaje
                self.emotion_stats.append(f"{emotion.title()}: {bar} {percentage}%\n")
            
            # Añadir la emoción dominante
            if sorted_emotions:
                dominant_emotion, highest_score = sorted_emotions[0]
                self.emotion_stats.append(f"\nEmoción dominante: {dominant_emotion.title()} ({int(highest_score)}%)")
        
        except Exception as e:
            print(f"Error al actualizar estadísticas: {str(e)}")
            
    def analyze_image_emotion(self):
        """Analizar emociones desde una imagen seleccionada"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar Imagen", "", "Imágenes (*.png *.jpg *.jpeg)"
            )
            
            if not file_path:
                return
                
            # Cargar la imagen
            image = cv2.imread(file_path)
            if image is None:
                QMessageBox.warning(self, "Error", "No se pudo cargar la imagen seleccionada.")
                return
            
            # Detectar emoción
            emotion, confidence, emotions_scores = self.emotion_recognition.detect_emotion(image)
            
            # Dibujar el mapeo facial y las barras de emociones
            result_frame = self.emotion_thread.draw_facial_mapping_and_bars(image, emotions_scores)
            
            # Convertir a QPixmap y mostrar
            rgb_frame = cv2.cvtColor(result_frame, cv2.COLOR_BGR2RGB)
            h, w, ch = rgb_frame.shape
            bytes_per_line = ch * w
            q_img = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(q_img)
            
            # Mostrar en la vista de cámara
            self.camera_view.setPixmap(pixmap.scaled(
                self.camera_view.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            ))
            
            # Mostrar resultados
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.emotion_results.clear()
            self.emotion_results.append(f"🖼️ Análisis de imagen: {os.path.basename(file_path)}\n")
            self.emotion_results.append(f"[{timestamp}] Emoción dominante: {emotion.upper()} (Confianza: {confidence:.2f})\n")
            
            # Mostrar estadísticas
            self.emotion_stats.clear()
            self.emotion_stats.append("📊 DISTRIBUCIÓN DE EMOCIONES:\n")
            for emo, score in emotions_scores.items():
                self.emotion_stats.append(f"{emo.title()}: {score:.2f}%\n")
            
            # Habilitar botón de exportación
            self.export_realtime_btn.setEnabled(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al analizar imagen: {str(e)}")

    def export_realtime_analysis(self):
        """Exportar análisis de emociones en tiempo real a PDF"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Guardar Análisis en Tiempo Real", "analisis_tiempo_real.pdf", "PDF Files (*.pdf)"
            )
            
            if not file_path:
                return
                
            # Crear documento PDF
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Título y encabezado
            title = Paragraph("Análisis de Emociones en Tiempo Real", styles['Title'])
            story.append(title)
            
            # Fecha y hora
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            report_info = f"Generado el: {timestamp}"
            story.append(Paragraph(report_info, styles['Normal']))
            story.append(Paragraph("<br/>", styles['Normal']))
            
            # Capturar el frame actual con las barras de emociones
            if hasattr(self, 'camera_view') and self.camera_view.pixmap() is not None:
                try:
                    # Usar un directorio específico para los archivos temporales
                    temp_dir = os.path.join(os.getcwd(), "temp")
                    os.makedirs(temp_dir, exist_ok=True)
                    
                    # Crear un nombre de archivo con timestamp para evitar conflictos
                    current_frame_path = os.path.join(temp_dir, f"frame_{int(time.time())}.png")
                    
                    # Guardar el pixmap actual como imagen
                    pixmap = self.camera_view.pixmap()
                    if not pixmap.save(current_frame_path, "PNG"):
                        raise Exception("No se pudo guardar la imagen")
                    
                    # Verificar que el archivo existe antes de intentar usarlo
                    if os.path.exists(current_frame_path) and os.path.getsize(current_frame_path) > 0:
                        # Añadir la imagen al PDF
                        story.append(Paragraph("Captura del Análisis en Tiempo Real", styles['Heading2']))
                        story.append(Image(current_frame_path, width=400, height=300))
                        story.append(Paragraph("<br/>", styles['Normal']))
                    else:
                        story.append(Paragraph("No se pudo incluir la captura de la cámara", styles['Normal']))
                    
                    # Eliminar archivo temporal después de usarlo (al final del método)
                except Exception as img_error:
                    story.append(Paragraph(f"Error al procesar imagen: {str(img_error)}", styles['Normal']))
            
            # Obtener los resultados actuales del análisis
            emotion_text = self.emotion_results.toPlainText()
            if emotion_text:
                story.append(Paragraph("Resultados del Análisis", styles['Heading2']))
                story.append(Paragraph(emotion_text.replace('\n', '<br/>'), styles['Normal']))
                story.append(Paragraph("<br/>", styles['Normal']))
            
            # Obtener estadísticas actuales
            stats_text = self.emotion_stats.toPlainText()
            if stats_text:
                story.append(Paragraph("Estadísticas", styles['Heading2']))
                story.append(Paragraph(stats_text.replace('\n', '<br/>'), styles['Normal']))
                story.append(Paragraph("<br/>", styles['Normal']))
            
            # Generar gráficos basados en las estadísticas actuales
            if hasattr(self, 'emotion_stats') and self.emotion_stats.toPlainText():
                try:
                    # Extraer datos de emociones del texto de estadísticas
                    emotions_data = {}
                    for line in self.emotion_stats.toPlainText().split('\n'):
                        if ':' in line and '%' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                emotion_name = parts[0].strip()
                                # Extraer el porcentaje (número antes del %)
                                percentage_text = parts[1].strip()
                                percentage = 0
                                for word in percentage_text.split():
                                    if word.isdigit():
                                        percentage = int(word)
                                        break
                                if emotion_name and percentage > 0:
                                    emotions_data[emotion_name] = percentage
                    
                    if emotions_data:
                        # Crear gráfico de pastel
                        plt.figure(figsize=(8, 6))
                        
                        # Colores para cada emoción
                        colors_map = {
                            'Feliz': '#2ecc71',
                            'Neutral': '#95a5a6', 
                            'Triste': '#3498db',
                            'Enojado': '#e74c3c',
                            'Sorprendido': '#f39c12',
                            'Miedo': '#9b59b6',
                            'Disgusto': '#34495e'
                        }
                        
                        # Preparar datos para el gráfico
                        labels = list(emotions_data.keys())
                        sizes = list(emotions_data.values())
                        colors = [colors_map.get(emotion, '#bdc3c7') for emotion in labels]
                        
                        # Crear gráfico de pastel
                        plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
                        plt.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
                        plt.title('Distribución de Emociones')
                        
                        # Guardar gráfico en archivo específico
                        chart_path = os.path.join(temp_dir, f"chart_{int(time.time())}.png")
                        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        # Verificar que el archivo existe antes de intentar usarlo
                        if os.path.exists(chart_path) and os.path.getsize(chart_path) > 0:
                            # Añadir gráfico al PDF
                            story.append(Paragraph("Gráfico de Emociones", styles['Heading2']))
                            story.append(Image(chart_path, width=400, height=300))
                        
                        # Crear gráfico de barras
                        plt.figure(figsize=(8, 6))
                        bars = plt.bar(labels, sizes, color=colors)
                        plt.title('Intensidad de Emociones')
                        plt.ylabel('Porcentaje')
                        plt.ylim(0, 100)
                        plt.xticks(rotation=45)
                        
                        # Añadir valores encima de las barras
                        for bar in bars:
                            height = bar.get_height()
                            plt.text(bar.get_x() + bar.get_width()/2., height + 1,
                                    f'{height}%', ha='center', va='bottom')
                        
                        # Guardar gráfico en archivo específico
                        bars_chart_path = os.path.join(temp_dir, f"bars_{int(time.time())}.png")
                        plt.savefig(bars_chart_path, dpi=300, bbox_inches='tight')
                        plt.close()
                        
                        # Verificar que el archivo existe antes de intentar usarlo
                        if os.path.exists(bars_chart_path) and os.path.getsize(bars_chart_path) > 0:
                            # Añadir gráfico al PDF
                            story.append(Paragraph("<br/>", styles['Normal']))
                            story.append(Image(bars_chart_path, width=400, height=300))
                except Exception as chart_error:
                    story.append(Paragraph(f"Error al generar gráficos: {str(chart_error)}", styles['Normal']))
            
            # Construir el PDF
            doc.build(story)
            
            # Limpiar archivos temporales después de construir el PDF
            try:
                if os.path.exists(temp_dir):
                    for temp_file in os.listdir(temp_dir):
                        os.remove(os.path.join(temp_dir, temp_file))
            except Exception:
                pass  # Ignorar errores al limpiar archivos temporales
            
            QMessageBox.information(self, "Éxito", f"Análisis en tiempo real guardado en: {file_path}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al exportar análisis en tiempo real: {str(e)}")










