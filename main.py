import sys
import os
from PySide6.QtWidgets import QApplication
from app.views.login_view import LoginWindow
from app.models.database import Database

def main():
    # Asegurar que existan los directorios necesarios
    os.makedirs("data/facial_data", exist_ok=True)
    
    # Inicializar la base de datos
    db = Database()
    db.setup()
    
    # Iniciar la aplicación
    app = QApplication(sys.argv)
    app.setApplicationName("KairosApp")
    
    # Mostrar ventana de login
    login_window = LoginWindow()
    login_window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()