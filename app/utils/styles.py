import os
from PySide6.QtGui import QColor, QFont, QPalette, QIcon
from PySide6.QtCore import Qt

class AppStyles:
    # Paleta de colores sobria y elegante
    PRIMARY_COLOR = "#2c3e50"  # Azul oscuro
    SECONDARY_COLOR = "#3498db"  # Azul claro
    ACCENT_COLOR = "#e74c3c"  # Rojo suave
    BACKGROUND_COLOR = "#f5f5f5"  # Gris muy claro
    TEXT_COLOR = "#333333"  # Casi negro
    LIGHT_TEXT_COLOR = "#ffffff"  # Blanco
    
    # Fuentes
    TITLE_FONT = QFont("Segoe UI", 18, QFont.Bold)
    SUBTITLE_FONT = QFont("Segoe UI", 14)
    NORMAL_FONT = QFont("Segoe UI", 10)
    SMALL_FONT = QFont("Segoe UI", 8)
    
    # Estilos para widgets
    @staticmethod
    def get_button_style(primary=True):
        if primary:
            return f"QPushButton {{ \
                        background-color: {AppStyles.SECONDARY_COLOR}; \
                        color: {AppStyles.LIGHT_TEXT_COLOR}; \
                        border: none; \
                        border-radius: 4px; \
                        padding: 8px 16px; \
                        font-weight: bold; \
                    }} \
                    QPushButton:hover {{ \
                        background-color: {AppStyles.PRIMARY_COLOR}; \
                    }} \
                    QPushButton:pressed {{ \
                        background-color: #1a2530; \
                    }}"
        else:
            return f"QPushButton {{ \
                        background-color: transparent; \
                        color: {AppStyles.SECONDARY_COLOR}; \
                        border: 1px solid {AppStyles.SECONDARY_COLOR}; \
                        border-radius: 4px; \
                        padding: 8px 16px; \
                    }} \
                    QPushButton:hover {{ \
                        background-color: rgba(52, 152, 219, 0.1); \
                    }}"
    
    @staticmethod
    def get_sidebar_style():
        return f"QWidget {{ \
                    background-color: {AppStyles.PRIMARY_COLOR}; \
                    color: {AppStyles.LIGHT_TEXT_COLOR}; \
                }}"
    
    @staticmethod
    def get_sidebar_button_style():
        return f"QPushButton {{ \
                    background-color: transparent; \
                    color: {AppStyles.LIGHT_TEXT_COLOR}; \
                    border: none; \
                    border-radius: 0; \
                    padding: 12px; \
                    text-align: left; \
                    font-size: 14px; \
                }} \
                QPushButton:hover {{ \
                    background-color: rgba(255, 255, 255, 0.1); \
                }} \
                QPushButton:checked {{ \
                    background-color: {AppStyles.SECONDARY_COLOR}; \
                    font-weight: bold; \
                }}"
    
    @staticmethod
    def get_group_box_style():
        return f"QGroupBox {{ \
                    border: 1px solid #dddddd; \
                    border-radius: 6px; \
                    margin-top: 12px; \
                    font-weight: bold; \
                }} \
                QGroupBox::title {{ \
                    subcontrol-origin: margin; \
                    left: 10px; \
                    padding: 0 5px; \
                }}"
    
    @staticmethod
    def get_table_style():
        return f"QTableWidget {{ \
                    border: 1px solid #dddddd; \
                    gridline-color: #f0f0f0; \
                    selection-background-color: {AppStyles.SECONDARY_COLOR}; \
                    selection-color: {AppStyles.LIGHT_TEXT_COLOR}; \
                }} \
                QHeaderView::section {{ \
                    background-color: {AppStyles.PRIMARY_COLOR}; \
                    color: {AppStyles.LIGHT_TEXT_COLOR}; \
                    padding: 6px; \
                    font-weight: bold; \
                    border: none; \
                }}"
    
    @staticmethod
    def get_input_style():
        return "QLineEdit, QComboBox, QDateEdit { \
                    border: 1px solid #dddddd; \
                    border-radius: 4px; \
                    padding: 8px; \
                } \
                QLineEdit:focus, QComboBox:focus, QDateEdit:focus { \
                    border: 1px solid #3498db; \
                }"
    
    @staticmethod
    def get_line_edit_style():
        return AppStyles.get_input_style()
    
    # Iconos
    @staticmethod
    def get_icon_path(icon_name):
        icons_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "resources", "icons")
        return os.path.join(icons_dir, f"{icon_name}.png")