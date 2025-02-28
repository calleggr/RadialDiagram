from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt

# Modern color scheme
COLORS = {
    'segment1': '#00BCD4',  # Turquoise
    'segment2': '#2196F3',  # Blue 
    'segment3': '#E91E63',  # Pink
    'segment4': '#F44336',  # Red
    'segment1_light': '#4DD0E1',
    'segment2_light': '#64B5F6',
    'segment3_light': '#F06292',
    'segment4_light': '#EF5350',
    'background': '#FAFAFA',
    'surface': '#FFFFFF',
    'text': '#212121',
    'text_secondary': '#757575',
    'divider': '#BDBDBD',
    'error': '#F44336'
}

# Modern styling
STYLESHEET = f"""
QMainWindow {{
    background-color: {COLORS['background']};
}}

QToolBar {{
    background-color: {COLORS['segment2']};
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
    background-color: {COLORS['segment2']};
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}}

QPushButton:hover {{
    background-color: {COLORS['segment2_light']};
}}

QPushButton:pressed {{
    background-color: {COLORS['segment2']};
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
    background: {COLORS['segment2']};
    border: none;
    width: 16px;
    height: 16px;
    margin: -6px 0;
    border-radius: 8px;
}}

QSlider::handle:horizontal:hover {{
    background: {COLORS['segment2_light']};
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
    palette.setColor(QPalette.Button, QColor(COLORS['segment2']))
    palette.setColor(QPalette.ButtonText, QColor('white'))
    palette.setColor(QPalette.Highlight, QColor(COLORS['segment2']))
    palette.setColor(QPalette.HighlightedText, QColor('white'))
    return palette
