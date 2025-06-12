from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QLabel, QFrame, QTextEdit, QGroupBox, QProgressBar)
from PySide6.QtCore import Qt, QThread, QTimer, Signal
from PySide6.QtGui import QPixmap, QImage, QFont
import cv2
import numpy as np
from datetime import datetime
from app.utils.emotion_recognition import EmotionRecognition
from app.models.database import Database

class EmotionLiveThread(QThread):
    """Hilo para captura y análisis de emociones en tiempo real"""
    frame_ready = Signal(np.ndarray)
    emotion_detected = Signal(str, float, str, dict)  # Agregar distribución de emociones
    
    def __init__(self):
        super().__init__()
        self.emotion_recognition = EmotionRecognition()
        self.running = False
        self.camera = None
        self.frame_count = 0
        self.detection_interval = 15  # Detectar cada 15 frames para mejor rendimiento
    
    def start_analysis(self):
        """Iniciar análisis de emociones"""
        try:
            self.camera = cv2.VideoCapture(0)
            if not self.camera.isOpened():
                return False
            
            self.running = True
            self.start()
            return True
        except Exception as e:
            print(f"Error al iniciar cámara: {e}")
            return False
    
    def stop_analysis(self):
        """Detener análisis de emociones"""
        self.running = False
        if self.camera:
            self.camera.release()
            self.camera = None
        self.quit()
        self.wait()
    
    def run(self):
        while self.running and self.camera and self.camera.isOpened():
            ret, frame = self.camera.read()
            if ret:
                # Emitir frame para mostrar en la interfaz
                self.frame_ready.emit(frame.copy())
                
                # Analizar emoción cada N frames
                self.frame_count += 1
                if self.frame_count % self.detection_interval == 0:
                    try:
                        emotion, confidence, emotions_scores = self.emotion_recognition.detect_emotion(frame)
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        
                        # Obtener distribución completa de emociones
                        distribution = self.emotion_recognition.get_emotion_distribution(emotions_scores)
                        
                        self.emotion_detected.emit(emotion, confidence, timestamp, distribution)
                    except Exception as e:
                        print(f"Error en detección de emoción: {e}")
            
            self.msleep(33)  # ~30 FPS

