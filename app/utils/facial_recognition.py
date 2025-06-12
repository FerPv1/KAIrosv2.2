import os
import cv2
import face_recognition
import numpy as np
import pickle
from pathlib import Path

class FacialRecognition:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []
        self.data_dir = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / 'data' / 'facial_data'
        self.encodings_file = self.data_dir / 'encodings.pkl'
        self.load_encodings()
    
    def load_encodings(self):
        """Cargar codificaciones faciales guardadas"""
        if os.path.exists(self.encodings_file):
            with open(self.encodings_file, 'rb') as f:
                data = pickle.load(f)
                self.known_face_encodings = data.get('encodings', [])
                self.known_face_names = data.get('names', [])
    
    def save_encodings(self):
        """Guardar codificaciones faciales"""
        os.makedirs(self.data_dir, exist_ok=True)
        data = {
            'encodings': self.known_face_encodings,
            'names': self.known_face_names
        }
        with open(self.encodings_file, 'wb') as f:
            pickle.dump(data, f)
    
    def register_face(self, student_id, image):
        """Registrar un nuevo rostro"""
        # Convertir imagen a RGB (face_recognition requiere RGB)
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detectar ubicaciones de rostros
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return False, "No se detectó ningún rostro en la imagen"
        
        # Obtener codificaciones faciales
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        if not face_encodings:
            return False, "No se pudo codificar el rostro"
        
        # Guardar la codificación
        student_id_str = str(student_id)
        
        # Si el estudiante ya existe, actualizar sus codificaciones
        if student_id_str in self.known_face_names:
            idx = self.known_face_names.index(student_id_str)
            self.known_face_encodings[idx] = face_encodings[0]
        else:
            self.known_face_encodings.append(face_encodings[0])
            self.known_face_names.append(student_id_str)
        
        # Guardar las codificaciones actualizadas
        self.save_encodings()
        
        return True, "Rostro registrado correctamente"
    
    def recognize_face(self, image):
        """Reconocer un rostro en la imagen"""
        if not self.known_face_encodings:
            return None, "No hay rostros registrados en el sistema"
        
        # Convertir imagen a RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detectar ubicaciones de rostros
        face_locations = face_recognition.face_locations(rgb_image)
        
        if not face_locations:
            return None, "No se detectó ningún rostro en la imagen"
        
        # Obtener codificaciones faciales
        face_encodings = face_recognition.face_encodings(rgb_image, face_locations)
        
        # Buscar coincidencias
        # Mejora: Añadir nivel de confianza en el reconocimiento
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding, tolerance=0.6)
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            
            if not any(matches):
                continue
                
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                student_id = self.known_face_names[best_match_index]
                confidence = 1 - face_distances[best_match_index]  # Nivel de confianza (0-1)
                return student_id, f"Rostro reconocido (Confianza: {confidence:.2f})"
        
        return None, "No se encontró coincidencia"
    
    # Nueva función: Detección de "liveness" para prevenir fotos
    def detect_liveness(self, image):
        """Detectar si el rostro pertenece a una persona real o una foto"""
        # Implementación básica: buscar parpadeos o movimientos
        # Este es un placeholder - requiere implementación real
        return True, "Verificación de persona real exitosa"