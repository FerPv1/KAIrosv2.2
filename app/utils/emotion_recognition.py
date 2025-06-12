import cv2
import numpy as np
from deepface import DeepFace
import random

class EmotionRecognition:
    def __init__(self):
        self.emotions = ['happy', 'sad', 'angry', 'surprised', 'scared', 'disgusted', 'neutral']
        self.emotion_history = {}
        self.confidence_threshold = 0.3  # Umbral mínimo de confianza
    
    def detect_emotion(self, image):
        """Detectar emoción en una imagen con confianza real"""
        try:
            # Convertir imagen a RGB si es necesario
            if len(image.shape) == 2 or image.shape[2] == 1:
                image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
            elif image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
            elif image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Analizar la emoción con DeepFace
            result = DeepFace.analyze(image, actions=['emotion'], enforce_detection=False)
            
            if isinstance(result, list):
                result = result[0]  # Tomar el primer rostro si hay varios
            
            # Obtener todas las emociones y sus probabilidades
            emotions_scores = result['emotion']
            dominant_emotion = result['dominant_emotion']
            
            # Obtener la confianza real de la emoción dominante
            confidence = emotions_scores[dominant_emotion] / 100.0  # DeepFace devuelve porcentajes
            
            # Mapear emociones de DeepFace a nuestro sistema
            emotion_mapping = {
                'happy': 'happy',
                'sad': 'sad',
                'angry': 'angry',
                'surprise': 'surprised',
                'fear': 'scared',
                'disgust': 'disgusted',
                'neutral': 'neutral'
            }
            
            mapped_emotion = emotion_mapping.get(dominant_emotion, 'neutral')
            
            # Solo devolver si la confianza es suficiente
            if confidence >= self.confidence_threshold:
                return mapped_emotion, confidence, emotions_scores
            else:
                return 'neutral', confidence, emotions_scores
                
        except Exception as e:
            print(f"Error al detectar emoción: {str(e)}")
            # Devolver valores por defecto en caso de error
            return 'neutral', 0.0, {}
    
    def get_emotion_distribution(self, emotions_scores):
        """Obtener distribución de todas las emociones"""
        distribution = {}
        emotion_mapping = {
            'happy': 'happy',
            'sad': 'sad', 
            'angry': 'angry',
            'surprise': 'surprised',
            'fear': 'scared',
            'disgust': 'disgusted',
            'neutral': 'neutral'
        }
        
        for deepface_emotion, our_emotion in emotion_mapping.items():
            if deepface_emotion in emotions_scores:
                distribution[our_emotion] = emotions_scores[deepface_emotion] / 100.0
            else:
                distribution[our_emotion] = 0.0
                
        return distribution
    
    # Nueva función: Registrar historial de emociones por estudiante
    def record_emotion(self, student_id, emotion, timestamp):
        """Registrar emoción en el historial del estudiante"""
        if student_id not in self.emotion_history:
            self.emotion_history[student_id] = []
        
        self.emotion_history[student_id].append({
            'emotion': emotion,
            'timestamp': timestamp
        })
    
    # Nueva función: Analizar tendencias emocionales
    def analyze_emotion_trends(self, student_id, start_date=None, end_date=None):
        """Analizar tendencias emocionales de un estudiante en un período"""
        if student_id not in self.emotion_history:
            return {}
        
        # Filtrar por fechas si se especifican
        emotions = self.emotion_history[student_id]
        # Implementar filtrado por fechas aquí
        
        # Contar frecuencia de cada emoción
        emotion_counts = {emotion: 0 for emotion in self.emotions}
        for entry in emotions:
            if entry['emotion'] in emotion_counts:
                emotion_counts[entry['emotion']] += 1
        
        return emotion_counts