class EmotionLiveView(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user_data = user_data
        self.db = Database()
        self.emotion_thread = None
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Título
        title = QLabel("Reconocimiento de Emociones en Tiempo Real")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #333; margin-bottom: 20px;")
        layout.addWidget(title)
        
        # Layout principal horizontal
        main_layout = QHBoxLayout()
        
        # Panel izquierdo - Cámara
        camera_group = QGroupBox("📹 Cámara en Vivo")
        camera_layout = QVBoxLayout(camera_group)
        
        # Área de video
        self.video_label = QLabel()
        self.video_label.setMinimumSize(640, 480)
        self.video_label.setStyleSheet("""
            QLabel {
                border: 2px solid #ddd;
                border-radius: 10px;
                background-color: #f0f0f0;
            }
        """)
        self.video_label.setAlignment(Qt.AlignCenter)
        self.video_label.setText("Cámara no iniciada")
        camera_layout.addWidget(self.video_label)
        
        # Controles de cámara
        controls_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("🎥 Iniciar Cámara")
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        self.start_btn.clicked.connect(self.start_emotion_analysis)
        
        self.stop_btn = QPushButton("⏹️ Detener Cámara")
        self.stop_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        self.stop_btn.clicked.connect(self.stop_emotion_analysis)
        self.stop_btn.setEnabled(False)
        
        # Botón de exportar PDF
        self.export_btn = QPushButton("📄 Exportar Reporte PDF")
        self.export_btn.clicked.connect(self.export_to_pdf)
        self.export_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF9800;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #F57C00;
            }
        """)
        
        # Agregar botones al layout
        controls_layout.addWidget(self.start_btn)
        controls_layout.addWidget(self.stop_btn)
        controls_layout.addWidget(self.export_btn)
        controls_layout.addStretch()
        
        camera_layout.addLayout(controls_layout)
        main_layout.addWidget(camera_group, 2)
        
        # Panel derecho - Resultados
        results_group = QGroupBox("📊 Resultados de Emociones")
        results_layout = QVBoxLayout(results_group)
        
        # Emoción actual
        self.current_emotion_label = QLabel("Emoción Actual: Ninguna")
        self.current_emotion_label.setFont(QFont("Arial", 14, QFont.Bold))
        self.current_emotion_label.setStyleSheet("color: #333; padding: 10px; background-color: #f9f9f9; border-radius: 5px;")
        results_layout.addWidget(self.current_emotion_label)
        
        # Confianza
        self.confidence_label = QLabel("Confianza: 0%")
        self.confidence_label.setFont(QFont("Arial", 12))
        self.confidence_label.setStyleSheet("color: #666; padding: 5px;")
        results_layout.addWidget(self.confidence_label)
        
        # Historial de emociones
        history_label = QLabel("📝 Historial de Emociones:")
        history_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(history_label)
        
        self.emotion_history = QTextEdit()
        self.emotion_history.setMaximumHeight(300)
        self.emotion_history.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: white;
            }
        """)
        results_layout.addWidget(self.emotion_history)
        
        # Estadísticas rápidas
        stats_label = QLabel("📈 Estadísticas de la Sesión:")
        stats_label.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout.addWidget(stats_label)
        
        self.stats_text = QTextEdit()
        self.stats_text.setMaximumHeight(150)
        self.stats_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #ddd;
                border-radius: 5px;
                padding: 10px;
                background-color: #f9f9f9;
            }
        """)
        self.stats_text.setText("Sesión no iniciada")
        results_layout.addWidget(self.stats_text)
        
        # En el método setup_ui, después de crear results_group:
        main_layout.addWidget(results_group, 1)
        
        # Crear barras de progreso para emociones
        self.create_emotion_progress_bars()
        
        # Agregar el grupo de barras de progreso al layout
        main_layout.addWidget(self.progress_group)
        
        # Inicializar estadísticas
        self.emotion_counts = {}
        self.session_start = None
        layout.addLayout(main_layout)
    
    def start_emotion_analysis(self):
        """Iniciar análisis de emociones"""
        if self.emotion_thread is None:
            self.emotion_thread = EmotionLiveThread()
            self.emotion_thread.frame_ready.connect(self.update_video_frame)
            self.emotion_thread.emotion_detected.connect(self.on_emotion_detected)  # Ya actualizado para 4 parámetros
        
        if self.emotion_thread.start_analysis():
            self.start_btn.setEnabled(False)
            self.stop_btn.setEnabled(True)
            self.video_label.setText("Iniciando cámara...")
            self.session_start = datetime.now()
            self.emotion_counts = {}
            self.emotion_history.clear()
            self.stats_text.setText("Sesión iniciada...")
        else:
            self.video_label.setText("Error: No se pudo iniciar la cámara")
    
    def stop_emotion_analysis(self):
        """Detener análisis de emociones"""
        if self.emotion_thread:
            self.emotion_thread.stop_analysis()
            self.emotion_thread = None
        
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.video_label.setText("Cámara detenida")
        self.current_emotion_label.setText("Emoción Actual: Ninguna")
        self.confidence_label.setText("Confianza: 0%")
        
        # Mostrar resumen final
        if self.session_start:
            duration = datetime.now() - self.session_start
            summary = f"Sesión finalizada\nDuración: {duration}\n\nEmociones detectadas:\n"
            for emotion, count in self.emotion_counts.items():
                summary += f"- {emotion.capitalize()}: {count} veces\n"
            self.stats_text.setText(summary)
    
    def update_video_frame(self, frame):
        """Actualizar frame de video en la interfaz"""
        # Convertir frame de OpenCV a QImage
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(rgb_frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        
        # Escalar imagen para ajustar al label
        pixmap = QPixmap.fromImage(qt_image)
        scaled_pixmap = pixmap.scaled(self.video_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.video_label.setPixmap(scaled_pixmap)
    
    def on_emotion_detected(self, emotion, confidence, timestamp, distribution):
        """Manejar detección de emoción con distribución completa"""
        # Actualizar emoción actual con confianza real
        self.current_emotion_label.setText(f"Emoción Actual: {emotion.capitalize()}")
        self.confidence_label.setText(f"Confianza: {confidence*100:.1f}%")
        
        # Actualizar barras de progreso en tiempo real
        self.update_emotion_progress_bars(distribution)
        
        # Agregar al historial solo si la confianza es alta
        if confidence > 0.5:  # Solo registrar si confianza > 50%
            history_entry = f"[{timestamp}] {emotion.capitalize()} (Confianza: {confidence*100:.1f}%)\n"
            self.emotion_history.append(history_entry)
            
            # Actualizar estadísticas acumuladas
            if emotion in self.emotion_counts:
                self.emotion_counts[emotion] += 1
            else:
                self.emotion_counts[emotion] = 1
        
        # Actualizar estadísticas en tiempo real
        if self.session_start:
            duration = datetime.now() - self.session_start
            total_detections = sum(self.emotion_counts.values())
            
            stats = f"Duración: {str(duration).split('.')[0]}\n"
            stats += f"Total detecciones: {total_detections}\n"
            stats += f"Confianza actual: {confidence*100:.1f}%\n\n"
            
            if total_detections > 0:
                stats += "Distribución acumulada:\n"
                for emo, count in sorted(self.emotion_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_detections) * 100
                    stats += f"• {emo.capitalize()}: {count} ({percentage:.1f}%)\n"
            
            # Análisis de patrones
            stats += "\n🔍 Análisis de Patrones:\n"
            stats += self.analyze_emotion_patterns()
            
            self.stats_text.setText(stats)
        
        # Guardar en base de datos
        self.save_emotion_to_database(emotion, confidence, timestamp)
    
    def update_emotion_progress_bars(self, distribution=None):
        """Actualizar las barras de progreso de emociones en tiempo real"""
        if not hasattr(self, 'emotion_progress_bars'):
            return
        
        # Si tenemos distribución en tiempo real, usarla
        if distribution:
            for emotion, widgets in self.emotion_progress_bars.items():
                percentage = distribution.get(emotion, 0) * 100
                widgets['bar'].setValue(int(percentage))
                widgets['label'].setText(f"{percentage:.1f}%")
        else:
            # Usar estadísticas acumuladas
            total_detections = sum(self.emotion_counts.values()) if self.emotion_counts else 1
            
            for emotion, widgets in self.emotion_progress_bars.items():
                count = self.emotion_counts.get(emotion, 0)
                percentage = (count / total_detections) * 100 if total_detections > 0 else 0
                
                widgets['bar'].setValue(int(percentage))
                widgets['label'].setText(f"{count} ({percentage:.1f}%)")
    
    def analyze_emotion_patterns(self):
        """Analizar patrones en las emociones detectadas"""
        if not self.emotion_counts:
            return "No hay datos suficientes"
        
        total = sum(self.emotion_counts.values())
        patterns = []
        
        # Emoción dominante
        dominant_emotion = max(self.emotion_counts, key=self.emotion_counts.get)
        dominant_percentage = (self.emotion_counts[dominant_emotion] / total) * 100
        patterns.append(f"• Emoción dominante: {dominant_emotion.capitalize()} ({dominant_percentage:.1f}%)")
        
        # Estado emocional general
        positive_emotions = ['feliz', 'sorprendido']
        negative_emotions = ['triste', 'enojado', 'miedo', 'disgusto']
        
        positive_count = sum(self.emotion_counts.get(e, 0) for e in positive_emotions)
        negative_count = sum(self.emotion_counts.get(e, 0) for e in negative_emotions)
        neutral_count = self.emotion_counts.get('neutral', 0)
        
        if positive_count > negative_count:
            patterns.append("• Estado general: Positivo")
        elif negative_count > positive_count:
            patterns.append("• Estado general: Negativo")
        else:
            patterns.append("• Estado general: Neutral")
        
        # Variabilidad emocional
        unique_emotions = len([e for e in self.emotion_counts if self.emotion_counts[e] > 0])
        if unique_emotions >= 5:
            patterns.append("• Variabilidad: Alta (emociones diversas)")
        elif unique_emotions >= 3:
            patterns.append("• Variabilidad: Media")
        else:
            patterns.append("• Variabilidad: Baja (emociones limitadas)")
        
        return "\n".join(patterns)
    
    def save_emotion_to_database(self, emotion, confidence, timestamp):
        """Guardar emoción en la base de datos"""
        try:
            conn = self.db.connect()
            cursor = conn.cursor()
            
            # Insertar emoción (usando estudiante_id = 1 como ejemplo)
            cursor.execute("""
                INSERT INTO emociones (estudiante_id, emocion, confianza, fecha_registro, contexto)
                VALUES (?, ?, ?, ?, ?)
            """, (1, emotion, confidence, timestamp, "Sesión en vivo"))
            
            conn.commit()
            conn.close()
        except Exception as e:
            print(f"Error al guardar emoción en BD: {e}")
    
    def closeEvent(self, event):
        """Limpiar recursos al cerrar"""
        if self.emotion_thread:
            self.stop_emotion_analysis()
        event.accept()

    def create_emotion_progress_bars(self):
        """Crear barras de progreso para mostrar niveles de emociones"""
        self.progress_group = QGroupBox("Niveles de Emociones")
        progress_layout = QVBoxLayout()
        
        # Diccionario de emociones con colores
        emotions = {
            'happy': ('#4CAF50', 'Feliz'),
            'sad': ('#2196F3', 'Triste'), 
            'angry': ('#F44336', 'Enojado'),
            'surprised': ('#FF9800', 'Sorprendido'),
            'scared': ('#9C27B0', 'Asustado'),
            'disgusted': ('#795548', 'Disgustado'),
            'neutral': ('#607D8B', 'Neutral')
        }
        
        self.emotion_progress_bars = {}
        
        for emotion_key, (color, emotion_name) in emotions.items():
            # Crear layout horizontal para cada emoción
            emotion_layout = QHBoxLayout()
            
            # Etiqueta de la emoción
            emotion_label = QLabel(emotion_name)
            emotion_label.setMinimumWidth(100)
            emotion_layout.addWidget(emotion_label)
            
            # Barra de progreso
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            progress_bar.setValue(0)
            progress_bar.setStyleSheet(f"""
                QProgressBar {{
                    border: 1px solid #ddd;
                    border-radius: 5px;
                    text-align: center;
                    background-color: #f0f0f0;
                }}
                QProgressBar::chunk {{
                    background-color: {color};
                    border-radius: 4px;
                }}
            """)
            
            emotion_layout.addWidget(progress_bar)
            
            # Etiqueta de porcentaje
            percent_label = QLabel("0%")
            percent_label.setMinimumWidth(40)
            emotion_layout.addWidget(percent_label)
            
            progress_layout.addLayout(emotion_layout)
            
            # Guardar referencias
            self.emotion_progress_bars[emotion_key] = {
                'bar': progress_bar,
                'label': percent_label
            }
        
        self.progress_group.setLayout(progress_layout)

    def export_to_pdf(self):
        """Exportar estadísticas a PDF"""
        try:
            from reportlab.lib.pagesizes import letter, A4
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib import colors
            from datetime import datetime
            import os
            
            # Crear directorio de reportes si no existe
            reports_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'reports')
            os.makedirs(reports_dir, exist_ok=True)
            
            # Nombre del archivo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = os.path.join(reports_dir, f"reporte_emociones_{timestamp}.pdf")
            
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
            story.append(Paragraph("Reporte de Análisis de Emociones", title_style))
            story.append(Spacer(1, 12))
            
            # Información de la sesión
            if self.session_start:
                duration = datetime.now() - self.session_start
                session_info = f"""
                <b>Fecha:</b> {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}<br/>
                <b>Duración de la sesión:</b> {str(duration).split('.')[0]}<br/>
                <b>Total de detecciones:</b> {sum(self.emotion_counts.values())}<br/>
                """
                story.append(Paragraph(session_info, styles['Normal']))
                story.append(Spacer(1, 20))
            
            # Tabla de estadísticas
            if self.emotion_counts:
                total = sum(self.emotion_counts.values())
                data = [['Emoción', 'Cantidad', 'Porcentaje']]
                
                for emotion, count in sorted(self.emotion_counts.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total) * 100
                    data.append([emotion.capitalize(), str(count), f"{percentage:.1f}%"])
                
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
                
                story.append(Paragraph("Distribución de Emociones", styles['Heading2']))
                story.append(Spacer(1, 12))
                story.append(table)
                story.append(Spacer(1, 20))
            
            # Análisis de patrones
            story.append(Paragraph("Análisis de Patrones", styles['Heading2']))
            story.append(Spacer(1, 12))
            patterns = self.analyze_emotion_patterns()
            story.append(Paragraph(patterns.replace('\n', '<br/>'), styles['Normal']))
            
            # Generar PDF
            doc.build(story)
            
            # Mostrar mensaje de éxito
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(self, "Éxito", f"Reporte exportado exitosamente:\n{filename}")
            
        except ImportError:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Error", "Para exportar a PDF, instala: pip install reportlab")
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Error", f"Error al exportar PDF: {str(e)}")