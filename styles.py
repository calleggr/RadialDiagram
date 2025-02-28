from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

# Modern color scheme
COLORS = {
    'primary': '#2196F3',  # Material Blue
    'primary_light': '#64B5F6',
    'primary_dark': '#1976D2',
    'accent': '#FF4081',  # Pink accent
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text': '#212121',
    'text_secondary': '#757575',
    'divider': '#BDBDBD',
    'success': '#4CAF50',
    'warning': '#FFC107',
    'error': '#F44336',
    'toolbar': '#1E88E5',
    'hover': '#E3F2FD'
}

# Modern styling
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QToolBar {{
    background-color: {COLORS['toolbar']};
    border: none;
    padding: 6px;
    spacing: 8px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    border: none;
    border-radius: 4px;
    padding: 6px;
    color: white;
}}

QToolBar QToolButton:hover {{
    background-color: rgba(255, 255, 255, 0.1);
}}

QToolBar QToolButton:pressed {{
    background-color: rgba(255, 255, 255, 0.2);
}}

QToolBar QToolButton:checked {{
    background-color: rgba(255, 255, 255, 0.2);
}}

QPushButton {{
    background-color: {COLORS['primary']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['primary_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['primary_dark']};
}}

QSlider {{
    height: 24px;
}}

QSlider::groove:horizontal {{
    border: none;
    height: 4px;
    background: {COLORS['divider']};
    border-radius: 2px;
}}

QSlider::handle:horizontal {{
    background: {COLORS['primary']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS['primary_light']};
    width: 20px;
    height: 20px;
    margin: -8px 0;
    border-radius: 10px;
}}

QLabel {{
    color: {COLORS['text']};
    font-size: 12px;
}}

QInputDialog {{
    background-color: {COLORS['surface']};
}}

QInputDialog QLabel {{
    color: {COLORS['text']};
    font-size: 14px;
}}

QInputDialog QLineEdit {{
    padding: 8px;
    border: 1px solid {COLORS['divider']};
    border-radius: 4px;
    background: white;
}}

QInputDialog QPushButton {{
    min-width: 80px;
}}

QMessageBox {{
    background-color: {COLORS['surface']};
}}

QMessageBox QLabel {{
    color: {COLORS['text']};
    font-size: 14px;
}}

QColorDialog {{
    background-color: {COLORS['surface']};
}}
"""

def get_modern_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(COLORS['background']))
    palette.setColor(QPalette.WindowText, QColor(COLORS['text']))
    palette.setColor(QPalette.Base, QColor(COLORS['surface']))
    palette.setColor(QPalette.AlternateBase, QColor(COLORS['background']))
    palette.setColor(QPalette.ToolTipBase, QColor(COLORS['surface']))
    palette.setColor(QPalette.ToolTipText, QColor(COLORS['text']))
    palette.setColor(QPalette.Text, QColor(COLORS['text']))
    palette.setColor(QPalette.Button, QColor(COLORS['primary']))
    palette.setColor(QPalette.ButtonText, QColor('white'))
    palette.setColor(QPalette.Highlight, QColor(COLORS['primary']))
    palette.setColor(QPalette.HighlightedText, QColor('white'))
    return palette
